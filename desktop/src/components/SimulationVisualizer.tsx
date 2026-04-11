/**
 * Real-time 3D Simulation Visualizer
 * Visualizes running simulations with Three.js
 */

import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';

interface Agent {
  id: string;
  position: THREE.Vector3;
  velocity: THREE.Vector3;
  role: string;
  status: 'idle' | 'active' | 'blocked' | 'completed';
  health: number;
  task?: string;
}

interface Floor {
  id: number;
  name: string;
  height: number;
  agents: Agent[];
  departments: Department[];
}

interface Department {
  id: string;
  name: string;
  position: THREE.Vector3;
  size: THREE.Vector3;
  capacity: number;
  occupied: number;
}

interface SimulationState {
  tick: number;
  floors: Floor[];
  totalAgents: number;
  activeTasks: number;
  completedTasks: number;
  worldStatus: string;
}

interface SimulationVisualizerProps {
  autoRotate?: boolean;
  showStats?: boolean;
}

export const SimulationVisualizer: React.FC<SimulationVisualizerProps> = ({
  autoRotate = false,
  showStats = true,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const controlsRef = useRef<OrbitControls | null>(null);
  const agentMeshesRef = useRef<Map<string, THREE.Mesh>>(new Map());
  const [simulationState, setSimulationState] = useState<SimulationState | null>(null);
  const [fps, setFps] = useState<number>(0);
  const [isPaused, setIsPaused] = useState(false);

  // Initialize Three.js scene
  useEffect(() => {
    if (!containerRef.current) return;

    // Scene
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0a0e1a);
    scene.fog = new THREE.Fog(0x0a0e1a, 20, 100);
    sceneRef.current = scene;

    // Camera
    const camera = new THREE.PerspectiveCamera(
      60,
      containerRef.current.clientWidth / containerRef.current.clientHeight,
      0.1,
      1000
    );
    camera.position.set(30, 25, 30);
    camera.lookAt(0, 0, 0);
    cameraRef.current = camera;

    // Renderer
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(
      containerRef.current.clientWidth,
      containerRef.current.clientHeight
    );
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    rendererRef.current = renderer;
    containerRef.current.appendChild(renderer.domElement);

    // Controls
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.autoRotate = autoRotate;
    controls.autoRotateSpeed = 1.0;
    controlsRef.current = controls;

    // Lighting
    const ambientLight = new THREE.AmbientLight(0x404040, 2);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 1.5);
    directionalLight.position.set(10, 20, 10);
    directionalLight.castShadow = true;
    directionalLight.shadow.camera.left = -50;
    directionalLight.shadow.camera.right = 50;
    directionalLight.shadow.camera.top = 50;
    directionalLight.shadow.camera.bottom = -50;
    scene.add(directionalLight);

    // Point lights for atmosphere
    const pointLight1 = new THREE.PointLight(0x00ff41, 1, 50);
    pointLight1.position.set(10, 10, 10);
    scene.add(pointLight1);

    const pointLight2 = new THREE.PointLight(0xff9f00, 1, 50);
    pointLight2.position.set(-10, 10, -10);
    scene.add(pointLight2);

    // Build initial environment
    buildEnvironment(scene);

    // FPS tracking
    let frameCount = 0;
    let lastTime = performance.now();

    // Animation loop
    const animate = () => {
      if (!isPaused) {
        requestAnimationFrame(animate);

        // FPS calculation
        frameCount++;
        const currentTime = performance.now();
        if (currentTime - lastTime >= 1000) {
          setFps(frameCount);
          frameCount = 0;
          lastTime = currentTime;
        }

        // Update controls
        controls.update();

        // Update simulation visualization
        if (simulationState) {
          updateAgents(scene, simulationState);
          updateDepartments(scene, simulationState);
        }

        // Render
        renderer.render(scene, camera);
      } else {
        requestAnimationFrame(animate);
      }
    };
    animate();

    // Handle resize
    const handleResize = () => {
      if (!containerRef.current) return;
      camera.aspect =
        containerRef.current.clientWidth / containerRef.current.clientHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(
        containerRef.current.clientWidth,
        containerRef.current.clientHeight
      );
    };
    window.addEventListener('resize', handleResize);

    // Cleanup
    return () => {
      window.removeEventListener('resize', handleResize);
      renderer.dispose();
      controls.dispose();
    };
  }, [autoRotate, isPaused]);

  // Build the 3D environment
  const buildEnvironment = (scene: THREE.Scene) => {
    // Ground plane
    const groundGeometry = new THREE.PlaneGeometry(100, 100);
    const groundMaterial = new THREE.MeshStandardMaterial({
      color: 0x0d1f2a,
      roughness: 0.8,
      metalness: 0.2,
    });
    const ground = new THREE.Mesh(groundGeometry, groundMaterial);
    ground.rotation.x = -Math.PI / 2;
    ground.receiveShadow = true;
    scene.add(ground);

    // Grid
    const gridHelper = new THREE.GridHelper(100, 50, 0x00ff41, 0x1a3a4a);
    scene.add(gridHelper);

    // Build floors
    const floorHeight = 5;
    for (let i = 0; i < 6; i++) {
      createFloor(scene, i, floorHeight * i);
    }
  };

  // Create a single floor
  const createFloor = (scene: THREE.Scene, floorNumber: number, yPosition: number) => {
    const floorNames = [
      'Lobby',
      'Python',
      'JavaScript',
      'Rust',
      'Go',
      'Security',
    ];
    const floorColors = [
      0xff9f00,
      0x3776ab,
      0xf7df1e,
      0xff6b35,
      0x00add8,
      0xff4444,
    ];

    // Floor platform
    const platformGeometry = new THREE.BoxGeometry(20, 0.5, 20);
    const platformMaterial = new THREE.MeshPhongMaterial({
      color: floorColors[floorNumber],
      emissive: floorColors[floorNumber],
      emissiveIntensity: 0.2,
      transparent: true,
      opacity: 0.8,
    });
    const platform = new THREE.Mesh(platformGeometry, platformMaterial);
    platform.position.set(0, yPosition, 0);
    platform.castShadow = true;
    platform.receiveShadow = true;
    scene.add(platform);

    // Floor label
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d')!;
    canvas.width = 512;
    canvas.height = 128;
    context.fillStyle = '#ffffff';
    context.font = 'bold 60px Arial';
    context.textAlign = 'center';
    context.fillText(floorNames[floorNumber], 256, 80);

    const texture = new THREE.CanvasTexture(canvas);
    const labelMaterial = new THREE.MeshBasicMaterial({
      map: texture,
      transparent: true,
    });
    const labelGeometry = new THREE.PlaneGeometry(4, 1);
    const label = new THREE.Mesh(labelGeometry, labelMaterial);
    label.position.set(0, yPosition + 2, 10.5);
    scene.add(label);

    // Pillars at corners
    const pillarGeometry = new THREE.CylinderGeometry(0.3, 0.3, 5, 8);
    const pillarMaterial = new THREE.MeshPhongMaterial({ color: 0x1a3a4a });
    const positions = [
      [-10, yPosition + 2.5, -10],
      [10, yPosition + 2.5, -10],
      [-10, yPosition + 2.5, 10],
      [10, yPosition + 2.5, 10],
    ];

    positions.forEach((pos) => {
      const pillar = new THREE.Mesh(pillarGeometry, pillarMaterial);
      pillar.position.set(pos[0], pos[1], pos[2]);
      pillar.castShadow = true;
      scene.add(pillar);
    });
  };

  // Update agent visualizations
  const updateAgents = (scene: THREE.Scene, state: SimulationState) => {
    const currentAgentIds = new Set<string>();

    state.floors.forEach((floor) => {
      floor.agents.forEach((agent) => {
        currentAgentIds.add(agent.id);

        let agentMesh = agentMeshesRef.current.get(agent.id);

        if (!agentMesh) {
          // Create new agent
          const geometry = new THREE.SphereGeometry(0.3, 16, 16);
          const material = new THREE.MeshPhongMaterial({
            color: getAgentColor(agent.status),
            emissive: getAgentColor(agent.status),
            emissiveIntensity: 0.5,
          });
          agentMesh = new THREE.Mesh(geometry, material);
          agentMesh.castShadow = true;
          scene.add(agentMesh);
          agentMeshesRef.current.set(agent.id, agentMesh);
        }

        // Update position with smooth interpolation
        agentMesh.position.lerp(agent.position, 0.1);

        // Update color based on status
        (agentMesh.material as THREE.MeshPhongMaterial).color.set(
          getAgentColor(agent.status)
        );

        // Add pulsing effect for active agents
        if (agent.status === 'active') {
          const scale = 1 + Math.sin(Date.now() * 0.005) * 0.2;
          agentMesh.scale.set(scale, scale, scale);
        } else {
          agentMesh.scale.set(1, 1, 1);
        }
      });
    });

    // Remove agents that no longer exist
    agentMeshesRef.current.forEach((mesh, id) => {
      if (!currentAgentIds.has(id)) {
        scene.remove(mesh);
        agentMeshesRef.current.delete(id);
      }
    });
  };

  // Update department visualizations
  const updateDepartments = (scene: THREE.Scene, state: SimulationState) => {
    state.floors.forEach((floor) => {
      floor.departments.forEach((dept) => {
        const deptMesh = scene.getObjectByName(`dept-${dept.id}`) as THREE.Mesh;

        if (!deptMesh) {
          // Create department box
          const geometry = new THREE.BoxGeometry(
            dept.size.x,
            dept.size.y,
            dept.size.z
          );
          const material = new THREE.MeshPhongMaterial({
            color: 0x1a3a4a,
            transparent: true,
            opacity: 0.3,
            wireframe: false,
          });
          const mesh = new THREE.Mesh(geometry, material);
          mesh.position.copy(dept.position);
          mesh.name = `dept-${dept.id}`;
          scene.add(mesh);

          // Department wireframe
          const edges = new THREE.EdgesGeometry(geometry);
          const lineMaterial = new THREE.LineBasicMaterial({ color: 0x00ff41 });
          const wireframe = new THREE.LineSegments(edges, lineMaterial);
          mesh.add(wireframe);
        }
      });
    });
  };

  // Get agent color based on status
  const getAgentColor = (status: string): number => {
    switch (status) {
      case 'active':
        return 0x00ff41;
      case 'idle':
        return 0x88ccff;
      case 'blocked':
        return 0xff9f00;
      case 'completed':
        return 0x00ff00;
      default:
        return 0xffffff;
    }
  };

  // Fetch simulation state
  useEffect(() => {
    const fetchState = async () => {
      try {
        const response = await fetch('/api/simulation/state');
        const data = await response.json();

        // Transform data to include Vector3 positions
        const transformedData: SimulationState = {
          ...data,
          floors: data.floors.map((floor: any) => ({
            ...floor,
            agents: floor.agents.map((agent: any) => ({
              ...agent,
              position: new THREE.Vector3(
                agent.position.x || Math.random() * 18 - 9,
                floor.height || 0,
                agent.position.z || Math.random() * 18 - 9
              ),
              velocity: new THREE.Vector3(0, 0, 0),
            })),
            departments: floor.departments.map((dept: any) => ({
              ...dept,
              position: new THREE.Vector3(
                dept.position?.x || 0,
                floor.height || 0,
                dept.position?.z || 0
              ),
              size: new THREE.Vector3(
                dept.size?.x || 3,
                dept.size?.y || 2,
                dept.size?.z || 3
              ),
            })),
          })),
        };

        setSimulationState(transformedData);
      } catch (error) {
        console.error('Failed to fetch simulation:', error);
      }
    };

    const interval = setInterval(fetchState, 100); // 10 FPS updates
    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{ width: '100%', height: '100%', position: 'relative' }}>
      <div ref={containerRef} style={{ width: '100%', height: '100%' }} />

      {/* Stats overlay */}
      {showStats && simulationState && (
        <div
          style={{
            position: 'absolute',
            top: 20,
            right: 20,
            padding: '15px',
            background: 'rgba(13, 31, 42, 0.9)',
            border: '2px solid #00ff41',
            borderRadius: '5px',
            color: '#00ff41',
            fontFamily: 'Courier New',
            fontSize: '13px',
            minWidth: '200px',
          }}
        >
          <h3 style={{ color: '#ff9f00', marginBottom: '10px' }}>
            Simulation Stats
          </h3>
          <div style={{ marginBottom: '5px' }}>
            <span style={{ color: '#88ccff' }}>FPS:</span>{' '}
            <span style={{ color: fps >= 60 ? '#00ff41' : '#ff9f00' }}>
              {fps}
            </span>
          </div>
          <div style={{ marginBottom: '5px' }}>
            <span style={{ color: '#88ccff' }}>Tick:</span>{' '}
            {simulationState.tick}
          </div>
          <div style={{ marginBottom: '5px' }}>
            <span style={{ color: '#88ccff' }}>Agents:</span>{' '}
            {simulationState.totalAgents}
          </div>
          <div style={{ marginBottom: '5px' }}>
            <span style={{ color: '#88ccff' }}>Active Tasks:</span>{' '}
            {simulationState.activeTasks}
          </div>
          <div style={{ marginBottom: '5px' }}>
            <span style={{ color: '#88ccff' }}>Completed:</span>{' '}
            {simulationState.completedTasks}
          </div>
          <div>
            <span style={{ color: '#88ccff' }}>Status:</span>{' '}
            <span
              style={{
                color:
                  simulationState.worldStatus === 'running'
                    ? '#00ff41'
                    : '#ff9f00',
              }}
            >
              {simulationState.worldStatus.toUpperCase()}
            </span>
          </div>

          <button
            onClick={() => setIsPaused(!isPaused)}
            style={{
              marginTop: '10px',
              width: '100%',
              padding: '8px',
              background: 'linear-gradient(180deg, #1a3a4a 0%, #0d1f2a 100%)',
              border: '2px solid #00ff41',
              color: '#00ff41',
              cursor: 'pointer',
              fontFamily: 'Courier New',
              borderRadius: '3px',
            }}
          >
            {isPaused ? '▶ Resume' : '⏸ Pause'}
          </button>
        </div>
      )}
    </div>
  );
};

export default SimulationVisualizer;
