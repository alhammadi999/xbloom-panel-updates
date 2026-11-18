import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from verify_release import verify


ROOT = Path(__file__).resolve().parents[1]


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.feed = json.loads((ROOT / "stable.json").read_text())
        self.feed["channel"] = "pilot"
        self.image = (ROOT / f'xbloom-saud-{self.feed["version"]}.bin').read_bytes()

    def check(self):
        (self.root / "pilot.json").write_text(json.dumps(self.feed))
        (self.root / f'xbloom-saud-{self.feed["version"]}.bin').write_bytes(self.image)
        return verify(self.root, "pilot")

    def test_matching_image(self):
        self.assertEqual(self.check()["version"], "3.4.0")

    def test_renamed_old_firmware_rejected(self):
        self.feed["version"] = "3.4.1"
        with self.assertRaisesRegex(ValueError, "embedded firmware"):
            self.check()

    def test_checksum_rejected(self):
        self.feed["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            self.check()

    def test_length_rejected(self):
        self.feed["bytes"] += 1
        with self.assertRaisesRegex(ValueError, "length"):
            self.check()

    def test_wrong_board_rejected(self):
        self.feed["board"] = "another-panel"
        with self.assertRaisesRegex(ValueError, "board"):
            self.check()

    def test_factory_image_rejected(self):
        data = bytearray(self.image)
        data[0x8000:0x8002] = b"\xaa\x50"
        self.image = bytes(data)
        self.feed["sha256"] = hashlib.sha256(self.image).hexdigest()
        with self.assertRaisesRegex(ValueError, "factory"):
            self.check()

    def test_invalid_version_rejected(self):
        self.feed["version"] = "../3.4.2"
        (self.root / "pilot.json").write_text(json.dumps(self.feed))
        with self.assertRaisesRegex(ValueError, "version"):
            verify(self.root, "pilot")

    def test_published_channels(self):
        for channel in ("stable", "pilot"):
            self.assertEqual(verify(ROOT, channel)["channel"], channel)


if __name__ == "__main__":
    unittest.main()
