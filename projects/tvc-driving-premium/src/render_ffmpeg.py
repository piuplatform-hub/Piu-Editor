"""Native deterministic renderer fallback: typography, gradient grade, beat edit and master audio."""
from pathlib import Path
import json,subprocess,sys

P=Path(__file__).resolve().parents[1]
ROOT=P.parents[1]
T=json.loads((P/'src/timeline.json').read_text(encoding='utf8'))
FPS=24;D=T['totalFrames']/FPS
OUT=ROOT/'output/tvc-driving-premium'
FONT='public/fonts/segoeui.ttf'
BOLD='public/fonts/segoeuib.ttf'
TEXT=P/'working/text';TEXT.mkdir(exist_ok=True)
count=0

def beat(n):return round(n*60/124*FPS)/FPS
def cmd(args,log):
 r=subprocess.run(args,cwd=P,capture_output=True,text=True,encoding='utf8',errors='replace')
 (P/'working'/log).write_text(r.stderr+r.stdout,encoding='utf8')
 if r.returncode:raise RuntimeError(r.stderr[-4000:])

def text(text,x,y,size=92,start=0,end=D,enter=None,color='0xf4f6f8',bold=False,slide=True):
 global count
 count+=1;f=TEXT/f't{count:03d}.txt';f.write_text(text,encoding='utf8')
 enter=start if enter is None else enter
 progress=f'min(1,max(0,(t-{enter:.6f})/0.48))'
 alpha=f'min(1,max(0,(t-{enter:.6f})/0.20))*min(1,max(0,({end:.6f}-t)/0.22))'
 pos=f'{y}+58*pow(1-{progress},3)' if slide else str(y)
 return f"drawtext=fontfile='{BOLD if bold else FONT}':textfile='working/text/{f.name}':fontsize={size}:fontcolor={color}:x='{x}':y='{pos}':alpha='{alpha}':enable='between(t,{start:.6f},{end:.6f})':shadowcolor=0x03101e@0.18:shadowx=0:shadowy=2"

TITLES=[
 (4,12,'KHỞI ĐẦU MỘT HÀNH TRÌNH',['VỮNG TAY LÁI.','MỞ LỐI TƯƠNG LAI.'],'Từ nền tảng hôm nay, đến tự tin ngày mai.',91,True),
 (12,20,'SẴN SÀNG CHO HÀNH TRÌNH MỚI',['MỖI KHỞI ĐẦU.','MỘT BƯỚC TIẾN.'],'Đào tạo lái xe tại Yên Thành',91,False),
 (20,28,'NỀN TẢNG',['HIỂU ĐÚNG.','VỮNG VÀNG HƠN.'],'Kiến thức • Tư duy • Kỹ năng',92,False),
 (28,36,'TRẢI NGHIỆM MÔ PHỎNG',['CÔNG NGHỆ.','GẦN HƠN THỰC TẾ.'],'Tiếp cận tình huống. Rèn luyện phản xạ.',86,True),
 (36,44,'THỰC HÀNH CABIN',['LÀM CHỦ','TỪNG THAO TÁC.'],'Tập trung trong từng chuyển động.',96,False),
 (44,52,'TỪ MÔ PHỎNG ĐẾN THỰC TẾ',['RÈN KỸ NĂNG.','VỮNG HÀNH TRÌNH.'],'Trải nghiệm trên sân tập lái.',89,True),
 (68,76,'TIẾN VỀ PHÍA TRƯỚC',['TỰ TIN','TRÊN MỖI HÀNH TRÌNH.'],'Cùng Trung tâm Yên Thành',81,False),
]

