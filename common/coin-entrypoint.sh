#!/bin/sh
set -eu
exec "$DAEMON" -datadir=/data -conf="/config/$CONF_NAME" "$@"
