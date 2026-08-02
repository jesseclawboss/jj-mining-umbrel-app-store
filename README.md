# JJ Mining Umbrel Community App Store

Apps included:
- **JJ Litecoin Node** — Litecoin Core 0.21.5.5 with a browser status page.
- **JJ Dogecoin Node** — Dogecoin Core 1.14.9 with a browser status page.
- **JJ LTC/DOGE P2Pool** — experimental merged-mining stack for Scrypt ASICs.

## Publish the store
1. Create a new **public** GitHub repository named `jj-mining-umbrel-app-store`.
2. Upload the contents of this folder to the repository root, or run the included `publish.sh` from a computer with Git installed.
3. In Umbrel: App Store → three-dot menu → Community App Stores → Add.
4. Enter `https://github.com/YOUR_GITHUB_USERNAME/jj-mining-umbrel-app-store`.

## Important
Dogecoin does not currently publish an official runtime Docker image. This package uses `coinmetrics/dogecoin:1.14.9`, pinned by version, for the standalone node. Review third-party images before storing wallet funds. The node apps are intended as full nodes/RPC backends; keep RPC private.

The merged-mining app is experimental and should first be tested with one ASIC. It uses its own LTC and DOGE node containers so it can be installed independently.
