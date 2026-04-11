# TSCG Enhanced Compression System

**Achieves 80%+ compression ratio on governance text** through adaptive algorithms, context-aware encoding, and streaming support.

## Features

### 1. Adaptive Algorithm Selection
Automatically selects the best compression algorithm based on content analysis:
- **LZ4**: Fast compression for small data and real-time use
- **Zstd**: Best balance for structured data (level 22)
- **Brotli**: Maximum compression for text with patterns (quality 11)
- **zlib**: Fallback for compatibility

### 2. Content-Aware Analysis
Detects content types and optimizes accordingly:
- Governance text (constitutional documents, proposals)
- TSCG symbolic flows
- JSON structured data
- Binary frames

### 3. Context-Aware Encoding
Preprocesses governance text by replacing verbose terms with compact symbols:
- "Selection pressure" → "SEL"
- "Capability authorization" → "CAP"
- "Constitutional" → compressed forms
- Fully reversible with `postprocess()`

### 4. Dictionary Learning
Trains custom dictionaries on governance corpus:
- Learns common governance patterns
- Optimized for repeated policy terminology
- Supports save/load for reuse

### 5. Streaming Compression
Real-time compression for network protocols:
- Chunk-based processing (64KB default)
- Minimal memory footprint
- Supports ZSTD, LZ4, and zlib streaming

## Benchmark Results

```
Context-Aware Encoding + Maximum Compression
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Realistic Doc (Brotli-11): 10,160 → 1,598 bytes (84.3% reduction)
Realistic Doc (ZSTD-22):   10,160 → 2,033 bytes (80.0% reduction)

✓ TARGET ACHIEVED: 84.3% compression (vs 69.7% baseline)
```

## Usage Examples

### Basic Compression

```python
from Project_AI.utils.tscg_enhanced import AdaptiveCompressor

# Create compressor
compressor = AdaptiveCompressor()

# Compress data (automatically selects best algorithm)
data = b"governance text..."
compressed = compressor.compress(data)

# Decompress
original = compressor.decompress(compressed)

# Get statistics
stats = compressor.get_stats()
print(f"Compression ratio: {compressor.get_compression_ratio():.1f}%")
```

### Context-Aware Encoding

```python
from Project_AI.utils.tscg_enhanced import (
    AdaptiveCompressor,
    ContextAwareEncoder
)

compressor = AdaptiveCompressor()
encoder = ContextAwareEncoder()

# Compress with context awareness
text = "Constitutional amendment requires capability authorization..."
compressed = encoder.encode_with_context(text, compressor)

# Decompress and restore context
restored = encoder.decode_with_context(compressed, compressor)
```

### Dictionary Learning

```python
from Project_AI.utils.tscg_enhanced import (
    TSCGDictionary,
    AdaptiveCompressor
)

# Train dictionary on samples
samples = [
    "proposal for quorum adjustment...",
    "governance framework modification...",
    "constitutional amendment procedure..."
]

dictionary = TSCGDictionary()
dictionary.train(samples)

# Use dictionary for compression
compressor = AdaptiveCompressor(dictionary=dictionary)
compressed = compressor.compress(data)

# Save dictionary for reuse
dictionary.save("governance_dict.pkl")

# Load dictionary
dictionary.load("governance_dict.pkl")
```

### Streaming Compression

```python
from io import BytesIO
from Project_AI.utils.tscg_enhanced import (
    StreamingCompressor,
    CompressionAlgorithm
)

# Create streaming compressor
stream_comp = StreamingCompressor(algorithm=CompressionAlgorithm.ZSTD)

# Compress stream
input_stream = BytesIO(large_data)
output_stream = BytesIO()
stream_comp.compress_stream(input_stream, output_stream)

# Decompress stream
output_stream.seek(0)
decompressed_stream = BytesIO()
stream_comp.decompress_stream(output_stream, decompressed_stream)
```

### Convenience Functions

