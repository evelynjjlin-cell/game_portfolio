# V03 runtime review — 26 November 2026

Branch: `feat/high-fidelity-environment-camera-v03`. Final runtime code revision: `9083310eeab8a13bfba1f0aa9bd98a9d2183b2f9`; the following delivery commit only updates documentation.

## Capture environment

Native Chromium 141 at 1363 × 1023, running the local Vite application from this branch with SwiftShader software rendering. Its fallback renders the same geometry and authored lights at native resolution with antialiasing, while omitting the extra SSAO passes. Hardware renderers retain the full SSAO path. Screenshots are actual runtime captures, not Blender renders or generated concept art.

The Vercel Preview loads the application and its About/Contact panels. The cloud browser reports `GL_VENDOR = Disabled` and cannot create a WebGL context, so it shows the explicit 3D fallback. Cloud inspection is not GPU rendering acceptance. The native browser has a certificate-trust limitation for the public URL; local captures were used without bypassing that warning.

## Observed results and capture inventory

| File | Observed content |
| --- | --- |
| `01-front.jpg` | Complete house, chimney and curved open-book base, without clipping. |
| `02-rear.jpg` | Complete rear facade after exiting the kitchen; returned overview remains visible. |
| `03-sunroom.jpg` | Paired woven chairs, tea service and plants through open glazed leaves. |
| `04-living-room.jpg` | Sofa, rug, coffee table, floor lamp and fireplace. The balcony console that crossed the arch was removed. |
| `05-library.jpg` | Full shelving, ladder, carved reading chair and lit side table through open green doors. |
| `06-art-studio.jpg` | Drawing desk, storage drawers, articulated task lamp and easel. Doors open inward; the balcony rail remains in the foreground. |
| `07-bedroom.jpg` | Padded bed, duvet, pillows, bedside oil lamps and curtains through the open entrance. |
| `08-kitchen.jpg` | Sage cabinets, sink, shelving, stove, kettle and preparation table through open doors. |
| `09-music-room.jpg` | Upright piano, keys, pedals, bench, records, record player and boombox. |
| `10-workshop.jpg` | Pegboard tools, workbench drawers, vice, hand plane, task lamp, stool and small gear model. |
| `11-evening-front.jpg` | Evening palette and interior illumination, with the whole house and book visible. |
| `V03-eight-room-review.jpg` | Labeled contact sheet assembled from the eight unaltered room screenshots. |

The sunroom through bedroom captures were made at `d8d931c`; later changes affected canvas presentation and render scheduling, not geometry or material assets. The front, rear, kitchen, music room, workshop and evening captures were collected at `9083310`. All use the final architectural geometry committed at `3e3d01c`.

## Corrections and verification

- Native-resolution antialiasing replaces low-resolution software rendering. Hardware retains its antialiased SSAO pipeline.
- A console intersecting the living-room opening was removed in the Blender source and the shell was rebuilt and compressed.
- Demand-rendered presentation could blank after an exit despite a correct finite saved camera pose. The final runtime renders continuously, preserves the drawing buffer and caches static shadows. In a clean native session, kitchen and music exits returned to the rear overview and remained visible; workshop-to-front also completed visibly. This is observed regression coverage, not a universal GPU guarantee.
- About and Contact expose the real public profile, email, LinkedIn and portfolio destinations. No message was sent and no case study was invented.
- `npm run build` passes for the final runtime revision.
- Earlier unchanged camera/state checks passed 144 responsive fits and 727 entry/exit/interruption paths, including exact saved position, quaternion, target, FOV and zoom restoration. Mathematical checks do not certify every visible intersection or device performance.
- Delivery manifest: 21 environment/interior GLBs, 23,487,120 bytes and 309 primitives. Assets and the Meshopt decoder are self-hosted; provenance and adaptation details are in `ASSET_CREDITS.md`.

## Remaining limits

Software rendering is visibly slow. No measured frame rate, smooth real-device transition, Safari/iOS acceptance or mobile-touch acceptance is claimed. The authored camera duration is not a verified wall-clock duration on this CPU renderer. Hardware SSAO was not visually accepted in this software-only environment. No runtime video was captured.

This is a stylized original house, not a visual match to the reference image. Its outer silhouette, garden density and material finish still differ. These captures are a reviewable implementation checkpoint, not final art approval. All eight project slots remain unassigned.

The work remains isolated on the V03 branch. `main` and the V02 branch were not merged or replaced. Use the V03 Preview URL delivered with this revision.
