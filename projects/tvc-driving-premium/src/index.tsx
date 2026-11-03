import React from 'react';
import {AbsoluteFill, Composition, OffthreadVideo, Sequence, staticFile, useCurrentFrame, interpolate, Easing, registerRoot, delayRender, continueRender} from 'remotion';
import timeline from './timeline.json';

const FPS=24;
const beat=(n:number)=>Math.round(n*60/124*FPS);
const NAVY='#06192b', WHITE='#f4f6f8', RED='#f05b47';
const clamp={extrapolateLeft:'clamp',extrapolateRight:'clamp'} as const;
const ease=Easing.bezier(.16,1,.3,1);

const FontReady:React.FC=()=>{
  const [hold]=React.useState(()=>delayRender('Loading Manrope Vietnamese'));
  React.useEffect(()=>{
    const face=new FontFace('Manrope',`url(${staticFile('fonts/Manrope.ttf')})`,{weight:'200 800'});
    face.load().then(font=>{document.fonts.add(font);continueRender(hold)}).catch(()=>continueRender(hold));
  },[hold]);return null;
};

const Reveal:React.FC<{text:string;delay:number;size?:number;color?:string;spacing?:number;weight?:number}>=({text,delay,size=92,color=WHITE,spacing=-3,weight=750})=>{
  const f=useCurrentFrame()-delay;
  const y=interpolate(f,[0,14],[115,0],{...clamp,easing:ease});
  const opacity=interpolate(f,[0,7],[0,1],clamp);
  return <div style={{overflow:'hidden',padding:'9px 8px 15px 0',margin:'-9px -8px -15px 0'}}>
    <div style={{fontSize:size,fontWeight:weight,lineHeight:1.16,letterSpacing:spacing,color,opacity,transform:`translateY(${y}%)`,filter:`blur(${interpolate(f,[0,12],[5,0],clamp)}px)`,whiteSpace:'nowrap'}}>{text}</div>
  </div>;
};

type TitleData={from:number;to:number;kicker:string;lines:string[];detail:string;right?:boolean;size?:number;accent?:boolean};
const TITLES:TitleData[]=[
  {from:4,to:12,kicker:'KHỞI ĐẦU MỘT HÀNH TRÌNH',lines:['VỮNG TAY LÁI.','MỞ LỐI TƯƠNG LAI.'],detail:'Từ nền tảng hôm nay, đến tự tin ngày mai.',size:91,accent:true},
  {from:12,to:20,kicker:'SẴN SÀNG CHO HÀNH TRÌNH MỚI',lines:['MỖI KHỞI ĐẦU.','MỘT BƯỚC TIẾN.'],detail:'Đào tạo lái xe tại Yên Thành',size:91},
  {from:20,to:28,kicker:'NỀN TẢNG',lines:['HIỂU ĐÚNG.','VỮNG VÀNG HƠN.'],detail:'Kiến thức • Tư duy • Kỹ năng',size:92},
  {from:28,to:36,kicker:'TRẢI NGHIỆM MÔ PHỎNG',lines:['CÔNG NGHỆ.','GẦN HƠN THỰC TẾ.'],detail:'Tiếp cận tình huống. Rèn luyện phản xạ.',size:86,accent:true},
  {from:36,to:44,kicker:'THỰC HÀNH CABIN',lines:['LÀM CHỦ','TỪNG THAO TÁC.'],detail:'Tập trung trong từng chuyển động.',size:96},
  {from:44,to:52,kicker:'TỪ MÔ PHỎNG ĐẾN THỰC TẾ',lines:['RÈN KỸ NĂNG.','VỮNG HÀNH TRÌNH.'],detail:'Trải nghiệm trên sân tập lái.',size:89,accent:true},
  {from:68,to:76,kicker:'TIẾN VỀ PHÍA TRƯỚC',lines:['TỰ TIN','TRÊN MỖI HÀNH TRÌNH.'],detail:'Cùng Trung tâm Yên Thành',size:81},
];

const Title:React.FC<{data:TitleData}>=({data})=>{
 const f=useCurrentFrame();const dur=beat(data.to)-beat(data.from);
 const alpha=interpolate(f,[dur-9,dur-1],[1,0],clamp);
 const lineWidth=interpolate(f,[5,25],[0,76],{...clamp,easing:ease});
 return <AbsoluteFill style={{opacity:alpha}}>
  <div style={{position:'absolute',inset:0,background:'linear-gradient(90deg,rgba(3,16,30,.72) 0%,rgba(3,16,30,.4) 43%,rgba(3,16,30,0) 86%),linear-gradient(0deg,rgba(3,16,30,.7),transparent 65%)'}}/>
  <div style={{position:'absolute',left:112,bottom:151}}>
   <div style={{display:'flex',alignItems:'center',gap:18,marginBottom:26,opacity:interpolate(f,[4,13],[0,1],clamp)}}>
    <div style={{width:lineWidth,height:3,background:RED}}/>
    <span style={{fontSize:19,fontWeight:650,letterSpacing:3.2,color:WHITE}}>{data.kicker}</span>
   </div>
   {data.lines.map((text,i)=><Reveal key={text} text={text} delay={beat(i === 0 ? .7 : 2.2)} size={data.size} color={data.accent&&i===1?'#ffb09b':WHITE}/>)}
   <div style={{marginTop:28,fontSize:24,color:'#e1e7ed',letterSpacing:.15,opacity:interpolate(f,[beat(3),beat(4)],[0,1],clamp),transform:`translateY(${interpolate(f,[beat(3),beat(4)],[10,0],clamp)}px)`}}>{data.detail}</div>
  </div>
 </AbsoluteFill>
};

