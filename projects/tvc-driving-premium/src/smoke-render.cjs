require('./remotion-file-stdio.cjs');
const path=require('node:path');
const {bundle}=require('@remotion/bundler');
const {openBrowser,selectComposition,renderStill}=require('@remotion/renderer');
(async()=>{
 const root=path.resolve(__dirname,'..');
 const serveUrl=await bundle({entryPoint:path.join(__dirname,'remotion-smoke.tsx'),outDir:path.join(root,'working/smoke-bundle'),publicDir:path.join(root,'public'),rspack:true,onProgress:p=>{if(p===100)console.log('Bundle ready')}});
 let browser;
 try {
  browser=await openBrowser('chrome',{logLevel:'info'});
  const composition=await selectComposition({serveUrl,id:'Smoke',puppeteerInstance:browser});
  await renderStill({serveUrl,composition,puppeteerInstance:browser,frame:10,output:path.join(root,'previews/remotion-working.png'),imageFormat:'png',disableSharedMemoryCapture:true});
  console.log('REMOTION SMOKE RENDER SUCCEEDED');
 }finally{if(browser)await browser.close({silent:true});}
})().catch(e=>{console.error(e);process.exitCode=1});
