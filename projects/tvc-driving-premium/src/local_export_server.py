"""Loopback-only Remotion frame receiver. No user files sent to third parties."""
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
import json,re,time
P=Path(__file__).resolve().parents[1]
UI=P/'working/v002-ui';FRAMES=P/'working/v002/remotion-frames';PREVIEW=P/'previews/v002'
FRAMES.mkdir(parents=True,exist_ok=True);PREVIEW.mkdir(exist_ok=True)
STATE=P/'working/v002/export-status.json'
def status(data):STATE.write_text(json.dumps(data,indent=2),encoding='utf8')
class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(UI),**kwargs)
 def log_message(self,*args):pass
 def do_GET(self):
  if self.path=='/status':
   data=STATE.read_bytes() if STATE.exists() else b'{}'
   self.send_response(200);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(data);return
  super().do_GET()
 def translate_path(self,path):
  if path.startswith('/public/'):
   p=(P/'public'/path[len('/public/'):].split('?',1)[0]).resolve()
   if p.is_relative_to(P/'public'):return str(p)
   return str(UI/'not-found')
  return super().translate_path(path)
 def do_POST(self):
  length=int(self.headers.get('Content-Length','0'))
  if length>15000000:self.send_error(413);return
  data=self.rfile.read(length)
  match=re.fullmatch(r'/(frame|preview)/(\d{4})',self.path)
  if match:
   kind,index=match.groups();frame=int(index)
   if frame>=975 or not data.startswith(b'\xff\xd8'):self.send_error(400);return
   folder=FRAMES if kind=='frame' else PREVIEW
   (folder/f'f{index}.jpg').write_bytes(data)
   status({'kind':kind,'lastFrame':frame,'frameCount':len(list(folder.glob('f*.jpg'))),'updated':time.time()})
  elif self.path in ['/complete','/error']:
   status({'event':self.path,'data':data.decode('utf8',errors='replace'),'updated':time.time()})
  else:self.send_error(404);return
  self.send_response(200);self.end_headers();self.wfile.write(b'ok')
if __name__=='__main__':
 status({'event':'ready','port':8765});print('Piu Remotion local export: http://127.0.0.1:8765',flush=True)
 ThreadingHTTPServer(('127.0.0.1',8765),Handler).serve_forever()
