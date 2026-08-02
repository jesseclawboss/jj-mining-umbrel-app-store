# Physical Umbrel verification only

- Install, update, restart, stop, reboot, and uninstall each app on an amd64 Umbrel; confirm data survives every operation and uninstall offers the expected data-removal behavior.
- Install both standalone node apps on an arm64 Umbrel and complete an initial sync; the merged-mining app is intentionally amd64-only.
- Connect one Scrypt ASIC to port 9327 and verify accepted/rejected shares, hashrate, worker identity, P2Pool peers, and both payout paths over a meaningful test window.
- Confirm router/firewall behavior for optional P2Pool P2P port 9326 and coin P2P ports 9333/22556 on the owner's LAN.
