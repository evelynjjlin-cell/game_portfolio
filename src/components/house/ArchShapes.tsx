import * as THREE from 'three';

/** Exact façade aperture: centered bounding box, elliptical crown above the spring line. */
export function archShape(width: number, height: number, rise: number): THREE.Shape {
  const radius = width / 2;
  const crown = Math.max(.001, Math.min(rise, height));
  const spring = height / 2 - crown;
  const shape = new THREE.Shape();
  shape.moveTo(-radius, -height / 2);
  shape.lineTo(radius, -height / 2);
  shape.lineTo(radius, spring);
  shape.absellipse(0, spring, radius, crown, 0, Math.PI, false, 0);
  shape.lineTo(-radius, -height / 2);
  shape.closePath();
  return shape;
}

export function extrudeProfile(shape: THREE.Shape, depth = .08, bevel = .008) {
  return new THREE.ExtrudeGeometry(shape, {
    depth, steps: 1, curveSegments: 24, bevelEnabled: bevel > 0,
    bevelThickness: bevel, bevelSize: bevel, bevelSegments: 2,
  });
}

/** Ring inset into an aperture; the crown and straight jambs share one profile. */
export function archFrameGeometry(width: number, height: number, rise: number, thickness: number, depth: number) {
  const outer = archShape(width, height, rise);
  const inner = archShape(width - thickness * 2, height - thickness * 2, Math.max(.001, rise - thickness));
  outer.holes.push(new THREE.Path(inner.getPoints(40).reverse()));
  return extrudeProfile(outer, depth, .008);
}

/** A half arched sash, with a little center clearance for independent hinge rotation. */
export function sashShape(width: number, height: number, rise: number, side: number, inset = 0) {
  const r = width / 2 - inset;
  const ry = Math.max(.001, rise - inset);
  const spring = height / 2 - rise;
  const bottom = -height / 2 + inset;
  const center = .012 + inset;
  const points: THREE.Vector2[] = [];
  if (side < 0) {
    points.push(new THREE.Vector2(-r, bottom), new THREE.Vector2(-center, bottom));
    const theta = Math.acos(-center / r);
    for (let i = 0; i <= 28; i++) {
      const angle = theta + (Math.PI - theta) * i / 28;
      points.push(new THREE.Vector2(r * Math.cos(angle), spring + ry * Math.sin(angle)));
    }
  } else {
    points.push(new THREE.Vector2(center, bottom), new THREE.Vector2(r, bottom));
    const theta = Math.acos(center / r);
    for (let i = 0; i <= 28; i++) {
      const angle = theta * i / 28;
      points.push(new THREE.Vector2(r * Math.cos(angle), spring + ry * Math.sin(angle)));
    }
  }
  const shape = new THREE.Shape(points);
  shape.closePath();
  return shape;
}
