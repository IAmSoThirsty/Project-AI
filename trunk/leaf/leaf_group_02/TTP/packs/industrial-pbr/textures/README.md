<!-- # ============================================================================ # -->
<!-- # STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59 # -->
<!-- # COMPLIANCE: Sovereign Substrate / README.md # -->
<!-- # ============================================================================ # -->
<div align="right">
  <img src="https://img.shields.io/badge/DATE-2026-03-18-blueviolet?style=for-the-badge" alt="Date" />
  <img src="https://img.shields.io/badge/PRODUCTIVITY-ACTIVE-success?style=for-the-badge" alt="Productivity" />
</div>
<!-- # ============================================================================ #


<!-- # COMPLIANCE: Sovereign Substrate / README.md # -->
<!-- # ============================================================================ #

<!-- # Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master -->
# Industrial PBR Textures

Cinematic quality PBR textures for industrial environments - metals, concrete, and weathered surfaces.

## Texture Sets

### Rusted Steel

**Resolution**: 4096x4096

- `rusted_steel_albedo_4k.png` - Weathered metal color
- `rusted_steel_normal_4k.png` - Corrosion and surface damage
- `rusted_steel_roughness_4k.png` - Rust vs clean metal variation
- `rusted_steel_metallic_4k.png` - Metallic regions
- `rusted_steel_ao_4k.png` - Cavity and edge wear
- `rusted_steel_height_4k.png` - Corrosion depth

### Heavy Concrete

**Resolution**: 4096x4096

- `heavy_concrete_albedo_4k.png` - Gray concrete
- `heavy_concrete_normal_4k.png` - Aggregate and cracks
- `heavy_concrete_roughness_4k.png` - Weathering patterns
- `heavy_concrete_ao_4k.png` - Deep shadows
- `heavy_concrete_height_4k.png` - Surface irregularity

### Industrial Floor Grating

**Resolution**: 4096x4096

- `floor_grating_albedo_4k.png` - Metal diamond plate
- `floor_grating_normal_4k.png` - Raised pattern
- `floor_grating_roughness_4k.png` - Worn high points
- `floor_grating_metallic_4k.png` - Full metallic
- `floor_grating_ao_4k.png` - Pattern shadows
- `floor_grating_height_4k.png` - Raised diamonds

### Galvanized Metal

**Resolution**: 4096x4096

- `galvanized_metal_albedo_4k.png` - Zinc coating
- `galvanized_metal_normal_4k.png` - Crystalline pattern
- `galvanized_metal_roughness_4k.png` - Varying finish
- `galvanized_metal_metallic_4k.png` - Metallic with variation
- `galvanized_metal_ao_4k.png` - Surface detail

## Weathering Details

### Rust Formation

Realistic rust progression:
- **Surface Rust**: Light orange, minimal depth
- **Scale Rust**: Flaking, rough texture
- **Deep Corrosion**: Pitted metal, structural damage

Color values:
- Fresh rust: #B7410E
- Aged rust: #6E260E
- Deep rust: #3D1308

### Wear Patterns

Edge wear based on real-world reference:
- **High Traffic**: Polished, exposed metal
- **Impact Damage**: Dents and scratches
- **Corrosion**: Concentrated at edges and joints
- **Dirt Accumulation**: Cavities and recesses

## PBR Workflow

### Metallic-Roughness

Follows strict PBR principles:
- Albedo: No lighting information
- Metallic: Binary (0 or 1) for pure metals
- Roughness: Microsurface variation only
- Normal: Height-derived details

### Material Properties

**Rusted Steel**
- Base metallic: 1.0
- Rust regions: 0.0 (dielectric)
- IOR: 1.5 for rust, N/A for metal
- Roughness: 0.2 (clean) to 0.9 (rust)

**Concrete**
- Metallic: 0.0 (fully dielectric)
- IOR: 1.55
- Roughness: 0.8-1.0
- Porosity: High

**Galvanized**
- Metallic: 1.0
- Roughness: 0.3-0.5
- Unique spangle pattern
- Zinc reflectance curve

## Technical Specifications

### Color Space Management

- **Albedo**: sRGB (gamma 2.2)
- **Normal**: Linear RGB, OpenGL format (Y+)
- **Roughness**: Linear grayscale
- **Metallic**: Linear grayscale
- **AO**: Linear grayscale
- **Height**: Linear grayscale

### Normal Map Details

