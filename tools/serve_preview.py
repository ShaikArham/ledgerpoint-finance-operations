from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
import os,re
from pathlib import Path
os.chdir(Path(__file__).resolve().parents[1])
class Handler(SimpleHTTPRequestHandler):
 def send_head(self):
  path=self.translate_path(self.path)
  if os.path.isfile(path) and self.headers.get('Range'):
   f=open(path,'rb');size=os.fstat(f.fileno()).st_size;m=re.match(r'bytes=(\d+)-(\d*)',self.headers['Range'])
   if m:
    start=int(m[1]);
    if start>=size:
     f.close();self.send_error(416);return None
    end=min(int(m[2]) if m[2] else size-1,size-1);self.send_response(206);self.send_header('Content-Type',self.guess_type(path));self.send_header('Accept-Ranges','bytes');self.send_header('Content-Range',f'bytes {start}-{end}/{size}');self.send_header('Content-Length',str(end-start+1));self.end_headers();f.seek(start);self.remaining=end-start+1;return f
   f.close()
  return super().send_head()
 def copyfile(self,source,outputfile):
  if hasattr(self,'remaining'):
   while self.remaining:
    data=source.read(min(self.remaining,65536))
    if not data:break
    outputfile.write(data);self.remaining-=len(data)
  else:super().copyfile(source,outputfile)
ThreadingHTTPServer(('127.0.0.1',8001),Handler).serve_forever()
