import React, {useEffect, useState} from 'react';
import {AbsoluteFill, Sequence, staticFile, useCurrentFrame, useVideoConfig, interpolate, Easing, delayRender, continueRender, cancelRender} from 'remotion';
import {Video, Audio} from '@remotion/media';
import {loadFont} from '@remotion/fonts';
import {useGsapTimeline} from '@remotion/gsap';
import {gsap} from 'gsap';
import {CustomEase} from 'gsap/CustomEase';
import {DrawSVGPlugin} from 'gsap/DrawSVGPlugin';
import timeline from './timeline.json';

gsap.registerPlugin(CustomEase, DrawSVGPlugin);
const NAVY = '#061b2b', BLUE = '#168fe5', PAPER = '#f4f1e9', INK = '#102c3c';
const C = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const S = Easing.bezier(.22, 1, .36, 1);
const scene = (id:string) => {
  const shot=timeline.shots.find(s=>s.id===id);
  if(!shot)throw new Error(`Unknown shot: ${id}`);
  return {start:shot.start, duration:shot.end-shot.start};
};

export const FontGate: React.FC<React.PropsWithChildren> = ({children}) => {
  const [ready, setReady] = useState(false);
  const [handle] = useState(() => delayRender('Loading full Vietnamese Be Vietnam Pro faces'));
  useEffect(() => {
    Promise.all(([['Regular','400'],['Medium','500'],['SemiBold','600'],['Bold','700']] as const).map(([face,weight])=>
      loadFont({family:'Be Vietnam Pro',url:staticFile(`fonts/BeVietnamPro-${face}.ttf`),weight,display:'block'})))
      .then(() => {setReady(true); continueRender(handle);}).catch(cancelRender);
  }, [handle]);
  return ready ? <>{children}</> : null;
};

export const TextFx: React.FC<{lines: string[]; size: number; delay?: number; color?: string; accentLine?: number; align?: 'left'|'center'|'right'; mode?: 'words'|'letters'; weight?: number; effect?:'lift'|'horizontal';still?:boolean}> =
({lines, size, delay=4, color=PAPER, accentLine=-1, align='left', mode='words', weight=700,effect='lift',still=false}) => {
  const {fps} = useVideoConfig();
  const ref = useGsapTimeline<HTMLDivElement>(({timeline: tl, selector}) => {
    CustomEase.create('piu-settle', '.18,.82,.22,1');
    if(still)return;
    tl.addLabel('reveal', delay/fps);
    lines.forEach((_, i) => {
      tl.fromTo(selector(`.fx-line-${i} .fx-unit`),
        effect==='horizontal'?{x:-36,opacity:0}:{y:36,rotationZ:.5,opacity:0},
        {x:0,y:0,rotationZ:0,opacity:1,duration:.68,ease:'piu-settle',stagger:.065},
        `reveal+=${i*.115}`);
    });
  });
  return <div ref={ref} data-text-fx="GSAP word reveal, unclipped Vietnamese glyphs" style={{fontSize:size,fontWeight:weight,letterSpacing:-size*.045,textAlign:align,lineHeight:1.3,fontKerning:'normal',overflow:'visible'}}>
    {lines.map((line,i)=><div key={line} className={`fx-line-${i}`} data-vietnamese-line={line} style={{position:'relative',color:i===accentLine?BLUE:color,whiteSpace:'nowrap',overflow:'visible',
      WebkitTextStroke:`${color===INK?.5:1.6}px ${color===INK?INK:'#041c30'}`,paintOrder:'stroke fill',textShadow:color===INK?'none':'0 3px 10px rgba(0,18,33,.55)'}}>
      {line.normalize('NFC').split(' ').map((unit,j,a)=><span key={j} className="fx-unit" style={{display:'inline-block',verticalAlign:'top',transformOrigin:'50% 60%',marginRight:j<a.length-1?'.24em':0,overflow:'visible'}}>{unit}</span>)}
    </div>)}
  </div>;
};

