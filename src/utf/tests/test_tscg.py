import unittest

from tscg.core import canonical, checksum, parse, validate
from tscg_b.core import pack_text, unpack_frame


class TSCGTests(unittest.TestCase):
    def test_roundtrip(self):
        text = "COG -> DNT -> SHD(v1) ^ CAP -> COM"
        expr = parse(text)
        validate(expr)
        canon = canonical(expr)
        self.assertIn("COG", canon)
        self.assertEqual(len(checksum(expr)), 64)

    def test_binary(self):
        text = "COG -> DNT -> SHD(v1) ^ CAP -> COM"
        frame = pack_text(text)
        info = unpack_frame(frame)
        self.assertIn("COG", info["text"])


if __name__ == "__main__":
    unittest.main()
