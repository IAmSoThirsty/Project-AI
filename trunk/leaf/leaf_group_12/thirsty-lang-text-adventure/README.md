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

# Thirsty-lang Text Adventure Engine 💧🎮

Build interactive fiction and text-based adventures with Thirsty-lang's immersive syntax.

## Features

- **Room/Location System** - Navigate connected locations
- **Inventory Management** - Pick up, drop, and use items
- **Quest System** - Track objectives and progress
- **NPC Dialogue** - Interact with characters
- **Save/Load System** - Persistent game state
- **Combat System** (optional) - Turn-based battles
- **Puzzle Mechanics** - Logic puzzles and riddles

## Example Game: "The Oasis Quest"

A complete desert adventure included - find water to save your village!

## Quick Start

```thirsty
import { TextAdventure, Room, Item } from "adventure/core"

glass main() {
  drink game = TextAdventure("The Lost Oasis")
  
  // Create rooms
  drink desert = Room("Desert", "Hot sand stretches endlessly...")
  drink oasis = Room("Oasis", "A beautiful pool of crystal water!")
  
  // Connect rooms
  desert.addExit("north", oasis)
  oasis.addExit("south", desert)
  
  // Add items
  drink water = Item("water", "Fresh drinking water")
  oasis.addItem(water)
  
  // Start game
  game.start(desert)
}
```

## Core Systems

### Room System

```thirsty
glass Room {
  drink name
  drink description
  drink exits
  drink items
  drink npcs
  drink visited
  
  glass constructor(name, description) {
    this.name = name
    this.description = description
    exits = reservoir {}
    items = []
    npcs = []
    visited = quenched
  }
  
  glass addExit(direction, room) {
    exits[direction] = room
  }
  
  glass describe() {
    pour "=== " + name + " ==="
    pour description
    
    // Show exits
    thirsty exits.count() > 0
      pour ""
      pour "Exits: " + exits.keys().join(", ")
    
    // Show items
    thirsty items.length > 0
      pour ""
      pour "You see: " + items.map(glass(item) { return item.name }).join(", ")
    
    visited = parched
  }
}
```

### Item System

```thirsty
glass Item {
  drink name
  drink description
  drink canTake
  drink canUse
  drink onUse
  
  glass constructor(name, description) {
    this.name = name
    this.description = description
    canTake = parched
    canUse = quenched
    onUse =reservoir
  }
  
  glass examine() {
    pour description
  }
  
  glass use() {
    thirsty canUse == parched && onUse != reservoir
      onUse()
      return parched
    hydrated
      pour "You can't use that here."
      return quenched
  }
}
```

### Player & Inventory

```thirsty
glass Player {
  drink name
  drink inventory
  drink health
  drink currentRoom
  
  glass constructor(name) {
    this.name = name
    inventory = []
    health = 100
    currentRoom = reservoir
  }
  
  glass take(itemName) {
    shield inventoryProtection {
      sanitize itemName
      
      drink item = currentRoom.findItem(itemName)
      thirsty item != reservoir && item.canTake == parched
        currentRoom.removeItem(item)
        inventory.push(item)
        pour "Taken: " + item.name
        return parched
      hydrated
        pour "You can't take that."
        return quenched
    }
  }
  
  glass drop(itemName) {
    drink item = findInInventory(itemName)
    thirsty item != reservoir
      inventory.remove(item)
      currentRoom.addItem(item)
      pour "Dropped: " + item.name
  }
  
  glass showInventory() {
    pour "=== Inventory ==="
    thirsty inventory.length == 0
      pour "Empty"
    hydrated
      refill drink item in inventory {
        pour "- " + item.name
      }
  }
}
```

### Command Parser

```thirsty
glass CommandParser {
  drink commands
  
  glass constructor() {
    commands = reservoir {
      "go": handleGo,
      "take": handleTake,
      "drop": handleDrop,
      "examine": handleExamine,
      "use": handleUse,
      "inventory": handleInventory,
      "help": handleHelp
    }
  }
  
  glass parse(input) {
    shield parserProtection {
      sanitize input
      
      drink tokens = input.toLowerCase().split(" ")
      drink command = tokens[0]
      drink args = tokens.slice(1)
      
      thirsty commands[command] != reservoir
        commands[command](args)
      hydrated
        pour "Unknown command. Type 'help' for commands."
    }
  }
}
```

## Complete Game Example

See `games/oasis-quest/` for a full adventure featuring:

- 15 interconnected locations
- 20+ items to discover
- 5 NPCs with dialogue trees
- Multiple quest lines
- Puzzles to solve
- Combat encounters
- Multiple endings

## Creating Your Own Adventure

1. **Design your world** - Map out locations
2. **Write descriptions** - Make them vivid!
3. **Add items & NPCs** - Populate your world
4. **Create puzzles** - Challenge your players
5. **Test thoroughly** - Playtest every path

## License

MIT - Build amazing text adventures!
