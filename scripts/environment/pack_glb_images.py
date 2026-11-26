"""Losslessly retain mesh buffers, compact embedded GLB images to 512px.

Usage: python3 scripts/environment/pack_glb_images.py path/to/room.glb [...]
Requires Pillow. No runtime decoder extension or external texture is introduced.
Already optimized JPEGs are retained without another lossy generation.
"""
import argparse
import io
import json
from pathlib import Path
import struct
from PIL import Image


def pack(path, max_dimension=512):
    data = path.read_bytes()
    assert struct.unpack_from("<I", data)[0] == 0x46546c67
    json_size = struct.unpack_from("<I", data, 12)[0]
    document = json.loads(data[20:20+json_size])
    binary = data[28+json_size:]
    assert len(document["buffers"]) == 1, "Expected one embedded GLB buffer"
    replacements = {}
    for entry in document.get("images", []):
        index = entry["bufferView"]
        view = document["bufferViews"][index]
        content = binary[view.get("byteOffset",0):view.get("byteOffset",0)+view["byteLength"]]
        image = Image.open(io.BytesIO(content))
        if entry.get("mimeType") == "image/jpeg" and max(image.size) <= max_dimension:
            continue
        image.thumbnail((max_dimension,max_dimension), Image.Resampling.LANCZOS)
        result = io.BytesIO()
        alpha = image.mode == "RGBA" and image.getextrema()[3][0] < 255
        if alpha:
            image.save(result, format="PNG", optimize=True)
            entry["mimeType"] = "image/png"
        else:
            image.convert("RGB").save(result, format="JPEG", quality=84, optimize=True)
            entry["mimeType"] = "image/jpeg"
        replacements[index] = result.getvalue()
    output = bytearray()
    content_offsets = {}
    for index, view in enumerate(document["bufferViews"]):
        content = replacements.get(index, binary[view.get("byteOffset",0):view.get("byteOffset",0)+view["byteLength"]])
        if content not in content_offsets:
            output.extend(b"\0" * ((-len(output))%4))
            content_offsets[content] = len(output)
            output.extend(content)
        view["byteOffset"] = content_offsets[content]
        view["byteLength"] = len(content)
    document["buffers"][0]["byteLength"] = len(output)
    output.extend(b"\0"*((-len(output))%4))
    encoded = json.dumps(document, separators=(",",":")).encode()
    encoded += b" "*((-len(encoded))%4)
    path.write_bytes(struct.pack("<III",0x46546c67,2,28+len(encoded)+len(output)) +
        struct.pack("<II",len(encoded),0x4e4f534a)+encoded +
        struct.pack("<II",len(output),0x004e4942)+output)
    print(f"{path.name}: {len(data):,} -> {path.stat().st_size:,} bytes")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="+", type=Path)
    parser.add_argument("--max-dimension", type=int, default=512)
    args = parser.parse_args()
    for file in args.files:
        pack(file, args.max_dimension)
