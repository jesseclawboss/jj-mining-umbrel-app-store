#!/usr/bin/env python3
import http.client,importlib.util,json,os,pathlib,subprocess,sys,tempfile,time
ROOT=pathlib.Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as td:
 os.environ["DASHBOARD_STATS_FILE"]=td+"/pool-stats.json"
 spec=importlib.util.spec_from_file_location("pool_dashboard",ROOT/"jjmining-ltc-doge-p2pool/dashboard/app.py");pool_dashboard=importlib.util.module_from_spec(spec);spec.loader.exec_module(pool_dashboard)
 pool_dashboard.payout_address=lambda: "ltc-address"
 local={"miner_hash_rates":{"address.worker1":205_000_000,"address.worker2":215_000_000},"miner_dead_hash_rates":{"address.worker1":1_000_000,"address.worker2":2_000_000}}
 best={"all_time":{"difficulty":12},"daily":{"difficulty":9,"started":100},"session":{"difficulty":10,"started":200}}
 telemetry=pool_dashboard.pool_telemetry(local,best,[],now=300)
 assert telemetry["local_hashrate"]==420_000_000 and telemetry["dead_hashrate"]==3_000_000 and telemetry["worker_count"]==2
 assert telemetry["best_difficulty"]=={"all_time":12,"daily":9,"daily_since":100,"session":10,"session_started":200}
 first=pool_dashboard.pool_telemetry(local,best,[{"hash":"a","ts":250}],now=301);assert not first["block_event"]
 second=pool_dashboard.pool_telemetry(local,best,[{"hash":"b","ts":302}],now=302);assert second["block_event"]
 restarted=pool_dashboard.pool_telemetry(local,{"all_time":{"difficulty":3},"daily":{},"session":{}},[],now=303);assert restarted["best_difficulty"]["all_time"]==12
 assert json.loads(pathlib.Path(td,"pool-stats.json").read_text())["all_time_best"]==12
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
  print("Dashboard aggregation, telemetry persistence, block-event, and offline-state tests passed")
 finally:p.terminate();p.wait(timeout=5)
