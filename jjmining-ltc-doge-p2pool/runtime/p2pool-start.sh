#!/bin/sh
set -eu
while [ ! -s /config/payout.env ]; do echo 'Waiting for payout addresses to be saved in dashboard'; sleep 10; done
. /config/payout.env
. /secrets/litecoin.env
LTC_USER="$RPC_USER"; LTC_PASSWORD="$RPC_PASSWORD"
. /secrets/dogecoin.env
exec pypy /app/run_p2pool.py --net litecoin --coind-address jjmining-ltc-doge-p2pool_litecoin_1 --coind-rpc-port 9332 --coind-p2p-port 9333 --merged-coind-address jjmining-ltc-doge-p2pool_mm-adapter_1 --merged-coind-rpc-port 44556 --merged-coind-p2p-port 22556 --merged-coind-p2p-address jjmining-ltc-doge-p2pool_dogecoin_1 --merged-coind-rpc-user "$RPC_USER" --merged-coind-rpc-password "$RPC_PASSWORD" --merged-operator-address "$DOGE_PAYOUT_ADDRESS" --address "$LTC_PAYOUT_ADDRESS" --give-author 0 -f 0 --disable-upnp --max-conns 0 --outgoing-conns 0 --disable-advertise --redistribute fee "$LTC_USER" "$LTC_PASSWORD"
