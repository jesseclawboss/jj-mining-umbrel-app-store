#!/usr/bin/env bash
set -euo pipefail
USER=${1:?Usage: ./publish.sh GITHUB_USERNAME}
REPO=jj-mining-umbrel-app-store
git init
git add .
git commit -m "Initial JJ Mining Umbrel App Store"
git branch -M main
git remote add origin "https://github.com/$USER/$REPO.git"
git push -u origin main
