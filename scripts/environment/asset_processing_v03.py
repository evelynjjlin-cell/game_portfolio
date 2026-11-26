"""Reproduce the V03 individually curated Poly Haven prop derivatives.

Python: asset_processing_v03.py download --cache /path/to/cache
Blender: blender -b --python asset_processing_v03.py -- build --cache /path/to/cache
Python: asset_processing_v03.py pack --cache /path/to/cache

Source assets are CC0, https://polyhaven.com/license . Downloads remain outside
the repository. Only optimized self-contained GLBs and provenance are committed.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import struct
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor

ASSETS = {
    "sofa_03": ("sofa-victorian", "living", "Carved upholstered Victorian sofa"),
    "electric_stove": ("electric-stove", "kitchen", "Enamel electric cooker and oven"),
    "vintage_electric_kettle": ("electric-kettle", "kitchen", "Vintage electric kettle"),
    "boombox": ("boombox", "music", "Portable stereo with detailed speaker grilles"),
    "bench_vice_01": ("bench-vise", "workshop", "Cast-metal bench vise"),
    "hand_plane_no4": ("hand-plane", "workshop", "Woodworking hand plane"),
    "desk_lamp_arm_01": ("articulated-desk-lamp", "art", "Articulated clamp lamp"),
    "vintage_oil_lamp": ("vintage-oil-lamp", "bedroom", "Vintage glass oil lamp"),
    "tea_set_01": ("tea-set", "sunroom", "Ceramic teapot, cups and saucers"),
}
REPO = Path(__file__).resolve().parents[2]
OUTPUT = REPO / "public/assets/models/v03"
USER_AGENT = "EvelynPortfolioAssetPipeline/1.0"


def fetch(url):
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=90) as response:
        return response.read()


def download(cache):
    cache.mkdir(parents=True, exist_ok=True)
    jobs = []
    for source in ASSETS:
        for endpoint in ("info", "files"):
            path = cache / f"{source}-{endpoint}.json"
            if not path.exists():
                path.write_bytes(fetch(f"https://api.polyhaven.com/{endpoint}/{source}"))
        data = json.loads((cache / f"{source}-files.json").read_text())["gltf"]["1k"]["gltf"]
        jobs.append((cache/source/f"{source}.gltf", data))
        jobs.extend((cache/source/name, metadata) for name, metadata in data["include"].items())

    def transfer(job):
        path, metadata = job
        path.parent.mkdir(parents=True, exist_ok=True)
        expected = metadata["md5"]
        if path.exists() and hashlib.md5(path.read_bytes()).hexdigest() == expected:
            return
        blob = fetch(metadata["url"])
        assert hashlib.md5(blob).hexdigest() == expected, f"Source checksum mismatch: {path}"
        path.write_bytes(blob)
        print("Downloaded", path.relative_to(cache), len(blob), flush=True)

    with ThreadPoolExecutor(max_workers=6) as pool:
        list(pool.map(transfer, jobs))


def build(cache):
    import bpy
    from mathutils import Vector, Matrix
    OUTPUT.mkdir(parents=True, exist_ok=True)
    existing = OUTPUT/"provenance.json"
    records = [r for r in json.loads(existing.read_text()) if r["source_id"] not in ASSETS] if existing.exists() else []
    for source, (slug, room, description) in ASSETS.items():
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.gltf(filepath=str(cache/source/f"{source}.gltf"))
        # The Blender glTF importer creates mesh display shapes for armatures.
        # These are editor helpers, not source geometry, and must never export.
        bone_shapes = {bone.custom_shape for arm in bpy.context.scene.objects
            if arm.type == "ARMATURE" for bone in arm.pose.bones if bone.custom_shape}
        original = [o for o in bpy.context.scene.objects if o.type == "MESH" and o not in bone_shapes]
        depsgraph = bpy.context.evaluated_depsgraph_get()
        meshes = []
        # Freeze imported rig/parent transforms into evaluated meshes. This also
        # prevents glTF hierarchy transforms from being applied twice on export.
        for obj in original:
            evaluated = obj.evaluated_get(depsgraph)
            mesh = bpy.data.meshes.new_from_object(evaluated, depsgraph=depsgraph)
            frozen = bpy.data.objects.new(obj.name + "_web", mesh)
            bpy.context.collection.objects.link(frozen)
            frozen.matrix_world = obj.matrix_world.copy()
            meshes.append(frozen)
        for obj in list(bpy.context.scene.objects):
            if obj not in meshes:
                bpy.data.objects.remove(obj, do_unlink=True)
        bpy.context.view_layer.update()
        points = [o.matrix_world @ Vector(v) for o in meshes for v in o.bound_box]
        low = Vector([min(v[i] for v in points) for i in range(3)])
        high = Vector([max(v[i] for v in points) for i in range(3)])
        size = high-low
        center = Vector(((low.x+high.x)/2, (low.y+high.y)/2, low.z))
        factor = 1/size.z
        for obj in meshes:
            transform = obj.matrix_world.copy()
            for vertex in obj.data.vertices:
                vertex.co = (transform @ vertex.co-center)*factor
            obj.matrix_world = Matrix.Identity(4)
        # Source normals, material regions, UVs and silhouettes remain intact.
        # Resize/repack embedded images after export to preserve alpha channels.
        for material in bpy.data.materials:
            if not material.use_nodes:
                continue
            for node in material.node_tree.nodes:
                if node.type == "NORMAL_MAP":
                    node.inputs["Strength"].default_value = 0.7
        target = OUTPUT / f"{slug}.glb"
        bpy.ops.export_scene.gltf(filepath=str(target), export_format="GLB",
            export_apply=True, export_image_format="AUTO", export_texcoords=True,
            export_normals=True, export_materials="EXPORT", export_yup=True,
            export_animations=False, export_cameras=False, export_lights=False)
        info = json.loads((cache/f"{source}-info.json").read_text())
        record = {
            "id": slug, "source_id": source, "source_name": info["name"],
            "source_url": f"https://polyhaven.com/a/{source}",
            "source_authors": info["authors"], "license": "CC0-1.0",
            "license_url": "https://polyhaven.com/license", "room": room,
            "license_verified_on": "2026-11-26",
            "permitted_distribution": ["public Git repository", "browser-accessible static GLB", "modified derivative"],
            "description": description, "triangles": sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in meshes),
            "meshes": len(meshes), "original_size_xyz_m": [round(size.x,5),round(size.z,5),round(size.y,5)],
            "normalized_size_xyz": [round(size.x*factor,5),1,round(size.y*factor,5)],
            "origin": "floor center", "up_axis": "+Y", "front_axis": "+Z",
            "adaptation": "Static evaluated meshes; floor-centered unit-height normalization; preserved UVs and source normals; normal-map strength 0.7; embedded PBR images resized to at most 512px, alpha preserved.",
        }
        records.append(record)
        # Save after each asset so parallel room assembly can consume ready files.
        (OUTPUT/"provenance.json").write_text(json.dumps(records,indent=2)+"\n")
        print("ASSET_RESULT", json.dumps(record), flush=True)


def pack(cache):
    from PIL import Image
    manifest = json.loads((OUTPUT/"provenance.json").read_text())
    for record in manifest:
        if record["source_id"] not in ASSETS:
            continue
        path = OUTPUT/f"{record['id']}.glb"
        data = path.read_bytes()
        length = struct.unpack_from("<I", data, 12)[0]
        document = json.loads(data[20:20+length])
        binary = data[28+length:]
        replacements = {}
        for entry in document.get("images", []):
            index = entry["bufferView"]
            view = document["bufferViews"][index]
            image = Image.open(io.BytesIO(binary[view.get("byteOffset",0):view.get("byteOffset",0)+view["byteLength"]]))
            image.thumbnail((512,512), Image.Resampling.LANCZOS)
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
        for index, view in enumerate(document["bufferViews"]):
            content = replacements.get(index, binary[view.get("byteOffset",0):view.get("byteOffset",0)+view["byteLength"]])
            output.extend(b"\0" * ((-len(output))%4))
            view["byteOffset"] = len(output)
            view["byteLength"] = len(content)
            output.extend(content)
        document["buffers"][0]["byteLength"] = len(output)
        output.extend(b"\0"*((-len(output))%4))
        encoded = json.dumps(document, separators=(",",":")).encode()
        encoded += b" "*((-len(encoded))%4)
        path.write_bytes(struct.pack("<III",0x46546c67,2,28+len(encoded)+len(output)) +
            struct.pack("<II",len(encoded),0x4e4f534a)+encoded +
            struct.pack("<II",len(output),0x004e4942)+output)
        record["bytes"] = path.stat().st_size
        record["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
        record["texture_max_dimension"] = 512
        source = record["source_id"]
        source_file = json.loads((cache/f"{source}-files.json").read_text())["gltf"]["1k"]["gltf"]
        record["source_gltf_url"] = source_file["url"]
        record["source_gltf_md5"] = source_file["md5"]
        print("Packed", path.name, record["bytes"], flush=True)
    (OUTPUT/"provenance.json").write_text(json.dumps(manifest,indent=2)+"\n")


if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else sys.argv[1:]
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("download","build","pack"))
    parser.add_argument("--cache", required=True, type=Path)
    parser.add_argument("--asset", choices=tuple(ASSETS), help="Process just one source asset")
    options = parser.parse_args(args)
    if options.asset:
        ASSETS = {options.asset: ASSETS[options.asset]}
    globals()[options.action](options.cache)
