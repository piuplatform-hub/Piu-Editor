import React from 'react';
import {Composition, registerRoot} from 'remotion';
import {FilmV3} from './Film';

const Root=()=> <Composition id="YenThanhV3" component={FilmV3} width={1920} height={1080} fps={24} durationInFrames={975}/>;
registerRoot(Root);
