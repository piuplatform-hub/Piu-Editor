import React from 'react';
import {AbsoluteFill, Composition, Easing, Img, OffthreadVideo, Sequence, interpolate,
  registerRoot, useCurrentFrame, useVideoConfig} from 'remotion';
import {useGsapTimeline} from '@remotion/gsap';
import {FX, FontGate, MediaImage} from '../v003/media-layers';
import plan from './timeline.json';

const PAPER = '#f6eadc';
const INK = '#402b24';
const OVERLAP = 58;
const CLAMP = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

type Card = {
  x: number; y: number; w: number; h: number;
  focus?: string; tilt?: number; arch?: boolean;
};
type AlbumLayout = {backdrop: string; cards: Card[]};
type TextCue = {lines: string[]; support?: string; inFrame: number; outFrame: number};
type Shot = {id: string; from: number; photos: string[]; text?: TextCue};

const ALBUMS: Record<string, AlbumLayout> = {
  veil: {backdrop: 'B21', cards: [
    {x: 654, y: 63, w: 524, h: 946, focus: '50% 25%', arch: true},
    {x: 1180, y: 122, w: 665, h: 831, focus: '50% 2%', tilt: 2},
  ]},
  portraits: {backdrop: 'B41', cards: [
    {x: 79, y: 146, w: 530, h: 823, focus: '50% 25%', tilt: -4},
    {x: 615, y: 37, w: 688, h: 1005, focus: '50% 27%'},
    {x: 1312, y: 143, w: 532, h: 803, focus: '50% 24%', tilt: 3.5},
  ]},
  toast: {backdrop: 'B12', cards: [
    {x: 49, y: 53, w: 1046, h: 975, focus: '50% 2%'},
    {x: 1118, y: 89, w: 752, h: 913, focus: '50% 22%', tilt: 2.2},
  ]},
  ceremony: {backdrop: 'B40', cards: [
    {x: 652, y: 68, w: 517, h: 938, focus: '50% 28%', arch: true},
    {x: 1189, y: 69, w: 650, h: 933, focus: '50% 22%', tilt: 1.8},
  ]},
  closing: {backdrop: 'B27', cards: [
    {x: 738, y: 55, w: 599, h: 974, focus: '50% 27%', tilt: -1.8},
    {x: 1353, y: 114, w: 488, h: 841, focus: '50% 38%', tilt: 2.1},
  ]},
};

const Lettering: React.FC<{cue: TextCue; scene: string}> = ({cue, scene}) => {
  const {fps} = useVideoConfig();
  const warm = scene === 'ceremony';
  const close = scene === 'closing';
  const opening = scene === 'opening';
  const ref = useGsapTimeline<HTMLDivElement>(({timeline, selector}) => {
    const start = cue.inFrame / fps;
    const end = cue.outFrame / fps;
    const words = selector('.title-line');
    const subline = selector('.title-support');
    const rule = selector('.title-rule');
    timeline.fromTo(words, {opacity: 0, y: 22, filter: 'blur(4px)'},
      {opacity: 1, y: 0, filter: 'blur(0px)', duration: 1.02, stagger: .17, ease: 'power3.out'}, start);
    timeline.fromTo(rule, {scaleX: 0, opacity: 0},
      {scaleX: 1, opacity: 1, duration: .93, ease: 'power2.inOut'}, start + .26);
    if (subline.length) {
      timeline.fromTo(subline, {opacity: 0, y: 11},
        {opacity: 1, y: 0, duration: .74, ease: 'sine.out'}, start + .4);
      timeline.to(subline, {opacity: 0, y: -8, duration: .52, ease: 'sine.inOut'}, end);
    }
    timeline.to(rule, {scaleX: .2, opacity: 0, duration: .5, ease: 'sine.inOut'}, end);
    timeline.to(words, {opacity: 0, y: -16, filter: 'blur(3px)', duration: .68,
      stagger: .07, ease: 'sine.inOut'}, end + .07);
  }, {dependencies: [cue, fps]});
  return <div ref={ref} style={{
    position: 'absolute', left: opening ? 104 : 110, top: opening ? 243 : close ? 370 : 317,
    color: warm ? '#fff4de' : INK, fontFamily: 'WeddingSerif', lineHeight: 1.03,
  }}>
    {cue.lines.map((line, index) => <div className="title-line" key={line}
      style={{fontStyle: index || close ? 'italic' : 'normal',
        fontSize: opening ? (index ? 151 : 145) : close ? 132 : index ? 110 : 124,
        marginTop: index ? -1 : 0}}>
      {line.normalize('NFC')}
    </div>)}
    <div className="title-rule" style={{width: opening ? 149 : 115, height: 2, marginTop: close ? 28 : 27,
      background: warm ? '#e0b382' : '#9a7055', transformOrigin: '0% 50%'}}/>
    {cue.support && <div className="title-support" style={{
      fontFamily: 'WeddingSans', fontWeight: 500, fontSize: 37, marginTop: 24,
    }}>{cue.support.normalize('NFC')}</div>}
  </div>;
};