```python
from Project_AI.utils.tscg_enhanced import (
    compress_governance_text,
    decompress_governance_text,
    create_enhanced_compressor
)

# Quick governance text compression
text = "Constitutional proposal..."
compressed = compress_governance_text(text)
restored = decompress_governance_text(compressed)

# Create compressor with dictionary training
samples = ["sample1", "sample2", "sample3"]
compressor = create_enhanced_compressor(dictionary_samples=samples)
```

## Frame Format

Enhanced TSCG frames use the following binary format:

```
[4B Magic: "TSCE"]
[1B Version: 0x01]
[1B Algorithm: LZ4|ZSTD|BROTLI|ZLIB]
[1B ContentType: GOVERNANCE|SYMBOLIC|BINARY|JSON]
[1B Flags: Reserved]
[4B Original Size]
[4B Compressed Size]
[NB Compressed Payload]
[4B CRC32 Checksum]
```

## Algorithm Comparison

On governance text (4,581 bytes):

| Algorithm | Size    | Ratio | Speed     |
|-----------|---------|-------|-----------|
| ZLIB      | 1,831 B | 60.0% | 2.9 MB/s  |
| LZ4       | 2,561 B | 44.1% | 4.4 MB/s  |
| ZSTD-22   | 1,813 B | 60.4% | 4.3 MB/s  |
| Brotli-11 | 1,419 B | 69.0% | 0.7 MB/s  |

**Best for text**: Brotli-11 (highest ratio)
**Best for speed**: LZ4 (fastest)
**Best balance**: ZSTD-22 (good ratio + speed)

## Performance Characteristics

- **Small data** (<512 bytes): LZ4 selected for speed
- **Governance text**: Brotli selected for maximum compression
- **Symbolic flows**: ZSTD with context preprocessing
- **Binary data**: LZ4 for fast throughput
- **Streaming**: ZSTD for balanced performance

## Dependencies

```
pip install lz4 pyzstd brotli
```

## Testing

Run comprehensive benchmark suite:

```bash
cd Project-AI/utils
python benchmark_tscg_enhanced.py
```

Expected output:
```
✓ TARGET ACHIEVED: 80%+ compression ratio met!
✓ Enhanced TSCG compression system validated
```

## Integration with Existing TSCG

The enhanced compression is fully compatible with existing TSCG:

```python
from project_ai.utils.tscg import TSCGEncoder, TSCGDecoder
from Project_AI.utils.tscg_enhanced import AdaptiveCompressor

# Encode TSCG expression
encoder = TSCGEncoder()
expression = encoder.encode_flow([
    {"name": "ING"},
    "→",
    {"name": "COG"},
    "→",
    {"name": "QRM"}
])

# Compress with enhanced system
compressor = AdaptiveCompressor()
compressed = compressor.compress(expression.encode('utf-8'))

# Later: decompress and decode
data = compressor.decompress(compressed)
decoder = TSCGDecoder()
decoded = decoder.decode_flow(data.decode('utf-8'))
```

## Architecture

```
AdaptiveCompressor
├── Content Analysis (detect type)
├── Algorithm Selection (choose best)
├── Compression (LZ4/ZSTD/Brotli/zlib)
├── Frame Building (metadata + CRC)
└── Statistics Tracking

ContextAwareEncoder
├── Preprocessing (term → symbol)
├── Postprocessing (symbol → term)
└── Integration with compressor

TSCGDictionary
├── Training (learn patterns)
├── Optimization (governance domain)
└── Persistence (save/load)

StreamingCompressor
├── Chunk Processing (64KB)
├── Algorithm Support (ZSTD/LZ4/zlib)
└── Memory Efficiency
```

## Future Enhancements

- [ ] Machine learning-based compression for governance patterns
- [ ] Delta compression for versioned constitutional documents
- [ ] GPU-accelerated decompression
- [ ] Custom entropy coder for TSCG symbols
- [ ] Real-time dictionary updates from live governance data

## License

Part of the Sovereign Governance Substrate project.
