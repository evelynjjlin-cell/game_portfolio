# V03 east-room source workflow

`build_interiors_east.py` authors and exports the art studio, kitchen, music room and workshop. Run from the repository root with Blender 4.3 or newer:

```sh
blender -b --python scripts/environment/build_interiors_east.py
python3 scripts/environment/pack_glb_images.py public/assets/interiors/art.glb public/assets/interiors/kitchen.glb public/assets/interiors/music.glb public/assets/interiors/workshop.glb
node scripts/environment/inspect_interiors_east.mjs
```

To rebuild one room, append `-- art`, `-- kitchen`, `-- music` or `-- workshop` to the Blender command. Existing records for other rooms are retained in `east-layout.json`. Blender writes matching fixture metadata with each GLB. The packer may change byte counts; refresh `bytes` in the JSON after packing/compression if byte-accurate manifests are required. The final deployment pipeline applies Meshopt afterward and must preserve named mechanism nodes.

Each room uses the `layout.json` dimensions. Runtime coordinates are +Y up, +Z toward the viewer, with the finished floor at Y0, entrance plane at Z0 and the room extending toward negative Z. The authored enclosure includes the floor, both sides, rear wall and ceiling. Wall/ceiling thickness adds 0.07m outside the requested clear interior. Entrance facade and opening leaves belong to the separate exterior/joinery assets.

Art studio furnishings clear the actual inward leaf sectors: pivots X±1.4975,Z−.13 and approximately 1.5m leaves. Frontmost drafting-table extent is X[−.67,.51],Z−1.54; the cabinet and easel stand farther back. Art ceiling beams begin at Z−1.72 because the leaf meeting corners reach Y2.5975.

The four arrangements are authored independently: flat-file cabinet/drawing desk/easel; fitted Shaker cabinetry/sink/island; full upright piano/tufted bench/record console; tool chest/pegboard/workbench/model mechanism. Static meshes merge by material. Final source geometry uses 17,19,22,20 draw primitives respectively. All PBR images are embedded and at most 512px.

`RecordPlatter` in music.glb has an identity rotation and spins about local Y. `WorkshopGear` in workshop.glb has an identity rotation and spins about local Z. Both origins lie at their physical axle centers. Do not combine these nodes with static room surfaces when optimizing.

Fixtures are described in `public/assets/interiors/{kind}-metadata.json`. These are floor-local coordinates and include named fixtures, color, intensity and suggested falloff distance. The runtime should create point lights; the GLBs contain fixture geometry and emissive surfaces, not exported Blender lights. Art and workshop task-lamp positions derive from the imported source's emissive lens center rather than approximate room-fill locations. The vise and both clamp lamps include correct mounting-height offsets.

Imported stove, electric kettle, boombox, articulated lamp, vise and hand plane are CC0 individual props prepared by `scripts/environment/asset_processing_v03.py` (see the repository credits and `public/assets/models/v03/provenance.json`). Everything else is original authored room geometry. No complete third-party room or house was imported.

The Blender workflow saves neutral front inspection renders under `../v03-review/east/`. The exported geometry audit checks bounds, finite coordinates, embedded resources and dynamic node preservation. The Blender previews are asset checks; final interaction and integrated architecture verification remain runtime checks.
