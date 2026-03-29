<!-- # ============================================================================ # -->
<!-- # STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59 # -->
<!-- # COMPLIANCE: Sovereign Substrate / EXPANSIONS.md # -->
<!-- # ============================================================================ # -->


<!-- # COMPLIANCE: Sovereign Substrate / EXPANSIONS.md # -->

<div align="right">
  <img src="https://img.shields.io/badge/DATE-2026-03-18-blueviolet?style=for-the-badge" alt="Date" />
  <img src="https://img.shields.io/badge/PRODUCTIVITY-ACTIVE-success?style=for-the-badge" alt="Productivity" />
</div>
<!-- # ============================================================================ #


<!-- # COMPLIANCE: Sovereign Substrate / EXPANSIONS.md # -->
<!-- # ============================================================================ #

<!--                                         [2026-03-03 13:45] -->
<!--                                        Productivity: Active -->
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

### Additional Features

- **Loops**: `refill` for iteration
- **Functions**: `glass` for function declarations
- **Arrays**: `reservoir` for collections
- **Objects**: `bottle` for structured data

### New Keywords

- `refill times` - For loop
- `refill while` - While loop
- `glass name(params)` - Function definition
- `sip` - Input from user
- `reservoir` - Array declaration
- `bottle` - Object declaration
- `return` - Return from function

### Example

```thirstyplusplus
glass calculateHydration(weight)
  drink dailyWater = weight * 0.033
  return dailyWater

drink myWeight = 70
drink needed = calculateHydration(myWeight)
pour needed

reservoir drinks = ["water", "juice", "tea"]
refill 3 times
  pour drinks[index]
```

**Use when**: Building complex applications with functions and data structures.

## ThirstOfGods (Ultimate Edition)

The most powerful variant with divine capabilities:

### Additional Features

- **Async/Await**: `cascade` and `await` for asynchronous operations
- **Classes**: `fountain` for object-oriented programming
- **Modules**: `import` and `export` for code organization
- **Error Handling**: `spillage` (try) and `cleanup` (catch)
- **Advanced Types**: Generics and type checking
- **Decorators**: Meta-programming capabilities

### New Keywords

- `fountain ClassName` - Class declaration
- `cascade` - Async function
- `await` - Wait for async operation
- `spillage` - Try block
- `cleanup` - Catch block
- `import` - Module import
- `export` - Module export
- `sacred` - Constant declaration
- `ocean` - Map/dictionary
- `stream` - Generator function

### Example

```thirstofgods
fountain HydrationTracker
  drink totalWater = 0

  glass addWater(amount)
    this.totalWater = this.totalWater + amount
    pour "Added " + amount + " liters"

  glass getTotal()
    return this.totalWater

cascade glass fetchWeatherData()
  drink data = await getWeather()
  return data

spillage
  drink tracker = new HydrationTracker()
  tracker.addWater(2.5)
  pour tracker.getTotal()
cleanup error
  pour "Spillage occurred: " + error
```

**Use when**: Building enterprise-level applications with the power of gods!

## Choosing Your Edition

| Feature | Base | Thirsty+ | Thirsty++ | ThirstOfGods |
|---------|------|----------|-----------|--------------|
| Variables | ✓ | ✓ | ✓ | ✓ |
| Output | ✓ | ✓ | ✓ | ✓ |
| Control Flow | ✗ | ✓ | ✓ | ✓ |
| Loops | ✗ | ✗ | ✓ | ✓ |
| Functions | ✗ | ✗ | ✓ | ✓ |
| Classes | ✗ | ✗ | ✗ | ✓ |
| Async/Await | ✗ | ✗ | ✗ | ✓ |
| Error Handling | ✗ | ✗ | ✗ | ✓ |
| Modules | ✗ | ✗ | ✗ | ✓ |

## Running Different Editions

```bash

# Base Thirsty-lang

npm start examples/hello.thirsty

# Thirsty+

npm run thirstyplus examples/control-flow.thirstyplus

# Thirsty++

npm run thirstyplusplus examples/functions.thirstyplusplus

# ThirstOfGods

npm run thirstofgods examples/classes.thirstofgods
```

## Migration Path

Start with base Thirsty-lang and upgrade as your thirst grows! Each edition is backward compatible with the previous one.

Stay hydrated at every level! 💧✨
