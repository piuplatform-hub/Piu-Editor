"""Prepare a beat-locked TVC montage and layered sound design. Originals untouched."""
from pathlib import Path
import array, json, math, random, subprocess, wave

PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT.parents[1]
WORK = PROJECT / 'working'
PUBLIC = PROJECT / 'public'
FPS = 24
BEAT = 60 / 124
TOTAL = round(84 * BEAT * FPS)

def run(args, log):
    result = subprocess.run(args, capture_output=True, text=True, encoding='utf8', errors='replace')
    (WORK / log).write_text(result.stdout + result.stderr, encoding='utf8')
    if result.returncode:
        raise RuntimeError((result.stderr or result.stdout)[-2500:])

def frame(beat): return round(beat * BEAT * FPS)

SHOTS = [
    (0,4,2,0.65,'Khởi đầu'),
    (4,12,3,0.35,'Tầm nhìn toàn cảnh'),
    (12,20,1,0.65,'Đội xe'),
    (20,28,4,0.45,'Nền tảng'),
    (28,36,0,0.65,'Mô phỏng'),
    (36,44,5,1.25,'Thao tác'),
    (44,52,6,2.85,'Thực tế'),
    (52,56,2,3.65,'Chuyển động'),
    (56,60,1,5.55,'Đồng bộ'),
    (60,62,5,5.7,'Chi tiết'),
    (62,64,4,5.8,'Con người'),
    (64,68,6,6.15,'Hành trình'),
    (68,76,3,5.65,'Tự tin'),
    (76,84,6,1.3,'Brand close'),
]

def prepare_video():
    paths=[];timeline=[]
    for i,(start,end,clip,trim,title) in enumerate(SHOTS):
        frames=frame(end)-frame(start)
        out=WORK/f'shot-{i:02d}.mp4'
        vf='fps=24,scale=1920:1080:flags=lanczos,setsar=1,eq=contrast=1.045:saturation=0.96:brightness=-0.008,colorbalance=rs=0.006:bs=0.012,format=yuv420p'
        run(['ffmpeg','-v','error','-ss',str(trim),'-i',str(PUBLIC/'video'/f'clip-{clip:02d}.mp4'),'-an',
             '-vf',vf,'-frames:v',str(frames),'-c:v','libx264','-preset','fast','-crf','17','-threads','3',
             '-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-y',str(out)],f'shot-{i:02d}.log')
        paths.append(out)
        timeline.append(dict(start=frame(start),end=frame(end),clip=clip,sourceStart=trim,title=title))
        print('SHOT',i,frames,'frames',flush=True)
    concat=WORK/'concat.txt'
    concat.write_text('\n'.join("file '"+p.as_posix()+"'" for p in paths),encoding='utf8')
    run(['ffmpeg','-v','error','-f','concat','-safe','0','-i',str(concat),'-an','-c','copy','-movflags','+faststart','-y',str(PUBLIC/'video/edit-base.mp4')],'concat.log')
    (PROJECT/'src/timeline.json').write_text(json.dumps(dict(fps=FPS,totalFrames=TOTAL,bpm=124,shots=timeline),ensure_ascii=False,indent=2),encoding='utf8')

def write_wave(path, left, right, rate=48000):
    pcm=array.array('h')
    for l,r in zip(left,right): pcm.extend((int(max(-1,min(1,l))*32767),int(max(-1,min(1,r))*32767)))
    with wave.open(str(path),'wb') as out:
        out.setnchannels(2);out.setsampwidth(2);out.setframerate(rate);out.writeframes(pcm.tobytes())

def design_effects():
    sr=48000;rng=random.Random(3721)
    for name,dur in [('air',0.6),('riser',1.7),('impact',1.7),('text',0.12)]:
        left=[];right=[];phase=0;low=0
        for i in range(int(sr*dur)):
            t=i/sr;x=t/dur;noise=rng.uniform(-1,1)
            low += .18*(noise-low)
            if name=='air':
                env=math.sin(math.pi*x)**2.4
                v=(noise-low*.8)*env*.28
                pan=-.75+1.5*x
            elif name=='riser':
                env=x*x*(min(1,(1-x)*30))
                phase+=2*math.pi*(220+1800*x*x)/sr
                v=(low*.65+math.sin(phase)*.07)*env*.5
                pan=math.sin(x*math.pi)*.28
            elif name=='impact':
                phase+=2*math.pi*(42+70*math.exp(-t*16))/sr
                v=(math.sin(phase)*math.exp(-t*4.2)*.52+low*math.exp(-t*32)*.35)*min(1,t*500)
                pan=0
            else:
                env=math.exp(-t*65)*min(1,t*1500)
                v=(math.sin(2*math.pi*1450*t)*.3+noise*.15)*env*.24
                pan=.15
            left.append(v*math.sqrt((1-pan)/2));right.append(v*math.sqrt((1+pan)/2))
        write_wave(PUBLIC/'sfx'/f'design-{name}.wav',left,right)

