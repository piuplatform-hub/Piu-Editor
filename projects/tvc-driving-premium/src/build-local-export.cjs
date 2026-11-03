const path=require('node:path'),fs=require('node:fs'),{rspack}=require('@rspack/core');
const out=path.resolve(__dirname,'../working/v002-ui');fs.mkdirSync(out,{recursive:true});
const compiler=rspack({mode:'production',entry:path.join(__dirname,'local-export-app.tsx'),output:{path:out,filename:'app.js'},resolve:{extensions:['.tsx','.ts','.js']},optimization:{minimize:false},module:{rules:[{test:/\.tsx?$/,loader:'builtin:swc-loader',options:{jsc:{parser:{syntax:'typescript',tsx:true},transform:{react:{runtime:'automatic'}}}}}]}});
compiler.run((err,stats)=>{compiler.close(()=>{});if(err||stats.hasErrors()){console.error(err||stats.toString({all:false,errors:true}));process.exitCode=1;return}
fs.writeFileSync(path.join(out,'index.html'),'<!doctype html><html lang="vi"><meta charset="utf-8"><title>Piu Editor · Remotion TVC v002</title><div id="root"></div><script src="/app.js"></script></html>');console.log('LOCAL REMOTION EXPORT APP READY');});
