# V0.2 verification — 26 November 2026

## Implementation and checks

- Original asymmetric three-wing shell; glass conservatory, furnished balcony, arched entrance, layered slate roofs, side gable, copper details and weather vane.
- Four independently selectable rooms on each facade; no case studies assigned. Interior dimensions, arched profiles and edge pivots are data-driven.
- CC0 modular plants, carved armchairs, wooden tables and lanterns are normalized and reused. All source/creator/license/adaptation details are in ASSET_CREDITS.md.
- Book uses curved closed page blocks, 60 visible paper strata, a clothbound cover, sewn headbands, curved spine and brass corners.
- `npm run build` passes. `npm run check:state` passes for interrupted transitions, rapid reversal, hover isolation, camera reset and eight empty project slots.
- All 16 arched leaf geometries were checked for finite vertices. Optimized model blobs were checked against the pushed Git tree.
- Front/rear shortcuts, rear-room opening and Contact were observed in the actual 3D renderer. The upper sill and porch roof were adjusted after visual inspection to clear the opening.
- Published navigation lists all eight updated rooms. Public email, LinkedIn and portfolio destinations were inspected; Copy email reports successful copying. No message was sent.
- Repeated roof/book geometry now uses 108 triangles per small rounded instance instead of 300. Indoor lanterns share their room's physical light; glow and room illumination respond to state and lamp toggles.

## Capture method

Actual running implementation captures use local Chromium with software WebGL, from pushed source. They are not concept art. Vercel build metadata identifies the corresponding source commit, and the deployed HTML/UI were separately checked in the cloud browser. That browser does not provide WebGL; the native test browser has a certificate-trust limitation for the public URL, so its 3D captures use the local development server without bypassing certificate warnings.

## Practical limits

- The supplied front concept guided the composition; no separate rear reference was attached. The rear is an original complementary arrangement.
- This is a real-time web interpretation, not a pixel-identical rendering of the concept image. No baked global illumination or SSAO postprocess is included; contact and directional shadows plus a small environment map provide the current shading.
- Actual iOS/Android touch, Safari rendering, hardware frame rates and low-end GPU profiling remain untested. Software WebGL is slow and is not evidence of mobile performance.
- Four professional modular models are included. Doors, windows, built-in shelving and architectural ornament remain custom geometry to preserve the required hinge dimensions and interaction system.
- Main and the original implementation branch remain separate. V0.2 deployments are Preview (`target: null`); no custom domain or DNS was changed. Use the preview URL delivered with this revision rather than the old production alias.
