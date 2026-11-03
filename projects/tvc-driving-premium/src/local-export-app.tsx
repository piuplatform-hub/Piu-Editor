import React from 'react';
import {createRoot} from 'react-dom/client';
import {Player,PlayerRef} from '@remotion/player';
import {toCanvas,getFontEmbedCSS} from 'html-to-image';
import {PremiumFilmV2,TOTAL,FPS} from './v002-film';

(window as any).remotion_staticBase='/public';

const App=()=>{
 const ref=React.useRef<PlayerRef>(null);const [status,setStatus]=React.useState('Sẵn sàng xem bản Remotion v002');
 const [busy,setBusy]=React.useState(false);const [pos,setPos]=React.useState(88);
 const seek=(n:number)=>{ref.current?.pause();ref.current?.seekTo(n);setPos(n)};
 const capture=async(preview:boolean)=>{
  if(busy)return;setBusy(true);ref.current?.pause();
  const frames=preview?[16,88,180,270,365,460,550,655,735,825,925]:Array.from({length:TOTAL},(_,i)=>i);
  try {
   await document.fonts.load('800 150px Manrope');await document.fonts.ready;
   let embedded:string|undefined;
   for(let i=0;i<frames.length;i++){
    const f=frames[i];seek(f);
    await new Promise<void>(r=>requestAnimationFrame(()=>requestAnimationFrame(()=>r())));
    const element=document.getElementById('piu-frame-v002') as HTMLElement;
    await Promise.all(Array.from(element.querySelectorAll('img')).map(img=>img.decode()));
    if(!embedded)embedded=await getFontEmbedCSS(element,{preferredFontFormat:'truetype'});
    const canvas=await toCanvas(element,{width:1920,height:1080,pixelRatio:1,fontEmbedCSS:embedded,cacheBust:false,backgroundColor:'#05182a'});
    const blob=await new Promise<Blob>((resolve,reject)=>canvas.toBlob(b=>b?resolve(b):reject(new Error('JPEG capture failed')),'image/jpeg',.985));
    const response=await fetch(`/${preview?'preview':'frame'}/${String(f).padStart(4,'0')}`,{method:'POST',headers:{'Content-Type':'image/jpeg'},body:blob});
    if(!response.ok)throw new Error(await response.text());
    setStatus(`${preview?'Khung xem thử':'Xuất Remotion'}: ${i+1}/${frames.length} • frame ${f}`);
    canvas.width=0;canvas.height=0;
   }
   await fetch('/complete',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({preview,frames:frames.length})});
   setStatus(preview?'Đã lưu 11 khung xem thử Full HD':'Hoàn tất 975 frame Remotion — sẵn sàng ghép nhạc và xuất MP4');
  }catch(e){setStatus(`Lỗi: ${String(e)}`);await fetch('/error',{method:'POST',body:String(e)}).catch(()=>{});}
  finally{setBusy(false)}
 };
 return <div style={{fontFamily:'Segoe UI,sans-serif',maxWidth:1160,margin:'24px auto',color:'#edf1f4'}}>
  <h1 style={{fontSize:28,marginBottom:5}}>Yên Thành · TVC v002</h1>
  <p style={{color:'#a6bacb'}}>Remotion • Kinetic typography • 40,625 giây • Full HD</p>
  <Player ref={ref} component={PremiumFilmV2} durationInFrames={TOTAL} compositionWidth={1920} compositionHeight={1080} fps={FPS} initialFrame={88} controls={!busy} style={{width:'100%',aspectRatio:'16/9'}}/>
  <div style={{display:'flex',gap:12,alignItems:'center',marginTop:18,flexWrap:'wrap'}}>
   <button disabled={busy} onClick={()=>capture(true)}>Lưu khung xem thử</button>
   <button disabled={busy} onClick={()=>capture(false)} style={{background:'#ff513d',color:'white'}}>Xuất toàn bộ frame Full HD</button>
   <label>Frame <input aria-label="Frame" type="number" min={0} max={TOTAL-1} value={pos} onChange={e=>seek(Number(e.target.value))} style={{width:85,padding:7}}/></label>
   <span role="status">{status}</span>
  </div>
  <p style={{fontSize:13,color:'#9bb0c0'}}>Bản v001 được giữ nguyên. Bản dựng và nguyên liệu chỉ xử lý trên máy này.</p>
  <audio controls src="/public/soundtrack-v002.m4a" style={{width:520}}/>
 </div>
};
document.body.style.cssText='margin:0;background:#0b111c';
const css=document.createElement('style');css.textContent='button{padding:11px 16px;border:0;border-radius:6px;font-size:15px;cursor:pointer}button:disabled{opacity:.5}';document.head.appendChild(css);
createRoot(document.getElementById('root')!).render(<App/>);
