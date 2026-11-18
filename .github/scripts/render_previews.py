from pathlib import Path
import struct
import sys
import zlib
import base64

for file in Path(sys.argv[1]).glob("*.ppm"):
    header, pixels = file.read_bytes().split(b"\n", 1)
    magic, width, height, maximum = header.split()
    width, height = int(width), int(height)
    assert magic == b"P6" and maximum == b"255" and len(pixels) == width*height*3
    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind+data)&0xffffffff)
    rows = b"".join(b"\0" + pixels[y*width*3:(y+1)*width*3] for y in range(height))
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB",width,height,8,2,0,0,0)) + chunk(b"IDAT", zlib.compress(rows)) + chunk(b"IEND", b"")
    file.with_suffix(".png").write_bytes(png)
    file.with_suffix(".png.b64").write_text(base64.b64encode(png).decode(), encoding="ascii")

