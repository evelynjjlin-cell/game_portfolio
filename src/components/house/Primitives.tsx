import { useLayoutEffect, useMemo, useRef } from 'react';
import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/examples/jsm/geometries/RoundedBoxGeometry.js';
import type { ThreeElements } from '@react-three/fiber';
import { materials } from './materials';
const boxes=new Map<string,THREE.BufferGeometry>();
export function boxGeometry(size:[number,number,number],radius=.025,segments=2){const key=[...size,radius,segments].join(':');if(!boxes.has(key))boxes.set(key,new RoundedBoxGeometry(...size,segments,Math.min(radius,Math.min(...size)/3)));return boxes.get(key)!;}
type BoxProps=Omit<ThreeElements['mesh'],'args'> & {size:[number,number,number]; radius?:number};
export function Box({size,radius=.025,material=materials.wood,...props}:BoxProps){return <mesh castShadow receiveShadow geometry={boxGeometry(size,radius)} material={material} {...props}/>;}
export function Cylinder({radius=.1,height=.1,top,material=materials.brass,...props}:{radius?:number;height?:number;top?:number}&Omit<ThreeElements['mesh'],'args'>){return <mesh castShadow receiveShadow material={material} {...props}><cylinderGeometry args={[top??radius,radius,height,20]}/></mesh>;}
export function Ball({scale=[1,1,1],material=materials.leaf,...props}:ThreeElements['mesh']){return <mesh castShadow receiveShadow material={material} scale={scale} {...props}><sphereGeometry args={[1,16,12]}/></mesh>;}
export function Beam({from,to,width=.06,material=materials.trim}:{from:[number,number,number];to:[number,number,number];width?:number;material?:THREE.Material}){const a=new THREE.Vector3(...from),b=new THREE.Vector3(...to),mid=a.clone().add(b).multiplyScalar(.5),q=new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0,1,0),b.sub(a).normalize());return <Box size={[width,new THREE.Vector3(...from).distanceTo(new THREE.Vector3(...to)),width]} position={mid} quaternion={q} material={material}/>;}
export type Piece={position:[number,number,number];rotation?:[number,number,number];scale?:[number,number,number]};
/** Repeated slate tiles, floorboards, and paper strata share one draw call each. */
export function Repeated({size,pieces,material}:{size:[number,number,number];pieces:Piece[];material:THREE.Material}){const ref=useRef<THREE.InstancedMesh>(null);const geometry=useMemo(()=>boxGeometry(size,.012,1),[...size]);useLayoutEffect(()=>{const dummy=new THREE.Object3D();pieces.forEach((p,i)=>{dummy.position.set(...p.position);dummy.rotation.set(...(p.rotation??[0,0,0]));dummy.scale.set(...(p.scale??[1,1,1]));dummy.updateMatrix();ref.current!.setMatrixAt(i,dummy.matrix);});ref.current!.instanceMatrix.needsUpdate=true;ref.current!.computeBoundingSphere();},[pieces]);return <instancedMesh ref={ref} args={[geometry,material,pieces.length]} castShadow receiveShadow/>;}
