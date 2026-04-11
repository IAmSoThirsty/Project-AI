/**
 * Enhanced Cognitive IDE with WebXR VR/AR Support
 * Provides immersive 3D code editing and simulation visualization
 */

import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { VRButton } from 'three/examples/jsm/webxr/VRButton.js';
import { XRControllerModelFactory } from 'three/examples/jsm/webxr/XRControllerModelFactory.js';

interface VRState {
  isVRSupported: boolean;
  isVRActive: boolean;
  frameRate: number;
  mode: 'desktop' | 'vr' | 'ar';
}

interface SimulationData {
  tick: number;
  agents: Array<{
    id: string;
    position: { x: number; y: number; z: number };
    role: string;
    status: string;
  }>;
  floors: Array<{
    id: number;
    language: string;
    departments: number;
  }>;
}

export const CognitiveIDE_VR: React.FC = () => {
  const containerRef = useRef<HTMLDivElement>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const [vrState, setVRState] = useState<VRState>({
    isVRSupported: false,
    isVRActive: false,
    frameRate: 0,
    mode: 'desktop',
  });
  const [simulationData, setSimulationData] = useState<SimulationData | null>(null);

  // Initialize Three.js scene with WebXR
  useEffect(() => {
    if (!containerRef.current) return;

    // Scene setup
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0a0e1a);
    scene.fog = new THREE.Fog(0x0a0e1a, 10, 50);
    sceneRef.current = scene;

    // Camera setup
    const camera = new THREE.PerspectiveCamera(
      75,
      window.innerWidth / window.innerHeight,
      0.1,
      1000
    );
    camera.position.set(0, 1.6, 5); // Eye level for VR
    cameraRef.current = camera;

    // Renderer setup with WebXR
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.xr.enabled = true;
    rendererRef.current = renderer;

    containerRef.current.appendChild(renderer.domElement);

    // Add VR button
    const vrButton = VRButton.createButton(renderer);
    document.body.appendChild(vrButton);

    // Check VR support
    if ('xr' in navigator) {
      (navigator as any).xr.isSessionSupported('immersive-vr').then((supported: boolean) => {
        setVRState(prev => ({ ...prev, isVRSupported: supported }));
      });
    }

    // VR Controllers
    const controllerModelFactory = new XRControllerModelFactory();
    
    const controller1 = renderer.xr.getController(0);
    controller1.addEventListener('selectstart', onSelectStart);
    controller1.addEventListener('selectend', onSelectEnd);
    scene.add(controller1);

    const controller2 = renderer.xr.getController(1);
    controller2.addEventListener('selectstart', onSelectStart);
    controller2.addEventListener('selectend', onSelectEnd);
    scene.add(controller2);

    const controllerGrip1 = renderer.xr.getControllerGrip(0);
    controllerGrip1.add(controllerModelFactory.createControllerModel(controllerGrip1));
    scene.add(controllerGrip1);

    const controllerGrip2 = renderer.xr.getControllerGrip(1);
    controllerGrip2.add(controllerModelFactory.createControllerModel(controllerGrip2));
    scene.add(controllerGrip2);

    // Create immersive environment
    createOfficeEnvironment(scene);
    createFloorVisualization(scene);
    createCodePanels(scene);

    // Lighting
    const ambientLight = new THREE.AmbientLight(0x404040, 2);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
    directionalLight.position.set(5, 10, 5);
    scene.add(directionalLight);

    // Grid floor
    const gridHelper = new THREE.GridHelper(20, 20, 0x00ff41, 0x0d1f2a);
    scene.add(gridHelper);

    // Animation loop with FPS tracking
    let lastTime = performance.now();
    let frameCount = 0;
    
    function animate() {
      const currentTime = performance.now();
      frameCount++;

      // Update FPS every second
      if (currentTime - lastTime >= 1000) {
        setVRState(prev => ({ 
          ...prev, 
          frameRate: frameCount,
          isVRActive: renderer.xr.isPresenting 
        }));
        frameCount = 0;
        lastTime = currentTime;
      }

      updateSimulationVisualization(scene, simulationData);
      renderer.render(scene, camera);
    }

    renderer.setAnimationLoop(animate);

    // Handle resize
    const handleResize = () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    };
    window.addEventListener('resize', handleResize);

    // Cleanup
    return () => {
      window.removeEventListener('resize', handleResize);
      renderer.dispose();
      vrButton.remove();
    };
  }, []);

  // Controller interaction handlers
  const onSelectStart = (event: any) => {
    const controller = event.target;
    // Implement interaction logic (e.g., grab code panels, trigger actions)
  };

  const onSelectEnd = (event: any) => {
    const controller = event.target;
    // Implement release logic
  };

  // Create immersive office environment
  const createOfficeEnvironment = (scene: THREE.Scene) => {
    // Office walls
    const wallMaterial = new THREE.MeshPhongMaterial({ 
      color: 0x1a3a4a, 
      transparent: true, 
      opacity: 0.7 
    });

    // Back wall
    const backWall = new THREE.Mesh(
      new THREE.BoxGeometry(20, 5, 0.2),
      wallMaterial
    );
    backWall.position.set(0, 2.5, -5);
    scene.add(backWall);

    // Side walls
    const leftWall = new THREE.Mesh(
      new THREE.BoxGeometry(0.2, 5, 10),
      wallMaterial
    );
    leftWall.position.set(-10, 2.5, 0);
    scene.add(leftWall);

    const rightWall = new THREE.Mesh(
      new THREE.BoxGeometry(0.2, 5, 10),
      wallMaterial
    );
    rightWall.position.set(10, 2.5, 0);
    scene.add(rightWall);
  };

  // Create floor visualization
  const createFloorVisualization = (scene: THREE.Scene) => {
    const floors = [
      { name: 'Lobby', y: 0, color: 0xff9f00 },
      { name: 'Python', y: 1.5, color: 0x3776ab },
      { name: 'JavaScript', y: 3, color: 0xf7df1e },
      { name: 'Rust', y: 4.5, color: 0xff6b35 },
      { name: 'Go', y: 6, color: 0x00add8 },
      { name: 'Security', y: 7.5, color: 0xff4444 },
    ];

    floors.forEach((floor, index) => {
      // Floor platform
      const floorGeometry = new THREE.BoxGeometry(8, 0.1, 3);
      const floorMaterial = new THREE.MeshPhongMaterial({ 
        color: floor.color,
        emissive: floor.color,
        emissiveIntensity: 0.3,
        transparent: true,
        opacity: 0.8
      });
      const floorMesh = new THREE.Mesh(floorGeometry, floorMaterial);
      floorMesh.position.set(-6, floor.y, 0);
      scene.add(floorMesh);

      // Floor label
      const canvas = document.createElement('canvas');
      const context = canvas.getContext('2d')!;
      canvas.width = 512;
      canvas.height = 128;
      context.fillStyle = '#00ff41';
      context.font = 'bold 48px Courier New';
      context.fillText(floor.name, 20, 80);

      const texture = new THREE.CanvasTexture(canvas);
      const labelMaterial = new THREE.MeshBasicMaterial({ 
        map: texture, 
        transparent: true 
      });
      const labelGeometry = new THREE.PlaneGeometry(2, 0.5);
      const label = new THREE.Mesh(labelGeometry, labelMaterial);
      label.position.set(-6, floor.y + 0.5, 1.6);
      scene.add(label);
    });
  };

  // Create floating code panels
  const createCodePanels = (scene: THREE.Scene) => {
    const panelPositions = [
      { x: 2, y: 1.6, z: -2 },
      { x: 4, y: 1.6, z: -1 },
      { x: 2, y: 2.5, z: -2 },
    ];

    panelPositions.forEach((pos, index) => {
      const canvas = document.createElement('canvas');
      const context = canvas.getContext('2d')!;
      canvas.width = 1024;
      canvas.height = 768;
      
      // Code panel background
      context.fillStyle = '#0d1f2a';
      context.fillRect(0, 0, canvas.width, canvas.height);
      
      // Code text
      context.fillStyle = '#00ff41';
      context.font = '20px Courier New';
      const codeLines = [
        'def cognitive_process():',
        '    # AI-assisted code editing',
        '    suggestions = ai.analyze(context)',
        '    for hint in suggestions:',
        '        apply_improvement(hint)',
        '    return optimized_code',
      ];
      
      codeLines.forEach((line, i) => {
        context.fillText(line, 20, 50 + i * 30);
      });

      const texture = new THREE.CanvasTexture(canvas);
      const material = new THREE.MeshBasicMaterial({ 
        map: texture, 
        transparent: true,
        opacity: 0.9
      });
      const geometry = new THREE.PlaneGeometry(2, 1.5);
      const panel = new THREE.Mesh(geometry, material);
      panel.position.set(pos.x, pos.y, pos.z);
      scene.add(panel);

      // Panel frame
      const frameGeometry = new THREE.EdgesGeometry(geometry);
      const frameMaterial = new THREE.LineBasicMaterial({ color: 0xff9f00 });
      const frame = new THREE.LineSegments(frameGeometry, frameMaterial);
      panel.add(frame);
    });
  };

  // Update simulation visualization in real-time
  const updateSimulationVisualization = (
    scene: THREE.Scene, 
    data: SimulationData | null
  ) => {
    if (!data) return;

    // Update agent positions (implementation would animate agents)
    data.agents.forEach(agent => {
      // Create or update agent visualization
      const agentMesh = scene.getObjectByName(agent.id) as THREE.Mesh;
      if (agentMesh) {
        agentMesh.position.set(agent.position.x, agent.position.y, agent.position.z);
      } else {
        // Create new agent visualization
        const geometry = new THREE.SphereGeometry(0.1, 16, 16);
        const material = new THREE.MeshPhongMaterial({ 
          color: 0x00ff41,
          emissive: 0x00ff41,
          emissiveIntensity: 0.5
        });
        const mesh = new THREE.Mesh(geometry, material);
        mesh.name = agent.id;
        mesh.position.set(agent.position.x, agent.position.y, agent.position.z);
        scene.add(mesh);
      }
    });
  };

  // Fetch simulation data
  useEffect(() => {
    const fetchSimulation = async () => {
      try {
        const response = await fetch('/api/simulation/state');
        const data = await response.json();
        setSimulationData(data);
      } catch (error) {
        console.error('Failed to fetch simulation:', error);
      }
    };

    const interval = setInterval(fetchSimulation, 100); // 10 FPS updates
    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{ width: '100%', height: '100vh', position: 'relative' }}>
      <div ref={containerRef} style={{ width: '100%', height: '100%' }} />
      
      {/* VR Status HUD */}
      <div style={{
        position: 'absolute',
        top: 20,
        left: 20,
        padding: '15px',
        background: 'rgba(13, 31, 42, 0.9)',
        border: '2px solid #00ff41',
        color: '#00ff41',
        fontFamily: 'Courier New',
        fontSize: '14px',
        borderRadius: '5px',
        zIndex: 1000,
      }}>
        <div>VR Support: {vrState.isVRSupported ? '✓ Yes' : '✗ No'}</div>
        <div>VR Active: {vrState.isVRActive ? '✓ Yes' : '✗ No'}</div>
        <div>Mode: {vrState.mode.toUpperCase()}</div>
        <div style={{ color: vrState.frameRate >= 60 ? '#00ff41' : '#ff9f00' }}>
          FPS: {vrState.frameRate}
        </div>
        {vrState.frameRate < 60 && (
          <div style={{ color: '#ff4444', marginTop: '5px' }}>
            ⚠ Performance Below Target
          </div>
        )}
      </div>
    </div>
  );
};

export default CognitiveIDE_VR;
