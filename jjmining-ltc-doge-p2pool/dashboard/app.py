import base64,json,os,re,urllib.request
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
CFG="/config/payout.env"
def creds(chain):
 d={}
 with open(f"/secrets/{chain}.env") as f:
  for line in f:k,_,v=line.strip().partition("=");d[k]=v
 return d
def rpc(chain,method,params=[]):
 c=creds(chain);port=9332 if chain=="litecoin" else 22555
 data=json.dumps({"jsonrpc":"1.0","id":"ui","method":method,"params":params}).encode();auth=base64.b64encode(f"{c['RPC_USER']}:{c['RPC_PASSWORD']}".encode()).decode()
 req=urllib.request.Request(f"http://{chain}:{port}/",data=data,headers={"Authorization":"Basic "+auth,"Content-Type":"application/json"})
 return json.load(urllib.request.urlopen(req,timeout=3))["result"]
def state():
 out={"configured":os.path.exists(CFG)}
 for chain in ("litecoin","dogecoin"):
  try:
   b=rpc(chain,"getblockchaininfo");n=rpc(chain,"getnetworkinfo");out[chain]={"available":True,"blocks":b["blocks"],"headers":b["headers"],"progress":round(b["verificationprogress"]*100,3),"peers":n["connections"],"synced":not b.get("initialblockdownload",True)}
  except Exception as e:out[chain]={"available":False,"error":str(e)[:120]}
 try:out["pool"]=json.load(urllib.request.urlopen("http://p2pool:9327/local_stats",timeout=2))
 except Exception:out["pool"]=None
 out["state"]="setup" if not out["configured"] else ("offline" if not out["litecoin"]["available"] or not out["dogecoin"]["available"] else ("syncing" if not out["litecoin"].get("synced") or not out["dogecoin"].get("synced") else ("healthy" if out["pool"] else "starting")))
 return out
class H(BaseHTTPRequestHandler):
 def send(self,c,t,b):b=b.encode();self.send_response(c);self.send_header("Content-Type",t);self.send_header("Content-Length",str(len(b)));self.send_header("Cache-Control","no-store");self.end_headers();self.wfile.write(b)
 def do_GET(self):
  if self.path=="/health":return self.send(200,"text/plain","ok")
  if self.path=="/api/status":return self.send(200,"application/json",json.dumps(state()))
  if self.path=="/":return self.send(200,"text/html; charset=utf-8",open('/app/index.html').read())
  self.send(404,"text/plain","not found")
 def do_POST(self):
  if self.path!="/api/config":return self.send(404,"text/plain","not found")
  try:
   n=int(self.headers.get("Content-Length","0"));d=json.loads(self.rfile.read(n));ltc=d.get("ltc","").strip();doge=d.get("doge","").strip()
   if not rpc("litecoin","validateaddress",[ltc]).get("isvalid"):raise ValueError("Invalid Litecoin address")
   if not rpc("dogecoin","validateaddress",[doge]).get("isvalid"):raise ValueError("Invalid Dogecoin address")
   if not re.fullmatch(r"[A-Za-z0-9]{20,100}",ltc+doge):raise ValueError("Unsupported address characters")
   tmp=CFG+".tmp";open(tmp,"w").write(f"LTC_PAYOUT_ADDRESS={ltc}\nDOGE_PAYOUT_ADDRESS={doge}\n");os.chmod(tmp,0o600);os.replace(tmp,CFG);return self.send(200,"application/json",'{"ok":true}')
  except Exception as e:return self.send(400,"application/json",json.dumps({"error":str(e)}))
 def log_message(self,*a):pass
ThreadingHTTPServer(("0.0.0.0",8080),H).serve_forever()