export const FillFx:React.FC<{text:string;size:number;delay?:number;align?:'left'|'right';still?:boolean}> = ({text,size,delay=5,align='left',still=false})=>{
  const {fps}=useVideoConfig();
  const ref=useGsapTimeline<HTMLDivElement>(({timeline:tl,selector})=>{
    if(still)return;
    tl.fromTo(selector('.fill-outline'),{opacity:0,y:18},{opacity:.8,y:0,duration:.5,ease:'power3.out'},delay/fps);
    tl.fromTo(selector('.fill-word'),{opacity:0},{opacity:1,duration:.45,ease:'power2.out',stagger:.12},delay/fps+.22);
    tl.to(selector('.fill-outline'),{opacity:0,duration:.25},delay/fps+1.05);
  });
  const type:React.CSSProperties={fontSize:size,fontWeight:700,letterSpacing:-size*.045,lineHeight:1.4,whiteSpace:'nowrap',textAlign:align,overflow:'visible'};
  return <div ref={ref} data-vietnamese-line={text} style={{position:'relative',...type}}>
    <div className="fill-outline" style={{opacity:0,color:'transparent',WebkitTextStroke:`1px ${PAPER}`}}>{text.normalize('NFC').split(' ').map((word,i,a)=><span key={i} style={{display:'inline-block',marginRight:i<a.length-1?'.24em':0,overflow:'visible'}}>{word}</span>)}</div>
    <div className="fill-solid" style={{position:'absolute',inset:0,color:BLUE,WebkitTextStroke:'1.6px #041c30',paintOrder:'stroke fill',textShadow:'0 3px 10px rgba(0,18,33,.6)',overflow:'visible'}}>{text.normalize('NFC').split(' ').map((word,i,a)=><span key={i} className="fill-word" style={{display:'inline-block',marginRight:i<a.length-1?'.24em':0,overflow:'visible'}}>{word}</span>)}</div>
  </div>;
};

const Label: React.FC<{children: React.ReactNode; delay?: number; color?: string; size?: number}> = ({children,delay=2,color=PAPER,size=23}) => {
  const {fps}=useVideoConfig();
  const ref=useGsapTimeline<HTMLDivElement>(({timeline:tl,selector}) => {
    tl.fromTo(selector('.label-rule'),{scaleX:0},{scaleX:1,duration:.65,ease:'power3.out'},delay/fps);
    tl.fromTo(selector('.label-copy'),{y:15,opacity:0},{y:0,opacity:1,duration:.65,ease:'power3.out'},delay/fps+.09);
  });
  return <div ref={ref} style={{display:'flex',alignItems:'center',gap:21,color,fontSize:size,fontWeight:600,letterSpacing:3.1,lineHeight:1.5}}>
    <span className="label-rule" style={{display:'block',width:53,height:3,background:BLUE,transformOrigin:'0 50%'}}/>
    <span className="label-copy" style={{WebkitTextStroke:color===INK?'0px':'0.65px #041c30',paintOrder:'stroke fill',textShadow:color===INK?'none':'0 2px 6px rgba(0,15,30,.45)'}}>{children}</span>
  </div>;
};

const Road: React.FC<{delay?:number; opacity?:number; color?:string; compact?:boolean}> = ({delay=0,opacity=.8,color=BLUE,compact=false}) => {
  const {fps}=useVideoConfig();
  const ref=useGsapTimeline<SVGSVGElement>(({timeline:tl,selector})=>{
    tl.fromTo(selector('.road-main'),{drawSVG:'0%'},{drawSVG:'100%',duration:1.1,ease:'power2.inOut'},delay/fps);
    tl.fromTo(selector('.road-side'),{drawSVG:'0%'},{drawSVG:'100%',duration:1.35,ease:'power2.inOut'},delay/fps+.1);
  });
  return <svg ref={ref} viewBox="0 0 1920 1080" width="1920" height="1080" style={{position:'absolute',inset:0,opacity,pointerEvents:'none'}}>
    <path className="road-side" d={compact?'M-50 900 H535 Q650 900 714 830 L825 714 Q882 655 975 655 H2060':'M-100 1130 L410 880 Q540 815 670 815 H1030 Q1180 815 1280 700 L1620 305 Q1725 185 1970 185'} fill="none" stroke={PAPER} strokeWidth="1" opacity=".30"/>
    <path className="road-main" d={compact?'M-50 920 H545 Q663 920 728 848 L839 732 Q891 675 980 675 H2060':'M-100 1160 L425 900 Q550 835 680 835 H1040 Q1194 835 1298 716 L1638 323 Q1739 205 1970 205'} fill="none" stroke={color} strokeWidth="4" strokeLinecap="round"/>
  </svg>;
};