def render(preview=False):
 # Generate a transparent navy graduated overlay once; not a modification of source images.
 gradient=P/'working/navy-gradient.png'
 if not gradient.exists():
  cmd(['ffmpeg','-v','error','-f','lavfi','-i',"nullsrc=s=1920x1080,format=rgba,geq=r=3:g=16:b=30:a='145*pow(1-X/W,1.6)+55*pow(Y/H,4)'",'-frames:v','1','-y',str(gradient)],'gradient.log')
 enables='+'.join(f'between(t,{beat(a):.6f},{beat(b):.6f})' for a,b,*_ in TITLES)
 prefix=''
 if preview:prefix="select='eq(n,20)+eq(n,84)+eq(n,175)+eq(n,272)+eq(n,365)+eq(n,458)+eq(n,550)+eq(n,680)+eq(n,820)+eq(n,940)',"
 graph=f"[0:v]{prefix}setsar=1[base];[base][1:v]overlay=0:0:enable='{enables}':eof_action=repeat[graded];[graded]"
 effects=[]
 for a,b,kicker,lines,detail,size,accent in TITLES:
  start,end=beat(a),beat(b)
  effects.append(f"drawbox=x=114:y=657:w=64:h=3:color=0xf05b47:t=fill:enable='between(t,{start+.24:.6f},{end-.2:.6f})'")
  effects.append(text('\u2009'.join(kicker),200,642,19,start,end,enter=start+.18,slide=False))
  for i,line in enumerate(lines):effects.append(text(line,110,685+i*111,size,start,end,enter=start+beat(.7 if i==0 else 2.2),bold=True,color='0xffb09b' if accent and i==1 else '0xf4f6f8'))
  effects.append(text(detail,114,925,24,start,end,enter=start+beat(3),slide=False))
 effects.append(text('HÀNH TRÌNH BẮT ĐẦU TỪ BẠN.',114,890,27,0,beat(4),enter=.18))
 for a,b,line in [(52,60,'CHUYỂN ĐỘNG.'),(60,64,'TẬP TRUNG.'),(64,68,'TIẾN LÊN.')]:
  effects.append(text(line,114,863,62,beat(a),beat(b),bold=True))
 endstart=beat(76)
 effects.append(f"drawbox=x=0:y=0:w=iw:h=ih:color=0x06192b@0.93:t=fill:enable='gte(t,{endstart:.6f})'")
 effects.append(text('TRUNG TÂM ĐÀO TẠO VÀ SÁT HẠCH LÁI XE','(w-tw)/2',361,29,endstart,D,enter=endstart+.26))
 effects.append(text('YÊN THÀNH','(w-tw)/2',430,154,endstart,D,enter=endstart+beat(.7),bold=True))
 effects.append(f"drawbox=x=904:y=638:w=112:h=5:color=0xf05b47:t=fill:enable='between(t,{endstart+.7:.6f},{D-.25:.6f})'")
 effects.append(text('BẮT ĐẦU HÀNH TRÌNH CỦA BẠN.','(w-tw)/2',687,32,endstart,D,enter=endstart+beat(2.4),slide=False))
 effects.extend(['drawbox=x=0:y=0:w=iw:h=82:color=0x06192b:t=fill','drawbox=x=0:y=1000:w=iw:h=80:color=0x06192b:t=fill'])
 effects.append(f"drawbox=x=112:y=29:w=5:h=23:color=0xf05b47:t=fill:enable='lt(t,{endstart:.6f})'")
 effects.append(text('YÊN THÀNH',136,23,29,0,endstart,slide=False,bold=True))
 effects.append(text('ĐÀO TẠO & SÁT HẠCH LÁI XE','w-tw-112',30,19,0,endstart,slide=False,color='0xadbfce'))
 for a,b,chapter in [(0,20,'KHỞI ĐẦU'),(20,44,'NỀN TẢNG & CÔNG NGHỆ'),(44,68,'KỸ NĂNG & TRẢI NGHIỆM'),(68,76,'HÀNH TRÌNH')]:
  effects.append(text(chapter,114,1027,17,beat(a),beat(b),slide=False,color='0xa7b7c5'))
 effects.append(f'fade=t=in:st=0:d=0.25,fade=t=out:st={D-.5:.6f}:d=0.5,format=yuv420p')
 graph+=','.join(effects)+'[v]'
 graph_file=P/'working'/('picture-preview-filter.txt' if preview else 'picture-filter.txt')
 graph_file.write_text(graph,encoding='utf8')
 args=['ffmpeg','-hide_banner','-loglevel','warning','-filter_complex_threads','2','-i',str(PUBLIC_VIDEO),'-loop','1','-framerate','24','-i',str(gradient)]
 if not preview:args+=['-i',str(P/'public/soundtrack.wav')]
 args+=['-filter_complex',graph,'-map','[v]']
 if preview:
  (P/'previews/designed').mkdir(exist_ok=True)
  args+=['-an','-fps_mode','vfr','-frames:v','10','-q:v','2','-y',str(P/'previews/designed/frame-%02d.jpg')]
 else:
  args+=['-map','2:a:0','-t',str(D),'-r','24','-c:v','libx264','-preset','slow','-crf','17','-threads','4','-c:a','aac','-b:a','320k','-ar','48000','-movflags','+faststart','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-y',str(OUT/'yen-thanh-tvc-v001.mp4')]
 cmd(args,'picture-preview.log' if preview else 'picture-render.log')
 print('RENDERED', 'preview frames' if preview else 'final TVC',flush=True)

PUBLIC_VIDEO=P/'public/video/edit-base.mp4'
if __name__=='__main__':render('--preview' in sys.argv)
