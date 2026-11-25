import React from 'react';
import {
  AbsoluteFill, Composition, Img, OffthreadVideo, Sequence, Easing, interpolate, registerRoot,
  useCurrentFrame, useVideoConfig,
} from 'remotion';
import {useGsapTimeline} from '@remotion/gsap';
import plan from './timeline.json';
import {FX, FontGate, MediaImage} from './media-layers';

const WIDTH = 1920;
const HEIGHT = 1080;
const INK = '#36241e';
const PAPER = '#f5eadc';
const CLAMP = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const OVERLAP = 61;

type AlbumId = 'veil' | 'portrait' | 'ceremony';
type LayoutBox = {
  x: number; y: number; width: number; height: number;
  position?: string; tilt?: number; arch?: boolean;
};

const LAYOUTS: Record<AlbumId, LayoutBox[]> = {
  veil: [
    {x: 101, y: 63, width: 616, height: 957, position: '50% 23%', arch: true},
    {x: 769, y: 86, width: 1052, height: 900, position: '50% 4%', tilt: -1.4},
  ],
  portrait: [
    {x: 63, y: 177, width: 545, height: 803, position: '50% 28%', tilt: -4.3},
    {x: 605, y: 39, width: 713, height: 997, position: '50% 24%'},
    {x: 1319, y: 136, width: 535, height: 809, position: '50% 22%', tilt: 4.3},
  ],
  ceremony: [
    {x: 76, y: 77, width: 564, height: 937, position: '50% 42%', arch: true},
    {x: 666, y: 32, width: 701, height: 1011, position: '50% 25%'},
    {x: 1398, y: 136, width: 439, height: 809, position: '50% 28%', tilt: 2.8},
  ],
};
const BACKDROPS: Record<AlbumId, string> = {veil: 'B21', portrait: 'B41', ceremony: 'B40'};

const Opening: React.FC<{photo: string; duration: number}> = ({photo, duration}) => {
  const {fps} = useVideoConfig();
  const ref = useGsapTimeline<HTMLDivElement>(({timeline, selector}) => {
    timeline.fromTo(selector('.opening-image'),
      {scale: 1.072, x: -14, y: -8},
      {scale: 1.014, x: 0, y: 0, duration: duration / fps, ease: 'sine.inOut'}, 0);
    timeline.fromTo(selector('.title-line'), {y: 23, opacity: 0},
      {y: 0, opacity: 1, duration: 1.15, stagger: .24, ease: 'power3.out'}, .25);
    timeline.fromTo(selector('.title-rule'), {scaleX: 0, opacity: 0},
      {scaleX: 1, opacity: .95, duration: 1.1, ease: 'power2.inOut'}, .74);
    timeline.fromTo(selector('.foreground-leaf'), {x: -17, y: 22, rotation: 4},
      {x: 4, y: -8, rotation: 0, duration: duration / fps, ease: 'sine.inOut'}, 0);
  }, {dependencies: [duration, fps]});
  return <AbsoluteFill ref={ref} style={{overflow: 'hidden', background: PAPER}}>
    <MediaImage id={photo} className="opening-image"/>
    <AbsoluteFill style={{background: 'linear-gradient(95deg, #ffefdd47 0%, #f7e5d21a 32%, transparent 57%)'}}/>
    <div style={{position: 'absolute', left: 104, top: 227, color: INK, fontFamily: 'WeddingSerif', lineHeight: .94}}>
      <div className="title-line" style={{fontSize: 145}}>Từ</div>
      <div className="title-line" style={{fontSize: 153, fontStyle: 'italic', marginTop: 6}}>hôm nay</div>
      <div className="title-rule" style={{height: 2, width: 164, marginTop: 34, background: '#9a7459', transformOrigin: '0 50%'}}/>
    </div>
    <Img className="foreground-leaf" src={FX('leaf 05.png')}
      style={{position: 'absolute', width: 285, height: 285, objectFit: 'contain', left: -21, bottom: 20, opacity: .68}}/>
  </AbsoluteFill>;
};