const CornerBrand:React.FC<{dark?:boolean}> = ({dark=false}) => <div style={{position:'absolute',left:100,top:57,display:'flex',alignItems:'center',gap:14,color:dark?INK:PAPER,textShadow:dark?undefined:'0 1px 12px rgba(0,0,0,.3)'}}>
  <span style={{width:5,height:25,background:BLUE}}/>
  <span style={{fontWeight:700,fontSize:26,letterSpacing:1}}>YÊN THÀNH</span>
</div>;

const SceneExit:React.FC<React.PropsWithChildren<{duration:number}>> = ({duration,children})=>{
  const frame=useCurrentFrame();
  return <AbsoluteFill style={{opacity:interpolate(frame,[duration-7,duration-1],[1,0],C)}}>{children}</AbsoluteFill>;
};

const Opening=()=>{
  const frame=useCurrentFrame();
  return <AbsoluteFill>
    <AbsoluteFill style={{background:'linear-gradient(90deg,rgba(3,20,33,.87),rgba(3,20,33,.32) 50%,rgba(3,20,33,.04))'}}/>
    <Road delay={1} opacity={.5}/>
    <div style={{position:'absolute',left:100,top:140}}><Label delay={2}>MỘT HÀNH TRÌNH MỚI</Label></div>
    <div style={{position:'absolute',left:95,top:315}}><TextFx lines={['TỰ TIN.']} size={204} delay={7} mode="letters"/></div>
    <div style={{position:'absolute',left:105,top:615,overflow:'visible'}}><TextFx lines={['TỪ KHỞI ĐẦU.']} size={69} delay={17} weight={500}/></div>
    <div style={{position:'absolute',left:108,top:750,width:360,height:1,background:'rgba(244,241,233,.4)',transformOrigin:'0 50%',scale:`${interpolate(frame,[14,45],[0,1],C)} 1`}}/>
    <div style={{position:'absolute',left:108,top:782,fontSize:19,fontWeight:600,letterSpacing:5,opacity:interpolate(frame,[27,43],[0,.85],C)}}>ĐÀO TẠO & SÁT HẠCH LÁI XE</div>
  </AbsoluteFill>;
};

const Brand=()=> <AbsoluteFill>
  <AbsoluteFill style={{background:'linear-gradient(90deg,rgba(3,20,33,.1),rgba(3,20,33,.15) 35%,rgba(3,20,33,.83))'}}/>
  <Road delay={10} opacity={.35}/>
  <div style={{position:'absolute',left:103,top:103,width:600,fontSize:24,lineHeight:1.6,letterSpacing:2,fontWeight:600}}><Label delay={5}>NƠI HÀNH TRÌNH BẮT ĐẦU</Label></div>
  <div style={{position:'absolute',right:103,top:336,textAlign:'right'}}><TextFx lines={['YÊN','THÀNH']} size={173} align="right" delay={7} accentLine={1} mode="letters"/></div>
  <div style={{position:'absolute',right:111,bottom:162,width:680,textAlign:'right',fontSize:25,lineHeight:1.55,fontWeight:500,letterSpacing:1.2}}>TRUNG TÂM ĐÀO TẠO<br/>VÀ SÁT HẠCH LÁI XE</div>
</AbsoluteFill>;

