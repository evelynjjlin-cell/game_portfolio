import { useMemo, useRef } from 'react';
import { useGLTF } from '@react-three/drei';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import type { RoomConfig } from '../../config/rooms';
import { useWorld } from '../../hooks/useWorld';
import { useSelectable } from '../../hooks/useSelectable';

/** Original Blender-authored joinery. No frame/panel geometry is rebuilt at runtime. */
const sharedMaterials = new Map<string, THREE.Material>();
function useJoineryAsset(id: string) {
  const { scene } = useGLTF(`/assets/environment/joinery/${id}.glb`);
  return useMemo(() => {
    const copy = scene.clone(true);
    copy.traverse(object => {
      if (!(object instanceof THREE.Mesh)) return;
      object.castShadow = true; object.receiveShadow = true;
      const normalize = (source: THREE.Material) => {
        // Static/material identity is retained across all facade instances.
        const key = source.name;
        let material = sharedMaterials.get(key);
        if (!material) {
          const next = source.clone() as THREE.MeshStandardMaterial;
          next.envMapIntensity = .45;
          if (next.map) next.map.anisotropy = 4;
          if (/glass/i.test(key)) {
            next.transparent = true; next.opacity = .12; next.depthWrite = false;
            next.side = THREE.DoubleSide; next.roughness = .14; next.metalness = .04;
          }
          material = next; sharedMaterials.set(key, next);
        }
        return material;
      };
      object.material = Array.isArray(object.material) ? object.material.map(normalize) : normalize(object.material);
      if (Array.isArray(object.material) ? object.material.some(m => /glass/i.test(m.name)) : /glass/i.test(object.material.name)) object.castShadow = false;
    });
    return {scene: copy, left: copy.getObjectByName('hinge_left'), right: copy.getObjectByName('hinge_right')};
  }, [scene]);
}

export function ArchitecturalJoinery({ room }: { room: RoomConfig }) {
  const model = useJoineryAsset(room.id), progress = useRef(0);
  useFrame((_, delta) => {
    const state = useWorld.getState(), phase = state.phases[room.id];
    const target = phase === 'opening' || phase === 'open' ? 1 : 0;
    progress.current = state.reducedMotion ? target : THREE.MathUtils.clamp(progress.current + (target ? 1 : -1) * delta / room.animation.duration, 0, 1);
    const eased = progress.current * progress.current * (3 - 2 * progress.current);
    const inward = room.hinge === 'inward';
    const angle = Math.min(room.animation.angle, inward ? 1.47 : 1.62) * eased * (inward ? -1 : 1);
    if (model.left) model.left.rotation.y = -angle;
    if (model.right) model.right.rotation.y = angle;
    if (progress.current === target && (phase === 'opening' || phase === 'closing')) state.finish(room.id, target ? 'open' : 'idle');
  });
  return <primitive object={model.scene} dispose={null} />;
}

/** Kept independent from room selection: the two architectural house doors open About. */
export function AboutJoinery({ back = false }: { back?: boolean }) {
  const model = useJoineryAsset(back ? 'about-back' : 'about-front');
  const events = useSelectable('Come in · About Evelyn', () => useWorld.getState().openDialog('about'));
  useFrame((_, delta) => {
    const state = useWorld.getState();
    if (model.left) model.left.rotation.y = THREE.MathUtils.damp(model.left.rotation.y, state.dialog === 'about' ? -1.38 : 0, state.reducedMotion ? 1000 : 6, delta);
  });
  return <group position={back ? [0,2.12,-3.24] : [3.8,2.12,3.24]} rotation={[0,back?Math.PI:0,0]} {...events}><primitive object={model.scene} dispose={null}/></group>;
}

export function preloadJoinery() {
  for (const facade of ['front','back']) for(let i=1;i<=4;i++) useGLTF.preload(`/assets/environment/joinery/${facade}-room-0${i}.glb`);
  useGLTF.preload('/assets/environment/joinery/about-front.glb');
  useGLTF.preload('/assets/environment/joinery/about-back.glb');
}
