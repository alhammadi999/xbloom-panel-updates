"""Reject feeds that do not describe the firmware actually being installed."""
import hashlib
import json
from pathlib import Path
import re
import sys

BOARD = "crowpanel-advance-43-saud"
VERSION = rb"(?:0|[1-9][0-9]{0,2})(?:\.(?:0|[1-9][0-9]{0,2})){2}"


def verify(folder, channel):
    feed = json.loads((folder / (channel + ".json")).read_text(encoding="utf-8"))
    version = feed["version"]
    if not isinstance(version, str) or not re.fullmatch(VERSION, version.encode()):
        raise ValueError("Invalid release version")
    if (feed["schema"], feed["board"], feed["channel"]) != (1, BOARD, channel):
        raise ValueError("Wrong schema, board or channel")
    image = (folder / ("xbloom-saud-" + version + ".bin")).read_bytes()
    if not 500000 <= len(image) <= 0x600000 or image[:1] != b"\xe9":
        raise ValueError("Invalid application size or image magic")
    if image[32:36] != b"\x32\x54\xcd\xab" or image[0x8000:0x8002] == b"\xaa\x50":
        raise ValueError("Expected OTA application, not a factory image")
    if feed["bytes"] != len(image) or feed["sha256"] != hashlib.sha256(image).hexdigest():
        raise ValueError("Firmware length or SHA-256 mismatch")
    marker = b"XBLOOM-OTA|" + BOARD.encode() + b"|"
    versions = set(re.findall(re.escape(marker) + b"(" + VERSION + rb")\|", image))
    if versions != {version.encode()}:
        raise ValueError(f"Feed {version} does not match embedded firmware versions {versions}")
    return {"channel": channel, "version": version, "bytes": len(image), "sha256": feed["sha256"]}


if __name__ == "__main__":
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
    for channel in ("stable", "pilot"):
        print(json.dumps(verify(root, channel)))
