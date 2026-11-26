import { useMemo, useRef, useState } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { Box, Cylinder, Beam, Repeated, type Piece } from './Primitives';
import { materials } from './materials';
import { ImportedAsset, ImportedPlant, ImportedLantern } from './ImportedAssets';
import { useSelectable } from '../../hooks/useSelectable';
import { useWorld } from '../../hooks/useWorld';

const bookColors = ['#5f7463', '#a48157', '#9a786a', '#d5c39b', '#506b6c', '#74624e'].map(color => {
  const material = materials.cover.clone(); material.color.set(color); return material;
});
const rugMaterials = ['#a38e71', '#b39781', '#73847d', '#a3a28b'].map(color => {
  const material = materials.fabric.clone(); material.color.set(color); return material;
});

/** Individual stitched spines, reused by both the bookcases and the attic. */
export function LittleBooks({ position = [0, 0, 0] as [number, number, number] }) {
  return <group position={position}>{bookColors.slice(0, 5).map((material, i) => {
    const h = .26 + (i % 3) * .035;
    return <group key={i} position={[i * .092 - .18, 0, 0]} rotation={[0, 0, i === 4 ? -.09 : 0]}>
      <Box size={[.075, h, .18]} position={[0, h / 2, 0]} radius={.008} material={material} />
      <Box size={[.055, h - .025, .15]} position={[0, h / 2, -.013]} radius={.004} material={materials.paper} />
      {[.045, h - .045].map(y => <Box key={y} size={[.06, .009, .007]} position={[0, y, .093]} radius={.003} material={materials.brass} />)}
    </group>;
  })}</group>;
}

export function Plant({ position = [0, 0, 0] as [number, number, number], scale = 1, interactive = false }: {
  position?: [number, number, number]; scale?: number; interactive?: boolean;
}) { return <ImportedPlant position={position} height={.88 * scale} interactive={interactive} />; }

export function Lamp({ position, interactive = true }: { position: [number, number, number]; interactive?: boolean }) {
  return <ImportedLantern position={position} height={.36} interactive={interactive} />;
}

/** Original built-in joinery, with measured bays, moulded cornice and batched books. */
function Bookcase({ width = 1.82, height = 1.63, position = [0, 0, -.8] as [number, number, number], seed = 1 }: {
  width?: number; height?: number; position?: [number, number, number]; seed?: number;
}) {
  const shelves = [.24, .66, 1.08, 1.5].filter(y => y < height);
  const books = useMemo(() => {
    const pieces: Piece[][] = bookColors.map(() => []), bands: Piece[] = [];
    for (let row = 0; row < shelves.length - 1; row++) {
      const count = Math.floor((width - .14) / .095);
      for (let i = 0; i < count; i++) {
        // Small irregular gaps are intentional; the shelving is inhabited, not a solid texture.
        if ((i + row * 3 + seed) % 9 === 0 || (row === 1 && i > count - 4)) continue;
        const h = .245 + ((i * 7 + row * 3 + seed) % 5) * .016;
        const x = -width / 2 + .13 + i * .091;
        const w = .063 + (i % 3) * .007;
        pieces[(i + row + seed) % bookColors.length].push({ position: [x, shelves[row] + .035 + h / 2, .025], scale: [w, h, .19], rotation: [0, 0, i === count - 1 ? -.06 : 0] });
        bands.push({ position: [x, shelves[row] + .08, .124], scale: [w * .7, .008, .008] });
        bands.push({ position: [x, shelves[row] + h - .015, .124], scale: [w * .7, .008, .008] });
      }
    }
    return { pieces, bands };
  }, [width, height, seed]);
  return <group position={position}>
    <Box size={[width, height, .035]} position={[0, height / 2, -.1]} radius={.006} material={materials.darkWood} />
    {[-1, 1].map(side => <group key={side}>
      <Box size={[.065, height, .26]} position={[side * (width / 2 - .03), height / 2, .015]} radius={.012} material={materials.wood} />
      <Box size={[.024, height - .12, .026]} position={[side * (width / 2 - .025), height / 2, .16]} radius={.005} material={materials.lightWood} />
    </group>)}
    {shelves.map(y => <group key={y}><Box size={[width, .055, .28]} position={[0, y, .015]} radius={.009} material={materials.wood} /><Box size={[width, .018, .022]} position={[0, y + .017, .16]} radius={.005} material={materials.lightWood} /></group>)}
    <Box size={[width + .08, .07, .32]} position={[0, height, .025]} radius={.015} material={materials.darkWood} />
    <Box size={[width + .04, .035, .29]} position={[0, height - .053, .018]} radius={.008} material={materials.lightWood} />
    <Box size={[width + .06, .09, .3]} position={[0, .055, .025]} radius={.012} material={materials.wood} />
    <Box size={[width - .12, .12, .035]} position={[0, .16, .12]} radius={.009} material={materials.lightWood} />
    {books.pieces.map((pieces, i) => <Repeated key={i} size={[1, 1, 1]} pieces={pieces} material={bookColors[i]} />)}
    <Repeated size={[1, 1, 1]} pieces={books.bands} material={materials.brass} />
  </group>;
}

