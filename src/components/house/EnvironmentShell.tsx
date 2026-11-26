import { useMemo } from 'react';
import { useGLTF } from '@react-three/drei';
import * as THREE from 'three';

/** Original Blender-built architectural shell. Source: scripts/environment/build_architecture.py.
 * Static pieces are consolidated into seventeen material meshes; window leaves and rooms
 * stay separate so their authored interaction pivots are independent of the architecture.
 */
export function EnvironmentShell() {
  const { scene } = useGLTF('/assets/environment/house-shell.glb');
  const shell = useMemo(() => {
    const copy = scene.clone(true);
    copy.traverse(object => {
      if (!(object instanceof THREE.Mesh)) return;
      const materials = Array.isArray(object.material) ? object.material : [object.material];
      const glazing = materials.some(material => /Conservatory glass/.test(material.name));
      object.castShadow = !glazing;
      object.receiveShadow = !glazing;
      for (const material of materials) {
        if (!(material instanceof THREE.MeshStandardMaterial)) continue;
        material.envMapIntensity = .35;
        if (material.map) material.map.anisotropy = 4;
        if (glazing) {
          material.transparent = true;
          material.opacity = .13;
          material.depthWrite = false;
          material.side = THREE.DoubleSide;
        }
      }
    });
    return copy;
  }, [scene]);
  return <primitive object={shell} dispose={null}/>;
}

useGLTF.preload('/assets/environment/house-shell.glb');
