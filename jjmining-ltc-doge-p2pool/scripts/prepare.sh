#!/usr/bin/env bash
set -euo pipefail
APP_DIR="${1:-$(pwd)}"
DATA_DIR="${APP_DATA_DIR:-$APP_DIR/data}"
mkdir -p "$DATA_DIR/config" "$DATA_DIR/data/litecoin" "$DATA_DIR/data/dogecoin" "$DATA_DIR/data/p2pool"
if [[ ! -f "$DATA_DIR/config/mm-adapter.yaml" ]]; then
  cp "$APP_DIR/config/mm-adapter.yaml.example" "$DATA_DIR/config/mm-adapter.yaml"
fi
cat <<MSG
Created data folders under: $DATA_DIR
Next:
1. Replace all CHANGE_ME values in docker-compose.yml and mm-adapter.yaml.
2. Set LTC_PAYOUT_ADDRESS to a legacy Litecoin address beginning with L.
3. Keep port 9327 restricted to your LAN.
MSG