function OpenNotebook({ position = [0, 0, 0] as [number, number, number] }) {
  return <group position={position} rotation={[0, -.12, 0]}>
    {[-1, 1].map(side => <group key={side} rotation={[0, 0, side * .035]}>
      <Box size={[.175, .014, .26]} position={[side * .09, .012, 0]} radius={.009} material={materials.cover} />
      <Box size={[.162, .018, .245]} position={[side * .088, .025, -.003]} radius={.005} material={materials.paper} />
    </group>)}
    <Cylinder radius={.007} height={.22} position={[.12, .042, .01]} rotation={[Math.PI / 2, 0, .12]} material={materials.wood} />
  </group>;
}

function Cup({ position }: { position: [number, number, number] }) {
  const profile = useMemo(() => [new THREE.Vector2(.025, 0), new THREE.Vector2(.045, .008), new THREE.Vector2(.055, .08), new THREE.Vector2(.052, .088), new THREE.Vector2(.046, .083), new THREE.Vector2(.038, .015)], []);
  return <group position={position}>
    <Cylinder radius={.085} height={.012} material={materials.cream} />
    <mesh position={[0, .007, 0]} material={materials.cream} castShadow><latheGeometry args={[profile, 20]} /></mesh>
    <mesh position={[.059, .051, 0]} material={materials.cream} castShadow><torusGeometry args={[.023, .006, 8, 18]} /></mesh>
    <Cylinder radius={.043} height={.003} position={[0, .084, 0]} material={materials.darkWood} />
  </group>;
}

function RecordPlayer({ position }: { position: [number, number, number] }) {
  const [playing, setPlaying] = useState(false), record = useRef<THREE.Group>(null);
  const events = useSelectable('Start or stop the record', () => setPlaying(value => !value));
  useFrame((_, dt) => { if (record.current && playing && !useWorld.getState().reducedMotion) record.current.rotation.y += dt * 1.6; });
  return <group position={position} {...events}>
    <Box size={[.58, .085, .37]} radius={.025} material={materials.darkWood} />
    <Box size={[.54, .018, .34]} position={[0, .051, 0]} radius={.014} material={materials.lightWood} />
    <group ref={record} position={[-.06, .068, 0]}>
      <Cylinder radius={.15} height={.008} material={materials.ink} />
      {[.11, .125, .14].map(r => <mesh key={r} rotation={[-Math.PI / 2, 0, 0]} position={[0, .005, 0]} material={materials.darkWood}><torusGeometry args={[r, .0009, 4, 36]} /></mesh>)}
      <Cylinder radius={.043} height={.011} material={bookColors[1]} />
      <Cylinder radius={.008} height={.025} material={materials.brass} />
    </group>
    <Beam from={[.22, .08, -.12]} to={[.07, .09, .09]} width={.013} material={materials.brass} />
    <Cylinder radius={.018} height={.015} position={[.23, .075, .12]} material={materials.brass} />
    <group position={[0, .04, -.18]} rotation={[-1.08, 0, 0]}><Box size={[.58, .025, .36]} position={[0, 0, -.18]} radius={.015} material={materials.wood} /><Box size={[.51, .012, .29]} position={[0, -.017, -.18]} radius={.008} material={materials.darkWood} /></group>
  </group>;
}

