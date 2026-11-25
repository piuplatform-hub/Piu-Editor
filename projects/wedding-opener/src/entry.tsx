import React, {CSSProperties, useEffect, useState} from 'react';
import {
  AbsoluteFill, cancelRender, Composition, continueRender, delayRender, Easing,
  getRemotionEnvironment, Html5Audio, Img, interpolate, registerRoot, Sequence,
  staticFile, useCurrentFrame,
} from 'remotion';
import timeline from './timeline.json';
import './film.css';

type WeddingDetails = {brideName: string; groomName: string; weddingDate: string};
type Transition = 'dissolve' | 'page' | 'curtain';
type Shot = {
  id: string;
  endFrame: number;
  layout: 'opening' | 'pair' | 'portrait' | 'wide' | 'tradition' | 'closing';
  photos: string[];
  tone?: 'paper' | 'sage' | 'wine';
  side?: 'left' | 'right';
  transition?: Transition;
  accent?: string;
  focus?: number;
};

const shots = timeline.shots as Shot[];
const durationInFrames = shots[shots.length - 1].endFrame;
const transitionFrames: Record<Transition, number> = {dissolve: 16, page: 18, curtain: 23};
const enter = (frame: number, start: number, length: number) =>
  interpolate(frame, [start, start + length], [0, 1], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic),
  });

function useWeddingFonts() {
  const [handle] = useState(() => delayRender('Loading wedding title fonts'));
  useEffect(() => {
    const fontFiles = [
      new FontFace('Cormorant', `url("${staticFile('fonts/CormorantGaramond.ttf')}")`, {weight: '300 700'}),
      new FontFace('Cormorant', `url("${staticFile('fonts/CormorantGaramond-Italic.ttf')}")`, {weight: '300 700', style: 'italic'}),
      new FontFace('BeVietnam', `url("${staticFile('fonts/BeVietnamPro-Medium.ttf')}")`, {weight: '500'}),
    ];
    Promise.all(fontFiles.map((font) => font.load())).then((fonts) => {
      fonts.forEach((font) => document.fonts.add(font));
      continueRender(handle);
    }).catch(cancelRender);
  }, [handle]);
}

function Picture({photo, className, focus = 50, zoom = 1, style, origin}: {
  photo: string;
  className: string;
  focus?: number;
  zoom?: number;
  style?: CSSProperties;
  origin?: string;
}) {
  return <div className={`picture ${className}`} style={style}>
    <Img src={staticFile(`photos/${photo}.jpg`)} alt="" style={{
      objectPosition: `50% ${focus}%`, transformOrigin: origin ?? `50% ${focus}%`, transform: `scale(${zoom})`,
    }} />
  </div>;
}

const rise = (progress: number, distance: number): CSSProperties => ({
  opacity: progress, transform: `translateY(${distance * (1 - progress)}px)`,
});

function Opening({photo, frame, drift}: {photo: string; frame: number; drift: number}) {
  return <>
    <AbsoluteFill style={{opacity: enter(frame, 0, 23)}}>
      <Picture photo={photo} className="opening-photo" focus={54} zoom={1 + .042 * drift} origin="68% 43%" />
      <div className="opening-paper" />
    </AbsoluteFill>
    <h2 className="opener-title">
      <span style={rise(enter(frame, 13, 28), 36)}>Từ</span>
      <span style={rise(enter(frame, 22, 31), 42)}><em>hôm nay</em></span>
    </h2>
  </>;
}

function AlbumPair({shot, frame, drift}: {shot: Shot; frame: number; drift: number}) {
  const left = enter(frame, 0, 24);
  const right = enter(frame, 7, 25);
  const accent = enter(frame, 14, 26);
  return <>
    <div className="rule album-rule-left" style={{transform: `scaleX(${left})`}} />
    <div className="rule album-rule-right" style={{transform: `scaleX(${right})`}} />
    <Picture photo={shot.photos[0]} className="mounted-photo album-photo album-left"
      zoom={1 + .018 * drift} style={{opacity: left, transform: `translateX(${-26 * (1 - left)}px)`}} />
    <Picture photo={shot.photos[1]} className="mounted-photo album-photo album-right"
      zoom={1 + .022 * drift} style={{opacity: right, transform: `translateX(${26 * (1 - right)}px)`}} />
    {shot.accent ? <div className="album-ampersand" style={rise(accent, 10)}>{shot.accent}</div>
      : <div className="rule album-center-rule" style={{opacity: .66 * accent}} />}
  </>;
}

function Portrait({shot, drift}: {shot: Shot; drift: number}) {
  const side = shot.side ?? 'right';
  const shift = (side === 'left' ? -1 : 1) * (15 - 30 * drift);
  return <>
    <Img className="portrait-wash" src={staticFile(`washes/${shot.photos[0]}.jpg`)} alt="" />
    <div className={`portrait-mark portrait-mark-${side}`} />
    <Picture photo={shot.photos[0]} className={`mounted-photo portrait-photo portrait-photo-${side}`}
      zoom={1.008 + .031 * drift} style={{transform: `translateX(${shift}px)`}} />
    <div className={`portrait-lines portrait-lines-${side}`} style={{transform: `translateY(${12 * (drift - .5)}px)`}} />
  </>;
}

