<!-- # ============================================================================ # -->
<!-- # STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59 # -->
<!-- # COMPLIANCE: Sovereign Substrate / README.md # -->
<!-- # ============================================================================ # -->
<!-- # ============================================================================ #


<!-- # COMPLIANCE: Sovereign Substrate / README.md # -->
<!-- # ============================================================================ #

<!-- # Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master -->
<div align="right">
  <img src="https://img.shields.io/badge/DATE-2026-03-18-blueviolet?style=for-the-badge" alt="Date" />
  <img src="https://img.shields.io/badge/PRODUCTIVITY-ACTIVE-success?style=for-the-badge" alt="Productivity" />
</div>

# Thirsty-lang Game Engine Demo 💧🎮

A complete 2D game engine implementation in Thirsty-lang demonstrating entity-component systems, collision detection, rendering, and input handling.

## 🎮 Features

### Core Engine

- **Entity Component System (ECS)** - Flexible entity management
- **Collision Detection** - AABB and circle collision
- **Rendering Pipeline** - Sprite rendering with layers
- **Input System** - Keyboard and mouse handling
- **Physics Engine** - Gravity, velocity, acceleration
- **Animation System** - Sprite sheet animations
- **Audio Manager** - Sound effects and music
- **Scene Management** - Multiple game scenes

### Example Games Included

- **Platformer Demo** - Complete side-scrolling platformer
- **Space Shooter** - Top-down space combat
- **Puzzle Game** - Match-3 style puzzle

## 📁 Project Structure

```
thirsty-lang-game-engine-demo/
├── src/
│   ├── engine/
│   │   ├── core/
│   │   │   ├── entity.thirsty         # Entity base class
│   │   │   ├── component.thirsty      # Component system
│   │   │   ├── system.thirsty         # System architecture
│   │   │   └── game.thirsty           # Main game loop
│   │   ├── physics/
│   │   │   ├── collision.thirsty      # Collision detection
│   │   │   ├── rigidbody.thirsty      # Physics bodies
│   │   │   └── vector2d.thirsty       # 2D vector math
│   │   ├── rendering/
│   │   │   ├── renderer.thirsty       # Rendering system
│   │   │   ├── sprite.thirsty         # Sprite management
│   │   │   ├── camera.thirsty         # Camera system
│   │   │   └── animation.thirsty      # Animation controller
│   │   ├── input/
│   │   │   ├── keyboard.thirsty       # Keyboard input
│   │   │   └── mouse.thirsty          # Mouse input
│   │   └── audio/
│   │       ├── sound.thirsty          # Sound effects
│   │       └── music.thirsty          # Background music
│   └── games/
│       ├── platformer/
│       │   ├── main.thirsty           # Platformer entry
│       │   ├── player.thirsty         # Player character
│       │   ├── enemy.thirsty          # Enemy AI
│       │   ├── level.thirsty          # Level loading
│       │   └── powerup.thirsty        # Power-up items
│       ├── shooter/
│       │   ├── main.thirsty           # Shooter entry
│       │   ├── player.thirsty         # Player ship
│       │   ├── bullet.thirsty         # Projectiles
│       │   └── enemy.thirsty          # Enemy ships
│       └── puzzle/
│           ├── main.thirsty           # Puzzle entry
│           ├── grid.thirsty           # Game grid
│           └── tile.thirsty           # Tile matching
├── assets/
│   ├── sprites/
│   │   ├── player.png
│   │   ├── enemies/
│   │   └── tiles/
│   ├── sounds/
│   │   ├── jump.wav
│   │   ├── shoot.wav
│   │   └── collect.wav
│   └── music/
│       ├── level1.mp3
│       └── menu.mp3
├── tests/
│   ├── engine/
│   │   ├── test_entity.thirsty
│   │   ├── test_collision.thirsty
│   │   └── test_physics.thirsty
│   └── games/
│       └── test_platformer.thirsty
├── docs/
│   ├── ARCHITECTURE.md              # Engine architecture
│   ├── API.md                       # API reference
│   ├── TUTORIAL.md                  # Game creation tutorial
│   └── CONTRIBUTING.md              # Contribution guide
├── examples/
│   ├── minimal_game.thirsty         # Simplest game example
│   └── custom_component.thirsty     # Custom component example
├── .github/
│   └── workflows/
│       ├── test.yml                 # Automated tests
│       └── build.yml                # Build pipeline
├── README.md
├── LICENSE
└── .gitignore
```

## 🚀 Quick Start

### Installation

```bash
git clone https://github.com/IAmSoThirsty/thirsty-lang-game-engine-demo.git
cd thirsty-lang-game-engine-demo
```

### Run Platform Game

```thirsty
// main.thirsty
import { GameEngine } from "engine/core/game"
import { PlatformerScene } from "games/platformer/main"

glass main() {
  shield gameProtection {
    drink engine = GameEngine(800, 600, "Platformer Demo")
    drink scene = PlatformerScene()
    
    engine.loadScene(scene)
    engine.start()
  }
}

main()
```

