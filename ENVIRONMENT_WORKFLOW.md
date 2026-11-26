# V03 environment workflow

The runtime house is an original Blender-authored composition assembled from a static architectural shell, a sculpted open-book foundation, independently hinged entrances, and eight furnished interiors. React Three Fiber loads the GLBs and supplies lighting, selection, camera travel and small room animations. No complete house or room scene was downloaded.

## Source of truth and coordinate contract

`scripts/environment/layout.json` defines the eight room IDs, residential identities, entrance positions, widths, heights, arch rises, depths and floor levels. The Blender builders and `src/config/rooms.ts` consume this shared layout. Runtime coordinates are **+Y up and +Z toward the front facade**. Back rooms rotate by π around Y. The builders convert their authored coordinates to Blender coordinates before exporting Y-up glTF.

Interior exports have a floor-centered origin at the entrance, with room depth toward local −Z. Joinery exports retain their named left/right hinge pivots. Runtime `Room` places the interior at the opening's floor and the joinery at the entrance center. Do not add a second house-wide vertical offset. Camera positions and targets in `rooms.ts` are already world-space values.

| Room ID | Identity | Interior builder |
| --- | --- | --- |
| `front-room-01` | Sunroom | `build_interiors_west.py` |
| `front-room-02` | Living Room | `build_interiors_west.py` |
| `front-room-03` | Library | `build_interiors_west.py` |
| `front-room-04` | Art Studio | `build_interiors_east.py` |
| `back-room-01` | Bedroom | `build_interiors_west.py` |
| `back-room-02` | Kitchen | `build_interiors_east.py` |
| `back-room-03` | Music Room | `build_interiors_east.py` |
| `back-room-04` | Workshop | `build_interiors_east.py` |

## Rebuild the committed exports

Run from the repository root. Requirements are Node/npm, Blender with its glTF exporter, and Python with Pillow for image packing. Existing `public/assets/textures` and normalized prop GLBs are build inputs. Use `npm ci` to install the locked JavaScript dependencies.

```sh
blender -b -t 2 -P scripts/environment/build_architecture.py
blender -b -t 2 -P scripts/environment/build_book.py
blender -b -t 2 -P scripts/environment/build_joinery.py
blender -b -t 2 -P scripts/environment/build_interiors_west.py
blender -b -t 2 -P scripts/environment/build_interiors_east.py
python3 scripts/environment/pack_glb_images.py public/assets/environment/*.glb public/assets/environment/joinery/*.glb public/assets/interiors/*.glb
node scripts/environment/compress_exports.mjs
```

The interior builders also accept selected identities after `--`, for example `blender -b -t 2 -P scripts/environment/build_interiors_east.py -- kitchen workshop`. They export per-room metadata with fixture positions and generate Blender review images outside the repository. Those review images are modeling diagnostics; they do not establish browser rendering acceptance.

The image packer retains geometry buffers, caps embedded images at 512 pixels, keeps alpha-bearing images as PNG, and uses JPEG for opaque images. Already optimized JPEGs are retained. Run it before geometry compression.

`compress_exports.mjs` applies `npx gltf-transform meshopt INPUT.glb TEMP.glb --level medium` to environment and interior exports, replaces each source with its compressed result, skips already compressed files, refreshes metadata byte counts and hashes, and writes `public/assets/environment/delivery-manifest.json`. Meshopt preserves the named nodes needed for hinges and room animation. The credited source prop derivatives under `public/assets/models/` are left unchanged. Do not substitute a scene-flattening operation that removes hinge or dynamic nodes.

## Asset provenance

`ASSET_CREDITS.md` separates original architecture and custom furniture from individually curated Poly Haven models and material scans. `public/assets/models/v03/provenance.json` records official source pages, authors, CC0 licence verification, original and normalized dimensions, source checksums and derivative hashes. All delivered assets are self-hosted.

To reproduce the nine additional V03 prop derivatives, choose a source cache outside the repository and run:

```sh
python3 scripts/environment/asset_processing_v03.py download --cache /path/to/asset-cache
blender -b -t 2 -P scripts/environment/asset_processing_v03.py -- build --cache /path/to/asset-cache
python3 scripts/environment/asset_processing_v03.py pack --cache /path/to/asset-cache
```

The download step verifies source checksums. Conversion freezes evaluated static meshes, excludes imported rig-display helpers, normalizes origins and dimensions, and packages the licensed textures. Rebuild affected interiors after changing these prop derivatives. Full source downloads and website preview images are not runtime assets and are not committed.

## Runtime composition and interaction

`House.tsx` imports `BookAsset`, `EnvironmentShell`, `Room`, independent About joinery and the mailbox. The older V02 `Architecture`, `OpenBook`, `Roof`, `Furniture`, `Scenery`, `ImportedAssets` and `HingedWindow` implementations remain in source as dormant references; they are not imported by the V03 `House` composition. Shared primitive/material helpers still serve smaller interactions.

The GLB shell uses consolidated material meshes; room models share source geometry while their reactive lamp materials are cloned per room. Runtime lighting combines a shadowed sun, hemisphere/fill lights, a small environment map, contact shadows, room-specific fixtures and glass-aware ambient occlusion. Transparent glazing and invisible entrance targets are excluded from AO occlusion. Rendering adapts device pixel ratio to observed performance.

`rooms.ts` holds each entrance normal, hinge direction, authored close-up, field of view, lighting values and animation timing. `cameraMath.ts` fits projected corners of the complete book/house/chimney bounds into the usable viewport with header and control clearance. The overview uses a 37° field of view; each room has its own camera and target. Room fitting increases distance only when a narrow viewport needs more entrance clearance.

Selecting a room opens its physical entrance immediately, waits 0.12 seconds, then moves the camera for 1.28 seconds. Cross-facade travel follows an exterior orbit before approaching the entrance normally. The camera remains outside the sash sweep. Manual orbit is disabled during travel and close-up. Exit retreats first, begins closure after 0.3 seconds, and restores the saved overview position, quaternion, target, field of view and zoom. A viewport resize preserves the viewing angle while recomputing fit distance.

`useWorld.ts` separates door phases from camera phases. Transition tokens reject stale camera callbacks and delayed closures after a reversal. Joinery uses retained animation progress, so opening and closing can reverse without snapping. Reduced-motion mode completes camera and door transitions promptly. All eight project references remain empty and unassigned.

## Save, then verify

Follow the requested sequence: **implement → commit → push → minimal check**. Do not merge the implementation branch into `main` without approval.

```sh
npm run check:state
npm run build
npm run dev
```

`check:state` exercises delayed closure, rapid reversal, stale callbacks, hover isolation, eight distinct empty room slots, responsive fits at six viewport sizes, exterior entry/exit routes, interrupted cross-facade exits, sash clearance and exact saved-pose restoration. These mathematical/state checks complement runtime inspection; they do not verify final materials, all mesh intersections, visual quality or device performance.

For runtime review, inspect the front and rear overview, open all eight rooms, return from a manually rotated rear view, interrupt entry and exit, test reduced motion, resize between portrait and landscape, and confirm that dragging does not select a room. Check About, Contact, mailbox and external links. Capture actual browser screenshots of both facades and every room, plus a transition recording where available. Record observed results and any limitations in `docs/verification.md`; Blender renders or generated concept images are not browser evidence.