function DrawingStand() {
  return <group position={[.47, 0, -.45]}>
    <Beam from={[-.24, .03, .1]} to={[-.13, 1.33, -.07]} width={.035} material={materials.wood} />
    <Beam from={[.24, .03, .1]} to={[.13, 1.33, -.07]} width={.035} material={materials.wood} />
    <Beam from={[0, .03, -.29]} to={[0, 1.24, -.08]} width={.03} material={materials.wood} />
    <Box size={[.6, .5, .03]} position={[0, 1.03, -.015]} rotation={[-.07, 0, 0]} radius={.009} material={materials.lightWood} />
    <Box size={[.5, .4, .009]} position={[0, 1.03, .007]} rotation={[-.07, 0, 0]} radius={.005} material={materials.paper} />
    <Box size={[.67, .045, .09]} position={[0, .76, .03]} radius={.008} material={materials.wood} />
    <Box size={[.08, .06, .03]} position={[0, 1.3, .015]} radius={.006} material={materials.brass} />
    <Beam from={[-.17, .94, .033]} to={[.05, 1.15, .027]} width={.009} material={materials.sage} />
    <Beam from={[.05, 1.15, .027]} to={[.17, .98, .03]} width={.009} material={materials.sage} />
    <Beam from={[-.17, .94, .033]} to={[.17, .94, .033]} width={.009} material={materials.sage} />
  </group>;
}

export function Furniture({ kind }: { kind: 'study' | 'reading' | 'music' | 'atelier' }) {
  const index = ['study', 'reading', 'music', 'atelier'].indexOf(kind);
  return <group>
    <Box size={[1.8, .012, 1.15]} position={[0, .015, -.02]} radius={.045} material={rugMaterials[index]} />
    <Box size={[1.65, .004, 1.02]} position={[0, .024, -.02]} radius={.04} material={materials.cream} />
    <Box size={[1.58, .004, .95]} position={[0, .027, -.02]} radius={.04} material={rugMaterials[index]} />
    {kind === 'study' && <>
      <Bookcase seed={2} />
      <ImportedAsset name="oak-side-table" height={.7} position={[.18, 0, -.37]} />
      <ImportedAsset name="carved-armchair" height={.95} position={[-.55, 0, .18]} rotation={[0, .08, 0]} />
      <OpenNotebook position={[.05, .71, -.33]} /><ImportedLantern height={.29} position={[.6, .705, -.4]} />
      <Cup position={[.4, .709, -.15]} />
    </>}
    {kind === 'reading' && <>
      <Bookcase seed={4} />
      <ImportedAsset name="carved-armchair" height={1.05} position={[-.35, 0, .12]} rotation={[0, .08, 0]} />
      <ImportedAsset name="oak-side-table" height={.48} position={[.65, 0, .1]} />
      <ImportedLantern height={.34} position={[.72, .485, .08]} /><Cup position={[.43, .492, .15]} />
      <ImportedPlant height={.46} position={[.76, 0, -.42]} />
    </>}
    {kind === 'music' && <>
      <Bookcase seed={7} />
      <ImportedAsset name="carved-armchair" height={.99} position={[.48, 0, .14]} rotation={[0, -.08, 0]} />
      <ImportedAsset name="oak-side-table" height={.61} position={[-.58, 0, -.22]} />
      <RecordPlayer position={[-.58, .66, -.2]} />
      <ImportedLantern height={.37} position={[-.85, 0, .35]} />
    </>}
    {kind === 'atelier' && <>
      <Bookcase width={.86} height={1.54} position={[-.51, 0, -.8]} seed={3} />
      <DrawingStand />
      <ImportedAsset name="carved-armchair" height={.94} position={[-.48, 0, .13]} rotation={[0, .1, 0]} />
      <ImportedAsset name="oak-side-table" height={.48} position={[.56, 0, .15]} />
      <OpenNotebook position={[.47, .488, .15]} /><ImportedLantern height={.27} position={[.84, .485, .12]} />
    </>}
  </group>;
}