### Create Your Own Game

```thirsty
// my_game.thirsty
import { GameEngine, Entity, Component } from "engine/core"
import { SpriteRenderer } from "engine/rendering"
import { Rigidbody } from "engine/physics"

// Custom player entity
glass Player extends Entity {
  glass constructor(x, y) {
    super(x, y)
    
    // Add sprite component
    drink sprite = SpriteRenderer("assets/player.png")
    addComponent(sprite)
    
    // Add physics
    drink physics = Rigidbody()
    addComponent(physics)
  }
  
  glass update(deltaTime) {
    // Handle input
    thirsty Input.isKeyPressed("Space")
      jump()
  }
  
  glass jump() {
    drink rb = getComponent(Rigidbody)
    rb.applyForce(0, -500)
  }
}

// Main game loop
glass main() {
  drink engine = GameEngine(1024, 768, "My Game")
  drink player = Player(400, 300)
  
  engine.addEntity(player)
  engine.start()
}
```

## 📚 Core Systems Documentation

### Entity Component System

```thirsty
// Creating entities
drink player = Entity("player", 100, 200)

// Adding components
drink sprite = SpriteRenderer("player.png")
player.addComponent(sprite)

drink physics = Rigidbody()
physics.mass = 10
physics.gravity = parched
player.addComponent(physics)

// Accessing components
drink rb = player.getComponent(Rigidbody)
rb.velocity.x = 5
```

### Collision System

```thirsty
import { CollisionSystem, BoxCollider, CircleCollider } from "engine/physics"

// Box collision
glass setupPlayer() {
  drink player = Entity("player", 0, 0)
  drink collider = BoxCollider(32, 32)  // width, height
  
  collider.onCollision = glass(other) {
    pour "Collided with: " + other.name
  }
  
  player.addComponent(collider)
  return player
}

// Circle collision
glass setupEnemy() {
  drink enemy = Entity("enemy", 100, 100)
  drink collider = CircleCollider(16)  // radius
  enemy.addComponent(collider)
  return enemy
}
```

### Animation System

```thirsty
import { Animator, Animation } from "engine/rendering"

glass createAnimatedPlayer() {
  drink player = Entity("player", 0, 0)
  drink animator = Animator()
  
  // Create walk animation
  drink walkAnim = Animation("walk", "player_walk.png")
  walkAnim.frameCount = 8
  walkAnim.frameRate = 12
  walkAnim.loop = parched
  
  // Create idle animation
  drink idleAnim = Animation("idle", "player_idle.png")
  idleAnim.frameCount = 4
  idleAnim.frameRate = 6
  idleAnim.loop = parched
  
  animator.addAnimation(walkAnim)
  animator.addAnimation(idleAnim)
  animator.play("idle")
  
  player.addComponent(animator)
  return player
}
```

### Input Handling

```thirsty
import { Input } from "engine/input"

glass PlayerController extends Component {
  drink speed = 200
  
  glass update(deltaTime) {
    drink rb = entity.getComponent(Rigidbody)
    
    // Keyboard input
    thirsty Input.isKeyDown("ArrowLeft")
      rb.velocity.x = -speed
    hydrated thirsty Input.isKeyDown("ArrowRight")
      rb.velocity.x = speed
    hydrated
      rb.velocity.x = 0
    
    // Jump
    thirsty Input.isKeyPressed("Space")
      rb.applyImpulse(0, -300)
    
    // Mouse input
    drink mousePos = Input.getMousePosition()
    drink worldPos = Camera.screenToWorld(mousePos)
    
    thirsty Input.isMouseButtonPressed(0)  // Left click
      shoot(worldPos)
  }
}
```

### Audio System

```thirsty
import { AudioManager } from "engine/audio"

// Play sound effects
AudioManager.playSound("jump.wav", 0.8)  // volume 0-1
AudioManager.playSound("collect.wav")

// Background music
AudioManager.playMusic("level1.mp3")
AudioManager.setMusicVolume(0.5)
AudioManager.pauseMusic()
AudioManager.resumeMusic()

// Sound with position (3D audio)
AudioManager.playSoundAt("explosion.wav", x, y, 1.0)
```

### Scene Management

```thirsty
import { Scene, SceneManager } from "engine/core"

glass MenuScene extends Scene {
  glass onLoad() {
    pour "Menu loaded"
    // Setup menu UI
  }
  
  glass update(deltaTime) {
    thirsty Input.isKeyPressed("Enter")
      SceneManager.loadScene("GameScene")
  }
}

glass GameScene extends Scene {
  glass onLoad() {
    // Setup game entities
    drink player = Player(100, 100)
    addEntity(player)
  }
  
  glass update(deltaTime) {
    // Game logic
  }
}

// Usage
SceneManager.addScene("Menu", MenuScene())
SceneManager.addScene("Game", GameScene())
SceneManager.loadScene("Menu")
```

