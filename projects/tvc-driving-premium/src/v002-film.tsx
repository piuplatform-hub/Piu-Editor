import React from 'react';
import {AbsoluteFill,Img,Sequence,staticFile,useCurrentFrame,spring,interpolate,Easing} from 'remotion';
export const TOTAL=975, FPS=24;
const NAVY='#05182a',RED='#ff513d',WHITE='#f5f3ee';
const C={extrapolateLeft:'clamp',extrapolateRight:'clamp'} as const;
export const b=(n:number)=>Math.round(n*60/124*24);
const out=Easing.bezier(.16,1,.3,1);

const Word:React.FC<{children:React.ReactNode;delay:number;size?:number;color?:string;outline?:boolean}>=({children,delay,size=144,color=WHITE,outline=false})=>{
 const f=useCurrentFrame()-delay;
 const p=spring({frame:Math.max(0,f),fps:24,config:{mass:.65,damping:16,stiffness:175},durationInFrames:19});
 const q=interpolate(f,[0,13],[0,1],C);
 return <span style={{display:'inline-block',fontSize:size,perspective:800,marginRight:'.17em',paddingBottom:'.1em',overflow:'visible'}}>
  <span style={{display:'inline-block',fontWeight:800,fontSize:size,lineHeight:1.03,letterSpacing:-size*.045,color:outline?'transparent':color,WebkitTextStroke:outline?`1.5px ${WHITE}`:undefined,
   opacity:interpolate(f,[0,3],[0,1],C),transformOrigin:'50% 100%',transform:`translate3d(${(1-p)*-35}px,${(1-p)*95}px,0) rotateX(${(1-q)*-70}deg) rotateZ(${(1-q)*-4}deg) scale(${.84+.16*p})`,filter:`blur(${(1-q)*10}px)`}}>{children}</span>
 </span>
};

const Line:React.FC<{text:string;delay:number;size?:number;color?:string;outline?:boolean;step?:number}>=({text,delay,size=144,color,outline,step=3})=> <div style={{whiteSpace:'nowrap',height:size*1.17}}>{text.split(' ').map((w,i)=><Word key={i} delay={delay+i*step} size={size} color={color} outline={outline}>{w}</Word>)}</div>;
const Small:React.FC<{text:string;delay?:number;size?:number;color?:string}>=({text,delay=0,size=22,color=WHITE})=>{
 const f=useCurrentFrame()-delay;
 return <div style={{fontSize:size,fontWeight:600,letterSpacing:size<24?3:.1,color,opacity:interpolate(f,[0,7],[0,1],C),transform:`translateY(${interpolate(f,[0,13],[16,0],{...C,easing:out})}px)`}}>{text}</div>;
};

type Scene={a:number;z:number;mode:string;kicker:string;lines:string[];detail:string;size:number};
const SCENES:Scene[]=[
 {a:4,z:12,mode:'hero',kicker:'MỘT KHỞI ĐẦU. MỘT TƯƠNG LAI.',lines:['MỞ LỐI','TƯƠNG LAI.'],detail:'Vững tay lái, tự tin tiến về phía trước.',size:158},
 {a:12,z:20,mode:'wide',kicker:'ĐÀO TẠO LÁI XE YÊN THÀNH',lines:['SẴN SÀNG','BỨT PHÁ.'],detail:'Bắt đầu bằng một lựa chọn vững vàng.',size:148},
 {a:20,z:28,mode:'panel',kicker:'NỀN TẢNG KIẾN THỨC',lines:['HIỂU','ĐÚNG.'],detail:'Để mỗi quyết định thêm tự tin.',size:145},
 {a:28,z:36,mode:'tech',kicker:'TRẢI NGHIỆM MÔ PHỎNG',lines:['GẦN HƠN','THỰC TẾ.'],detail:'Công nghệ mô phỏng lái xe.',size:145},
 {a:36,z:44,mode:'stack',kicker:'THỰC HÀNH CABIN',lines:['LÀM CHỦ','TỪNG','THAO TÁC.'],detail:'Tập trung trong từng chuyển động.',size:114},
 {a:44,z:52,mode:'wide',kicker:'TRÊN SÂN TẬP',lines:['RÈN KỸ NĂNG.','VỮNG HÀNH TRÌNH.'],detail:'Từ mô phỏng đến thực tế.',size:105},
 {a:68,z:76,mode:'stack',kicker:'TIẾN VỀ PHÍA TRƯỚC',lines:['TỰ TIN.','TRÊN MỖI','HÀNH TRÌNH.'],detail:'Cùng Trung tâm Yên Thành.',size:116},
];