def prepare_audio():
    design_effects()
    probes=json.loads((WORK/'probes.json').read_text(encoding='utf8'))
    music=ROOT/probes[-1]['relativePath']
    duration=TOTAL/FPS
    # Start at a stable musical downbeat, preserve the supplied track's melodic bed.
    run(['ffmpeg','-v','error','-ss','19.71','-i',str(music),'-t',str(duration),'-af',
         f'highpass=f=35,afade=t=in:st=0:d=0.12,afade=t=out:st={duration-1.75}:d=1.75,loudnorm=I=-17.5:TP=-2.5:LRA=8',
         '-ar','48000','-ac','2','-c:a','pcm_s24le','-y',str(WORK/'music-bed.wav')],'music-bed.log')
    events=[]
    def add(kind,time,gain=1):events.append(dict(kind=kind,time=max(0,time),gain=gain))
    # Main transitions have air; key anchors get low-end weight, never every cut.
    for beat in [4,12,20,28,36,44,52,56,60,62,64,68,76]:
        add('air',frame(beat)/FPS-.21,.31 if beat in [60,62] else .48)
    for beat in [4,20,36,68,76]:add('impact',frame(beat)/FPS,.44 if beat!=76 else .62)
    for beat in [3,19,35,75]:add('riser',frame(beat)/FPS-1.20,.32)
    # Each title line and key label gets a precise quiet transient.
    for beat in [4.7,6.2,12.8,14.2,20.9,22.2,28.8,30.4,36.8,38.3,44.8,46.1,68.8,70.1,76.7,78.4]:
        add('click',frame(beat)/FPS,.21)
    for beat in [5.8,13.9,22.0,30.2,38.1,46.0,70.0]:add('text',frame(beat)/FPS,.28)
    kind_files={k:PUBLIC/'sfx'/f'design-{k}.wav' for k in ['air','riser','impact','text']}
    kind_files['click']=PUBLIC/'sfx/click_003.ogg'
    inputs=['ffmpeg','-v','error','-i',str(WORK/'music-bed.wav')]
    kinds=list(kind_files)
    for k in kinds:inputs+=['-i',str(kind_files[k])]
    filters=[];uses={k:[] for k in kinds}
    for n,e in enumerate(events):uses[e['kind']].append((n,e))
    for k,uses_k in uses.items():
        idx=kinds.index(k)+1
        labels=''.join(f'[{k}{n}]' for n,e in uses_k)
        filters.append(f'[{idx}:a]asplit={len(uses_k)}{labels}')
    outputs=['[0:a]']
    for n,e in enumerate(events):
        gain=e['gain'];delay=round(e['time']*1000)
        filters.append(f"[{e['kind']}{n}]volume={gain},adelay={delay}:all=1[e{n}]")
        outputs.append(f'[e{n}]')
    filters.append(''.join(outputs)+f'amix=inputs={len(outputs)}:duration=first:dropout_transition=0:normalize=0,alimiter=limit=0.87:level=false:latency=true,atrim=duration={duration}[mix]')
    graph=WORK/'sound-filter.txt';graph.write_text(';\n'.join(filters),encoding='utf8')
    run(inputs+['-filter_complex',';'.join(filters),'-map','[mix]','-ar','48000','-c:a','pcm_s24le','-y',str(WORK/'mix-premaster.wav')],'sound-mix.log')
    # Two-pass loudness mastering for a controlled web-delivery mix.
    measure=subprocess.run(['ffmpeg','-hide_banner','-i',str(WORK/'mix-premaster.wav'),'-af','loudnorm=I=-15:TP=-1.5:LRA=8:print_format=json','-f','null','-'],capture_output=True,text=True)
    (WORK/'loudness-analysis.log').write_text(measure.stderr,encoding='utf8')
    if measure.returncode:raise RuntimeError(measure.stderr[-2500:])
    stats,_=json.JSONDecoder().raw_decode(measure.stderr[measure.stderr.rfind('{'):])
    norm=f"loudnorm=I=-15:TP=-1.5:LRA=8:measured_I={stats['input_i']}:measured_TP={stats['input_tp']}:measured_LRA={stats['input_lra']}:measured_thresh={stats['input_thresh']}:offset={stats['target_offset']}:linear=true"
    run(['ffmpeg','-v','error','-i',str(WORK/'mix-premaster.wav'),'-af',norm,'-ar','48000','-ac','2','-c:a','pcm_s24le','-y',str(PUBLIC/'soundtrack.wav')],'sound-master.log')
    (PROJECT/'src/sound-events.json').write_text(json.dumps(dict(duration=duration,musicStart=19.71,events=events,normalization=stats),indent=2),encoding='utf8')
    print('AUDIO',len(events),'events',duration,'seconds',flush=True)

if __name__=='__main__':
    import sys
    mode=sys.argv[1] if len(sys.argv)>1 else 'all'
    if mode in ['all','video']:prepare_video()
    if mode in ['all','audio']:prepare_audio()