const Knowledge=()=>{
  const ref=useGsapTimeline<HTMLDivElement>(({timeline:tl,selector})=>{
    tl.fromTo(selector('.paper-panel'),{xPercent:-105},{xPercent:0,duration:.8,ease:'power4.out'},0);
    tl.fromTo(selector('.chapter-nr'),{opacity:0,y:20},{opacity:1,y:0,duration:.9,ease:'power3.out'},.3);
  });
  return <AbsoluteFill ref={ref}>
    <div className="paper-panel" style={{position:'absolute',inset:'0 auto 0 0',width:835,background:PAPER}}/>
    <div style={{position:'absolute',left:102,top:145}}><Label delay={8} color={INK}>NỀN TẢNG</Label></div>
    <div className="chapter-nr" style={{position:'absolute',left:100,top:255,color:'rgba(16,44,60,.12)',fontSize:130,fontWeight:500,letterSpacing:-8}}>01</div>
    <div style={{position:'absolute',left:98,top:460}}><TextFx lines={['VỮNG','KIẾN THỨC.']} size={101} delay={10} color={INK} accentLine={0} effect="horizontal"/></div>
    <div style={{position:'absolute',left:106,bottom:163,fontSize:28,color:INK,fontWeight:500,lineHeight:1.6}}>Hiểu từ nền tảng.<br/>Vững trong từng quyết định.</div>
    <div style={{position:'absolute',left:104,bottom:97,width:623,height:1,background:'rgba(16,44,60,.2)'}}/>
  </AbsoluteFill>;
};

const Simulation=()=> <AbsoluteFill>
  <AbsoluteFill style={{background:'linear-gradient(0deg,rgba(3,20,33,.88),rgba(3,20,33,0) 85%)'}}/>
  <Road delay={4} opacity={.14} compact/>
  <CornerBrand/>
  <div style={{position:'absolute',left:105,bottom:380}}><Label delay={3}>MÔ PHỎNG TÌNH HUỐNG</Label></div>
  <div style={{position:'absolute',left:100,bottom:170}}><TextFx lines={['HIỂU ĐÚNG.']} size={135} delay={7}/></div>
  <div style={{position:'absolute',right:110,bottom:130,fontSize:22,letterSpacing:3,fontWeight:500}}>QUAN SÁT. NHẬN DIỆN. PHẢN XẠ.</div>
</AbsoluteFill>;

const Cabin=()=> <AbsoluteFill>
  <AbsoluteFill style={{background:'linear-gradient(90deg,rgba(3,20,33,.86),rgba(3,20,33,.32) 55%,rgba(3,20,33,.1))'}}/>
  <CornerBrand/>
  <div style={{position:'absolute',left:105,top:240}}><Label delay={5}>THỰC HÀNH CABIN</Label></div>
  <div style={{position:'absolute',left:98,top:414}}><TextFx lines={['RÈN TỪNG','THAO TÁC.']} size={137} delay={9} accentLine={1}/></div>
  <div style={{position:'absolute',left:106,bottom:172,fontSize:29,fontWeight:400,letterSpacing:.2}}>Tập trung trong từng chuyển động.</div>
</AbsoluteFill>;

const Fleet=()=> <AbsoluteFill>
  <AbsoluteFill style={{background:'linear-gradient(0deg,rgba(3,20,33,.92),rgba(3,20,33,.22) 57%,rgba(3,20,33,.04))'}}/>
  <CornerBrand/>
  <div style={{position:'absolute',left:105,top:540}}><Label delay={4}>TỪ RÈN LUYỆN ĐẾN THỰC HÀNH</Label></div>
  <div style={{position:'absolute',left:99,top:610}}><FillFx text="SẴN SÀNG CẦM LÁI." size={119} delay={7}/></div>
  <div style={{position:'absolute',left:108,bottom:129,fontSize:27,fontWeight:400}}>Mỗi bước tiến, thêm một phần tự tin.</div>
</AbsoluteFill>;

const Practice=()=> <AbsoluteFill>
  <AbsoluteFill style={{background:'linear-gradient(270deg,rgba(3,20,33,.87),rgba(3,20,33,.18) 62%,rgba(3,20,33,.02))'}}/>
  <CornerBrand/>
  <div style={{position:'absolute',right:110,top:255}}><Label delay={5}>TRÊN SÂN THỰC HÀNH</Label></div>
  <div style={{position:'absolute',right:104,top:430}}><TextFx lines={['TỰ TIN']} size={123} delay={6} align="right"/><FillFx text="TIẾN BƯỚC." size={123} delay={12} align="right"/></div>
  <div style={{position:'absolute',right:112,bottom:179,fontSize:28,fontWeight:400}}>Vững tay lái. Mở hành trình.</div>
