#!/usr/bin/env python3
import pathlib,re,sys,yaml
ROOT=pathlib.Path(__file__).resolve().parents[1]; errors=[]
apps=[]
for manifest in sorted(ROOT.glob("jjmining-*/umbrel-app.yml")):
 data=yaml.safe_load(manifest.read_text()); app=manifest.parent; apps.append(app)
 required=("manifestVersion","id","name","tagline","category","version","port","description","developer","repo","support","gallery","releaseNotes")
 for key in required:
  if key not in data:errors.append(f"{manifest}: missing {key}")
 if data.get("id")!=app.name:errors.append(f"{manifest}: id must match folder")
 if not str(data.get("id","")).startswith("jjmining-"):errors.append(f"{manifest}: id must use jjmining prefix")
 compose=app/"docker-compose.yml"; c=yaml.safe_load(compose.read_text()); services=c.get("services",{})
 if "app_proxy" not in services:errors.append(f"{compose}: missing app_proxy")
 else:
  host=services["app_proxy"].get("environment",{}).get("APP_HOST","")
  expected=f"{data['id']}_dashboard_1"
  if host!=expected:errors.append(f"{compose}: APP_HOST must be {expected}")
 text=compose.read_text()
 for pattern,label in [(r":latest\b","latest image"),(r"CHANGE_ME|change-me","default credential"),(r"rpcpassword:\s*[^$\n]","literal RPC password")]:
  if re.search(pattern,text,re.I):errors.append(f"{compose}: contains {label}")
 if re.search(r"ports:\s*\n(?:.*\n){0,3}.*(?:9332|22555):",text):errors.append(f"{compose}: publishes an RPC port")
store=yaml.safe_load((ROOT/"umbrel-app-store.yml").read_text())
if store.get("id")!="jjmining":errors.append("umbrel-app-store.yml: id must be jjmining")
print(f"Validated {len(apps)} Umbrel apps")
if errors:
 print("\n".join("ERROR: "+e for e in errors),file=sys.stderr);sys.exit(1)
