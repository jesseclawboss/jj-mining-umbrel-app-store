# JJ Mining Umbrel Community App Store

A self-hosted Umbrel app store for Litecoin and Dogecoin nodes and experimental LTC/DOGE AuxPoW merged mining.

## Apps and architecture support

| App | Version | Architecture | Storage |
|---|---:|---|---:|
| JJ Litecoin Node | Litecoin Core 0.21.5.6 | amd64, arm64 | Allow at least 150 GB and growth headroom |
| JJ Dogecoin Node | Dogecoin Core 1.14.9 | amd64, arm64 | Allow at least 250 GB and growth headroom |
| JJ LTC/DOGE Solo Merged Mining | Isolated P2Pool engine commit `44a10f3` plus both nodes | **amd64 only** | Combined chain sizes plus at least 20 GB headroom |

Storage figures are planning estimates, not hard limits. Chain sizes and initial-sync times continually increase. Initial synchronization can take hours to days depending on CPU, disk, peers, and bandwidth. An SSD, 8 GB RAM, stable broadband, and substantially more free space than the current chain size are strongly recommended. Do not install the merged stack on arm64: its pinned PyPy 2 runtime is x86-64 only.

## Add to Umbrel

1. In Umbrel, open **App Store → three-dot menu → Community App Stores → Add**.
2. Enter `https://github.com/jesseclawboss/jj-mining-umbrel-app-store`.
3. Install an app from the JJ Mining store.

Recommended order is Litecoin Node, then Dogecoin Node, then the merged-mining app. The merged app is independently installable and runs its own nodes; the standalone nodes are useful for proving that the hardware and network can sync each chain first.

## Why the old dashboard returned ECONNRESET

The old Compose files mounted `${APP_DATA_DIR}/dashboard` over `/app`, but installation never copied `server.py` into that data directory. The dashboard container exited because `/app/server.py` did not exist. Umbrel's proxy then had no listening upstream and reset the browser connection. The new dashboard code is built into its image, starts before RPC is available, reports a starting/offline state, and has an independent HTTP health check.

## Security and persistence

- An idempotent installation service creates separate 256-bit RPC passwords under `${APP_DATA_DIR}/secrets`; no default credential is committed.
- RPC ports 9332 and 22555 are never published. The mining app publishes only Stratum/web port 9327. Its private sharechain port is not published; coin nodes relay valid blocks through their normal P2P connections.
- Blockchain, configuration, secrets, and P2Pool state live under `${APP_DATA_DIR}`. Rebuilds, routine updates, container recreation, and reboots do not delete them.
- Daemons receive `SIGTERM` and a two-minute grace period. Back up only while apps are stopped to obtain a consistent copy.
- The Umbrel app proxy protects dashboards with the Umbrel login. Stratum has no Umbrel authentication; restrict it to the trusted LAN with the host/router firewall.

## Solo merged-mining setup

