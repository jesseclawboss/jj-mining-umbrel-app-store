#!/bin/sh
set -eu
while [ ! -s /config/payout.env ]; do echo 'Waiting for payout addresses to be saved in dashboard'; sleep 10; done
. /config/payout.env
. /secrets/litecoin.env
LTC_USER="$RPC_USER"; LTC_PASSWORD="$RPC_PASSWORD"
. /secrets/dogecoin.env
exec pypy /app/run_p2pool.py --net litecoin --coind-address litecoin --coind-rpc-port 9332 --coind-p2p-port 9333 --merged-coind-address mm-adapter --merged-coind-rpc-port 44556 --merged-coind-p2p-port 22556 --merged-coind-p2p-address dogecoin --merged-coind-rpc-user "$RPC_USER" --merged-coind-rpc-password "$RPC_PASSWORD" --merged-operator-address "$DOGE_PAYOUT_ADDRESS" --address "$LTC_PAYOUT_ADDRESS" --give-author 2 -f 0 --disable-upnp --max-conns 20 --redistribute pplns "$LTC_USER" "$LTC_PASSWORD"