</AbsoluteFill>;

const Montage:React.FC<{word:string;number:string}> = ({word,number})=>{
  const f=useCurrentFrame();
  const {fps}=useVideoConfig();
  const ref=useGsapTimeline<HTMLDivElement>(({timeline:tl,selector})=>{
    tl.fromTo(selector('.montage-solid'),{scale:.93,x:-45,opacity:0,letterSpacing:12},{scale:1,x:0,opacity:1,letterSpacing:-8,duration:.65,ease:'power4.out'},2/fps);
    tl.fromTo(selector('.montage-echo'),{x:90,opacity:0},{x:22,opacity:.28,duration:.8,ease:'power3.out'},4/fps);
    tl.fromTo(selector('.montage-rule'),{scaleX:0},{scaleX:1,duration:.6,ease:'power3.out'},.18);
  });
  return <AbsoluteFill ref={ref} style={{justifyContent:'center',alignItems:'center'}}>
    <AbsoluteFill style={{background:'rgba(3,20,33,.47)'}}/>
    <CornerBrand/>
    <div style={{position:'absolute',left:110,top:155,fontSize:22,letterSpacing:5,fontWeight:500}}>MỖI CHUYỂN ĐỘNG. MỘT BƯỚC TIẾN.</div>
    <div className="montage-echo" style={{position:'absolute',fontSize:185,fontWeight:700,letterSpacing:-8,color:'transparent',WebkitTextStroke:`1px ${PAPER}`,translate:'0 26px'}}>{word}</div>
    <div className="montage-solid" style={{fontSize:185,fontWeight:700,letterSpacing:-8,position:'relative',WebkitTextStroke:'1.8px #041c30',paintOrder:'stroke fill',textShadow:'0 3px 12px rgba(0,18,33,.6)'}}>{word}</div>
    <div className="montage-rule" style={{position:'absolute',top:726,left:112,right:112,height:3,background:BLUE,transformOrigin:'0 50%'}}/>
    <div style={{position:'absolute',bottom:140,right:110,fontSize:27,fontWeight:500,letterSpacing:5,opacity:interpolate(f,[3,13],[0,.8],C)}}>{number} / YÊN THÀNH</div>
  </AbsoluteFill>;
};

const Signature=()=>{
  const f=useCurrentFrame();
  return <AbsoluteFill style={{background:NAVY}}>
    <Road delay={0} opacity={.55}/>
    <div style={{position:'absolute',left:0,right:0,top:208,textAlign:'center',fontSize:23,fontWeight:500,letterSpacing:3.2,opacity:interpolate(f,[5,20],[0,1],C)}}>TRUNG TÂM ĐÀO TẠO VÀ SÁT HẠCH LÁI XE</div>
    <div style={{position:'absolute',left:0,right:0,top:350}}><TextFx lines={['YÊN THÀNH']} size={171} delay={7} align="center" mode="letters"/></div>
    <div style={{position:'absolute',left:864,top:598,width:192,height:4,background:BLUE,scale:`${interpolate(f,[13,32],[0,1],{...C,easing:S})} 1`}}/>
    <div style={{position:'absolute',left:0,right:0,top:670,textAlign:'center'}}><TextFx lines={['Vững tay lái. Tự tin mỗi hành trình.']} size={38} delay={20} align="center" weight={450}/></div>
    <div style={{position:'absolute',left:0,right:0,bottom:136,textAlign:'center',fontSize:17,letterSpacing:5,fontWeight:500,opacity:interpolate(f,[28,45],[0,.6],C)}}>HÀNH TRÌNH BẮT ĐẦU TỪ BẠN</div>
  </AbsoluteFill>;
};

const RoadWipe=()=>{
  const ref=useGsapTimeline<HTMLDivElement>(({timeline:tl,selector})=>{
    tl.fromTo(selector('.wipe-navy'),{xPercent:-122},{xPercent:122,duration:16/24,ease:'power1.inOut'},0);
    tl.fromTo(selector('.wipe-red'),{xPercent:-124},{xPercent:124,duration:16/24,ease:'power1.inOut'},1/24);
  });
  return <AbsoluteFill ref={ref} style={{pointerEvents:'none',overflow:'hidden'}}>
    <div className="wipe-red" style={{position:'absolute',inset:'0 -200px',background:BLUE,transform:'skewX(-12deg)'}}/>
    <div className="wipe-navy" style={{position:'absolute',inset:'0 -200px',background:NAVY,transform:'skewX(-12deg)'}}/>
  </AbsoluteFill>;
};

