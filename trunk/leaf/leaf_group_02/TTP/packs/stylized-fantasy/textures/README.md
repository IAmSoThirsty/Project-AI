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
# Stylized Fantasy Textures

Hand-painted textures with a fantasy art style inspired by games like World of Warcraft and Torchlight.

## Texture Sets

### Stone Brick Wall

**Resolution**: 2048x2048

- `stone_brick_albedo.png` - Hand-painted stone color
- `stone_brick_normal.png` - Sculpted detail normal map
- `stone_brick_roughness.png` - Surface variation
- `stone_brick_ao.png` - Painted ambient occlusion

### Magical Crystals

**Resolution**: 2048x2048

- `crystal_albedo.png` - Vibrant crystal colors
- `crystal_normal.png` - Faceted geometry
- `crystal_roughness.png` - Smooth vs rough faces
- `crystal_emission.png` - Glowing core
- `crystal_opacity.png` - Transparency mask

### Enchanted Wood

**Resolution**: 2048x2048

- `enchanted_wood_albedo.png` - Stylized wood grain
- `enchanted_wood_normal.png` - Carved runes and detail
- `enchanted_wood_roughness.png` - Polished vs weathered
- `enchanted_wood_emission.png` - Glowing rune lines
- `enchanted_wood_ao.png` - Artistic shadows

### Fantasy Metal

**Resolution**: 2048x2048

- `fantasy_metal_albedo.png` - Gold and bronze tones
- `fantasy_metal_normal.png` - Ornate engravings
- `fantasy_metal_roughness.png` - Tarnish patterns
- `fantasy_metal_metallic.png` - Metallic mask
- `fantasy_metal_ao.png` - Detail shadows

## Art Style

### Visual Characteristics
- Reduced color palette
- Exaggerated proportions
- Painted highlights and shadows
- Soft edges, no photorealism
- Vibrant, saturated colors
- Hand-painted feel

### Inspiration
- **Color Theory**: Complementary color schemes
- **Lighting**: Baked artistic lighting
- **Details**: Painterly brush strokes visible
- **Stylization**: 70% stylized, 30% realistic

## Color Palette

### Stone
- Base: #8B7D6B
- Highlights: #C4B5A0
- Shadows: #4A4238
- Accent: #6B8E23 (moss)

### Crystals
- Blue: #4169E1, #87CEEB
- Purple: #8B008B, #DA70D6
- Green: #32CD32, #90EE90
- Emission: Pure white #FFFFFF

### Wood
- Base: #8B4513
- Grain: #654321
- Runes: #FFD700 (gold)
- Age: #2F4F2F (dark green)

### Metal
- Gold: #FFD700, #DAA520
- Bronze: #CD7F32, #8B4513
- Patina: #2E8B57
- Shine: #FFFACD

## Technical Details

### Texturing Workflow
1. Block out forms in 3D
2. Hand-paint base colors in Substance Painter
3. Add stylized details with custom brushes
4. Bake lighting information into albedo
5. Create supporting PBR maps

### Brush Settings
- Opacity: 60-80%
- Flow: Variable with pen pressure
- Spacing: 10-15%
- Hardness: 30-50% for soft edges

## PBR Implementation

While stylized, these textures still use PBR:

### Albedo
- Contains some ambient lighting (stylized)
- Pure colors without heavy shadow/light
- Saturation: Higher than photorealistic

### Normal
- Moderate strength (0.5-0.8)
- Artistic, not accurate to geometry
- Enhances painted details

### Roughness
- Higher contrast than realistic
- 0.3-0.7 typical range
- Painterly variation

### Metallic
- Binary: 0 or 1 mostly
- Artistic metals (not physically accurate)
- Gold has slight roughness

## Magical Effects

### Glowing Elements

Emission maps for magical glow:
```glsl
vec3 emission = texture(emissionMap, uv).rgb;
emission *= glowIntensity * (0.5 + 0.5 * sin(time * frequency));
finalColor += emission;
```

### Crystal Refraction
```glsl
// Simple fake refraction
vec3 refractedUV = uv + normal.xy * refractionStrength;
vec3 refractColor = texture(sceneColor, refractedUV).rgb;
finalColor = mix(crystalColor, refractColor, transparency);
```

### Rune Animation
Animate emission intensity:
- Pulse frequency: 1-2 Hz
- Min intensity: 0.3
- Max intensity: 1.0

## Tiling

All textures tile seamlessly:
- Manual painting across seams
- Mirror and blend technique
- Tested at 4x4 tiling

Minimize tiling artifacts:
- Add detail variation (cracks, moss)
- Offset UVs slightly per object
- Use vertex color variation

## Material Variations

Include 3 color variations per material:

- **Variation 1**: Original
- **Variation 2**: Hue shift +30°
- **Variation 3**: Hue shift -30°

Blend in shader using vertex colors or ID maps.

## Usage Guidelines

### Lighting
- Works best with stylized lighting
- Ambient light: Slightly colored
- Rim lighting: Exaggerated
- Shadows: Soft, artistic

### Shading Model
```glsl
// Stylized specular
float specular = pow(saturate(dot(H, N)), glossiness);
specular = step(0.5, specular) * 0.8;  // Toon shading

// Stylized diffuse
float diffuse = dot(N, L) * 0.5 + 0.5; // Half-Lambert
diffuse = smoothstep(0.4, 0.6, diffuse); // Smooth step
```

### Post-Processing
- Slight bloom on emission
- Color grading: Vibrant
- Outlines: Optional cel-shading
- Vignette: Subtle

## Performance

Optimized for real-time:
- 2K resolution suitable for hero assets
- 1K for background props
- Standard PBR shader compatible
- Low overdraw on crystals

## File Sizes

Approximate sizes:
- Per material (5 maps): ~25 MB uncompressed
- BC7 compressed: ~8 MB
- Mobile (ASTC): ~6 MB

## Integration Examples

### Unity
```csharp
// Set up stylized material
material.SetTexture("_MainTex", albedo);
material.SetTexture("_BumpMap", normal);
material.SetFloat("_BumpScale", 0.7f);
material.SetTexture("_EmissionMap", emission);
material.EnableKeyword("_EMISSION");
```

### Unreal
Use base material with stylized shading:
- Lighting Mode: Stylized
- Two-sided: Yes (for foliage)
- Blend Mode: Translucent (crystals)

## Artist Notes

Created using:
- Sculpting: ZBrush
- Painting: Substance Painter + custom brushes
- Baking: Marmoset Toolbag
- Touch-up: Photoshop

Artistic direction:
- Focus on readable shapes
- Emphasize silhouette
- Color > realism
- Fun > accuracy

## License

CC BY 4.0 - Attribution required.

---

**Note**: Actual texture files would be stored here. For this demo, placeholder file paths are documented.
