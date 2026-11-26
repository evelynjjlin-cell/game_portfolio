import { Suspense, useMemo, useRef, useState } from 'react';
import { useGLTF } from '@react-three/drei';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { useSelectable } from '../../hooks/useSelectable';
import { useWorld } from '../../hooks/useWorld';

/** Human-made, CC0 individual props. Source, artists and processing: ASSET_CREDITS.md.
 * All files are floor-centred, +Y up, and one unit high. Repeated instances share
 * GPU geometry/textures; no runtime dependency on an external asset service.
 */
export type ImportedAssetName = 'potted-plant' | 'carved-armchair' | 'oak-side-table' | 'wooden-lantern';
type TransformProps = { position?: [number, number, number]; rotation?: [number, number, number]; height?: number };
const normalized = new Map<ImportedAssetName, THREE.Group>();
function PreparedAsset({ name }: { name: ImportedAssetName }) {
  const { scene } = useGLTF(`/assets/models/${name}.glb`);
  const instance = useMemo(() => {
    let prototype = normalized.get(name);
    if (!prototype) {
      prototype = scene.clone(true);
      const materials = new Map<THREE.Material, THREE.Material>();
      prototype.traverse(object => {
        if (!(object instanceof THREE.Mesh)) return;
        object.castShadow = name !== 'potted-plant';
        object.receiveShadow = true;
        const prepare = (original: THREE.Material) => {
          if (materials.has(original)) return materials.get(original)!;
          const material = original.clone() as THREE.MeshStandardMaterial;
          material.envMapIntensity = .3;
          material.roughness = Math.max(.6, material.roughness);
          if (material.normalScale) material.normalScale.multiplyScalar(.6);
          if (material.map) material.map.anisotropy = 4;
          if(name === 'carved-armchair' && /fabric|cloth|cushion/i.test(material.name)) material.color.set('#e7d9bb');
          if (name === 'potted-plant' && /leaves/.test(material.name)) {
            material.side = THREE.DoubleSide;
            material.alphaTest = .42;
            material.transparent = false;
            material.color.set('#d5ddc5');
          }
          if (name === 'wooden-lantern' && /glass/.test(material.name)) {
            material.transparent = true;
            material.opacity = .13;
            material.depthWrite = false;
            material.color.set('#e3d6bc');
            material.roughness = .3;
          }
          materials.set(original, material);
          return material;
        };
        object.material = Array.isArray(object.material) ? object.material.map(prepare) : prepare(object.material);
      });
      normalized.set(name, prototype);
    }
    return prototype.clone(true);
  }, [name, scene]);
  return <primitive object={instance} dispose={null} />;
}
export function ImportedAsset({ name, height = 1, position, rotation }: TransformProps & { name: ImportedAssetName }) {
  return <group position={position} rotation={rotation} scale={height}><Suspense fallback={null}><PreparedAsset name={name} /></Suspense></group>;
}
export function ImportedPlant({ height = .75, position, rotation, interactive = false }: TransformProps & { interactive?: boolean }) {
  const group = useRef<THREE.Group>(null);
  const motion = useRef(0);
  const events = useSelectable('A little rustle', () => { motion.current = 2.2; });
  useFrame((_, dt) => {
    if (!group.current || motion.current <= 0) return;
    motion.current = Math.max(0, motion.current - dt * 2);
    const leaves = group.current.getObjectByName('potted_plant_02_leaves');
    if (leaves) leaves.rotation.z = useWorld.getState().reducedMotion ? 0 : Math.sin(motion.current * 12) * motion.current * .018;
  });
  return <group ref={group} {...(interactive ? events : {})}><ImportedAsset name="potted-plant" height={height} position={position} rotation={rotation}/></group>;
}
export function ImportedLantern({ height = .46, position, rotation, interactive = true, active = false, hovered = false }: TransformProps & { interactive?: boolean; active?: boolean; hovered?: boolean }) {
  const [on, setOn] = useState(true);
  const light = useRef<THREE.PointLight>(null);
  const glow = useRef<THREE.MeshStandardMaterial>(null);
  const events = useSelectable('Switch the lantern', () => setOn(value => !value));
  const evening = useWorld(s => s.evening);
  useFrame((_, dt) => {
    const target = on ? (active ? 1.8 : hovered ? 1.25 : evening ? .9 : .38) : 0;
    if (light.current) light.current.intensity = THREE.MathUtils.damp(light.current.intensity, target, 5, dt);
    if (glow.current) glow.current.emissiveIntensity = THREE.MathUtils.damp(glow.current.emissiveIntensity, target * 1.6, 5, dt);
  });
  return <group position={position} rotation={rotation} {...(interactive ? events : {})}>
    <ImportedAsset name="wooden-lantern" height={height}/>
    <mesh position={[0, height * .33, 0]} scale={[height * .037, height * .065, height * .037]}>
      <sphereGeometry args={[1, 8, 8]}/><meshStandardMaterial ref={glow} color="#ffe1b0" emissive="#ffbe6a" emissiveIntensity={1.2}/>
    </mesh>
    <pointLight ref={light} position={[0, height * .4, 0]} color="#ffc27d" intensity={.38} distance={height * 5} decay={2}/>
  </group>;
}
