# V0.35 exterior refinement

Recoverable V03 checkpoint: `90e2a68b2b7e1157447eda1fd5b40c5d8d3e2c6e` on `feat/high-fidelity-environment-camera-v03`.
Working branch: `feat/facade-refinement-side-elevation-v035`.

## Phase 1 — corners

Replaced alternating oversized corner blocks with continuous slim L-shaped limestone returns. The new outer arris projects 35 mm in model units from the plaster plane, with fine recessed course joints and a consistent stone tone on all four corners. The front/back opening coordinates and all hinged joinery remain unchanged.

## Phase 2 — envelope continuity

Added full-depth continuous stone reveals behind the existing entrance surrounds, reduced face-stone projection and mortar gaps, and unified the surround tone. Dressed side plinths, closed oak soffit returns, greenhouse ledger/flashing, balcony drip edges and a solid fine-jointed chimney core now connect the major elements. Downpipes sit on the side returns with connecting swan necks, clearing the refined corner arris. Room layouts, opening outlines and pivots remain unchanged.

## Phase 3 — left and right elevations

Both end walls now have four small recessed arched casements aligned over two storeys, each cut through the side masonry with a deep stone reveal, inset green sash, divided glazing and projecting sill/drip. The old applied dark disk is replaced by a true attic oculus. A restrained timber gable frame and a limestone floor course relate the side walls to the front and rear. Removed the large side-wall ivy strands; the design no longer relies on foliage to fill blank wall space. These fixed architectural windows are not new project entrances.

## Phase 4 — four-sided cohesion

The walnut, bronze and forest-slate tones were brought into a restrained common palette; limestone tone variation is subtler. Concealed ridge bedding closes the bright slit under the barrel caps while retaining the roof silhouette. Continuous chamfered limestone side paths follow the curved book surface and meet the existing terrace. Narrow muted planted edges replace scattered side moss islands and loose stepping stones. Existing terrace furniture and the two entrance planters are retained.

## Phase 5 — verification and delivery

Reviewed on 27 November 2026. The architecture phases were committed and pushed separately before their minimal checks:

| Phase | Pushed commit |
| --- | --- |
| Corners | `ae9af1bc63bf1870b6dbb62ad5594f5555ccbd7b` |
| Envelope continuity | `be02e6bb33a71446d518fbde8df53ec0abf8e5fe` |
| Side elevations | `11b27b819769793a84c4a8c4d61f9f3cd0605993` |
| Cohesion | `ff9c68b0179e46df2b4d3d9d7feb4386e5c73652` |

`npm run build` passes. `npm run check:state` passes: eight unique room slots, 144 responsive compositions and 727 collision-free camera entry, return and interruption routes, including restoration of the original overview pose. The complete delivery manifest matches all 21 GLBs: 24,384,468 bytes and 310 primitives. The shell is 370,082 triangles, 18 material meshes and 4,723,276 compressed bytes.

The eight interior assets, hinged joinery, book asset, room configuration/layout and camera/state implementation have no changes relative to the recoverable V03 checkpoint. The branch has not been merged into `main`.

### Capture method and limits

The facade images are captures of the running application in native Chromium 141 using SwiftShader, from runtime commit `ff9c68b0179e46df2b4d3d9d7feb4386e5c73652`. They are not Blender renders or generated concept images. Software-rendered camera changes take time to settle; captures are taken after the geometry is visible. This is a visual and functional spot review, not an FPS benchmark or Safari/mobile acceptance test. The separate cloud browser cannot start WebGL in this environment; it is used only to inspect the HTML controls and information panels.

| Actual runtime capture | View |
| --- | --- |
| `01-front.jpg` | Front three-quarter overview |
| `02-rear.jpg` | Rear facade |
| `03-left.jpg` | Left end wall, conservatory and terrace side |
| `04-right.jpg` | Right end wall, mailbox side |

All four views visibly show the final refined masonry, roof and paving assets. About and Contact opened and closed successfully in the browser; the existing email, LinkedIn and UX portfolio links remain present.
