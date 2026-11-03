/* Native Remotion render. Uses bundled Chromium; v001/v002 outputs are untouched. */
const fs=require('node:fs');
const path=require('node:path');
const {bundle}=require('@remotion/bundler');
const {selectComposition,renderStill,renderMedia,openBrowser}=require('@remotion/renderer');
const config=require('./timeline.json');
const project=path.resolve(__dirname,'../..');
const root=path.resolve(project,'../..');
const work=path.join(project,'working/v004');
const previews=path.join(project,'previews/v004');
const mode=process.argv[2]||'preview';
if(!['stills','seek','preview','final','diagnosis','accents'].includes(mode))throw new Error(`Unknown render mode: ${mode}`);
const output=mode==='final'?path.join(root,'output/tvc-driving-premium/yen-thanh-tvc-v004.mp4'):path.join(previews,'yen-thanh-v004-opening.mp4');

(async()=>{
  fs.mkdirSync(work,{recursive:true});fs.mkdirSync(previews,{recursive:true});
  if((mode==='final'||mode==='preview')&&fs.existsSync(output))throw new Error(`Refusing to overwrite ${output}`);
  const serveUrl=await bundle({entryPoint:path.join(__dirname,'entry.tsx'),publicDir:path.join(project,'public/v004'),outDir:path.join(work,'bundle'),onProgress:p=>{if(p===100)console.log('V004 bundle ready')}});
  const browser=await openBrowser('chrome');
  const browserErrors=[];
  const onBrowserLog=log=>{if(log.type==='error'){browserErrors.push(log.text);console.error('Browser:',log.text)}};
  try{
    const composition=await selectComposition({serveUrl,id:mode==='diagnosis'?'AccentDiagnosis':mode==='accents'?'AccentRegression':'YenThanhV4',puppeteerInstance:browser,onBrowserLog});
    if(mode==='diagnosis'){
      await renderStill({serveUrl,composition,puppeteerInstance:browser,frame:0,output:path.join(previews,'accent-diagnosis.png'),imageFormat:'png',onBrowserLog});
    }else if(mode==='accents'){
      const reference=await selectComposition({serveUrl,id:'AccentReference',puppeteerInstance:browser,onBrowserLog});
      await renderStill({serveUrl,composition:reference,puppeteerInstance:browser,frame:72,output:path.join(previews,'accent-reference.png'),imageFormat:'png',onBrowserLog});
      for(const frame of [8,14,20,28,40,60,72]){
        await renderStill({serveUrl,composition,puppeteerInstance:browser,frame,output:path.join(previews,`accent-${String(frame).padStart(4,'0')}.png`),imageFormat:'png',onBrowserLog});
      }
    }else if(mode==='stills'||mode==='seek'){
      const frames=mode==='seek'?[420,18,916,220,132,674,52,960,334,812,272,620,530,695,755,855]:config.previewFrames;
      for(const frame of frames){
        await renderStill({serveUrl,composition,puppeteerInstance:browser,frame,output:path.join(previews,`${mode}-${String(frame).padStart(4,'0')}.png`),imageFormat:'png',onBrowserLog});
        console.log(`Rendered ${mode} frame ${frame}`);
      }
    }else{
      let last=-1;
      await renderMedia({serveUrl,composition,puppeteerInstance:browser,codec:'h264',outputLocation:output,
        crf:16,x264Preset:'medium',pixelFormat:'yuv420p',colorSpace:'bt709',imageFormat:'png',
        audioCodec:'aac',audioBitrate:'320k',concurrency:3,overwrite:false,
        frameRange:mode==='preview'?[0,287]:undefined,
        onBrowserLog,onProgress:p=>{const n=Math.floor(p.progress*100/5)*5;if(n!==last){last=n;console.log(`${mode}: ${n}% (${p.renderedFrames} frames)`);}}});
      console.log(`Rendered: ${output}`);
    }
    fs.writeFileSync(path.join(work,`render-${mode}-receipt.json`),JSON.stringify({mode,composition:{id:composition.id,width:composition.width,height:composition.height,fps:composition.fps,durationInFrames:composition.durationInFrames},browserErrors,completedAt:new Date().toISOString()},null,2));
    if(browserErrors.length)throw new Error('Browser errors were recorded; inspect receipt');
  }finally{await browser.close({silent:true})}
})().catch(e=>{console.error(e);process.exitCode=1});
