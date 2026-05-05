# Packages and Great Wells

## Package manifest

Every package may carry a `thirsty.json` manifest:

```json
{
  "name": "coolpkg",
  "version": "1.0.0",
  "entry": "src/main.thirsty",
  "description": "A package from the Great Wells",
  "tags": ["great-well", "hydrated"]
}
```

## Commands

- `thirsty publish .`
- `thirsty gallery list`
- `thirsty gallery search echo`
- `thirsty gallery show coolpkg`
- `thirsty install coolpkg`
- `thirsty packages list`

## Built-in importable modules

- `thirst::time`
- `thirst::crypto`
- `thirst::reservoir`