const TitleScene:React.FC<{s:Scene}>=({s})=>{
 const f=useCurrentFrame(),dur=b(s.z)-b(s.a);
 const exiting=interpolate(f,[dur-8,dur],[1,0],C);
 const p=interpolate(f,[0,15],[0,1],{...C,easing:out});
 const panel=s.mode==='panel';const stack=s.mode==='stack';
 const x=panel?1260:110,y=panel?285:stack?300:s.mode==='hero'?300:430;
 return <AbsoluteFill style={{opacity:exiting}}>
  {panel?<div style={{position:'absolute',right:0,top:0,bottom:0,width:730,background:NAVY,clipPath:`inset(0 0 0 ${(1-p)*100}%)`}}/>:
   <AbsoluteFill style={{background:s.mode==='hero'?'linear-gradient(90deg,rgba(3,18,32,.72),rgba(3,18,32,.04) 85%)':'linear-gradient(0deg,rgba(3,18,32,.80),rgba(3,18,32,0) 90%)'}}/>}
  {s.mode==='tech'&&<div style={{position:'absolute',right:95,top:170,fontSize:150,fontWeight:800,letterSpacing:-7,color:'transparent',WebkitTextStroke:'1px rgba(255,255,255,.2)',transform:`translateX(${(1-p)*160}px)`}}>MÔ PHỎNG</div>}
  <div style={{position:'absolute',left:x,top:y,width:panel?600:1700}}>
   <div style={{display:'flex',gap:18,alignItems:'center',marginBottom:24}}><div style={{width:interpolate(f,[2,17],[0,65],{...C,easing:out}),height:4,background:RED}}/><Small text={s.kicker} delay={3} size={panel?17:21}/></div>
   {s.lines.map((line,i)=><Line key={line} text={line} delay={b(.5+i*1.1)} size={s.size} step={3} color={i===s.lines.length-1?RED:WHITE}/>)}
   <div style={{marginTop:24}}><Small text={s.detail} delay={b(3.7)} size={panel?23:27} color="#dbe3e9"/></div>
  </div>
  {s.mode==='hero'&&<div style={{position:'absolute',right:120,bottom:146,width:130,height:130,border:'1px solid rgba(255,255,255,.4)',borderRadius:'50%',transform:`rotate(${f*1.8}deg)`,opacity:p}}><svg width="130" height="130" viewBox="0 0 130 130"><path d="M42 65H88M70 47L88 65L70 83" fill="none" stroke={WHITE} strokeWidth="3"/></svg></div>}
 </AbsoluteFill>;
};

const Montage:React.FC<{word:string;outline?:boolean}>=({word,outline})=>{
 const f=useCurrentFrame();const p=spring({frame:f,fps:24,config:{stiffness:210,damping:15},durationInFrames:15});
 return <AbsoluteFill style={{justifyContent:'center',alignItems:'center',background:'rgba(3,16,28,.19)'}}>
  <div style={{position:'absolute',fontSize:182,fontWeight:800,letterSpacing:-8,color:'transparent',WebkitTextStroke:'1px rgba(255,255,255,.30)',transform:`translate(${(1-p)*95+18}px,20px) scale(1.04)`}}>{word}</div>
  <div style={{position:'relative',transform:`scale(${.76+.24*p}) rotate(${(1-p)*-5}deg)`}}><Line text={word} delay={2} size={178} color={outline?RED:WHITE} step={1}/></div>
  <div style={{position:'absolute',height:7,background:RED,bottom:300,width:interpolate(f,[2,15],[0,200],{...C,easing:out})}}/>
 </AbsoluteFill>
};