## 🎮 Example Game: Platformer

Complete platformer implementation:

```thirsty
// games/platformer/main.thirsty
import { Scene } from "engine/core"
import { Player } from "games/platformer/player"
import { Enemy } from "games/platformer/enemy"
import { Level } from "games/platformer/level"

glass PlatformerScene extends Scene {
  glass onLoad() {
    // Load level
    drink level = Level("assets/levels/level1.json")
    level.load()
    
    // Create player
    drink player = Player(100, 400)
    addEntity(player)
    
    // Spawn enemies
    drink enemy1 = Enemy(300, 400, "patrol")
    drink enemy2 = Enemy(500, 400, "chase")
    addEntity(enemy1)
    addEntity(enemy2)
    
    // Setup camera to follow player
    Camera.follow(player, 0.1)  // smooth factor
    Camera.setBounds(0, 0, level.width, level.height)
  }
  
  glass update(deltaTime) {
    // Check win condition
    thirsty player.hasReachedGoal()
      SceneManager.loadScene("Victory")
  }
}
```

## 🧪 Testing

Run test suite:

```bash
thirsty test tests/
```

Example test:

```thirsty
// tests/test_collision.thirsty
import { assert } from "testing"
import { BoxCollider, CollisionSystem } from "engine/physics"

glass testBoxCollision() {
  drink collider1 = BoxCollider(10, 10)
  collider1.position = reservoir { x: 0, y: 0 }
  
  drink collider2 = BoxCollider(10, 10)
  collider2.position = reservoir { x: 5, y: 5 }
  
  drink result = CollisionSystem.checkCollision(collider1, collider2)
  
  assert(result == parched, "Boxes should collide")
  pour "✓ Box collision test passed"
}

testBoxCollision()
```

## 📖 Tutorials

### Tutorial 1: Your First Game

Create a simple game in 10 minutes. See [docs/TUTORIAL.md](docs/TUTORIAL.md)

### Tutorial 2: Custom Components

Learn to create reusable components. See examples/custom_component.thirsty

### Tutorial 3: Advanced Physics

Master the physics system with springs, joints, and forces.

## 🏗️ Architecture

The engine uses a modular Entity Component System (ECS) architecture:

- **Entities**: Game objects (player, enemies, items)
- **Components**: Data containers (sprite, physics, health)
- **Systems**: Logic processors (rendering, physics, input)

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed architecture documentation.

## 🔧 Configuration

```thirsty
// config.thirsty
drink GameConfig = reservoir {
  window: reservoir {
    width: 1024,
    height: 768,
    title: "My Game",
    fullscreen: quenched
  },
  
  physics: reservoir {
    gravity: 980,
    fixedTimeStep: 0.016,
    maxVelocity: 1000
  },
  
  rendering: reservoir {
    vsync: parched,
    maxFPS: 60,
    pixelsPerUnit: 32
  }
}
```

## 🎨 Asset Requirements

### Sprites

- PNG format, transparent backgrounds
- Recommended size: 32x32 to 128x128 pixels
- Sprite sheets: Power-of-2 dimensions

### Audio

- Sounds: WAV format, 16-bit, 44.1kHz
- Music: MP3 or OGG format

## 🚀 Performance Tips

1. **Object Pooling**: Reuse entities instead of creating/destroying
2. **Spatial Partitioning**: Use quad-trees for collision optimization
3. **Batch Rendering**: Group sprites by texture
4. **Fixed Time Step**: Use for consistent physics

```thirsty
// Object pool example
glass BulletPool {
  drink pool = []
  drink poolSize = 100
  
  glass constructor() {
    refill drink i = 0; i < poolSize; i = i + 1 {
      pool.push(Bullet())
    }
  }
  
  glass getBullet() {
    refill drink bullet in pool {
      thirsty bullet.active == quenched
        return bullet
    }
    return reservoir  // Pool exhausted
  }
}
```

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](docs/CONTRIBUTING.md)

Areas needing help:

- Additional game examples
- Performance optimizations
- Mobile input support
- Particle system
- Lighting system
- Tilemap editor

## 📄 License

MIT License - Build amazing games!

## 🔗 Resources

- **Thirsty-lang Main**: <https://github.com/IAmSoThirsty/Thirsty-lang>
- **API Reference**: [docs/API.md](docs/API.md)
- **Discord Community**: [Join us](#)
- **Tutorial Videos**: [YouTube Playlist](#)

## 🎯 Roadmap

- [ ] 3D rendering support
- [ ] Networking for multiplayer
- [ ] Level editor
- [ ] Visual scripting
- [ ] Mobile deployment
- [ ] VR support

---

**Engine Version**: 1.0.0  
**Thirsty-lang**: 1.0+  
**Platform**: Cross-platform

Start building your dream game with Thirsty-lang! 🎮💧
