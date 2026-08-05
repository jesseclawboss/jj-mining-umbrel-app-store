import base64,json,os,re,time,urllib.request
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
CFG="/config/payout.env"
def creds(chain):
 d={}
 with open(f"/secrets/{chain}.env") as f:
  for line in f:k,_,v=line.strip().partition("=");d[k]=v
 return d
def rpc(chain,method,params=[]):
 c=creds(chain);port=9332 if chain=="litecoin" else 22555
 host=os.environ.get(f"{chain.upper()}_RPC_HOST",chain)
 data=json.dumps({"jsonrpc":"1.0","id":"ui","method":method,"params":params}).encode();auth=base64.b64encode(f"{c['RPC_USER']}:{c['RPC_PASSWORD']}".encode()).decode()
 req=urllib.request.Request(f"http://{host}:{port}/",data=data,headers={"Authorization":"Basic "+auth,"Content-Type":"application/json"})
 return json.load(urllib.request.urlopen(req,timeout=3))["result"]
def pool_json(path):
 host=os.environ.get("P2POOL_HOST","p2pool")
 return json.load(urllib.request.urlopen(f"http://{host}:9327/{path}",timeout=3))
def payout_address():
 if not os.path.exists(CFG):return None
 for line in open(CFG):
  key,_,value=line.strip().partition("=")
  if key=="LTC_PAYOUT_ADDRESS":return value
 return None
def state():
 out={"configured":os.path.exists(CFG)}
 for chain in ("litecoin","dogecoin"):
  try:
   b=rpc(chain,"getblockchaininfo");n=rpc(chain,"getnetworkinfo");out[chain]={"available":True,"blocks":b["blocks"],"headers":b["headers"],"progress":round(b["verificationprogress"]*100,3),"peers":n["connections"],"synced":not b.get("initialblockdownload",True)}
  except Exception as e:out[chain]={"available":False,"error":str(e)[:120]}
 try:
  local=pool_json("local_stats");address=payout_address()
  rates=local.get("miner_hash_rates",{});local_rate=sum(rates.values())
  dead_rate=sum(local.get("miner_dead_hash_rates",{}).values())
  out["pool"]={"mode":"private-solo","local_hashrate":local_rate,"dead_hashrate":dead_rate,"peers":local.get("peers",{}),"shares":local.get("shares",{}),"uptime":local.get("uptime"),"version":local.get("version"),"protocol_version":local.get("protocol_version"),"warnings":local.get("warnings",[]),"payout_address":address,"attempts_to_block":local.get("attempts_to_block"),"attempts_to_merged_block":local.get("attempts_to_merged_block")}
 except Exception as e:out["pool"]={"available":False,"error":str(e)[:120]}
 out["state"]="setup" if not out["configured"] else ("offline" if not out["litecoin"]["available"] or not out["dogecoin"]["available"] else ("syncing" if not out["litecoin"].get("synced") or not out["dogecoin"].get("synced") else ("healthy" if out["pool"] and out["pool"].get("available",True) else "starting")))
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