const Album: React.FC<{id: AlbumId; photos: string[]; duration: number}> = ({id, photos, duration}) => {
  const {fps} = useVideoConfig();
  const wine = id === 'ceremony';
  const placement = LAYOUTS[id];
  const ref = useGsapTimeline<HTMLDivElement>(({timeline, selector}) => {
    timeline.fromTo(selector('.album-background'), {scale: 1.035, x: -12},
      {scale: 1.09, x: 8, duration: duration / fps, ease: 'sine.inOut'}, 0);
    placement.forEach((box, index) => {
      const direction = index === 0 ? -1 : 1;
      const start = index * .15;
      const arrival = (index === 1 ? 1.13 : 1.3);
      const targets = selector('[data-photo="' + index + '"]');
      timeline.fromTo(targets,
        {x: 49 * direction, y: 34 + index * 10, scale: .972, rotation: (box.tilt ?? 0) + direction * 2.4, opacity: .18},
        {x: 0, y: 0, scale: 1, rotation: box.tilt ?? 0, opacity: 1, duration: arrival, ease: 'power2.out'}, start);
      timeline.to(targets,
        {x: 13 * direction, y: -7 + index * 3, rotation: (box.tilt ?? 0) - direction * .65,
          duration: Math.max(1, duration / fps - start - arrival), ease: 'sine.inOut'},
        start + arrival);
    });
    const accents = selector('.botanical');
    if (accents.length) {
      timeline.fromTo(accents, {x: -12, y: 33, opacity: 0}, {
        x: 0, y: 0, opacity: .90, stagger: .13, duration: 1.55, ease: 'power2.out',
      }, .4);
    }
  }, {dependencies: [id, duration, fps]});
  return <AbsoluteFill ref={ref} style={{background: wine ? '#601c2b' : PAPER, overflow: 'hidden'}}>
    <MediaImage className="album-background" id={BACKDROPS[id] + '-background'}/>
    <AbsoluteFill style={{background: wine
      ? 'radial-gradient(ellipse at 45% 20%, #c7634f33, #3109142e 81%)'
      : 'radial-gradient(ellipse at 30% 10%, #fff7e960, #b68b6026 92%)'}}/>
    {photos.map((photo, index) => {
      const box = placement[index];
      const round = box.arch ? box.width / 2 + 'px ' + box.width / 2 + 'px 4px 4px' : '5px';
      return <div key={photo} data-photo={index} style={{
        position: 'absolute', left: box.x, top: box.y, width: box.width, height: box.height,
        borderRadius: round, background: wine ? '#dfb578' : '#fff4e2',
        border: wine ? '4px solid #e4bf87' : '7px solid #f9eddf', boxSizing: 'border-box',
        boxShadow: wine ? '0 18px 45px #2909108a' : '0 17px 37px #4f342945',
        overflow: 'hidden', transformOrigin: '50% 57%',
      }}>
        <MediaImage id={photo} position={box.position}/>
      </div>;
    })}
    {id === 'veil' && <>
      <Img className="botanical" src={FX('leaf 04.png')} style={{
        position: 'absolute', objectFit: 'contain', width: 330, left: -71, bottom: -32,
      }}/>
      <Img className="botanical" src={FX('Flower 03.png')} style={{
        position: 'absolute', objectFit: 'contain', width: 178, left: 48, bottom: -27,
      }}/>
    </>}
  </AbsoluteFill>;
};

const Reveal: React.FC<React.PropsWithChildren<{id: string}>> = ({id, children}) => {
  const frame = useCurrentFrame();
  const progress = interpolate(frame, [0, OVERLAP - 5], [0, 1], {...CLAMP, easing: Easing.inOut(Easing.cubic)});
  const iris = -18 + (progress * 160);
  const wipe = -23 + (progress * 149);
  const mask = id === 'veil'
    ? 'radial-gradient(ellipse at 38% 51%, #000 ' + iris + '%, transparent ' + (iris + 18) + '%)'
    : 'linear-gradient(108deg, #000 ' + wipe + '%, transparent ' + (wipe + 23) + '%)';
  return <AbsoluteFill style={id === 'opening' ? {} : id === 'ceremony' ? {opacity: progress} : {maskImage: mask}}>
    {children}
  </AbsoluteFill>;
};

const CeremonyFlare: React.FC = () => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 17, plan.accentFrames - 1], [0, .37, 0], CLAMP);
  return <AbsoluteFill style={{opacity, mixBlendMode: 'screen', pointerEvents: 'none'}}>
    <OffthreadVideo src={FX('ceremony-flare.mp4')} muted
      style={{height: '100%', width: '100%', objectFit: 'cover'}}/>
  </AbsoluteFill>;
};

const Preview: React.FC = () => {
  const ceremony = plan.scenes.find((scene) => scene.id === 'ceremony');
  if (!ceremony) throw new Error('Missing ceremony scene');
  return <FontGate>
    <AbsoluteFill style={{background: PAPER, overflow: 'hidden'}}>
      {plan.scenes.map((scene, index) => {
        const next = plan.scenes[index + 1];
        const duration = (next ? next.from + OVERLAP : plan.durationInFrames) - scene.from;
        return <Sequence key={scene.id} from={scene.from} durationInFrames={duration} name={scene.id}>
          <Reveal id={scene.id}>
            {scene.id === 'opening'
              ? <Opening photo={scene.photos[0]} duration={duration}/>
              : <Album id={scene.id as AlbumId} photos={scene.photos} duration={duration}/>}
          </Reveal>
        </Sequence>;
      })}
      <Sequence from={ceremony.from - 3} durationInFrames={plan.accentFrames} name="Vệt sáng Song Hỷ">
        <CeremonyFlare/>
      </Sequence>
    </AbsoluteFill>
  </FontGate>;
};

const Root: React.FC = () => <Composition id="TuHomNayPreview" component={Preview} width={WIDTH} height={HEIGHT}
  fps={plan.fps} durationInFrames={plan.durationInFrames}/>;
registerRoot(Root);
