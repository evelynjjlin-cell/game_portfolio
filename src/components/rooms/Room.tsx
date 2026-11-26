import { useMemo, useRef } from 'react';
import { useFrame, useLoader } from '@react-three/fiber';
import { useGLTF } from '@react-three/drei';
import * as THREE from 'three';
import { useWorld } from '../../hooks/useWorld';
import { useSelectable } from '../../hooks/useSelectable';
import { rooms, type RoomConfig } from '../../config/rooms';
import { ArchitecturalJoinery } from './ArchitecturalJoinery';
import { Box } from '../house/Primitives';
import { extrudeProfile, archShape } from '../house/ArchShapes';
import { materials } from '../house/materials';

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

/** Floor-origin Blender interiors: +Y up, the facade at Z=0, depth into -Z. */
function useInterior(kind: RoomConfig['kind']) {
  const {scene} = useGLTF(`/assets/interiors/${kind}.glb`, false, true);
  return useMemo(() => {
    const copy = scene.clone(true), lamps: THREE.MeshStandardMaterial[] = [];
    const localMaterials = new Map<THREE.Material, THREE.Material>();
    copy.traverse(object => {
      if (!(object instanceof THREE.Mesh)) return;
      object.castShadow = object.receiveShadow = true;
      const normalize = (source: THREE.Material) => {
        let material = localMaterials.get(source);
        if (!material) {
          const next = source.clone() as THREE.MeshStandardMaterial;
          next.envMapIntensity = .42;
          if (next.map) next.map.anisotropy = 4;
          if (/^emissive_/i.test(source.name)) lamps.push(next);
          if (next.transparent) next.depthWrite = false;
          localMaterials.set(source, next); material = next;
        }
        return material;
      };
      object.material = Array.isArray(object.material) ? object.material.map(normalize) : normalize(object.material);
    });
    return {scene:copy, lamps, record:copy.getObjectByName('RecordPlatter'), gear:copy.getObjectByName('WorkshopGear')};
  }, [scene]);
}

export function Room({ room }: { room: RoomConfig }) {
  const model = useInterior(room.kind);
  const metadata = useLoader(THREE.FileLoader, `/assets/interiors/${room.kind}-metadata.json`) as string;
  const fixtures = useMemo(()=>JSON.parse(metadata).lights as {name:string;position:[number,number,number];color:string;intensity:number}[],[metadata]);
  const lights = useRef<(THREE.PointLight|null)[]>([]);
  const fill = useRef<THREE.PointLight>(null);
  const {width,height,arch} = room.opening;
  const hitSurface = useMemo(() => new THREE.ShapeGeometry(archShape(width-.08,height-.06,arch),48), [width,height,arch]);
  const select = useSelectable(`Open the ${room.label.toLowerCase()}`, () => useWorld.getState().selectRoom(room.id), over => useWorld.getState().hover(over ? room.id : null));
  useFrame((_, dt) => {
    const s = useWorld.getState(), phase = s.phases[room.id];
    const active = phase==='open'||phase==='opening';
    const level = active ? room.lighting.open : phase==='focused' ? room.lighting.focused : room.lighting.idle;
    const intensity = level * (s.evening ? 1.22 : 1);
    lights.current.forEach((light,i)=>{if(light) light.intensity=THREE.MathUtils.damp(light.intensity,fixtures[i].intensity*(active?1.8:phase==='focused'?1.35:1)*(s.evening?1.2:1),s.reducedMotion?1000:7,dt);});
    if(fill.current) fill.current.intensity=THREE.MathUtils.damp(fill.current.intensity,intensity*.34,s.reducedMotion?1000:7,dt);
    model.lamps.forEach(lamp=>{lamp.emissiveIntensity=THREE.MathUtils.damp(lamp.emissiveIntensity,active?1.3:phase==='focused'?1.0:.68,s.reducedMotion?1000:7,dt);});
    if(active&&!s.reducedMotion){if(model.record)model.record.rotation.y+=dt*.65;if(model.gear)model.gear.rotation.z+=dt*.19;}
  });
  return <group position={room.position} rotation={[0,room.orientation,0]} {...select}>
    <group position={[0,-height/2,0]}><primitive object={model.scene} dispose={null}/></group>
    <ArchitecturalJoinery room={room}/>
    {/* Only the visible, front-facing aperture is selectable. Solid architecture blocks it. */}
    <mesh geometry={hitSurface} position={[0,0,.165]} name={room.entranceMesh} userData={{noAO:true}}>
      <meshBasicMaterial transparent opacity={0} depthWrite={false} colorWrite={false} side={THREE.FrontSide}/>
    </mesh>
    <group position={[0,-height/2,0]}>{fixtures.map((fixture,i)=><pointLight key={fixture.name} ref={value=>{lights.current[i]=value;}} position={fixture.position} color={fixture.color} intensity={fixture.intensity} distance={room.depth+1.1} decay={2}/>)}</group>
    <pointLight ref={fill} position={[0,.15,-.32]} color={room.lighting.color} intensity={room.lighting.idle*.34} distance={room.depth+1} decay={2}/>
  </group>;
}

for(const room of rooms){useGLTF.preload(`/assets/interiors/${room.kind}.glb`,false,true);useLoader.preload(THREE.FileLoader,`/assets/interiors/${room.kind}-metadata.json`);}
