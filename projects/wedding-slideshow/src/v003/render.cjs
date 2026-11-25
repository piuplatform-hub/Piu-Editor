const fs = require('node:fs');
const path = require('node:path');
const {createHash} = require('node:crypto');
const {spawnSync} = require('node:child_process');
const {bundle} = require('@remotion/bundler');
const {openBrowser, renderMedia, renderStill, selectComposition} = require('@remotion/renderer');

const project = path.resolve(__dirname, '../..');
const root = path.resolve(project, '../..');
const version = process.argv[3] || 'v003';
if (!['v003', 'v004'].includes(version)) throw new Error('Choose v003 or v004');
const source = path.join(project, 'src', version);
const plan = require(path.join(source, 'timeline.json'));
const working = path.join(project, 'working', version);
const preview = path.join(project, 'previews', version);
const publicDir = path.join(project, 'public', version);
const movie = path.join(preview, plan.movie || 'tu-hom-nay-v003-remotion.mp4');
const tools = path.join(project, 'node_modules/@remotion/compositor-win32-x64-msvc');
const chrome = path.join(root, 'projects/tvc-thanh-vinh-premium/node_modules/.remotion/chrome-headless-shell',
  'win64/chrome-headless-shell-win64/chrome-headless-shell.exe');

function binary(name, args) {
  const result = spawnSync(path.join(tools, name + '.exe'), args, {encoding: 'utf8', windowsHide: true});
  if (result.error || result.status !== 0) {
    throw result.error || new Error(result.stderr);
  }
  return result.stdout;
}

function checksum(filename) {
  return createHash('sha256').update(fs.readFileSync(filename)).digest('hex');
}

function mix(picture) {
  const pending = path.join(working, 'preview.pending.mp4');
  binary('ffmpeg', ['-v', 'error', '-nostdin', '-y', '-i', picture, '-i', path.join(working, 'music.wav'),
    '-map', '0:v:0', '-map', '1:a:0', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '256k',
    '-movflags', '+faststart', pending]);
  const report = JSON.parse(binary('ffprobe', ['-v', 'error', '-show_streams', '-show_format', '-of', 'json', pending]));
  const [video, audio] = report.streams;
  const duration = plan.durationInFrames / plan.fps;
  if (report.streams.length !== 2 || video.width !== 1920 || video.height !== 1080 ||
    video.codec_name !== 'h264' || video.pix_fmt !== 'yuv420p' || video.color_space !== 'bt709' ||
    video.avg_frame_rate !== plan.fps + '/1' || Number(video.nb_frames) !== plan.durationInFrames ||
    audio.codec_name !== 'aac' || Number(audio.sample_rate) !== 48000 || audio.channels !== 2 ||
    [video.duration, audio.duration, report.format.duration].some((value) => Math.abs(Number(value) - duration) > .005)) {
    throw new Error('Encoded preview does not match the timeline and audio mix');
  }
  binary('ffmpeg', ['-v', 'error', '-xerror', '-nostdin', '-i', pending, '-map', '0:v:0', '-map', '0:a:0',
    '-c:v', 'rawvideo', '-c:a', 'pcm_s16le', '-f', 'null', '-']);
  fs.renameSync(pending, movie);
  fs.writeFileSync(path.join(working, 'preview-qa.json'), JSON.stringify({
    video: path.relative(root, movie), bytes: fs.statSync(movie).size, sha256: checksum(movie),
    duration, frames: plan.durationInFrames, fps: plan.fps, width: video.width, height: video.height,
    audio: 'AAC 48000 Hz stereo', fullDecode: true,
  }, null, 2) + '\n');
  console.log('Saved ' + movie);
}

async function main() {
  const mode = process.argv[2];
  if (!['stills', 'render'].includes(mode)) throw new Error('Choose stills or render');
  if (mode === 'render' && fs.existsSync(movie)) throw new Error('Preview already exists: ' + movie);
  fs.mkdirSync(working, {recursive: true});
  fs.mkdirSync(preview, {recursive: true});
  const serveUrl = await bundle({
    entryPoint: path.join(source, 'entry.tsx'), publicDir, outDir: path.join(working, 'bundle'),
  });
  const browser = await openBrowser('chrome', {browserExecutable: fs.existsSync(chrome) ? chrome : undefined});
  const errors = [];
  const onBrowserLog = ({type, text}) => {
    if (type === 'error') {
      errors.push(text);
      console.error(text);
    }
  };
  try {
    const composition = await selectComposition({
      serveUrl, id: 'TuHomNayPreview', puppeteerInstance: browser, onBrowserLog,
    });
    if (mode === 'stills') {
      const smokeFrames = plan.stillFrames || [66, 386, 999, 353, 684, 1189, 66];
      const paths = [];
      for (const [index, frame] of smokeFrames.entries()) {
        const output = path.join(preview, 'check-' + (index + 1) + '-' + frame + '.png');
        await renderStill({serveUrl, composition, frame, imageFormat: 'png', output,
          puppeteerInstance: browser, onBrowserLog});
        paths.push(output);
      }
      if (checksum(paths[0]) !== checksum(paths.at(-1))) {
        throw new Error('The same frame differs after out-of-order timeline seeking');
      }
      if (errors.length) throw new Error('Browser errors during stills');
      console.log('Rendered smoke stills. Frame ' + smokeFrames[0] + ' repeats exactly after out-of-order seeks.');
      return;
    }
    const rawPicture = path.join(working, 'picture.mp4');
    let lastPercent = -1;
    await renderMedia({
      serveUrl, composition, codec: 'h264', crf: 17, x264Preset: 'fast',
      pixelFormat: 'yuv420p', colorSpace: 'bt709', imageFormat: 'jpeg', jpegQuality: 95, muted: true,
      concurrency: 5, outputLocation: rawPicture, overwrite: true, puppeteerInstance: browser, onBrowserLog,
      onProgress: ({progress, renderedFrames}) => {
        const percent = Math.floor(progress * 10) * 10;
        if (percent !== lastPercent) {
          lastPercent = percent;
          console.log(percent + '% · ' + renderedFrames + '/' + plan.durationInFrames + ' frames');
        }
      },
    });
    if (errors.length) throw new Error('Browser errors during preview render');
    mix(rawPicture);
  } finally {
    await browser.close({silent: true});
  }
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
