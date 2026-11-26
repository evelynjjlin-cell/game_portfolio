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
