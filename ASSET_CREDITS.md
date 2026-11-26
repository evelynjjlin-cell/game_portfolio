# Asset credits and distribution manifest

Verified 26 November 2026. The architectural composition, house shell, arched joinery, animated hinges, book geometry, UX, camera behaviour and implementation are original to this portfolio. No complete house model or proprietary game content is included. The following individually selected, human-made third-party models and PBR textures are **public-domain CC0 assets**, freely available from Poly Haven.

## Licence and redistribution

All listed assets use [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/). [Poly Haven's official licence](https://polyhaven.com/license) explicitly permits commercial use, modification and redistribution, including sharing the files within another work. Attribution is optional; voluntary artist credits are preserved here. Public GitHub storage and browser-accessible GLB/JPEG files are permitted. These source assets remain CC0; original authorship is not claimed and their licence has not been replaced. Poly Haven's website text, logo and example renders are not included.

## Modular 3D models

| Local asset | Source and creator | Licence / attribution | Adaptation and delivery | Distribution restrictions |
|---|---|---|---|---|
| `public/assets/models/potted-plant.glb` | [Potted Plant 02](https://polyhaven.com/a/potted_plant_02) — Rico Cilliers | CC0; credit optional | Terracotta plant; mesh reduction to 21,338 triangles; floor-centred, one unit high; 512px colour/normal/roughness maps; leaf alpha preserved; restrained leaf tint; 888,260 bytes | No copyright redistribution restriction under CC0 |
| `public/assets/models/carved-armchair.glb` | [Arm Chair 01](https://polyhaven.com/a/ArmChair_01) — Kirill Sannikov | CC0; credit optional | Original carved wood and upholstery retained; 5,626 triangles; floor-centred, one unit high; 512px PBR maps; reduced normal intensity and varnish response; 297,228 bytes | No copyright redistribution restriction under CC0 |
| `public/assets/models/oak-side-table.glb` | [Small Wooden Table 01](https://polyhaven.com/a/small_wooden_table_01) — Ulan Cabanilla | CC0; credit optional | Original rounded legs and stretchers retained; 3,410 triangles; floor-centred, one unit high; 512px PBR maps; restrained roughness; 172,080 bytes | No copyright redistribution restriction under CC0 |
| `public/assets/models/wooden-lantern.glb` | [Wooden Lantern 01](https://polyhaven.com/a/wooden_lantern_01) — James Ray Cock | CC0; credit optional | Original frame, door and handle retained; 8,321 triangles; floor-centred, one unit high; 512px maps; simplified transparent glass response; added runtime emissive flame and local light; 490,604 bytes | No copyright redistribution restriction under CC0 |

The four optimized self-contained GLBs total **1,848,172 bytes (1.76 MiB)**. Original high-resolution downloads are not committed. Repeated placements share geometry, materials and textures. Plant meshes do not cast real-time shadows. Other props use the scene's existing shadow map; no prop adds a shadow-rendering light. No model loader makes third-party requests. `public/assets/models/manifest.json` records dimensions and mesh counts.

## V03 curated room props

The following **nine additional individual assets** were selected from Poly Haven's official model inventory for specific room functions. Each source is CC0, with optional attribution; public repository storage, browser delivery and modified derivatives are allowed under the official licence linked above. These are professional third-party components, not original portfolio sculptures. No complete room or house was downloaded.

| Local asset under `public/assets/models/v03/` | Official source and credited creator(s) | Intended room | Triangles | Packed bytes |
|---|---|---|---:|---:|
| `sofa-victorian.glb` | [Sofa 03](https://polyhaven.com/a/sofa_03) — Fran Calvente | Living room | 8,003 | 392,408 |
| `electric-stove.glb` | [Electric Stove](https://polyhaven.com/a/electric_stove) — Kuutti Siitonen | Kitchen | 13,914 | 664,140 |
| `electric-kettle.glb` | [Vintage Electric Kettle](https://polyhaven.com/a/vintage_electric_kettle) — SV Garip | Kitchen | 14,838 | 638,464 |
| `boombox.glb` | [Boombox](https://polyhaven.com/a/boombox) — Thomas Paul Mouilleron | Music room | 10,168 | 597,176 |
| `bench-vise.glb` | [Bench Vice 01](https://polyhaven.com/a/bench_vice_01) — Antanas Kep (modeling/texturing), Yann Kervran (rigging) | Workshop | 2,863 | 252,100 |
| `hand-plane.glb` | [Hand Plane No4](https://polyhaven.com/a/hand_plane_no4) — Satyaki Mandal | Workshop | 8,220 | 384,588 |
| `articulated-desk-lamp.glb` | [Desk Lamp Arm 01](https://polyhaven.com/a/desk_lamp_arm_01) — Kuutti Siitonen (modeling/texturing), Yann Kervran (rigging) | Art studio | 24,102 | 958,552 |
| `vintage-oil-lamp.glb` | [Vintage Oil Lamp](https://polyhaven.com/a/vintage_oil_lamp) — Monsta3D | Bedroom | 7,208 | 372,540 |
| `tea-set.glb` | [Tea Set 01](https://polyhaven.com/a/tea_set_01) — Rico Cilliers (modeling), James Ray Cock (texturing), Jurita Burger (graphic design) | Sunroom | 40,296 | 1,051,700 |

The V03 prop library totals **5,311,668 bytes (5.07 MiB), 129,612 triangles** before placement into room exports. Each derivative retains the source silhouette, material regions, UV coordinates and normals. Models are static evaluated meshes, normalized to one unit high with a floor-centered origin, +Y up and +Z front. Bone-display helpers added by Blender's glTF importer are excluded. Original PBR images are embedded at a maximum 512px dimension; opaque images use quality-84 JPEG, alpha-bearing images retain PNG. Normal-map strength is 0.7. No geometric decimation was applied to these nine assets. Rigged originals are delivered as a static pose, not as working appliance or vise mechanisms.

`public/assets/models/v03/provenance.json` records each official source URL, author roles, licence verification, original and normalized dimensions, source glTF MD5, derivative SHA-256, file size and triangle count. `scripts/environment/asset_processing_v03.py` reproduces download/checksum verification, Blender conversion and image packing. Downloaded full-resolution source packages and Poly Haven preview renders are excluded from the repository. The small difference between some source-page and exported triangle counts reflects the actual glTF mesh topology, not a claim of mesh reduction.

## Original Blender environment work

The V03 architectural shell, roof assembly, stone openings, book base, door/window dimensions and hinged joinery are authored for this composition in Blender. Room cabinetry, beds and bedding, soft curtains, shelves, workbenches, desks, piano-related furnishings and other supplemental furniture are custom Blender geometry where present. Their authorship is separate from the listed Poly Haven models and materials. Room GLBs may combine these original constructions with the credited CC0 props; embedding a prop into a room does not change its provenance. Custom joinery is necessary to match actual openings, hinge clearance, independent interactions and the eight room volumes.

`scripts/environment/pack_glb_images.py` also packs embedded images in exported room GLBs without altering mesh buffers or requiring an additional runtime decoder. It preserves already optimized JPEGs and alpha channels and coalesces identical binary chunks. Source props may be instantiated more than once where function calls for a pair, such as two bedside lamps; complete room layouts are authored individually.

The terrace and garden in `public/assets/environment/garden.glb` are authored by `scripts/environment/build_garden.py`: original bentwood chairs and turned table, linen cushions, wheel-thrown flowerpots, individual hydrangea florets, cupped ivy leaves and stems, sparse grass/moss islands, stone pavers, cup and candleholder. One existing Potted Plant 02 derivative supplies the botanical accent beside the terrace; its Rico Cilliers/CC0 credit above applies here too. The static garden contains 55,930 triangles in 16 material batches before transport compression. Planting follows the original book's curved page surface and is composed around the actual door/window coordinates, with the eight room openings, About doors and mailbox kept clear. No third-party garden or complete furniture arrangement was used.

## PBR material sources

| Local derivative files | Source and creator | Licence / attribution | Adaptation | Distribution restrictions |
|---|---|---|---|---|
| `plaster-{color,normal,roughness}.jpg` | [Beige Wall 001](https://polyhaven.com/a/beige_wall_001) — Dimitrios Savva (photography), Rico Cilliers (processing) | CC0; optional credit | 512px; neutralized albedo and roughness for warm ivory plaster | No copyright redistribution restriction under CC0 |
| `oak-{color,normal,roughness}.jpg` | [Wood Table 001](https://polyhaven.com/a/wood_table_001) — Dimitrios Savva (photography), Rico Cilliers (processing) | CC0; optional credit | 512px; neutralized grain, palette applied in material | No copyright redistribution restriction under CC0 |
| `slate-{color,normal,roughness}.jpg` | [Roof Slates 03](https://polyhaven.com/a/roof_slates_03) — Rob Tuytel | CC0; optional credit | 128px single slate face crop from 1K source, coordinates `(312,321,347,348)`; neutral colour. Roof tile geometry and arrangement are original | No copyright redistribution restriction under CC0 |
| `stone-{color,normal,roughness}.jpg` | [Sandstone Blocks 04](https://polyhaven.com/a/sandstone_blocks_04) — Rob Tuytel | CC0; optional credit | 512px crop from 1K source, coordinates `(120,50,900,590)`; neutralized colour | No copyright redistribution restriction under CC0 |
| `bookcloth-{color,normal,roughness}.jpg`, `paper-color.jpg` | [Book Pattern](https://polyhaven.com/a/book_pattern) — Rob Tuytel | CC0; optional credit | 512px; neutralized albedo and roughness; paper-colour derivative | No copyright redistribution restriction under CC0 |

Texture files live in `public/assets/textures/`. All normals use OpenGL orientation and linear sampling. Colour textures use sRGB. The 16 optimized JPEG derivatives total 301,684 bytes. Brass response, palette colours and supplementary procedural surface variation are original implementation materials.

## Selection decisions and scope

Individual carved furniture, a natural botanical model and a detailed lantern were imported for their believable silhouettes and manageable mesh counts. Door/window joinery remains custom geometry so openings, dimensions, hinge clearance and independent room interactions match this original architectural composition. No ready-made building was used. Assets requiring payment, login-only redistribution rights, unclear licences or proprietary game extraction were not used.

Photographic material detail is deliberately softened and all assets share the miniature's warm lighting. These sources supply professional component geometry; they do not establish that the final environment has been independently art-reviewed or matches the concept image exactly.
