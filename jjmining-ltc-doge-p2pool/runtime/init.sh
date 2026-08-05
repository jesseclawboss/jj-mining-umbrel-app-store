#!/bin/sh
set -eu
umask 077
mkdir -p /secrets /config /data/litecoin /data/dogecoin /data/p2pool /data/solo
make_creds(){ file="$1"; [ -s "$file" ] && return; printf 'RPC_USER=jjrpc_%s\nRPC_PASSWORD=%s\n' "$(od -An -N8 -tx1 /dev/urandom|tr -d ' \n')" "$(od -An -N32 -tx1 /dev/urandom|tr -d ' \n')" > "$file"; }
make_creds /secrets/litecoin.env; make_creds /secrets/dogecoin.env
. /secrets/litecoin.env
cat > /config/litecoin.conf <<EOF
server=1
daemon=0
printtoconsole=1
txindex=1
rpcbind=0.0.0.0
rpcallowip=172.16.0.0/12
rpcallowip=10.0.0.0/8
rpcuser=$RPC_USER
rpcpassword=$RPC_PASSWORD
EOF
. /secrets/dogecoin.env
cat > /config/dogecoin.conf <<EOF
server=1
daemon=0
printtoconsole=1
txindex=1
rpcbind=0.0.0.0
rpcallowip=172.16.0.0/12
rpcallowip=10.0.0.0/8
rpcuser=$RPC_USER
rpcpassword=$RPC_PASSWORD
EOF
cat > /config/mm-adapter.yaml <<EOF
server:
  host: "0.0.0.0"
  port: 44556
  rpc_user: "$RPC_USER"
  rpc_password: "$RPC_PASSWORD"
upstream:
  host: "jjmining-ltc-doge-p2pool_dogecoin_1"
  port: 22555
  rpc_user: "$RPC_USER"
  rpc_password: "$RPC_PASSWORD"
  timeout: 30
chain:
  name: "dogecoin"
  chain_id: 98
  network_magic: "c0c0c0c0"
EOF
chmod 600 /secrets/* /config/*.conf /config/mm-adapter.yaml
chown -R 1000:1000 /secrets /config /data
