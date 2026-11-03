/* Windows runtime compatibility: this host supports file-backed child stdio,
 * but Node's anonymous pipe creation returns EPERM. No permission changes.
 * Applies only to the bundled Remotion headless browser; no vendor files edited.
 */
const cp = require('node:child_process');
const fs = require('node:fs');
const path = require('node:path');
const {PassThrough} = require('node:stream');
const originalSpawn = cp.spawn;
const originalExec = cp.exec;
const ownedBrowsers = new Map();
const logs = path.resolve(__dirname, '../working/remotion-v002-browser');
fs.mkdirSync(logs, {recursive:true});

cp.spawn = function(executable, args, options={}) {
  if (path.basename(String(executable)).toLowerCase() !== 'chrome-headless-shell.exe')
    return originalSpawn.call(this, executable, args, options);
  const stamp = `${Date.now()}-${Math.random().toString(36).slice(2,7)}`;
  const names = ['stdout','stderr'].map(n=>path.join(logs, `${stamp}-${n}.log`));
  const fds = names.map(n=>fs.openSync(n,'w+'));
  let child;
  // This host does not provide Chromium's multi-process IPC channels either.
  // Keep rendering in the bundled browser's single process, without changing
  // filesystem/network permissions or modifying the installed executable.
  const launchArgs=[...args.filter(a=>a!=='--remotion-shared-memory-capture'),'--single-process','--in-process-gpu'];
  try {child = originalSpawn.call(this, executable, launchArgs, {...options, stdio:['ignore', ...fds]});}
  catch(e) {fds.forEach(fd=>fs.closeSync(fd)); throw e;}
  const streams = names.map(()=>new PassThrough());
  child.stdout=streams[0]; child.stderr=streams[1];
  const offsets=[0,0];
  const pump=()=>fds.forEach((fd,i)=>{
    const size=fs.fstatSync(fd).size;
    if(size>offsets[i]) {
      const b=Buffer.alloc(size-offsets[i]);
      fs.readSync(fd,b,0,b.length,offsets[i]); offsets[i]=size;
      streams[i].write(b);
    }
  });
  const timer=setInterval(pump,40);
  streams.forEach(s=>{s.ref=()=>timer.ref();s.unref=()=>timer.unref();});
  if(child.pid)ownedBrowsers.set(child.pid,child);
  child.once('close',()=>{
    clearInterval(timer);pump();fds.forEach(fd=>fs.closeSync(fd));
    streams.forEach(s=>s.end());ownedBrowsers.delete(child.pid);
  });
  console.log(`Remotion browser ${child.pid}: file-backed stdout/stderr transport`);
  return child;
};

// Remotion's Windows cleanup otherwise invokes a shell with unavailable pipes.
// Only terminate a browser launched by this adapter, through its own process handle.
cp.exec=function(command, ...rest) {
  const match=String(command).match(/^taskkill \/pid (\d+) \/T \/F$/i);
  if(match && ownedBrowsers.has(Number(match[1]))) {
    const child=ownedBrowsers.get(Number(match[1]));
    child.kill();
    const callback=rest.find(x=>typeof x==='function');
    if(callback)setImmediate(()=>callback(null,'',''));
    return child;
  }
  return originalExec.call(this,command,...rest);
};
