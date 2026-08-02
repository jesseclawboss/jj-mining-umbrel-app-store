import base64, json, os, shutil, time, urllib.error, urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

COIN=os.environ.get("COIN","Litecoin"); HOST=os.environ.get("RPC_HOST",COIN.lower()); PORT=os.environ.get("RPC_PORT","9332")
CREDS=os.environ.get("RPC_CREDENTIALS_FILE","/run/jjmining/rpc.env"); DATA=os.environ.get("DATA_DIR","/data")
START=time.time()
def credentials():
    values={}
    with open(CREDS,encoding="utf-8") as f:
        for line in f:
            k,_,v=line.strip().partition("="); values[k]=v
    return values["RPC_USER"],values["RPC_PASSWORD"]
def rpc(method):
    user,pw=credentials(); payload=json.dumps({"jsonrpc":"1.0","id":"dashboard","method":method,"params":[]}).encode()
    auth=base64.b64encode(f"{user}:{pw}".encode()).decode()
    req=urllib.request.Request(f"http://{HOST}:{PORT}/",data=payload,headers={"Content-Type":"application/json","Authorization":"Basic "+auth})
    with urllib.request.urlopen(req,timeout=3) as response: result=json.load(response)
    if result.get("error"): raise RuntimeError(result["error"])
    return result["result"]
def status():
    try:
        chain=rpc("getblockchaininfo"); net=rpc("getnetworkinfo"); usage=shutil.disk_usage(DATA)
        progress=max(0,min(100,float(chain.get("verificationprogress",0))*100)); peers=net.get("connections",0)
        state="syncing" if chain.get("initialblockdownload") or progress<99.99 else ("degraded" if peers==0 else "healthy")
        return {"state":state,"rpc":True,"coin":COIN,"blocks":chain.get("blocks"),"headers":chain.get("headers"),"progress":round(progress,4),"peers":peers,"chain":chain.get("chain"),"version":net.get("subversion"),"disk_used":usage.used,"disk_total":usage.total,"message":"Node is synchronizing" if state=="syncing" else ("No peers connected" if state=="degraded" else "Node is ready")}
    except Exception as e:
        return {"state":"starting" if time.time()-START<600 else "offline","rpc":False,"coin":COIN,"message":"Waiting for node RPC","detail":str(e)[:180]}
class Handler(BaseHTTPRequestHandler):
    def send(self,code,ctype,body):
        body=body.encode(); self.send_response(code); self.send_header("Content-Type",ctype); self.send_header("Content-Length",str(len(body))); self.send_header("Cache-Control","no-store"); self.end_headers(); self.wfile.write(body)
    def do_GET(self):
        if self.path=="/health": return self.send(200,"text/plain","ok\n")
        if self.path=="/api/status": return self.send(200,"application/json",json.dumps(status()))
        if self.path=="/":
            with open("/app/index.html",encoding="utf-8") as f: return self.send(200,"text/html; charset=utf-8",f.read().replace("{{COIN}}",COIN))
        self.send(404,"text/plain","not found\n")
    def log_message(self,fmt,*args): print("dashboard:",fmt%args,flush=True)
ThreadingHTTPServer(("0.0.0.0",8080),Handler).serve_forever()
