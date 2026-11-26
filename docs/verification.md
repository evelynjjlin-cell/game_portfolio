# V0.1 verification — 26 November 2026

## Implemented and observed

- Real-time Three.js geometry, curved and layered hardcover book, complete front/rear façades, coherent side walls, eight furnished interiors, roof/dormers/attic.
- Front/back navigation and manual side rotation work. A rear room opens and closes to the prior rear viewpoint. A front room opens to its own furnished interior.
- Actual hinged glass doors and shutters visibly rotate from their edge pivots; no empty project dialog appears.
- Daylight/evening changes actual scene lighting; the theme remains readable.
- Contact opens both from the header and the physical mailbox. Correct mailto, LinkedIn, and UX portfolio URLs were inspected. Copy email produces the Copied status. No email was sent.
- The real 3D scene renders at a 390 × 844 viewport with readable navigation and no horizontal page overflow in the observed layout.
- WebGL-unavailable fallback was observed in the cloud browser; About and Contact remain available.
- `npm run build` compiles the production bundle. `npm run check:state` checks interrupted room transitions, rapid reversal, hover isolation, camera-view reset state, and eight unassigned project slots.

## Capture method

Actual running implementation screenshots were captured using Chromium with software WebGL on the development machine, from the pushed source. These are not image-generated concepts. Captures cover front, rear, side, opened front/rear rooms, evening, contact, and a 390 × 844 viewport. They are delivered separately to avoid adding bulky review images to the source repository.

## Limits

- No approved concept image was attached; visual direction follows the detailed written brief.
- Physical iPhone/Android touch and Safari rendering/performance have not been tested. The mobile capture is a resized desktop browser, not a physical handset.
- Software rendering is slower than GPU hardware and cannot substantiate a mobile frame-rate claim. Resolution adapts automatically; hardware benchmarking remains outstanding.
- Decorative lamp/record/plant/attic behaviors are implemented, but have not all been individually timed or exercised on physical devices.
- No real project content, sound, résumé, account, or backend has been introduced. All project fields remain empty.
- The initial Vercel creation labeled its first deployment Production despite the requested target. Subsequent deployments omit that target and are Preview (`target: null`). Main remains the original README commit; no custom domain or DNS was changed. Do not use the old production alias for review; use the final preview URL delivered with the task.
