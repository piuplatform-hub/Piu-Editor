import React from 'react';
import {Composition, registerRoot} from 'remotion';
import {FilmV4} from './Film';
import {AccentDiagnosis} from './AccentDiagnosis';
import {AccentRegression} from './AccentRegression';

const Root=()=> <>
  <Composition id="YenThanhV4" component={FilmV4} width={1920} height={1080} fps={24} durationInFrames={975}/>
  <Composition id="AccentDiagnosis" component={AccentDiagnosis} width={1920} height={1600} fps={24} durationInFrames={1}/>
  <Composition id="AccentRegression" component={AccentRegression} width={1920} height={1500} fps={24} durationInFrames={96} defaultProps={{reference:false}}/>
  <Composition id="AccentReference" component={AccentRegression} width={1920} height={1500} fps={24} durationInFrames={96} defaultProps={{reference:true}}/>
</>;
registerRoot(Root);