const Finish:React.FC=()=>{
 const f=useCurrentFrame();const p=interpolate(f,[0,16],[0,1],{...C,easing:out});
 return <AbsoluteFill style={{alignItems:'center',justifyContent:'center'}}>
  <AbsoluteFill style={{background:NAVY,clipPath:`inset(0 ${(1-p)*50}% 0 ${(1-p)*50}%)`}}/>
  <div style={{position:'absolute',left:130,right:130,top:145,bottom:145,border:'1px solid rgba(240,240,238,.13)',opacity:p}}/>
  <div style={{zIndex:2,textAlign:'center',marginTop:-35}}>
   <Small text="TRUNG TÂM ĐÀO TẠO VÀ SÁT HẠCH LÁI XE" delay={8} size={22}/>
   <div style={{marginTop:35}}><Line text="YÊN THÀNH" delay={b(.6)} size={174} step={4}/></div>
   <div style={{width:interpolate(f,[18,38],[0,125],{...C,easing:out}),height:5,background:RED,margin:'35px auto'}}/>
   <Small text="BẮT ĐẦU HÀNH TRÌNH CỦA BẠN." delay={b(2.6)} size={28}/>
  </div>
 </AbsoluteFill>
};

export const PremiumFilmV2:React.FC=()=>{
 const frame=useCurrentFrame();const src=staticFile(`frames-v002/f${String(frame).padStart(4,'0')}.jpg`);
 const shotStarts=[0,46,139,232,325,418,511,557,604,627,650,697,790,883,975];
 const start=[...shotStarts].reverse().find(x=>frame>=x)||0;
 const end=shotStarts.find(x=>x>frame)||975;
 const scale=interpolate(frame,[start,end],[1.025,1],C);
 const wipeAt=[b(12),b(20),b(28),b(36),b(44),b(68),b(76)].find(x=>Math.abs(frame-x)<5);
 const wipe=wipeAt===undefined?null:interpolate(frame,[wipeAt-4,wipeAt+4],[-110,110],C);
 return <AbsoluteFill id="piu-frame-v002" style={{background:NAVY,color:WHITE,fontFamily:'Manrope, sans-serif',overflow:'hidden',width:1920,height:1080}}>
  <style>{`@font-face{font-family:Manrope;src:url('${staticFile('fonts/Manrope.ttf')}') format('truetype');font-weight:200 800;font-display:block;}`}</style>
  <AbsoluteFill style={{transform:`scale(${scale})`}}><Img src={src} style={{width:'100%',height:'100%',objectFit:'cover'}}/></AbsoluteFill>
  <AbsoluteFill style={{background:'linear-gradient(180deg,rgba(2,15,26,.60),transparent 23%,transparent 78%,rgba(2,15,26,.35))'}}/>
  {frame<b(4)&&<AbsoluteFill style={{justifyContent:'center',paddingLeft:110,background:'linear-gradient(90deg,rgba(3,16,30,.65),transparent)'}}><Small text="HÀNH TRÌNH BẮT ĐẦU TỪ BẠN." delay={1}/><div style={{marginTop:24}}><Line text="VỮNG TAY LÁI." delay={3} size={151} step={3}/></div></AbsoluteFill>}
  {SCENES.map(s=><Sequence key={s.a} from={b(s.a)} durationInFrames={b(s.z)-b(s.a)} layout="none"><TitleScene s={s}/></Sequence>)}
  {[[52,56,'BỨT PHÁ.'],[56,60,'TẬP TRUNG.'],[60,64,'LÀM CHỦ.'],[64,68,'TIẾN LÊN.']].map(([a,z,word])=><Sequence key={a} from={b(a as number)} durationInFrames={b(z as number)-b(a as number)} layout="none"><Montage word={word as string} outline={a===56||a===64}/></Sequence>)}
  {frame>=b(76)&&<Sequence from={b(76)}><Finish/></Sequence>}
  {frame<b(76)&&<div style={{position:'absolute',top:40,left:104,right:104,display:'flex',justifyContent:'space-between',alignItems:'center'}}><div style={{fontSize:28,fontWeight:800,letterSpacing:1.5,display:'flex',gap:15,alignItems:'center'}}><span style={{width:5,height:24,background:RED}}/>YÊN THÀNH</div><div style={{fontSize:15,fontWeight:650,letterSpacing:2.8}}>ĐÀO TẠO & SÁT HẠCH LÁI XE</div></div>}
  {wipe!==null&&<AbsoluteFill style={{background:RED,transform:`translateX(${wipe}%) skewX(-12deg)`,width:'25%',left:'38%',opacity:.95}}/>}
  <AbsoluteFill style={{background:NAVY,pointerEvents:'none',opacity:interpolate(frame,[0,7,TOTAL-13,TOTAL-1],[1,0,0,1],C)}}/>
 </AbsoluteFill>;
};