const Shot:React.FC<{id:string;duration:number}> = ({id,duration})=>{
  const frame=useCurrentFrame();
  return <AbsoluteFill style={{overflow:'hidden'}}>
    <AbsoluteFill style={{scale:interpolate(frame,[0,duration],[1.018,1],C),filter:'saturate(0.91) contrast(1.035)'}}>
      <Video src={staticFile(`video/${id}.mp4`)} muted objectFit="cover" style={{width:'100%',height:'100%'}}/>
    </AbsoluteFill>
  </AbsoluteFill>;
};

const FinishFade=()=>{
  const f=useCurrentFrame();
  return <AbsoluteFill style={{background:NAVY,pointerEvents:'none',opacity:interpolate(f,[0,5,timeline.totalFrames-17,timeline.totalFrames-1],[1,0,0,1],C)}}/>;
};

export const FilmV4:React.FC = ()=> <AbsoluteFill style={{background:NAVY,color:PAPER,fontFamily:'Be Vietnam Pro, sans-serif',overflow:'hidden'}}>
  <FontGate>
    {timeline.shots.map(shot=><Sequence key={shot.id} name={shot.chapter} from={shot.start} durationInFrames={shot.end-shot.start} premountFor={24}>
      <Shot id={shot.id} duration={shot.end-shot.start}/>
    </Sequence>)}
    <Sequence name="Text FX • Mở phim" from={scene('opening').start} durationInFrames={scene('opening').duration}><SceneExit duration={scene('opening').duration}><Opening/></SceneExit></Sequence>
    <Sequence name="Text FX • Yên Thành" from={scene('brand').start} durationInFrames={scene('brand').duration}><SceneExit duration={scene('brand').duration}><Brand/></SceneExit></Sequence>
    <Sequence name="Text FX • Kiến thức" from={scene('knowledge').start} durationInFrames={scene('knowledge').duration}><SceneExit duration={scene('knowledge').duration}><Knowledge/></SceneExit></Sequence>
    <Sequence name="Text FX • Mô phỏng" from={scene('simulation').start} durationInFrames={scene('simulation').duration}><SceneExit duration={scene('simulation').duration}><Simulation/></SceneExit></Sequence>
    <Sequence name="Text FX • Cabin" from={scene('cabin').start} durationInFrames={scene('cabin').duration}><SceneExit duration={scene('cabin').duration}><Cabin/></SceneExit></Sequence>
    <Sequence name="Text FX • Đội xe" from={scene('fleet').start} durationInFrames={scene('fleet').duration}><SceneExit duration={scene('fleet').duration}><Fleet/></SceneExit></Sequence>
    <Sequence name="Text FX • Thực hành" from={scene('practice').start} durationInFrames={scene('practice').duration}><SceneExit duration={scene('practice').duration}><Practice/></SceneExit></Sequence>
    <Sequence name="Text FX • Cao trào 1" from={674} durationInFrames={116}><SceneExit duration={116}><Montage word="VỮNG VÀNG." number="01"/></SceneExit></Sequence>
    <Sequence name="Text FX • Cao trào 2" from={scene('montage-drive').start} durationInFrames={scene('signature').start-scene('montage-drive').start}><SceneExit duration={scene('signature').start-scene('montage-drive').start}><Montage word="TIẾN BƯỚC." number="02"/></SceneExit></Sequence>
    <Sequence name="Text FX • Kết thương hiệu" from={scene('signature').start} durationInFrames={scene('signature').duration}><Signature/></Sequence>
    {timeline.graphicTransitions.map(at=><Sequence key={at} name="SVG road transition" from={at-8} durationInFrames={18}><RoadWipe/></Sequence>)}
    <Audio src={staticFile('soundtrack.wav')}/>
    <FinishFade/>
  </FontGate>
</AbsoluteFill>;
