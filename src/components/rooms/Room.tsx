import { useMemo, useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { useWorld } from '../../hooks/useWorld';
import { useSelectable } from '../../hooks/useSelectable';
import { HingedWindow } from './HingedWindow';
import type { RoomConfig } from '../../config/rooms';
import { Box, Cylinder, Repeated, type Piece } from '../house/Primitives';
import { extrudeProfile } from '../house/ArchShapes';
import { materials, colored } from '../house/materials';
import { Furniture } from '../house/Furniture';

export function StoneSurround({ width, height, rise }: { width: number; height: number; rise: number }) {
  const crown = useMemo(() => Array.from({ length: 11 }, (_, i) => {
    const a = i / 11 * Math.PI + .008, b = (i + 1) / 11 * Math.PI - .008;
    const r = width / 2 + .018, outer = r + .19, ry = rise + .018;
    const center = height / 2 - rise;
    const path = new THREE.Shape();
    path.moveTo(r * Math.cos(a), center + ry * Math.sin(a));
    path.absellipse(0, center, r, ry, a, b, false, 0);
    path.lineTo(outer * Math.cos(b), center + (ry + .19) * Math.sin(b));
    path.absellipse(0, center, outer, ry + .19, b, a, true, 0);
    path.closePath();
    return extrudeProfile(path, .16 + (i === 5 ? .025 : 0), .012);
  }), [width, height, rise]);
  const jambHeight = height - rise;
  const rows = Math.max(3, Math.round(jambHeight / .28));
  const stones = useMemo(() => [.96, 1.02, 1].map(value => {
    const m = materials.trim.clone(); m.color.multiplyScalar(value); return m;
  }), []);
  return <group position={[0, 0, -.012]}>
    {crown.map((geometry, i) => <mesh key={i} geometry={geometry} material={stones[i % 3]} castShadow receiveShadow />)}
    {[-1, 1].flatMap(side => Array.from({ length: rows }, (_, i) =>
      <Box key={`${side}-${i}`} size={[.19, jambHeight / rows - .018, .17]} radius={.012}
        position={[side * (width / 2 + .115), -height / 2 + jambHeight / rows * (i + .5), .07]}
        material={stones[(i + (side > 0 ? 1 : 0)) % 3]} />))}
  </group>;
}

export function Room({ room }: { room: RoomConfig }) {
  const light = useRef<THREE.PointLight>(null);
  const bulb = useRef<THREE.MeshStandardMaterial>(null);
  const { width, height, arch, style } = room.opening;
  const depth = room.depth;
  const select = useSelectable(`Open the ${room.label.toLowerCase()}`, () => useWorld.getState().selectRoom(room.id), over => useWorld.getState().hover(over ? room.id : null));
  useFrame((_, dt) => {
    const s = useWorld.getState(), phase = s.phases[room.id];
    const target = phase === 'open' || phase === 'opening' ? room.lighting.open : phase === 'focused' ? room.lighting.focused : room.lighting.idle;
    const intensity = target * (s.evening ? 1.25 : 1);
    if (light.current) light.current.intensity = THREE.MathUtils.damp(light.current.intensity, intensity, s.reducedMotion ? 1000 : 6, dt);
    if (bulb.current) bulb.current.emissiveIntensity = THREE.MathUtils.damp(bulb.current.emissiveIntensity, .5 + intensity * .18, s.reducedMotion ? 1000 : 6, dt);
  });
  const wall = useMemo(() => colored(room.wall), [room.wall]);
  const boards = useMemo(() => Array.from({ length: 9 }, (_, i) => ({ position: [-width / 2 + width / 9 * (i + .5), -height / 2 + .025, -depth / 2] } as Piece)), [width, height, depth]);
  const sill = style === 'greenhouse' ? materials.darkWood : materials.trim;
  return <group position={room.position} rotation={[0, room.facade === 'back' ? Math.PI : 0, 0]} {...select}>
    <Box size={[width + .06, height + .1, .08]} position={[0, 0, -depth]} material={wall} />
    <Box size={[width + .06, .09, depth]} position={[0, height / 2 + .03, -depth / 2]} material={style === 'greenhouse' ? materials.glass : materials.cream} castShadow={style !== 'greenhouse'} />
    {[-1, 1].map(side => <group key={side}>
      <Box size={[.07, height, depth]} position={[side * width / 2, 0, -depth / 2]} material={style === 'greenhouse' ? materials.glass : wall} castShadow={style !== 'greenhouse'} />
      {style === 'greenhouse' && <>
        {[.02, depth / 2, depth - .02].map(z => <Box key={z} size={[.045, height, .045]} position={[side * width / 2, 0, -z]} material={materials.brass} radius={.007} />)}
        {[-height / 2 + .1, -.15, height / 2 - .07].map(y => <Box key={y} size={[.045, .045, depth]} position={[side * width / 2, y, -depth / 2]} material={materials.brass} radius={.007} />)}
      </>}
      <Box size={[.035, .13, depth]} position={[side * (width / 2 - .047), -height / 2 + .1, -depth / 2]} material={materials.darkWood} radius={.006} />
    </group>)}
    <Repeated size={[width / 9 - .008, .045, depth]} pieces={boards} material={materials.lightWood} />
    <Box size={[width - .08, .13, .035]} position={[0, -height / 2 + .1, -depth + .055]} material={materials.darkWood} radius={.006} />
    <group position={[0, -height / 2 + .06, -depth * .43]}>
      <Furniture kind={room.furniture} />
    </group>
    {style !== 'greenhouse' && <StoneSurround width={width} height={height} rise={arch} />}
    <Box size={[width + (style === 'greenhouse' ? .12 : .48), .12, .43]} position={[0, -height / 2 - .075, .085]} material={sill} radius={.025} />
    <Box size={[width + .23, .025, .48]} position={[0, -height / 2 - .012, .075]} material={sill} radius={.009} />
    <HingedWindow room={room} />
    <group position={[width * .12, height / 2 - .34, -depth * .5]}>
      <Cylinder radius={.012} height={.32} position={[0, .14, 0]} material={materials.brass} />
      <Cylinder radius={.055} height={.035} position={[0, .3, 0]} material={materials.brass} />
      <mesh position={[0, -.035, 0]} castShadow><coneGeometry args={[.19, .18, 24, 1, true]} /><meshStandardMaterial color="#b99b66" metalness={.65} roughness={.4} side={THREE.DoubleSide} /></mesh>
      <mesh position={[0, -.08, 0]}><sphereGeometry args={[.07, 16, 10]} /><meshStandardMaterial ref={bulb} color="#ffe2af" emissive="#ffb95f" emissiveIntensity={.8} /></mesh>
    </group>
    <pointLight ref={light} position={[0, height / 2 - .62, -depth * .52]} color={room.lighting.color} intensity={room.lighting.idle} distance={depth + 1.65} decay={2} />
  </group>;
}
