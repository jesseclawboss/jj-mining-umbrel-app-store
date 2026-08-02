from http.server import BaseHTTPRequestHandler,HTTPServer
import json,urllib.request,base64,os
HOST=os.getenv("RPC_HOST","dogecoin"); PORT=os.getenv("RPC_PORT","22555")
USER=os.getenv("RPC_USER","jjrpc"); PW=os.getenv("RPC_PASSWORD","jj-dogecoin-change-me")
def rpc(method):
 d=json.dumps({"jsonrpc":"1.0","id":"jj","method":method,"params":[]}).encode(); r=urllib.request.Request(f"http://{HOST}:{PORT}/",data=d,headers={"Content-Type":"application/json","Authorization":"Basic "+base64.b64encode(f"{USER}:{PW}".encode()).decode()}); return json.loads(urllib.request.urlopen(r,timeout=4).read())["result"]
class H(BaseHTTPRequestHandler):
 def do_GET(self):
  try:
   chain=rpc("getblockchaininfo"); net=rpc("getnetworkinfo"); body=f"<h1>JJ Dogecoin Node</h1><p>Status: <b>Running</b></p><p>Blocks: {chain.get('blocks')}</p><p>Headers: {chain.get('headers')}</p><p>Sync: {chain.get('verificationprogress',0)*100:.2f}%</p><p>Peers: {net.get('connections')}</p><p>Version: {net.get('subversion')}</p>"
  except Exception as e: body=f"<h1>JJ Dogecoin Node</h1><p>Node is starting or syncing.</p><pre>{e}</pre>"
  html=f"<html><style>body{background:#111;color:#eee;font:18px system-ui;padding:40px;max-width:760px;margin:auto}b{color:#7ee787}</style><body>{body}<p>RPC is private inside the app network.</p></body></html>".encode(); self.send_response(200); self.send_header('Content-Type','text/html'); self.end_headers(); self.wfile.write(html)
HTTPServer(('0.0.0.0',8080),H).serve_forever()
