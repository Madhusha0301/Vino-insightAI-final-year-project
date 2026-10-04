import React, { useRef, useMemo, Suspense } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, ContactShadows, Float } from '@react-three/drei';
import * as THREE from 'three';

/**
 * Realistic procedural 3D wine bottle — built entirely from a lathed
 * silhouette (THREE.LatheGeometry), not a flat primitive stack, so it
 * has the true curved shoulder/neck profile of a real Bordeaux-style
 * bottle. A hand-drawn canvas texture is used for the label so it reads
 * like a genuine product label rather than a flat color swatch.
 * No external photo/model files are used — everything is generated at
 * runtime, which keeps the project dependency-free and fully original work.
 */

// Bottle silhouette: [radius, height] pairs from base to top of neck.
const PROFILE = [
  [0.001, 0.00], [0.60, 0.00], [0.62, 0.04], [0.62, 0.10],
  [0.60, 1.00], [0.60, 1.55], [0.55, 1.80], [0.40, 2.05],
  [0.24, 2.28], [0.205, 2.55], [0.20, 3.05], [0.205, 3.28],
  [0.19, 3.35], [0.19, 3.55], [0.17, 3.60],
];

function makeLabelTexture(aroma, cream, wine) {
  const canvas = document.createElement('canvas');
  canvas.width = 320; canvas.height = 420;
  const ctx = canvas.getContext('2d');

  // background
  ctx.fillStyle = cream;
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  // border
  ctx.strokeStyle = wine;
  ctx.lineWidth = 6;
  ctx.strokeRect(14, 14, canvas.width - 28, canvas.height - 28);
  ctx.lineWidth = 1.5;
  ctx.strokeRect(26, 26, canvas.width - 52, canvas.height - 52);

  // decorative top ornament (grape cluster dots)
  ctx.fillStyle = wine;
  const cx = canvas.width / 2;
  [[-18, 60], [0, 50], [18, 60], [-9, 75], [9, 75], [0, 88]].forEach(([dx, dy]) => {
    ctx.beginPath();
    ctx.arc(cx + dx, dy, 8, 0, Math.PI * 2);
    ctx.fill();
  });

  // Title
  ctx.fillStyle = wine;
  ctx.textAlign = 'center';
  ctx.font = 'bold 34px Georgia, serif';
  ctx.fillText('VinoInsight', cx, 170);
  ctx.font = 'italic 20px Georgia, serif';
  ctx.fillText('A I   E S T A T E', cx, 200);

  // divider
  ctx.beginPath();
  ctx.moveTo(70, 225); ctx.lineTo(canvas.width - 70, 225);
  ctx.lineWidth = 2;
  ctx.stroke();

  // aroma descriptor
  ctx.font = '16px Georgia, serif';
  ctx.fillStyle = '#5a4632';
  const words = (aroma || 'Balanced & Floral').split(' ');
  let line = '', lines = [];
  words.forEach(w => {
    const test = line ? line + ' ' + w : w;
    if (ctx.measureText(test).width > canvas.width - 90) { lines.push(line); line = w; }
    else line = test;
  });
  lines.push(line);
  lines.forEach((l, i) => ctx.fillText(l, cx, 260 + i * 24));

  // bottom text
  ctx.font = '13px Georgia, serif';
  ctx.fillStyle = wine;
  ctx.fillText('PREDICTED  PROFILE', cx, canvas.height - 55);
  ctx.font = 'bold 15px Georgia, serif';
  ctx.fillText('CHEMISTRY-ANALYSED', cx, canvas.height - 32);

  const tex = new THREE.CanvasTexture(canvas);
  tex.anisotropy = 4;
  return tex;
}

const AROMA_COLORS = {
  'Sweet & Fruity':      '#5C1428',
  'Sharp & Earthy':      '#2E2015',
  'Full-Bodied & Warm':  '#3D0E14',
  'Crisp & Fresh':       '#1F3D1A',
  'Balanced & Floral':   '#4A0F1D',
};