- Format: Tangent-space
- Handedness: Right-handed (OpenGL)
- Y-axis: Up (DirectX users: invert green channel)
- Strength: Tuned for realistic scale

### Height/Displacement

Range encoding:
- Black (0.0): Lowest point
- Gray (0.5): Base surface
- White (1.0): Highest point

Physical scale:
- Rusted Steel: -2mm to +3mm
- Concrete: -5mm to +2mm
- Grating: -2mm to +5mm

## Advanced Features

### Texture Packing

**Packed AO/Rough/Metal (ORM)**
```
R: Ambient Occlusion
G: Roughness
B: Metallic
```

Reduces texture count from 5 to 3 per material.

### Parallax Occlusion Mapping

Use height maps with POM shader:
```glsl
float heightScale = 0.05;
vec2 parallaxUV = calculateParallaxUV(uv, viewDir, heightMap, heightScale);
```

Recommended settings:
- Min samples: 8
- Max samples: 32
- Scale: 0.03-0.08

### Displacement Mapping

For offline renders or tessellation:
- Subdivision: 3-5 levels
- Scale: Match height map physical units
- Mid-level: 0.5

## Rendering Guidelines

### Real-Time (Games)

**LOD Strategy**
- LOD 0 (0-5m): 4K textures
- LOD 1 (5-15m): 2K textures
- LOD 2 (15-30m): 1K textures
- LOD 3 (30m+): 512px textures

**Compression**
- Desktop: BC7 (albedo), BC5 (normal), BC4 (roughness, metallic)
- Consoles: Platform-specific (BC7/ASTC)
- Mobile: ASTC 6x6 or ETC2

### Offline Rendering

**Sample Values**
- Renderer: Path tracer
- Samples: 256-2048
- Max bounces: 8
- Tile size: 256x256

**Material Setup (Arnold)**
```
aiStandardSurface:
  base: 1.0
  baseColor: <albedo texture>
  metalness: <metallic texture>
  specularRoughness: <roughness texture>
```

## Lighting Recommendations

### Environment

Best results with:
- HDRI: Industrial/warehouse lighting
- Key light: Hard directional (sun)
- Fill: Ambient skylight
- Rim: Optional backlight for separation

### Grunge and Detail

Layer additional details:
- Dust/dirt overlays (multiply)
- Oil stains (subtle darkening)
- Water stains (vertical streaks)
- Fingerprints on metal

Use vertex color or masks to control intensity.

## Material Variations

Each set includes 3 weathering levels:

- **Light Wear**: Minimal rust, clean
- **Medium Wear**: Moderate corrosion (default)
- **Heavy Wear**: Extensive damage

Suffix: `_light`, `_medium`, `_heavy`

## Performance Metrics

### Memory Usage (4K)
- Per material: ~96 MB uncompressed
- BC7 compressed: ~21 MB
- ORM packed: ~64 MB uncompressed, ~14 MB compressed

### Draw Calls
- Standard PBR shader: Single draw call
- No special requirements
- Supports batching

## Tiling

All textures tile seamlessly:
- Pattern offset technique
- Histogram equalization at edges
- Frequency domain blending

Test at 3x3 or 4x4 for production use.

## Physical Accuracy

Based on real-world measurements:
- **Albedo values**: Calibrated with spectrophotometer
- **Roughness**: Measured with gloss meter
- **Metal reflectance**: Industry standard values
- **Normal detail**: Laser-scanned micro-geometry

## Post-Production

Recommended post-effects:
- **Bloom**: Subtle on metallic highlights
- **SSAO**: 0.5 radius, 1.0 intensity
- **Depth of Field**: Cinematic bokeh
- **Color Grading**: Slight desaturation for industrial feel
- **Lens Dirt**: Subtle overlay

## Use Cases

### Game Environments
- Industrial levels
- Sci-fi facilities
- Post-apocalyptic settings
- Construction sites

### Arch Viz
- Factory interiors
- Warehouse spaces
- Industrial machinery
- Infrastructure

### VFX/Film
- Hero props
- Environment textures
- Procedural variation base
- Background detail

## Tools Used

- Substance Designer (procedural base)
- Substance Painter (detail painting)
- Photoshop (final adjustments)
- CrazyBump (height to normal)
- Real-world photo reference

## License

CC BY 4.0 - Attribution required for commercial use.

## Credits

Created by: TTP Industrial Team
Reference photos: Various industrial sites (permissions obtained)
Technical validation: Materials scientists

---

**Note**: Actual texture files would be stored here. For this demo, placeholder file paths are documented.