The mining app pins [`frstrtr/p2pool-merged-v36`](https://github.com/frstrtr/p2pool-merged-v36) commit `44a10f30ea4fc8a2b60dfb47d5df7fc3b010ede7` as its Stratum and AuxPoW engine. It uses the upstream engine's documented `PERSIST=False` bootstrap/solo mode, removes all bootstrap addresses, disables incoming and outgoing sharechain connections, and does not publish the P2Pool peer port. It does not use Miningcore or participate in public PPLNS. Only locally connected ASICs contribute work; network-valid LTC and DOGE blocks pay the configured addresses directly.

1. Install and open **JJ LTC/DOGE Merged Mining**. Its dashboard stays available while both nodes start.
2. Wait until both nodes show fully synchronized.
3. Enter an LTC address and a legacy DOGE address. The dashboard calls each local node's `validateaddress`; invalid addresses are not saved and P2Pool does not start.
4. Configure the ASIC:
   - URL: `stratum+tcp://umbrel.local:9327`
   - Username: `LTC_ADDRESS,DOGE_ADDRESS.worker-name`
   - Password: `x`
5. Check accepted and stale hashrate in the dashboard. The public peer count must remain zero. Local shares are diagnostic proofs of work, not payments; only network-valid blocks produce payouts.

Payout addresses are stored with mode 0600. Saving new addresses takes effect after restarting the app. Use an LTC address you control and a legacy DOGE address you control. The application never manages either wallet's private keys.

## Updates, backups, and recovery

Before updating, read `releaseNotes` in the manifest and upstream Core/P2Pool release notes. Stop the app, copy the complete app data directory (including `data`, `config`, and `secrets`) to another disk, then update. Never restore only RPC configuration without its matching secrets. A node database can usually be rebuilt from the network; wallet/payout private keys are **not managed by these apps** and must be backed up in the wallet that owns them.

If chain data is corrupt, stop the app, preserve a backup, and use the relevant daemon's reindex option only after reviewing its logs. Never delete `${APP_DATA_DIR}/data` as an update step. Uninstall may remove the entire app data directory depending on Umbrel's confirmation flow; make a backup first.

## Troubleshooting on Umbrel

SSH to the Umbrel and locate the installed app directory first. On current installations it is commonly below `~/umbrel/app-data/<app-id>`; use Umbrel's actual data path if different.

```bash
APP_ID=jjmining-litecoin-node
APP_DIR="$HOME/umbrel/app-data/$APP_ID"
cd "$APP_DIR"

# ECONNRESET: verify proxy target and dashboard listener/logs
docker compose ps
docker compose logs --tail=200 app_proxy dashboard
docker compose exec dashboard wget -qO- http://127.0.0.1:8080/health

# Failed or restarting containers
docker compose ps --all
docker compose logs --tail=300
docker inspect "${APP_ID}_dashboard_1" --format '{{json .State.Health}}'

# Private RPC failures (credentials remain inside the container)
docker compose exec litecoin litecoin-cli -datadir=/data -conf=/config/litecoin.conf getblockchaininfo
# Dogecoin app equivalent:
docker compose exec dogecoin dogecoin-cli -datadir=/data -conf=/config/dogecoin.conf getblockchaininfo

# Permissions and storage
id
df -h "$APP_DIR"
find "$APP_DIR" -maxdepth 2 -printf '%M %u:%g %p\n' | head -100

# Architecture incompatibility
uname -m
docker image inspect "$(docker compose images -q p2pool)" --format '{{.Architecture}}'
```

For the merged stack use `APP_ID=jjmining-ltc-doge-p2pool`, then inspect `dashboard`, `litecoin`, `dogecoin`, `mm-adapter`, and `p2pool`. A missing node intentionally leaves the pool unavailable and produces a useful dashboard state rather than a reset. Report issues with sanitized logs; never post `secrets/*.env`, `*.conf`, or live payout private keys.

## Local validation and Compose testing

Prerequisites: Python 3.12, Docker with Compose v2, and enough disk for image builds.

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt
python scripts/validate.py
python scripts/test_dashboard.py
yamllint .

APP_DATA_DIR=/tmp/jj-litecoin docker compose -f jjmining-litecoin-node/docker-compose.yml -f tests/app-proxy.override.yml config --quiet
APP_DATA_DIR=/tmp/jj-litecoin docker compose -f jjmining-litecoin-node/docker-compose.yml -f tests/app-proxy.override.yml up --build -d
curl --fail http://localhost:2101/ || docker compose -f jjmining-litecoin-node/docker-compose.yml -f tests/app-proxy.override.yml logs
APP_DATA_DIR=/tmp/jj-litecoin docker compose -f jjmining-litecoin-node/docker-compose.yml -f tests/app-proxy.override.yml down
```

Umbrel injects `app_proxy`; the committed test override supplies a harmless local proxy image and publishes the dashboard on port 2101 for this smoke test. It is never used by Umbrel.

CI parses every manifest and Compose file, enforces folder/ID/proxy consistency, rejects default credentials and RPC publication, lints YAML, tests immediate dashboard startup without RPC, validates Compose resolution, and builds the custom images. Items requiring real Umbrel/ASIC hardware are limited to [TODO.md](TODO.md).

## Upstream sources

- [Umbrel official app repository and packaging guide](https://github.com/getumbrel/umbrel-apps)
- [Umbrel Community App Store template](https://github.com/getumbrel/umbrel-community-app-store)
- [Litecoin Core releases](https://github.com/litecoin-project/litecoin/releases)
- [Dogecoin Core releases](https://github.com/dogecoin/dogecoin/releases)
- [P2Pool V36 merged-mining implementation](https://github.com/frstrtr/p2pool-merged-v36)

Support and repository: <https://github.com/jesseclawboss/jj-mining-umbrel-app-store>