const WidePhoto: React.FC<{photo: string; frames: number}> = ({photo, frames}) => {
  const {fps} = useVideoConfig();
  const ref = useGsapTimeline<HTMLDivElement>(({timeline, selector}) => {
    timeline.fromTo(selector('.wide-photo'), {scale: 1.085, x: -22, y: -9},
      {scale: 1.015, x: 0, y: 0, duration: frames / fps, ease: 'sine.inOut'}, 0);
    timeline.fromTo(selector('.opening-leaf'), {x: -18, y: 24, rotation: -5},
      {x: 5, y: 0, rotation: 0, duration: frames / fps, ease: 'sine.inOut'}, 0);
  }, {dependencies: [frames, fps]});
  return <AbsoluteFill ref={ref} style={{overflow: 'hidden'}}>
    <MediaImage id={photo} className="wide-photo"/>
    <AbsoluteFill style={{background: 'linear-gradient(103deg, #ffefdc69, #ffefdc1c 40%, transparent 54%)'}}/>
    <Img className="opening-leaf" src={FX('leaf 05.png')} style={{position: 'absolute', left: -16, bottom: 5,
      width: 257, opacity: .61, objectFit: 'contain'}}/>
  </AbsoluteFill>;
};

const Album: React.FC<{shot: Shot; frames: number}> = ({shot, frames}) => {
  const layout = ALBUMS[shot.id];
  const red = shot.id === 'ceremony';
  const {fps} = useVideoConfig();
  const ref = useGsapTimeline<HTMLDivElement>(({timeline, selector}) => {
    timeline.fromTo(selector('.background'), {scale: 1.04, x: -10},
      {scale: 1.09, x: 9, duration: frames / fps, ease: 'sine.inOut'}, 0);
    layout.cards.forEach((box, index) => {
      const side = index === 0 ? -1 : 1;
      const tilt = box.tilt ?? 0;
      const start = .08 + .135 * index;
      const arrival = 1.24;
      const targets = selector('[data-frame="' + index + '"]');
      timeline.fromTo(targets,
        {x: 42 * side, y: 29 + 8 * index, rotation: tilt + side * 1.9, scale: .973, opacity: .4},
        {x: 0, y: 0, rotation: tilt, scale: 1, opacity: 1, duration: arrival, ease: 'power2.out'}, start);
      timeline.to(targets, {x: side * 15, y: -9 + 3 * index, rotation: tilt - side * .55,
        duration: frames / fps - arrival - start, ease: 'sine.inOut'}, start + arrival);
    });
    const flowers = selector('.album-flower');
    if (flowers.length) {
      timeline.fromTo(flowers, {y: 23, opacity: 0},
        {y: 0, opacity: .79, duration: 1.56, stagger: .14, ease: 'sine.out'}, .48);
    }
  }, {dependencies: [layout, frames, fps]});
  return <AbsoluteFill ref={ref} style={{overflow: 'hidden', background: red ? '#671f2d' : PAPER}}>
    <MediaImage id={layout.backdrop + '-background'} className="background"/>
    <AbsoluteFill style={{background: red
      ? 'linear-gradient(95deg, #3a101be0 0%, #5b172881 33%, transparent 64%)'
      : 'linear-gradient(100deg, #fff4e4a6 0%, #fff5e333 44%, transparent 71%)'}}/>
    {shot.photos.map((photo, index) => {
      const card = layout.cards[index];
      return <div key={photo} data-frame={index} style={{
        position: 'absolute', left: card.x, top: card.y, width: card.w, height: card.h,
        borderRadius: card.arch ? (card.w / 2) + 'px ' + (card.w / 2) + 'px 4px 4px' : '4px',
        border: red ? '4px solid #e0b580' : '7px solid #fff3e5',
        boxSizing: 'border-box', overflow: 'hidden', background: red ? '#d09a66' : '#f7e8d8',
        boxShadow: red ? '0 19px 42px #320c175b' : '0 17px 37px #69482f46',
        transformOrigin: '50% 58%',
      }}><MediaImage id={photo} position={card.focus}/></div>;
    })}
    {shot.id === 'veil' && <>
      <Img className="album-flower" src={FX('leaf 04.png')} style={{position: 'absolute', left: -70, bottom: -55, width: 308}}/>
      <Img className="album-flower" src={FX('Flower 03.png')} style={{position: 'absolute', left: 65, bottom: -20, width: 154}}/>
    </>}
  </AbsoluteFill>;
};

