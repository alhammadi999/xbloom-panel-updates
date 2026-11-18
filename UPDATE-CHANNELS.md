# xBloom Panel updates

Firmware for Saud’s CrowPanel Advance 4.3 (ESP32-S3). Stable customer releases use `stable.json`. Pilot panels use `pilot.json`. Each manifest names the version, board, byte length and SHA-256 of the matching application image. In Settings → Software update, choose Customers or Pilot test. An online install requires confirmation on the panel.

The first online-capable build must be uploaded once through the existing local update page. Subsequent updates are available directly on the panel.

## Pilot 3.4.2

Pilot 3.4.1 was incorrectly published with the unchanged 3.4.0 application. Its
hash was valid but its embedded version was not 3.4.1. The panel correctly
rejected it after downloading, before activating the image or restarting.

Pilot 3.4.2 is built from firmware source with an embedded 3.4.2 identity.
Verification failures identify a checksum or version mismatch, remain visible,
and require a new check before retrying. Download progress remains below 100%
until image verification and activation succeed; only then does the panel
announce completion and restart. Stable remains 3.4.0 with its original bytes.

Test on one panel: choose Pilot test, press Check now, confirm 3.4.2, then install.
Keep power connected. After the automatic restart, verify Installed 3.4.2, wait
at least 30 seconds, and check again: the Pilot channel should be up to date.
Verify Wi-Fi and the selected channel survived the restart. If installation
fails, record the exact error and do not treat the download counter as success.

Before publishing, run `python scripts/verify_release.py` and
`python -m unittest discover -s scripts -p 'test_*.py' -v`.
CI runs these checks on pushes and pull requests. A failed workflow reports a
bad publication; it does not prevent direct pushes to main. Run checks locally
before publishing. Never rename an older binary to advertise a newer version.
Use the source project's `prepare_panel_release.py pilot` command to derive the
manifest from the built application's identity. Promotion to Customers is a
separate decision requiring the owner's approval.

Firmware build and file verification are automated. Restart, rollback, display,
and machine interaction still require testing on the physical panel.
