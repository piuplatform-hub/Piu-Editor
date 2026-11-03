"""V002 media prep: frame-accurate Remotion plates and a new punchier sound palette."""
from pathlib import Path
import array,json,math,random,subprocess,sys,wave
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1]
W=P/'working/v002';W.mkdir(parents=True,exist_ok=True)
S=P/'public/sfx-v002';S.mkdir(exist_ok=True)
FPS=24;N=975;D=N/FPS
def beat(b):return round(b*60/124*FPS)/FPS
def run(args,log):
 r=subprocess.run(args,capture_output=True,text=True,encoding='utf8',errors='replace')
 (W/log).write_text(r.stdout+r.stderr,encoding='utf8')
 if r.returncode:raise RuntimeError(r.stderr[-2500:])
def plates():
 folder=P/'public/frames-v002';folder.mkdir(exist_ok=True)
 run(['ffmpeg','-v','error','-i',str(P/'public/video/edit-base.mp4'),'-an','-q:v','2','-start_number','0','-y',str(folder/'f%04d.jpg')],'plates.log')
 assert len(list(folder.glob('f*.jpg')))==N
 print('Prepared',N,'frame-accurate plates',flush=True)
def sound():
 sr=48000;rng=random.Random(260203)
 for name,duration in [('slam',.46),('whip',.7),('impact',1.9),('riser',1.9),('tick',.16)]:
  raw=[];phase=0;low=0
  for i in range(round(sr*duration)):
   t=i/sr;x=t/duration;noise=rng.uniform(-1,1);low+=(.05+.22*x)*(noise-low)
   attack=min(1,t*900)
   if name=='impact':
    phase+=2*math.pi*(37+100*math.exp(-t*24))/sr
    v=(.82*math.sin(phase)*math.exp(-t*3.8)+.35*(noise-low)*math.exp(-t*50)) * attack
   elif name=='slam':
    phase+=2*math.pi*(95+220*math.exp(-t*32))/sr
    v=(math.sin(phase)*.6*math.exp(-t*18)+(noise-low)*.5*math.exp(-t*70))*attack
   elif name=='whip':
    env=math.sin(math.pi*x)**3.4
    phase+=2*math.pi*(150+2300*x*x)/sr
    v=((noise-low)*.38+low*.35+math.sin(phase)*.1)*env
   elif name=='riser':
    phase+=2*math.pi*(70+1200*x*x*x)/sr
    v=(low*.45+(noise-low)*.18+math.sin(phase)*.09)*x**2.3*min(1,(1-x)*50)
   else:
    phase+=2*math.pi*(1300-650*x)/sr
    v=(math.sin(phase)*.35+(noise-low)*.5)*math.exp(-t*60)*attack
   raw.append(v)
  pcm=array.array('h')
  for i,v in enumerate(raw):
   delay1=raw[i-430] if i>=430 else 0;delay2=raw[i-790] if i>=790 else 0
   pan=(i/len(raw)*1.4-.7) if name=='whip' else 0
   l=(v+.13*delay1)*math.sqrt((1-pan)/2);r=(v+.13*delay2)*math.sqrt((1+pan)/2)
   pcm.extend([int(max(-.98,min(.98,l))*32767),int(max(-.98,min(.98,r))*32767)])
  with wave.open(str(S/f'{name}.wav'),'wb') as f:
   f.setnchannels(2);f.setsampwidth(2);f.setframerate(sr);f.writeframes(pcm.tobytes())
 music=next((ROOT/'Source/music').glob('*.mp3'))
 run(['ffmpeg','-v','error','-ss','38.07','-i',str(music),'-t',str(D),'-af',
      f'highpass=f=34,equalizer=f=90:t=q:w=0.8:g=1.4,equalizer=f=280:t=q:w=1:g=-1,afade=t=in:d=0.1,afade=t=out:st={D-1.4}:d=1.4,loudnorm=I=-17:TP=-2.5:LRA=8',
      '-ar','48000','-ac','2','-c:a','pcm_s24le','-y',str(W/'music.wav')],'music.log')
 events=[]
 def cue(kind,b,gain,offset=0):events.append(dict(kind=kind,time=max(0,beat(b)+offset),gain=gain))
 for b in [0,4,12,20,28,36,44,52,56,60,64,68,76]:cue('impact',b,.67 if b in [4,52,76] else .43)
 for b in [4,12,20,28,36,44,52,56,60,62,64,68,76]:cue('whip',b,.75,-.22)
 for b in [4,20,36,52,68,76]:cue('riser',b,.65,-1.5)
 for b in [4.5,5.6,6.7,12.5,13.6,20.5,21.8,28.5,29.5,30.5,36.5,37.5,38.5,44.5,45.7,52.3,56.3,60.3,64.3,68.5,69.5,70.5,76.6,78]:cue('slam',b,.45)
 for b in [6.9,14,22,30.7,38.7,46.5,70.7,78.5]:cue('tick',b,.36)
 kinds=['impact','whip','riser','slam','tick'];args=['ffmpeg','-v','error','-i',str(W/'music.wav')]
 for k in kinds:args+=['-i',str(S/f'{k}.wav')]
 graph=[];labels=['[0:a]']
 for k in kinds:
  items=[(i,e) for i,e in enumerate(events) if e['kind']==k]
  graph.append(f'[{1+kinds.index(k)}:a]asplit={len(items)}'+''.join(f'[{k}{i}]' for i,e in items))
 for i,e in enumerate(events):
  graph.append(f"[{e['kind']}{i}]volume={e['gain']},adelay={round(e['time']*1000)}:all=1[c{i}]");labels.append(f'[c{i}]')
 graph.append(''.join(labels)+f'amix=inputs={len(labels)}:normalize=0:duration=first,alimiter=limit=0.86:level=false:latency=true,atrim=duration={D}[out]')
 run(args+['-filter_complex',';'.join(graph),'-map','[out]','-c:a','pcm_s24le','-y',str(W/'premaster.wav')],'mix.log')
 m=subprocess.run(['ffmpeg','-hide_banner','-i',str(W/'premaster.wav'),'-af','loudnorm=I=-14.5:TP=-1.5:LRA=8:print_format=json','-f','null','-'],capture_output=True,text=True)
 stats,_=json.JSONDecoder().raw_decode(m.stderr[m.stderr.rfind('{'):])
 norm=f"loudnorm=I=-14.5:TP=-1.5:LRA=8:measured_I={stats['input_i']}:measured_TP={stats['input_tp']}:measured_LRA={stats['input_lra']}:measured_thresh={stats['input_thresh']}:offset={stats['target_offset']}:linear=true"
 run(['ffmpeg','-v','error','-i',str(W/'premaster.wav'),'-af',norm,'-ar','48000','-ac','2','-t',str(D),'-c:a','pcm_s24le','-y',str(P/'public/soundtrack-v002.wav')],'master.log')
 (P/'src/sound-v002.json').write_text(json.dumps({'musicStart':38.07,'events':events,'normalization':stats},indent=2),encoding='utf8')
 print('New sound palette:',len(events),'cues',flush=True)
if __name__=='__main__':
 mode=sys.argv[1] if len(sys.argv)>1 else 'all'
 if mode in ['all','plates']:plates()
 if mode in ['all','sound']:sound()
