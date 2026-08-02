#!/bin/sh
set -eu
while [ ! -s /secrets/dogecoin.env ]; do sleep 1; done
. /secrets/dogecoin.env
cat > /config/mm-adapter.yaml <<EOF
server:
  host: "0.0.0.0"
  port: 44556
  rpc_user: "$RPC_USER"
  rpc_password: "$RPC_PASSWORD"
upstream:
  host: "dogecoin"
  port: 22555
  rpc_user: "$RPC_USER"
  rpc_password: "$RPC_PASSWORD"
  timeout: 30
chain:
  name: "dogecoin"
  chain_id: 98
  network_magic: "c0c0c0c0"
EOF
exec python /app/adapter.py --config /config/mm-adapter.yaml
