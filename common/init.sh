#!/bin/sh
set -eu
umask 077
mkdir -p /secrets /config /data
if [ ! -s /secrets/rpc.env ]; then
  user="jjrpc_$(od -An -N8 -tx1 /dev/urandom | tr -d ' \n')"
  password="$(od -An -N32 -tx1 /dev/urandom | tr -d ' \n')"
  printf 'RPC_USER=%s\nRPC_PASSWORD=%s\n' "$user" "$password" > /secrets/rpc.env
fi
. /secrets/rpc.env
cat > "/config/$CONF_NAME" <<EOF
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
chmod 600 /secrets/rpc.env "/config/$CONF_NAME"
chown -R 1000:1000 /secrets /config /data
