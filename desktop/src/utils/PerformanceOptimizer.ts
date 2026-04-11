/**
 * Performance Optimization Utilities for VR/AR Rendering
 * Ensures 60 FPS in immersive modes
 */

import * as THREE from 'three';

export class PerformanceOptimizer {
  private targetFPS = 60;
  private frameTime = 1000 / 60; // 16.67ms
  private renderBudget = 15; // ms per frame for rendering
  private currentFPS = 0;
  private frameCount = 0;
  private lastTime = performance.now();
  private adaptiveQuality = true;
  private qualityLevel = 1.0;

  // LOD (Level of Detail) settings
  private lodDistances = {
    high: 10,
    medium: 30,
    low: 60,
  };

  constructor() {
    this.startMonitoring();
  }

  // Start FPS monitoring
  private startMonitoring() {
    setInterval(() => {
      this.currentFPS = this.frameCount;
      this.frameCount = 0;

      // Adaptive quality adjustment
      if (this.adaptiveQuality) {
        this.adjustQuality();
      }
    }, 1000);
  }

  // Track frame rendering
  public frameRendered() {
    this.frameCount++;
  }

  // Get current FPS
  public getFPS(): number {
    return this.currentFPS;
  }

  // Adjust quality based on performance
  private adjustQuality() {
    if (this.currentFPS < 55 && this.qualityLevel > 0.5) {
      // Decrease quality if FPS drops
      this.qualityLevel = Math.max(0.5, this.qualityLevel - 0.1);
      console.log(`⚡ Reducing quality to ${(this.qualityLevel * 100).toFixed(0)}%`);
    } else if (this.currentFPS >= 60 && this.qualityLevel < 1.0) {
      // Increase quality if performance is good
      this.qualityLevel = Math.min(1.0, this.qualityLevel + 0.05);
      console.log(`✨ Increasing quality to ${(this.qualityLevel * 100).toFixed(0)}%`);
    }
  }

  // Get current quality level
  public getQualityLevel(): number {
    return this.qualityLevel;
  }

  // Optimize scene for VR performance
  public optimizeScene(scene: THREE.Scene, camera: THREE.Camera): void {
    scene.traverse((object) => {
      if (object instanceof THREE.Mesh) {
        this.optimizeMesh(object, camera);
      }
    });
  }

  // Optimize individual mesh
  private optimizeMesh(mesh: THREE.Mesh, camera: THREE.Camera): void {
    const distance = camera.position.distanceTo(mesh.position);

    // Apply LOD based on distance
    if (distance > this.lodDistances.low) {
      this.applyLowQuality(mesh);
    } else if (distance > this.lodDistances.medium) {
      this.applyMediumQuality(mesh);
    } else if (distance > this.lodDistances.high) {
      this.applyHighQuality(mesh);
    } else {
      this.applyMaxQuality(mesh);
    }

    // Frustum culling
    mesh.frustumCulled = true;

    // Optimize materials
    if (mesh.material instanceof THREE.Material) {
      this.optimizeMaterial(mesh.material);
    }
  }

  // Apply different quality levels
  private applyLowQuality(mesh: THREE.Mesh): void {
    mesh.visible = false; // Hide distant objects
  }

  private applyMediumQuality(mesh: THREE.Mesh): void {
    mesh.visible = true;
    if (mesh.material instanceof THREE.MeshPhongMaterial) {
      mesh.material.flatShading = true;
    }
  }

  private applyHighQuality(mesh: THREE.Mesh): void {
    mesh.visible = true;
    if (mesh.material instanceof THREE.MeshPhongMaterial) {
      mesh.material.flatShading = false;
    }
  }

  private applyMaxQuality(mesh: THREE.Mesh): void {
    mesh.visible = true;
    if (mesh.material instanceof THREE.MeshPhongMaterial) {
      mesh.material.flatShading = false;
    }
  }

  // Optimize material
  private optimizeMaterial(material: THREE.Material): void {
    // Reduce texture size for distant objects
    if (material instanceof THREE.MeshStandardMaterial) {
      material.roughness = Math.max(0.5, material.roughness);
      material.metalness = Math.min(0.5, material.metalness);
    }

    // Disable unnecessary features based on quality
    if (this.qualityLevel < 0.8) {
      material.needsUpdate = false;
    }
  }

  // Object pooling for frequently created/destroyed objects
  private objectPool = new Map<string, any[]>();

