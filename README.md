# Evelyn Lin — a miniature world

A real-time 3D portfolio foundation: a furnished, double-sided house on a curved open book. No case studies are assigned in V0.1.

## Develop

Node 24 LTS is recommended.

```sh
npm ci
npm run dev
npm run build
```

Built with React, TypeScript, Vite, Three.js, React Three Fiber, Drei, and Zustand. Versions are locked in `package-lock.json`. No authentication, backend, analytics, paid API, remote textures, or temporary asset URLs are required.

## Explore

- Drag to orbit the whole house; wheel / pinch to zoom. Vertical orbit and distance limits keep the camera outside the model.
- Front, Back, and Reset follow a smooth arc around the house.
- Click a visible room window to open its two glass doors and hinged shutters. Close room / Escape reverses the animation and returns to the saved viewing angle. Selecting another room closes the previous room.
- Open the front or rear entrance for About; open the mailbox for Contact. Header shortcuts always provide the same information.
- Click a desk lamp, record player, plant, or attic mobile for a small environmental interaction. The record is silent; no sound autoplays.
- Use Explore for keyboard-accessible room selection. Dialogs trap focus, restore it on close, and support Escape. Reduced motion is respected.
- The sun/moon control changes actual scene illumination. Low frame rate reduces rendering resolution; only one light casts dynamic shadows.
- If WebGL cannot start, the header and contact interface remain usable.

## Structure

- `src/config/profile.ts`: all verified biography and contact information.
- `src/config/rooms.ts`: eight stable room IDs, physical locations, animation, camera, light, and future content configuration.
- `src/config/lighting.ts`: daylight and evening settings.
- `src/components/house/`: architecture, swept book geometry, reusable geometry, procedural surface maps, furnishings.
- `src/components/rooms/`: independently hinged window panels / shutters and local lighting.
- `src/components/camera/`: spherical camera transitions that never take a shortcut through the building.
- `src/hooks/useWorld.ts`: reversible room lifecycle and interface state.
- `src/hooks/useSelectable.ts`: visible-mesh pointer selection with a drag threshold.
- `src/components/interactions/`: mailbox, entrance, attic mechanism.
- `src/components/case-study/`: inactive, reusable real-content renderer.

All models are procedural TypeScript geometry. No GLB is needed. Shared box geometry/materials and instanced slate tiles, floorboards, and paper strata keep these assets small and reproducible. The material maps use seeded local texture data. The written art direction is the available reference; no reference image was attached to this task.

## Assign a future project

1. Choose an existing stable ID in `src/config/rooms.ts`.
2. Fill `project.title`, `description`, `contentRef`, and optionally `route` / `prototypeUrl` with verified content.
3. Add the corresponding entry to `caseStudyContent` in `src/components/case-study/CaseStudy.tsx`. It supports overview, role, game mechanics, player experience, research, process, prototypes, iteration, media, outcomes, and reflection.
4. Set `availability: 'published'`. The interface only appears after the room finishes opening and its content exists.
5. Keep images/video in `public/` or a permanent user-owned service. Do not use temporary chat assets.

All V0.1 project fields are empty, and all rooms remain `unassigned`. No empty case-study modal appears.

## Deployment and scope

Repository: `evelynjjlin-cell/game_portfolio`

Implementation branch: `feat/interactive-3d-house-foundation`

Vercel project: `game-portfolio` in team `evelyn-lin`; Vite build, `dist` output. Main contains only the initial README and must remain separate until Evelyn approves the preview. No changes to other repositories, existing websites, custom domains, or DNS.

Development indexing is disabled in HTML, `public/robots.txt`, and `vercel.json` response headers. Remove these intentionally only when approved for public indexing.

## Verification

Production compilation is run after each pushed phase. Final checks and actual implementation captures are documented in `docs/verification.md` when available. A browser without WebGL can verify only the accessible fallback, not the 3D scene; never confuse that with a successful visual check.
