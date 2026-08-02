#!/bin/sh
set -eu
umask 077
mkdir -p /data /config /secrets
secret_name="${SECRET_NAME:-rpc.env}"
secret_file="/secrets/$secret_name"
if [ ! -s "$secret_file" ]; then
  printf 'RPC_USER=jjrpc_%s\nRPC_PASSWORD=%s\n' \
    "$(od -An -N8 -tx1 /dev/urandom | tr -d ' \n')" \
    "$(od -An -N32 -tx1 /dev/urandom | tr -d ' \n')" > "$secret_file"
fi
. "$secret_file"
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
chmod 600 "$secret_file" "/config/$CONF_NAME"
exec "$DAEMON" -datadir=/data -conf="/config/$CONF_NAME" "$@"
