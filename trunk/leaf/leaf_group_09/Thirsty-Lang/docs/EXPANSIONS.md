<!-- # ============================================================================ # -->
<!-- # STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59 # -->
<!-- # COMPLIANCE: Sovereign Substrate / EXPANSIONS.md # -->
<!-- # ============================================================================ # -->
<!-- # ============================================================================ #


<!-- # COMPLIANCE: Sovereign Substrate / EXPANSIONS.md # -->
<!-- # ============================================================================ #

<!-- # Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master -->
<div align="right">
  <img src="https://img.shields.io/badge/DATE-2026-03-18-blueviolet?style=for-the-badge" alt="Date" />
  <img src="https://img.shields.io/badge/PRODUCTIVITY-ACTIVE-success?style=for-the-badge" alt="Productivity" />
</div>

# Thirsty-lang Expansions

Thirsty-lang comes in multiple flavors to suit different levels of thirst! 💧

## Base: Thirsty-lang

The core language with basic features:

- Variable declaration (`drink`)
- Output (`pour`)
- Comments

**Use when**: You're just starting your hydration journey.

## Thirsty+ (Thirsty Plus)

Enhanced features for intermediate users:

### Additional Features

- **Control Flow**: `thirsty` (if) and `hydrated` (else)
- **Arithmetic**: Basic math operations (+, -, *, /)
- **Comparison**: equals, greater than, less than
- **String concatenation**: Join strings with `+`

### New Keywords

- `thirsty condition` - If statement
- `hydrated` - Else statement
- `parched` - Boolean true
- `quenched` - Boolean false

### Example

```thirstyplus
drink temperature = 25
thirsty temperature > 20
  pour "It's warm! Drink more water!"
hydrated
  pour "Stay hydrated anyway!"
```

**Use when**: You need basic logic and control flow.

## Thirsty++ (Thirsty Plus Plus)

Advanced features for power users:

### ✅ Implemented Features

- **Loops**: `refill` for iteration
- **Functions**: `glass` for function declarations with parameters and return values
- **Arrays**: `reservoir` for dynamic collections
- **Standard Library**: Built-in Math and String utilities

### Keywords

- `refill condition` - While loop
- `glass name(params)` - Function definition
- `sip` - Input from user
- `reservoir` - Array declaration
- `return` - Return from function

### Example

```thirstyplusplus
glass calculateHydration(weight) {
  drink dailyWater = weight * 0.033
  return dailyWater
}

drink myWeight = 70
drink needed = calculateHydration(myWeight)
pour needed

reservoir drinks = ["water", "juice", "tea"]
drink i = 0
refill i < drinks.length {
  pour drinks[i]
  drink i = i + 1
}

// Using standard library
drink area = Math.PI * Math.pow(5, 2)
pour "Circle area: " + area
```

**Use when**: Building complex applications with functions and data structures.

## ThirstOfGods (Ultimate Edition)

The most powerful variant with divine capabilities:

### ✅ Implemented Features

- **Classes**: `fountain` for object-oriented programming
- **Object Instantiation**: Create instances of classes
- **Class Methods**: Define and call methods on instances
- **Class Properties**: Instance variables with default values
- **this keyword**: Access instance properties within methods

### 🔮 Future Features (Planned)

- **Async/Await**: `cascade` and `await` for asynchronous operations
- **Modules**: `import` and `export` for code organization
- **Error Handling**: `spillage` (try) and `cleanup` (catch)

### Keywords

- `fountain ClassName` - Class declaration
- `this` - Reference to instance properties

### Example

```thirstofgods
fountain HydrationTracker {
  drink totalWater = 0
  drink goal = 2000

  glass addWater(amount) {
    drink this.totalWater = this.totalWater + amount
    pour "Added " + amount + "ml. Total: " + this.totalWater + "ml"
  }

  glass checkGoal() {
    thirsty this.totalWater >= this.goal {
      pour "Goal reached! Great hydration!"
      return true
    }
    hydrated {
      drink remaining = this.goal - this.totalWater
      pour "Still need " + remaining + "ml to reach goal"
      return false
    }
  }
}

drink tracker = HydrationTracker()
tracker.addWater(500)
tracker.addWater(800)
tracker.checkGoal()
```

**Use when**: Building enterprise-level applications with object-oriented design.

## Choosing Your Edition

| Feature | Base | Thirsty+ | Thirsty++ | ThirstOfGods |
|---------|------|----------|-----------|--------------|
| Variables | ✓ | ✓ | ✓ | ✓ |
| Output | ✓ | ✓ | ✓ | ✓ |
| Control Flow | ✗ | ✓ | ✓ | ✓ |
| Operators | ✗ | ✓ | ✓ | ✓ |
| Loops | ✗ | ✓ | ✓ | ✓ |
| Functions | ✗ | ✗ | ✓ | ✓ |
| Arrays | ✗ | ✗ | ✓ | ✓ |
| Standard Library | ✗ | ✗ | ✓ | ✓ |
| Classes | ✗ | ✗ | ✗ | ✓ |
| OOP | ✗ | ✗ | ✗ | ✓ |

## Running Your Code

All editions are currently available in the standard Thirsty-lang interpreter:

```bash

# Run any Thirsty-lang program

npm start examples/hello.thirsty
npm start examples/functions.thirsty
npm start examples/arrays.thirsty
npm start examples/classes.thirsty
npm start examples/stdlib.thirsty
```

**Note:** All features from all editions are available by default. The edition system is designed as a progressive learning path rather than separate runtime modes.

## Migration Path

Start with base Thirsty-lang and upgrade as your thirst grows! Each edition is backward compatible with the previous one.

1. **Start with Base**: Learn variables and output
2. **Move to Thirsty+**: Add control flow and conditionals
3. **Advance to Thirsty++**: Master functions, arrays, and the standard library
4. **Ascend to ThirstOfGods**: Embrace object-oriented programming

Stay hydrated at every level! 💧✨