  public getFromPool(type: string, factory: () => any): any {
    if (!this.objectPool.has(type)) {
      this.objectPool.set(type, []);
    }

    const pool = this.objectPool.get(type)!;
    return pool.length > 0 ? pool.pop() : factory();
  }

  public returnToPool(type: string, object: any): void {
    if (!this.objectPool.has(type)) {
      this.objectPool.set(type, []);
    }

    const pool = this.objectPool.get(type)!;
    if (pool.length < 100) {
      // Limit pool size
      pool.push(object);
    }
  }

  // Batch geometry updates
  public batchGeometryUpdates(geometries: THREE.BufferGeometry[]): void {
    geometries.forEach((geometry) => {
      geometry.computeBoundingSphere();
      geometry.computeBoundingBox();
    });
  }

  // Optimize renderer settings for VR
  public optimizeRenderer(renderer: THREE.WebGLRenderer): void {
    // Pixel ratio optimization
    const pixelRatio = Math.min(window.devicePixelRatio, 2);
    renderer.setPixelRatio(pixelRatio * this.qualityLevel);

    // Shadow map optimization
    if (this.qualityLevel < 0.7) {
      renderer.shadowMap.enabled = false;
    } else {
      renderer.shadowMap.enabled = true;
      renderer.shadowMap.type = THREE.PCFShadowMap;
    }

    // Tone mapping
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.0;

    // Power preference
    renderer.capabilities.precision = this.qualityLevel > 0.8 ? 'highp' : 'mediump';
  }

  // Memory management
  public cleanupUnusedObjects(scene: THREE.Scene): void {
    const objectsToRemove: THREE.Object3D[] = [];

    scene.traverse((object) => {
      // Mark objects for removal if they haven't been visible recently
      if (
        object.userData.lastVisibleFrame &&
        this.frameCount - object.userData.lastVisibleFrame > 600
      ) {
        objectsToRemove.push(object);
      }
    });

    objectsToRemove.forEach((object) => {
      this.disposeObject(object);
      scene.remove(object);
    });
  }

  // Dispose object and free memory
  private disposeObject(object: THREE.Object3D): void {
    if (object instanceof THREE.Mesh) {
      object.geometry.dispose();

      if (Array.isArray(object.material)) {
        object.material.forEach((material) => material.dispose());
      } else {
        object.material.dispose();
      }
    }
  }

  // Enable/disable adaptive quality
  public setAdaptiveQuality(enabled: boolean): void {
    this.adaptiveQuality = enabled;
  }

  // Set target FPS
  public setTargetFPS(fps: number): void {
    this.targetFPS = fps;
    this.frameTime = 1000 / fps;
    this.renderBudget = this.frameTime - 1.67; // Leave buffer for other operations
  }

  // Get performance stats
  public getStats() {
    return {
      fps: this.currentFPS,
      targetFPS: this.targetFPS,
      qualityLevel: this.qualityLevel,
      frameTime: this.frameTime,
      renderBudget: this.renderBudget,
      isOptimal: this.currentFPS >= this.targetFPS * 0.9,
    };
  }
}

// Utility: Debounce function for performance-critical operations
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null;

  return function (this: any, ...args: Parameters<T>) {
    const context = this;

    if (timeout) {
      clearTimeout(timeout);
    }

    timeout = setTimeout(() => {
      func.apply(context, args);
    }, wait);
  };
}

// Utility: Throttle function for limiting execution frequency
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean = false;

  return function (this: any, ...args: Parameters<T>) {
    const context = this;

    if (!inThrottle) {
      func.apply(context, args);
      inThrottle = true;

      setTimeout(() => {
        inThrottle = false;
      }, limit);
    }
  };
}

// Utility: Request animation frame with FPS limiting
export class FPSLimiter {
  private lastFrameTime = 0;
  private targetInterval: number;

  constructor(targetFPS: number = 60) {
    this.targetInterval = 1000 / targetFPS;
  }

  public requestFrame(callback: (deltaTime: number) => void): void {
    requestAnimationFrame((currentTime) => {
      const deltaTime = currentTime - this.lastFrameTime;

      if (deltaTime >= this.targetInterval) {
        this.lastFrameTime = currentTime - (deltaTime % this.targetInterval);
        callback(deltaTime);
      } else {
        this.requestFrame(callback);
      }
    });
  }
}

export default PerformanceOptimizer;