function Tradition({photo, frame, drift}: {photo: string; frame: number; drift: number}) {
  const image = enter(frame, 9, 31);
  const rule = enter(frame, 44, 31);
  return <>
    <Picture photo={photo} className="mounted-photo tradition-photo" zoom={1 + .022 * drift}
      style={{transform: `translateX(${35 * (1 - image)}px)`}} />
    <h2 className="tradition-title">
      <span style={rise(enter(frame, 24, 27), 32)}>Ngày</span>
      <span style={rise(enter(frame, 32, 30), 38)}><em>chung đôi</em></span>
    </h2>
    <div className="rule tradition-rule" style={{transform: `scaleX(${rule})`}} />
  </>;
}

function Closing({photo, frame, drift, details}: {
  photo: string;
  frame: number;
  drift: number;
  details: WeddingDetails;
}) {
  const names = [details.brideName, details.groomName].map((name) => name.trim().normalize('NFC')).filter(Boolean);
  const longest = Math.max(0, ...names.map((name) => Array.from(name).length));
  const nameSize = Math.min(132, 1540 / Math.max(8, longest));
  const fade = enter(frame, 8, 37);
  return <>
    <Picture photo={photo} className="mounted-photo closing-photo" zoom={1 + .019 * drift} />
    <div className="closing-message" style={rise(fade, 22)}>
      {names.length ? <h2 className="names-title" style={{fontSize: nameSize}}>
        <span>{names[0]}</span>
        {names.length === 2 ? <><span className="name-joiner"><em>&amp;</em></span><span>{names[1]}</span></> : null}
      </h2> : <h2 className="closing-title"><em>Cảm ơn</em></h2>}
      {details.weddingDate ? <div className="closing-date">{details.weddingDate.trim()}</div> : null}
      <p className={`closing-copy${names.length ? ' closing-copy-with-names' : ''}`}>
        {names.length ? 'Cảm ơn đã đến chung vui' : 'đã đến chung vui'}<br />cùng chúng mình
      </p>
      <div className="closing-rule" style={{transform: `scaleX(${enter(frame, 30, 34)})`}} />
    </div>
  </>;
}

function sceneLayer(transition: Transition | undefined, frame: number): CSSProperties {
  if (!transition) return {};
  const progress = enter(frame, 0, transitionFrames[transition]);
  if (transition === 'dissolve') return {opacity: progress};
  if (transition === 'page') return {clipPath: `inset(0 ${(1 - progress) * 100}% 0 0)`};
  const outside = (1 - progress) * 50;
  return {clipPath: `inset(0 ${outside}% 0 ${outside}%)`};
}

function Scene({shot, shotFrames, details}: {shot: Shot; shotFrames: number; details: WeddingDetails}) {
  const frame = useCurrentFrame();
  const drift = Math.min(1, frame / (shotFrames - 1));
  const photo = shot.photos[0];
  let content;
  switch (shot.layout) {
    case 'opening': content = <Opening photo={photo} frame={frame} drift={drift} />; break;
    case 'pair': content = <AlbumPair shot={shot} frame={frame} drift={drift} />; break;
    case 'portrait': content = <Portrait shot={shot} drift={drift} />; break;
    case 'wide': content = <>
      <Picture photo={photo} className="wide-photo" focus={shot.focus} zoom={1 + .054 * drift} />
      <div className="wide-shade" />
    </>; break;
    case 'tradition': content = <Tradition photo={photo} frame={frame} drift={drift} />; break;
    case 'closing': content = <Closing photo={photo} frame={frame} drift={drift} details={details} />; break;
  }
  return <AbsoluteFill className={`scene tone-${shot.tone ?? 'paper'}`} style={sceneLayer(shot.transition, frame)}>
    {content}
  </AbsoluteFill>;
}

function WeddingFilm(details: WeddingDetails) {
  useWeddingFonts();
  return <AbsoluteFill className="wedding-film">
    {getRemotionEnvironment().isRendering ? null : <Html5Audio src={staticFile('soundtrack.wav')} />}
    {shots.map((shot, index) => {
      const startFrame = index === 0 ? 0 : shots[index - 1].endFrame;
      const shotFrames = shot.endFrame - startFrame;
      const outgoing = shots[index + 1]?.transition;
      return <Sequence key={shot.id} name={shot.id} from={startFrame}
        durationInFrames={shotFrames + (outgoing ? transitionFrames[outgoing] : 0)}>
        <Scene shot={shot} shotFrames={shotFrames} details={details} />
      </Sequence>;
    })}
  </AbsoluteFill>;
}

registerRoot(() => <Composition id="TuHomNay" component={WeddingFilm}
  width={timeline.width} height={timeline.height} fps={timeline.fps} durationInFrames={durationInFrames}
  defaultProps={{brideName: '', groomName: '', weddingDate: ''}} />);