const EndCard:React.FC=()=>{
 const f=useCurrentFrame();
 const dim=interpolate(f,[0,15],[0,.88],{...clamp,easing:ease});
 return <AbsoluteFill style={{alignItems:'center',justifyContent:'center'}}>
  <AbsoluteFill style={{background:NAVY,opacity:dim}}/>
  <div style={{zIndex:1,textAlign:'center',marginTop:-10}}>
   <div style={{fontSize:23,letterSpacing:4,fontWeight:600,color:'#cad6df',marginBottom:32,opacity:interpolate(f,[8,20],[0,1],clamp)}}>TRUNG TÂM ĐÀO TẠO VÀ SÁT HẠCH LÁI XE</div>
   <Reveal text="YÊN THÀNH" delay={beat(.7)} size={156} spacing={-4.5} weight={800}/>
   <div style={{width:interpolate(f,[18,40],[0,112],{...clamp,easing:ease}),height:5,background:RED,margin:'34px auto 30px'}}/>
   <div style={{fontSize:30,fontWeight:500,letterSpacing:1.1,color:WHITE,opacity:interpolate(f,[beat(2.4),beat(3.6)],[0,1],clamp)}}>BẮT ĐẦU HÀNH TRÌNH CỦA BẠN.</div>
  </div>
 </AbsoluteFill>
};

const Film:React.FC=()=>{
 const frame=useCurrentFrame();const finish=beat(76);
 const chapter=frame<beat(20)?'KHỞI ĐẦU':frame<beat(44)?'NỀN TẢNG & CÔNG NGHỆ':frame<beat(68)?'KỸ NĂNG & TRẢI NGHIỆM':'HÀNH TRÌNH';
 const outro=interpolate(frame,[timeline.totalFrames-15,timeline.totalFrames-1],[1,0],clamp);
 return <AbsoluteFill style={{background:NAVY,color:WHITE,fontFamily:'Manrope, sans-serif',opacity:outro}}>
  <FontReady/>
  <OffthreadVideo src={staticFile('video/edit-base.mp4')} muted style={{width:'100%',height:'100%',objectFit:'cover'}}/>
  <AbsoluteFill style={{boxShadow:'inset 0 0 160px 25px rgba(2,14,24,.15)',pointerEvents:'none'}}/>
  {TITLES.map(t=><Sequence key={t.from} from={beat(t.from)} durationInFrames={beat(t.to)-beat(t.from)} layout="none"><Title data={t}/></Sequence>)}
  {frame<beat(4)&&<div style={{position:'absolute',left:114,bottom:152,fontSize:23,letterSpacing:4,fontWeight:550,textShadow:'0 2px 20px #001',opacity:interpolate(frame,[5,16,38,46],[0,1,1,0],clamp)}}>HÀNH TRÌNH BẮT ĐẦU TỪ BẠN.</div>}
  {frame>=beat(52)&&frame<beat(68)&&<>
   <div style={{position:'absolute',left:0,right:0,bottom:0,height:360,background:'linear-gradient(0deg,rgba(3,16,30,.5),transparent)'}}/>
   <div style={{position:'absolute',left:114,bottom:158,fontSize:52,fontWeight:750,letterSpacing:-1.5}}>{frame<beat(60)?'CHUYỂN ĐỘNG.':frame<beat(64)?'TẬP TRUNG.':'TIẾN LÊN.'}</div>
  </>}
  {frame>=finish&&<Sequence from={finish}><EndCard/></Sequence>}
  {/* Clean cinematic letterbox and restrained brand furniture. */}
  <div style={{position:'absolute',left:0,right:0,top:0,height:82,background:NAVY}}/>
  <div style={{position:'absolute',left:0,right:0,bottom:0,height:80,background:NAVY}}/>
  {frame<finish&&<>
   <div style={{position:'absolute',top:29,left:112,display:'flex',gap:15,alignItems:'center',fontSize:23,fontWeight:750,letterSpacing:2.7}}><span style={{display:'inline-block',width:5,height:23,background:RED}}/>YÊN THÀNH</div>
   <div style={{position:'absolute',top:33,right:112,fontSize:15,fontWeight:500,letterSpacing:2.2,color:'#adbfce'}}>ĐÀO TẠO & SÁT HẠCH LÁI XE</div>
   <div style={{position:'absolute',bottom:31,left:114,fontSize:14,letterSpacing:2.5,color:'#a7b7c5'}}>{chapter}</div>
  </>}
 </AbsoluteFill>
};

const Root:React.FC=()=> <Composition id="PremiumDriving" component={Film} durationInFrames={timeline.totalFrames} fps={24} width={1920} height={1080}/>;
registerRoot(Root);
