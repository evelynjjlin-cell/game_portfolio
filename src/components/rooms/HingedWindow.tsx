import { useMemo, useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { Box, Cylinder } from '../house/Primitives';
import { materials } from '../house/materials';
import { archFrameGeometry, extrudeProfile, sashShape } from '../house/ArchShapes';
import type { RoomConfig } from '../../config/rooms';
import { useWorld } from '../../hooks/useWorld';

function GlazedSash({ room, side }: { room: RoomConfig; side: number }) {
  const { width, height, arch, style } = room.opening;
  const w = width - .15, h = height - .15, rise = Math.max(.001, arch - .075);
  const hinge = side * w / 2;
  const sash = useMemo(() => {
    const outer = sashShape(w, h, rise, side);
    const inner = sashShape(w, h, rise, side, .065);
    outer.holes.push(new THREE.Path(inner.getPoints().reverse()));
    const frame = extrudeProfile(outer, .065, .006);
    const glazing = extrudeProfile(inner, .008, 0);
    frame.translate(-hinge, 0, 0);
    glazing.translate(-hinge, 0, .018);
    return { frame, glazing };
  }, [w, h, rise, side, hinge]);
  const timber = style === 'shutter' ? materials.roof : style === 'greenhouse' ? materials.brass : materials.wood;
  const mid = -side * (w / 4 + .006);
  const sashWidth = w / 2 - .035;
  const barY = -h / 2 + (style === 'greenhouse' ? .62 : .7);
  return <group>
    <mesh geometry={sash.frame} material={timber} castShadow receiveShadow />
    <mesh geometry={sash.glazing} material={materials.glass} renderOrder={1} />
    <Box size={[sashWidth - .08, .042, .07]} position={[mid, barY, .025]} material={timber} radius={.008} />
    <Box size={[.03, h - rise - .13, .065]} position={[mid, (-h / 2 + (h / 2 - rise)) / 2, .022]} material={timber} radius={.006} />
    {style !== 'greenhouse' && <group position={[mid, -h / 2 + .29, .025]}>
      <Box size={[sashWidth - .1, .43, .065]} radius={.012} material={timber} />
      <Box size={[sashWidth - .22, .31, .016]} position={[0, 0, .043]} radius={.018} material={style === 'shutter' ? materials.roofEdge : materials.lightWood} />
      <Box size={[sashWidth - .2, .017, .022]} position={[0, -.15, .055]} radius={.004} material={timber} />
    </group>}
    <group position={[-side * (w / 2 - .1), -h / 2 + .88, .085]}>
      <Box size={[.05, .2, .018]} radius={.018} material={materials.brass} />
      <Cylinder radius={.018} height={.115} position={[0, .005, .037]} material={materials.brass} />
      <Cylinder radius={.025} height={.042} position={[0, -.046, .018]} rotation={[Math.PI / 2, 0, 0]} material={materials.brass} />
      <Cylinder radius={.025} height={.042} position={[0, .06, .018]} rotation={[Math.PI / 2, 0, 0]} material={materials.brass} />
    </group>
  </group>;
}

export function HingedWindow({ room }: { room: RoomConfig }) {
  const leaves = useRef<(THREE.Group | null)[]>([]);
  const amount = useRef(0);
  const { width, height, arch, style } = room.opening;
  const frame = useMemo(() => archFrameGeometry(width, height, arch, .075, .14), [width, height, arch]);
  const w = width - .15;
  const hingeYs = [-height / 2 + .23, Math.min(height / 2 - arch - .12, height / 2 - .25)];
  useFrame((_, dt) => {
    const s = useWorld.getState(), phase = s.phases[room.id];
    const target = phase === 'opening' || phase === 'open' ? 1 : 0;
    amount.current = s.reducedMotion ? target : THREE.MathUtils.clamp(amount.current + (target ? 1 : -1) * dt / room.animation.duration, 0, 1);
    const eased = amount.current * amount.current * (3 - 2 * amount.current);
    [-1, 1].forEach((side, index) => {
      const leaf = leaves.current[index];
      // Local +Z is outdoors on both façades. Hinge-first transform keeps every arc physically rigid.
      if (leaf) leaf.rotation.y = side * eased * Math.min(room.animation.angle, Math.PI * .53);
    });
    if (amount.current === target && (phase === 'opening' || phase === 'closing')) s.finish(room.id, target ? 'open' : 'idle');
  });
  const frameMaterial = style === 'greenhouse' ? materials.brass : style === 'shutter' ? materials.roof : materials.darkWood;
  return <group>
    <mesh geometry={frame} position={[0, 0, -.035]} material={frameMaterial} castShadow receiveShadow />
    {[-1, 1].map((side, index) => <group key={side}>
      <group position={[side * w / 2, 0, .205]} ref={el => { leaves.current[index] = el; }}>
        <GlazedSash room={room} side={side} />
      </group>
      {hingeYs.map((y, i) => <group key={i} position={[side * w / 2, y, .205]}>
        <Cylinder radius={.025} height={.14} material={materials.brass} />
        <Cylinder radius={.032} height={.02} position={[0, .076, 0]} material={materials.brass} />
      </group>)}
    </group>)}
  </group>;
}
