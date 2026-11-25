const fs = require('node:fs');
const path = require('node:path');
const {gsap} = require('gsap');
const {bundle} = require('@remotion/bundler');
const {openBrowser, renderStill, selectComposition} = require('@remotion/renderer');
const plan = require('./timeline.json');

const project = path.resolve(__dirname, '../..');
const root = path.resolve(project, '../..');
const work = path.join(project, 'working/v005');
const artwork = path.join(work, 'lettering');
const browserPath = path.join(root, 'projects/tvc-thanh-vinh-premium/node_modules/.remotion/chrome-headless-shell',
  'win64/chrome-headless-shell-win64/chrome-headless-shell.exe');

function samples(ease) {
  const value = gsap.parseEase(ease);
  return Array.from({length: 513}, (_, i) => value(i / 512));
}

function writeMotion() {
  const lettering = Array.from({length: 4}, () => ({alpha: 0, y: 22, rule: .03}));
  const leave = Array.from({length: 4}, () => ({alpha: 1, y: 0, rule: 1}));
  const arrival = gsap.timeline({paused: true});
  const departure = gsap.timeline({paused: true});
  lettering.forEach((layer, index) => {
    arrival.to(layer, {alpha: 1, y: 0, rule: 1, duration: index === 3 ? .91 : 1.08, ease: 'power3.out'}, index * .16);
  });
  leave.forEach((layer, index) => {
    departure.to(layer, {alpha: 0, y: -15, rule: .48, duration: .76, ease: 'sine.inOut'}, index * .075);
  });
  const snapshot = (layers) => layers.map(({alpha, y, rule}) => [alpha, y, rule]);
  const atFps = (timeline, layers) => Array.from({length: Math.ceil(timeline.duration() * plan.fps) + 2}, (_, frame) => {
    timeline.time(frame / plan.fps);
    return snapshot(layers);
  });
  fs.writeFileSync(path.join(work, 'motion.json'), JSON.stringify({
    fps: plan.fps,
    titleIn: atFps(arrival, lettering), titleOut: atFps(departure, leave),
    drift: samples('sine.inOut'), reveal: samples('power2.inOut'), layers: samples('power3.out'),
  }));
  arrival.kill();
  departure.kill();
}

async function main() {
  fs.mkdirSync(artwork, {recursive: true});
  writeMotion();
  const serveUrl = await bundle({entryPoint: path.join(__dirname, 'lettering.tsx'),
    publicDir: path.join(project, 'public/v005'), outDir: path.join(work, 'lettering-bundle')});
  const browser = await openBrowser('chrome', {browserExecutable: fs.existsSync(browserPath) ? browserPath : undefined});
  const errors = [];
  const onBrowserLog = ({type, text}) => {
    if (type === 'error') errors.push(text);
  };
  try {
    const ids = plan.chapters.flatMap((chapter) => chapter.scenes)
      .filter((scene) => scene.text).map((scene) => scene.text.id).concat('date');
    for (const cueId of ids) {
      const inputProps = {cueId};
      const composition = await selectComposition({
        serveUrl, id: 'WeddingLetterArtwork', inputProps, puppeteerInstance: browser, onBrowserLog,
      });
      await renderStill({serveUrl, composition, frame: 0, imageFormat: 'png', inputProps,
        output: path.join(artwork, cueId + '.png'), puppeteerInstance: browser, onBrowserLog});
    }
    if (errors.length) throw new Error(errors.join('\n'));
    console.log('Rendered ' + ids.length + ' lettering assets in Remotion and sampled the GSAP timelines at 50 fps.');
  } finally {
    await browser.close({silent: true});
  }
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
