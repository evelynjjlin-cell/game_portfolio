import {useEffect,useMemo} from 'react';
import {useFrame,useThree} from '@react-three/fiber';
import * as THREE from 'three';
import {EffectComposer} from 'three/addons/postprocessing/EffectComposer.js';
import {RenderPass} from 'three/addons/postprocessing/RenderPass.js';
import {SSAOPass} from 'three/addons/postprocessing/SSAOPass.js';
import {OutputPass} from 'three/addons/postprocessing/OutputPass.js';

/** Glass and invisible entrance targets must never become opaque AO occluders. */
class ArchitecturalAO extends SSAOPass {
 render(renderer:THREE.WebGLRenderer,write:THREE.WebGLRenderTarget,read:THREE.WebGLRenderTarget,delta:number,mask:boolean){
  const hidden:THREE.Object3D[]=[];
  this.scene.traverse(o=>{if(o instanceof THREE.Mesh&&o.visible){const ms=Array.isArray(o.material)?o.material:[o.material];if(o.userData.noAO||ms.every(m=>m.transparent)){hidden.push(o);o.visible=false;}}});
  try {super.render(renderer,write,read,delta,mask);} finally {hidden.forEach(o=>{o.visible=true;});}
 }
}
export function AmbientOcclusion(){
 const {gl,scene,camera,size,viewport}=useThree();
 const pipeline=useMemo(()=>{
  const target=new THREE.WebGLRenderTarget(1,1,{type:THREE.HalfFloatType,samples:0});
  const composer=new EffectComposer(gl,target);
  const beauty=new RenderPass(scene,camera),ao=new ArchitecturalAO(scene,camera,256,256,12),output=new OutputPass();
  ao.kernelRadius=.24;ao.minDistance=.0006;ao.maxDistance=.045;
  composer.addPass(beauty);composer.addPass(ao);composer.addPass(output);
  return{composer,beauty,ao,output};
 },[gl,scene,camera]);
 useEffect(()=>{pipeline.composer.setPixelRatio(viewport.dpr);pipeline.composer.setSize(size.width,size.height);pipeline.ao.setSize(Math.max(1,Math.floor(size.width*viewport.dpr*.65)),Math.max(1,Math.floor(size.height*viewport.dpr*.65)));},[pipeline,size.width,size.height,viewport.dpr]);
 useEffect(()=>()=>{pipeline.composer.dispose();pipeline.ao.dispose();pipeline.output.dispose();},[pipeline]);
 useFrame((_,delta)=>{
  pipeline.ao.ssaoMaterial.uniforms.cameraProjectionMatrix.value.copy(camera.projectionMatrix);
  pipeline.ao.ssaoMaterial.uniforms.cameraInverseProjectionMatrix.value.copy(camera.projectionMatrixInverse);
  pipeline.composer.render(delta);
 },1);
 return null;
}
