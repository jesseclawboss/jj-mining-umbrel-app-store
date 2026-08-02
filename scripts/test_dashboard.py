#!/usr/bin/env python3
import http.client,os,pathlib,subprocess,sys,tempfile,time
ROOT=pathlib.Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as td:
 env=os.environ|{"COIN":"Litecoin","RPC_HOST":"127.0.0.1","RPC_PORT":"1","RPC_CREDENTIALS_FILE":td+"/rpc.env","DATA_DIR":td}
 pathlib.Path(td,"rpc.env").write_text("RPC_USER=test\nRPC_PASSWORD=test\n")
 p=subprocess.Popen([sys.executable,str(ROOT/"common/node-dashboard/app.py")],env=env,cwd=ROOT/"common/node-dashboard",stdout=subprocess.DEVNULL)
 try:
  for _ in range(30):
   try:
    c=http.client.HTTPConnection("127.0.0.1",8080,timeout=1);c.request("GET","/health");assert c.getresponse().status==200;break
   except OSError:time.sleep(.1)
  else:raise AssertionError("dashboard did not listen promptly")
  c=http.client.HTTPConnection("127.0.0.1",8080,timeout=2);c.request("GET","/api/status");r=c.getresponse();body=r.read().decode();assert r.status==200 and '"rpc": false' in body and '"state": "starting"' in body
  print("Dashboard startup/offline-state test passed")
 finally:p.terminate();p.wait(timeout=5)