function Bottle({ aroma }) {
  const group = useRef();
  const glassColor = AROMA_COLORS[aroma] || AROMA_COLORS['Balanced & Floral'];

  const latheGeom = useMemo(() => {
    const pts = PROFILE.map(([r, y]) => new THREE.Vector2(r, y));
    return new THREE.LatheGeometry(pts, 48);
  }, []);

  const labelTexture = useMemo(() => makeLabelTexture(aroma, '#F2E9D8', '#6B1626'), [aroma]);

  useFrame((_, delta) => {
    if (group.current) group.current.rotation.y += delta * 0.35;
  });

  return (
    <group ref={group} position={[0, -1.7, 0]}>
      {/* Glass body via lathe silhouette */}
      <mesh geometry={latheGeom} castShadow receiveShadow>
        <meshPhysicalMaterial
          color={glassColor}
          roughness={0.12}
          metalness={0.05}
          transmission={0.55}
          thickness={0.6}
          ior={1.45}
          clearcoat={0.6}
          clearcoatRoughness={0.15}
          transparent
          opacity={0.96}
        />
      </mesh>

      {/* Cork */}
      <mesh position={[0, 3.63, 0]}>
        <cylinderGeometry args={[0.15, 0.16, 0.22, 24]} />
        <meshStandardMaterial color="#D9C4A0" roughness={0.8} />
      </mesh>
      {/* Foil cap */}
      <mesh position={[0, 3.4, 0]}>
        <cylinderGeometry args={[0.205, 0.19, 0.32, 24]} />
        <meshStandardMaterial color="#C9A84C" roughness={0.25} metalness={0.75} />
      </mesh>

      {/* Label (curved slightly around the body) */}
      <mesh position={[0, 1.05, 0.615]}>
        <planeGeometry args={[1.0, 1.32]} />
        <meshStandardMaterial map={labelTexture} roughness={0.55} transparent />
      </mesh>
    </group>
  );
}

// Error boundary (project audit fix): <Environment preset="..."> from
// @react-three/drei used to be used here for reflections, but that preset
// fetches an HDR image from an external CDN at runtime (contradicting this
// file's own "no external photo/model files are used" design goal above)
// - and with no error boundary anywhere in the 3D bottle's render tree, a
// blocked/failed fetch (corporate proxy, offline demo, ad-blocker, or a
// restricted network environment) crashed the WebGL context and took the
// ENTIRE page to a blank black screen, not just the bottle - discovered
// via headless-browser screenshot testing for the User Manual, where the
// external CDN was unreachable. The Environment preset has been removed
// (replaced with a few extra local light sources below for a similar
// glassy highlight, with zero external dependency) and this ErrorBoundary
// is added as defense-in-depth: if the 3D bottle ever throws for any other
// reason (a WebGL-unsupported browser, a GPU driver issue, etc.), only the
// bottle's box degrades to a plain message - the rest of the page (results,
// dashboard, whatever the bottle is embedded in) keeps working normally.
class Bottle3DErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }
  static getDerivedStateFromError() {
    return { hasError: true };
  }
  componentDidCatch(error) {
    console.warn('WineBottle3D failed to render, falling back gracefully:', error);
  }
  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          width: '100%', height: this.props.height, borderRadius: 16,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          background: 'rgba(255,255,255,0.03)', border: '1px solid var(--border)',
          color: 'var(--text-dim)', fontSize: '0.8rem', textAlign: 'center', padding: 16,
        }}>
          3D preview unavailable in this browser/environment
        </div>
      );
    }
    return this.props.children;
  }
}

function WineBottle3DInner({ aroma = 'Balanced & Floral', height = 340 }) {
  return (
    <div style={{ width: '100%', height, cursor: 'grab', borderRadius: 16, overflow: 'hidden' }}>
      <Canvas shadows camera={{ position: [0, 0.3, 5.2], fov: 38 }} dpr={[1, 2]}>
        <ambientLight intensity={0.55} />
        <directionalLight position={[3, 5, 3]} intensity={1.3} castShadow />
        <directionalLight position={[-4, 2, -3]} intensity={0.5} color="#C9A84C" />
        <spotLight position={[0, 4, 2]} angle={0.4} intensity={0.6} penumbra={0.6} />
        {/* Extra local point lights stand in for the removed HDR Environment
            preset's reflections - no external asset fetch required. */}
        <pointLight position={[2, 1, 3]} intensity={0.4} color="#ffffff" />
        <pointLight position={[-2, -1, 2]} intensity={0.25} color="#C9A84C" />
        <Suspense fallback={null}>
          <Float speed={1.1} rotationIntensity={0.08} floatIntensity={0.35}>
            <Bottle aroma={aroma} />
          </Float>
          <ContactShadows position={[0, -1.72, 0]} opacity={0.5} scale={6} blur={2.4} far={3} />
        </Suspense>
        <OrbitControls
          enableZoom={false}
          enablePan={false}
          minPolarAngle={Math.PI / 2.4}
          maxPolarAngle={Math.PI / 1.9}
        />
      </Canvas>
    </div>
  );
}

export default function WineBottle3D(props) {
  return (
    <Bottle3DErrorBoundary height={props.height || 340}>
      <WineBottle3DInner {...props} />
    </Bottle3DErrorBoundary>
  );
}
