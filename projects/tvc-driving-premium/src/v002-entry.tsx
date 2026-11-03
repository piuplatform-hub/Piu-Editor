import React from 'react';
import {Composition,registerRoot} from 'remotion';
import {PremiumFilmV2,TOTAL,FPS} from './v002-film';
registerRoot(()=> <Composition id="PremiumDrivingV2" component={PremiumFilmV2} durationInFrames={TOTAL} fps={FPS} width={1920} height={1080}/>);
