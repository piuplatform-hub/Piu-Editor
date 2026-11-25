import React from 'react';
import {AbsoluteFill, Composition, registerRoot} from 'remotion';
import {FontGate} from '../v003/media-layers';
import plan from './timeline.json';

const cues = plan.chapters.flatMap((chapter) => chapter.scenes).filter((scene) => scene.text);
const face = 'WeddingSerif';
const sans = 'WeddingSans';

const DateArtwork: React.FC = () => <div style={{
  position: 'absolute', left: 18, top: 16, width: 350, padding: '11px 17px 13px',
  background: '#2d191aee', borderLeft: '2px solid #d7ab80', color: '#fff3df', borderRadius: '0 5px 5px 0',
  boxSizing: 'border-box', fontFamily: sans, fontWeight: 500, fontVariantNumeric: 'tabular-nums',
}}>
  {[[plan.solarDate, 'Dương lịch'], [plan.lunarDate, 'Âm lịch']].map(([date, label], i) =>
    <div key={date} style={{display: 'grid', gridTemplateColumns: '192px 1fr', alignItems: 'baseline',
      marginTop: i * 4, lineHeight: 1.3, fontSize: 30}}>
      <span>{date}</span><span style={{color: '#efdbc4', fontSize: 21}}>{label}</span>
    </div>)}
</div>;

const Artwork: React.FC<{cueId: string}> = ({cueId}) => {
  if (cueId === 'date') return <FontGate withSans><DateArtwork/></FontGate>;
  const scene = cues.find((item) => item.text?.id === cueId);
  if (!scene?.text) throw new Error('Unknown lettering cue ' + cueId);
  const {text} = scene;
  const wine = scene.palette === 'wine';
  const ink = wine ? '#fff1db' : '#3f2923';
  return <FontGate withSans>
    <AbsoluteFill style={{color: ink, fontFamily: face}}>
      {text.eyebrow && <div style={{position: 'absolute', left: 18, top: 11, fontSize: 37, fontStyle: 'italic',
        lineHeight: 1.3, color: wine ? '#f1c999' : '#805942'}}>{text.eyebrow.normalize('NFC')}</div>}
      {text.lines.map((line, index) => <div key={line.text} style={{
        position: 'absolute', left: 18, top: 88 + index * 166, fontStyle: line.italic ? 'italic' : 'normal',
        fontSize: line.size, lineHeight: 1.2, whiteSpace: 'nowrap',
      }}>{line.text.normalize('NFC')}</div>)}
      <div style={{position: 'absolute', top: 443, left: 18, width: text.names ? 147 : 110, height: 2,
        background: wine ? '#edbf88' : '#a27958'}}/>
    </AbsoluteFill>
  </FontGate>;
};

const Root: React.FC = () => <Composition id="WeddingLetterArtwork" component={Artwork}
  defaultProps={{cueId: '001'}} width={752} height={468} fps={50} durationInFrames={1}/>;
registerRoot(Root);
