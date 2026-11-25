const fs = require('node:fs');
const path = require('node:path');
const {spawnSync} = require('node:child_process');
const {bundle} = require('@remotion/bundler');
const {openBrowser, selectComposition, renderStill, renderMedia} = require('@remotion/renderer');
const timeline = require('./timeline.json');

const project = path.resolve(__dirname, '..');
const workspace = path.resolve(project, '../..');
const work = path.join(project, 'working/v001');
const stills = path.join(project, 'previews/v001');
const publicDir = path.join(project, 'public');
const deliverable = path.join(workspace, 'output/wedding-opener/tu-hom-nay-v001.mp4');
const bindings = path.join(project, 'node_modules/@remotion/compositor-win32-x64-msvc');
const sharedChrome = path.join(workspace, 'projects/tvc-thanh-vinh-premium/node_modules/.remotion/chrome-headless-shell',
  'win64/chrome-headless-shell-win64/chrome-headless-shell.exe');
const totalFrames = timeline.shots.at(-1).endFrame;
const endCardStart = timeline.shots.at(-2).endFrame;

function readDetails() {
  const file = path.join(project, 'working/wedding-details.json');
  if (!fs.existsSync(file)) return {};
  const saved = JSON.parse(fs.readFileSync(file, 'utf8'));
  return Object.fromEntries(['brideName', 'groomName', 'weddingDate']
    .filter((key) => typeof saved[key] === 'string')
    .map((key) => [key, saved[key].trim().normalize('NFC')]));
}

function ffmpeg(args) {
  const result = spawnSync(path.join(bindings, 'ffmpeg.exe'), args, {encoding: 'utf8', windowsHide: true});
  if (result.error || result.status !== 0) throw result.error || new Error(result.stderr);
}

function pictureFrames() {
  const frames = new Set([24, 73, endCardStart + 25, totalFrames - 2]);
  let start = 0;
  for (const shot of timeline.shots) {
    frames.add(Math.round((start + shot.endFrame) / 2));
    if (shot.transition === 'curtain') {
      for (const after of [-1, 3, 13, 31, 65]) frames.add(start + after);
    }
    start = shot.endFrame;
  }
  return [...frames].sort((a, b) => a - b);
}

async function main() {
  const mode = process.argv[2] ?? 'stills';
  if (mode !== 'stills' && mode !== 'final') throw new Error(`Unknown render mode: ${mode}`);
  if (mode === 'final' && fs.existsSync(deliverable)) throw new Error(`V001 already exists: ${deliverable}`);
  fs.mkdirSync(work, {recursive: true});
  fs.mkdirSync(stills, {recursive: true});
  const serveUrl = await bundle({entryPoint: path.join(__dirname, 'entry.tsx'), publicDir,
    outDir: path.join(work, 'bundle')});
  const browser = await openBrowser('chrome', {
    browserExecutable: process.env.PIU_WEDDING_CHROME || (fs.existsSync(sharedChrome) ? sharedChrome : undefined),
  });
  const browserErrors = [];
  const onBrowserLog = (log) => {
    if (log.type === 'error') {
      browserErrors.push(log.text);
      console.error(log.text);
    }
  };

  try {
    let details = readDetails();
    let composition = await selectComposition({serveUrl, id: 'TuHomNay', inputProps: details,
      puppeteerInstance: browser, onBrowserLog});
    if (mode === 'stills') {
      const frames = pictureFrames();
      for (const frame of frames) {
        await renderStill({serveUrl, composition, frame, inputProps: details, imageFormat: 'png',
          output: path.join(stills, `frame-${String(frame).padStart(4, '0')}.png`),
          puppeteerInstance: browser, onBrowserLog});
      }
      console.log(`Rendered ${frames.length} stills`);
    } else {
      const renderPart = async (label, from, to) => {
        let lastReported = -1;
        await renderMedia({serveUrl, composition, inputProps: details, codec: 'h264', crf: 17,
          colorSpace: 'bt709', pixelFormat: 'yuv420p', imageFormat: 'jpeg', jpegQuality: 99,
          x264Preset: 'fast', muted: true, concurrency: 5, frameRange: [from, to],
          outputLocation: path.join(work, `${label}.mp4`), overwrite: true, puppeteerInstance: browser,
          onBrowserLog, onProgress: ({progress, renderedFrames}) => {
            const percent = Math.floor(progress * 20) * 5;
            if (lastReported !== percent) {
              lastReported = percent;
              console.log(`${label} ${percent}% (${renderedFrames}/${to - from + 1} frames)`);
            }
          }});
      };
      await renderPart('main-picture', 0, endCardStart - 1);

      details = readDetails();
      composition = await selectComposition({serveUrl, id: 'TuHomNay', inputProps: details,
        puppeteerInstance: browser, onBrowserLog});
      await renderPart('end-card', endCardStart, totalFrames - 1);

      if (browserErrors.length) throw new Error('Browser errors occurred during render');
      const concat = path.join(work, 'picture-parts.txt');
      fs.writeFileSync(concat, `file 'main-picture.mp4'\nduration ${(endCardStart / timeline.fps).toFixed(6)}\nfile 'end-card.mp4'\n`);
      const pending = path.join(work, 'tu-hom-nay-combined.mp4');
      ffmpeg(['-v', 'error', '-y', '-f', 'concat', '-safe', '1', '-i', concat,
        '-i', path.join(publicDir, 'soundtrack.wav'), '-map', '0:v:0', '-map', '1:a:0',
        '-map_metadata', '-1', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '256k',
        '-metadata', 'title=Từ hôm nay', '-metadata', 'comment=Nhạc: Ngày Đầu Tiên — Đức Phúc',
        '-movflags', '+faststart', pending]);
      fs.mkdirSync(path.dirname(deliverable), {recursive: true});
      if (fs.existsSync(deliverable)) throw new Error(`V001 already exists: ${deliverable}`);
      fs.renameSync(pending, deliverable);
      console.log(`Saved ${deliverable}`);
    }

    if (browserErrors.length) throw new Error('Browser errors occurred during render');
    fs.writeFileSync(path.join(work, `render-${mode}.json`), JSON.stringify({
      mode, totalFrames, details, endCardStart, width: composition.width, height: composition.height,
      fps: composition.fps, browserErrors, completedAt: new Date().toISOString(),
    }, null, 2) + '\n');
  } finally {
    await browser.close({silent: true});
  }
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