const DateCard: React.FC = () => {
  const {fps} = useVideoConfig();
  const ref = useGsapTimeline<HTMLDivElement>(({timeline, selector}) => {
    timeline.fromTo(selector('.date-card'), {opacity: 0, y: 15},
      {opacity: 1, y: 0, duration: .91, ease: 'power2.out'}, 0);
    timeline.fromTo(selector('.date-row'), {opacity: 0, y: 5},
      {opacity: 1, y: 0, stagger: .12, duration: .63, ease: 'sine.out'}, 8 / fps);
  }, {dependencies: [fps]});
  return <AbsoluteFill ref={ref} style={{pointerEvents: 'none'}}>
    <div className="date-card" style={{
      position: 'absolute', right: 101, bottom: 89, padding: '15px 21px 16px', borderLeft: '2px solid #e3b882',
      background: '#2a1719e8', borderRadius: '0 5px 5px 0', color: '#fff5e6',
      fontFamily: 'WeddingSans', fontWeight: 500, fontVariantNumeric: 'tabular-nums',
      boxShadow: '0 5px 18px #2410103d', lineHeight: 1.35,
    }}>
      {[[plan.weddingDate.solar, 'Dương lịch'], [plan.weddingDate.lunar, 'Âm lịch']].map(([date, label]) =>
        <div key={date} className="date-row" style={{display: 'flex', alignItems: 'baseline',
          gap: 18, fontSize: 29, marginTop: label === 'Âm lịch' ? 4 : 0}}>
          <span>{date}</span><span style={{fontSize: 22, color: '#edd9c2'}}>{label}</span>
        </div>)}
    </div>
  </AbsoluteFill>;
};

const Scene: React.FC<{shot: Shot; frames: number}> = ({shot, frames}) => {
  const frame = useCurrentFrame();
  const progress = interpolate(frame, [0, OVERLAP - 3], [0, 1], {...CLAMP, easing: Easing.inOut(Easing.cubic)});
  const radial = -20 + 153 * progress;
  const across = -24 + 154 * progress;
  const reveal = shot.id === 'veil'
    ? {maskImage: 'radial-gradient(ellipse at 44% 53%, #000 ' + radial + '%, transparent ' + (radial + 20) + '%)'}
    : shot.id === 'portraits' || shot.id === 'closing'
      ? {maskImage: 'linear-gradient(110deg, #000 ' + across + '%, transparent ' + (across + 24) + '%)'}
      : {opacity: progress};
  return <AbsoluteFill style={shot.id === 'opening' ? {} : reveal}>
    {shot.id === 'opening' ? <WidePhoto photo={shot.photos[0]} frames={frames}/> : <Album shot={shot} frames={frames}/>}
    {shot.text && <Lettering cue={shot.text} scene={shot.id}/>}
  </AbsoluteFill>;
};

const Flare: React.FC = () => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 19, plan.accentFrames - 1], [0, .29, 0], CLAMP);
  return <AbsoluteFill style={{opacity, mixBlendMode: 'screen'}}>
    <OffthreadVideo src={FX('ceremony-flare.mp4')} muted style={{width: '100%', height: '100%', objectFit: 'cover'}}/>
  </AbsoluteFill>;
};

const Preview: React.FC = () => {
  const ceremony = plan.scenes.find((shot) => shot.id === 'ceremony');
  if (!ceremony) throw new Error('Missing ceremony shot');
  return <FontGate withSans>
    <AbsoluteFill style={{background: PAPER, overflow: 'hidden'}}>
      {plan.scenes.map((shot, index) => {
        const next = plan.scenes[index + 1];
        const frames = (next ? next.from + OVERLAP : plan.durationInFrames) - shot.from;
        return <Sequence key={shot.id} from={shot.from} durationInFrames={frames} name={shot.id}>
          <Scene shot={shot} frames={frames}/>
        </Sequence>;
      })}
      <Sequence from={ceremony.from - 2} durationInFrames={plan.accentFrames} name="Vệt sáng Song Hỷ">
        <Flare/>
      </Sequence>
      <Sequence from={plan.weddingDate.from} name="Ngày cưới">
        <DateCard/>
      </Sequence>
    </AbsoluteFill>
  </FontGate>;
};

const Root: React.FC = () => <Composition id="TuHomNayPreview" component={Preview}
  width={1920} height={1080} fps={plan.fps} durationInFrames={plan.durationInFrames}/>;
registerRoot(Root);
