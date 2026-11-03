import React,{useEffect,useState} from 'react';
import {AbsoluteFill,delayRender,continueRender,staticFile,cancelRender} from 'remotion';
import {loadFont} from '@remotion/fonts';

// Controlled reproduction: same font/size/content, only the glyph clipping changes.
export const AccentDiagnosis=()=>{
  const [handle]=useState(()=>delayRender('Controlled accent comparison'));
  const [ready,setReady]=useState(false);
  useEffect(()=>{loadFont({family:'Manrope',url:staticFile('fonts/Manrope.ttf'),weight:'200 800'})
    .then(()=>{setReady(true);continueRender(handle)}).catch(cancelRender)},[handle]);
  if(!ready)return null;
  return <AbsoluteFill style={{background:'#e9eef1',color:'#09243a',fontFamily:'Manrope',padding:50}}>
    <div style={{display:'flex',gap:60}}>
      {[true,false].map(clipped=><div key={String(clipped)} style={{width:880}}>
        <div style={{fontSize:27,fontWeight:600,marginBottom:45}}>{clipped?'v003: clipPath inset(0) on each word':'Reference: identical glyphs without clipping'}</div>
        {['TỰ TIN.','VỮNG','KIẾN THỨC.','HIỂU ĐÚNG.','RÈN TỪNG','THAO TÁC.','SẴN SÀNG CẦM LÁI.'].map(text=><div key={text} style={{fontSize:text.length>14?63:100,fontWeight:750,lineHeight:1.13,letterSpacing:'-.052em',padding:'0.12em 0.12em 0.14em',marginBottom:10}}>
          {text.split(' ').map((word,i)=><span key={i} style={{display:'inline-block',verticalAlign:'top',clipPath:clipped?'inset(0 0% 0 0)':undefined,marginRight:'.24em'}}>{word}</span>)}
        </div>)}
      </div>)}
    </div>
  </AbsoluteFill>;
};
