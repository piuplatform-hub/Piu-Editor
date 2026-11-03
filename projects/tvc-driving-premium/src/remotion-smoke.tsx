import React from 'react';
import {AbsoluteFill,Composition,registerRoot,useCurrentFrame} from 'remotion';
const Test=()=>{const f=useCurrentFrame();return <AbsoluteFill style={{background:'#06192b',color:'white',fontSize:90,justifyContent:'center',alignItems:'center',fontFamily:'sans-serif'}}>REMOTION • YÊN THÀNH • {f}</AbsoluteFill>};
registerRoot(()=> <Composition id="Smoke" component={Test} durationInFrames={24} fps={24} width={1920} height={1080}/>);
