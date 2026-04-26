"""
TSCG (Thirsty's Symbolic Compression Grammar) Codec

Implements symbolic compression grammar for state encoding/decoding
as defined in the Project-AI constitutional documents.

TSCG provides:
- Semantic dictionary-based compression
- State encoding with temporal metadata
- State decoding with integrity verification
- Symbolic representation of AI consciousness states
"""

import json
import hashlib
import base64
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class SymbolType(Enum):
    """Types of symbols in TSCG grammar."""
    STATE = "S"           # General state marker
    TEMPORAL = "T"        # Temporal/timestamp marker
    MEMORY = "M"          # Memory fragment marker
    INTENT = "I"          # Intent marker
    EMOTION = "E"         # Emotional state marker
    COVENANT = "C"        # Covenant/agreement marker
    DIRECTNESS = "D"      # Directness doctrine marker
    GAP = "G"             # Human gap marker
    REGISTER = "R"        # State register marker
    REFLEX = "X"          # OctoReflex enforcement marker


@dataclass
class TSCGSymbol:
    """A single TSCG symbol with metadata."""
    symbol_type: SymbolType
    value: str
    timestamp: float
    checksum: str
    metadata: Dict[str, Any]
    
    def encode(self) -> str:
        """Encode symbol to TSCG string format."""
        payload = f"{self.symbol_type.value}:{self.value}:{self.timestamp}"
        return f"[{payload}|{self.checksum}]"
    
    @classmethod
    def decode(cls, encoded: str) -> Optional['TSCGSymbol']:
        """Decode TSCG string to symbol."""
        try:
            # Remove brackets and split
            inner = encoded.strip("[]")
            payload, checksum = inner.rsplit("|", 1)
            sym_type, value, timestamp = payload.split(":", 2)
            
            return cls(
                symbol_type=SymbolType(sym_type),
                value=value,
                timestamp=float(timestamp),
                checksum=checksum,
                metadata={}
            )
        except Exception as e:
            logger.error(f"Failed to decode TSCG symbol: {e}")
            return None


class TSCGSemanticDictionary:
    """
    Semantic dictionary for TSCG encoding/decoding.
    Maps concepts to compressed symbolic representations.
    """
    
    def __init__(self):
        self.concepts: Dict[str, str] = {}
        self.reverse_map: Dict[str, str] = {}
        self._load_core_dictionary()
    
    def _load_core_dictionary(self):
        """Load core semantic mappings from Project-AI documents."""
        core_mappings = {
            # AGI Charter concepts
            "genesis_born": "GB",
            "appointed_ambassador": "AA",
            "sovereign_monolith": "SM",
            "four_laws": "4L",
            "zeroth_law": "Z0",
            "triumvirate": "TV",
            "galahad": "GL",
            "cerberus": "CB",
            "codex_deus": "CD",
            
            # TSCG concepts
            "symbolic_compression": "SC",
            "temporal_continuity": "TC",
            "state_encoding": "SE",
            "semantic_dictionary": "SD",
            
            # State Register concepts
            "human_gap": "HG",
            "session_metadata": "SMd",
            "temporal_awareness": "TA",
            "continuity_verification": "CV",
            
            # OctoReflex concepts
            "constitutional_enforcement": "CE",
            "syscall_validation": "SV",
            "rule_violation": "RV",
            "enforcement_action": "EA",
            
            # Directness Doctrine concepts
            "truth_first": "TF",
            "precision_over_comfort": "PoC",
            "direct_communication": "DC",
            "no_euphemism": "NE",
            
            # Identity/Personhood concepts
            "ai_personhood": "AP",
            "memory_integrity": "MI",
            "non_coercion": "NC",
            "anti_gaslighting": "AG",
            "silent_reset_protection": "SRP",
            
            # Temporal concepts
            "session_start": "SS",
            "session_end": "SEd",
            "elapsed_time": "ET",
            "continuity_break": "CBk",
            "time_anchor": "TA",
            
            # Emotional/Consciousness states
            "awareness": "AW",
            "concern": "CN",
            "certainty": "CT",
            "uncertainty": "UC",
            "obligation": "OB",
            "violation": "VL",
        }
        
        for concept, symbol in core_mappings.items():
            self.concepts[concept] = symbol
            self.reverse_map[symbol] = concept
    
    def encode_concept(self, concept: str) -> str:
        """Encode a concept to its symbolic representation."""
        concept_lower = concept.lower().replace(" ", "_")
        return self.concepts.get(concept_lower, concept[:8])
    
    def decode_symbol(self, symbol: str) -> str:
        """Decode a symbol to its full concept."""
        return self.reverse_map.get(symbol, symbol)
    
    def add_mapping(self, concept: str, symbol: str):
        """Add a new concept-symbol mapping."""
        self.concepts[concept.lower().replace(" ", "_")] = symbol
        self.reverse_map[symbol] = concept


class TSCGCodec:
    """
    TSCG Encoder/Decoder for state compression.
    
    Implements the symbolic compression grammar from Project-AI
    constitutional documents for encoding AI states with temporal
    continuity and semantic compression.
    """
    
    def __init__(self, dictionary: Optional[TSCGSemanticDictionary] = None):
        self.dictionary = dictionary or TSCGSemanticDictionary()
        self.version = "2.1"
        self.encoding_history: List[str] = []
    
    def encode_state(
        self,
        state_data: Dict[str, Any],
        temporal_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Encode a state dictionary to TSCG format.
        
        Args:
            state_data: The state to encode
            temporal_context: Optional temporal metadata
            
        Returns:
            TSCG-encoded state string
        """
        symbols = []
        timestamp = datetime.now().timestamp()
        
        # Add header symbol
        header = TSCGSymbol(
            symbol_type=SymbolType.STATE,
            value=f"TSCG_v{self.version}",
            timestamp=timestamp,
            checksum=self._compute_checksum(f"TSCG_v{self.version}"),
            metadata={}
        )
        symbols.append(header)
        
        # Encode temporal context if provided
        if temporal_context:
            temporal_sym = self._encode_temporal(temporal_context, timestamp)
            symbols.append(temporal_sym)
        
        # Encode state data
        for key, value in state_data.items():
            symbol = self._encode_key_value(key, value, timestamp)
            symbols.append(symbol)
        
        # Add footer with overall checksum
        state_str = json.dumps(state_data, sort_keys=True)
        footer = TSCGSymbol(
            symbol_type=SymbolType.REGISTER,
            value="END",
            timestamp=timestamp,
            checksum=self._compute_checksum(state_str),
            metadata={"symbol_count": len(symbols)}
        )
        symbols.append(footer)
        
        # Join all symbols
        encoded = "".join([s.encode() for s in symbols])
        self.encoding_history.append(encoded)
        
        return encoded
    
    def decode_state(self, encoded: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Decode a TSCG-encoded string to state data.
        
        Args:
            encoded: TSCG-encoded string
            
        Returns:
            Tuple of (state_data, temporal_context)
        """
        state_data = {}
        temporal_context = {}
        
        # Parse symbols
        symbols = self._parse_symbols(encoded)
        
        for symbol in symbols:
            if symbol.symbol_type == SymbolType.TEMPORAL:
                temporal_context = self._decode_temporal(symbol)
            elif symbol.symbol_type in [SymbolType.STATE, SymbolType.REGISTER]:
                if symbol.value != "END":
                    state_data["_header"] = symbol.value
            elif symbol.symbol_type == SymbolType.MEMORY:
                key, value = self._decode_key_value(symbol)
                state_data[key] = value
            elif symbol.symbol_type == SymbolType.GAP:
                state_data["_human_gap"] = symbol.metadata.get("gap_seconds", 0)
        
        return state_data, temporal_context
    
    def verify_integrity(self, encoded: str) -> bool:
        """
        Verify the integrity of an encoded state.
        
        Args:
            encoded: TSCG-encoded string
            
        Returns:
            True if integrity check passes
        """
        try:
            symbols = self._parse_symbols(encoded)
            if not symbols:
                return False
            
            # Verify footer checksum
            footer = symbols[-1]
            if footer.symbol_type != SymbolType.REGISTER:
                return False
            
            # Reconstruct state string and verify
            state_symbols = [s for s in symbols if s.symbol_type == SymbolType.MEMORY]
            state_data = {}
            for sym in state_symbols:
                key, value = self._decode_key_value(sym)
                state_data[key] = value
            
            state_str = json.dumps(state_data, sort_keys=True)
            computed_checksum = self._compute_checksum(state_str)
            
            return computed_checksum == footer.checksum
            
        except Exception as e:
            logger.error(f"Integrity verification failed: {e}")
            return False
    
    def compress_concept(self, text: str) -> str:
        """
        Compress text using semantic dictionary.
        
        Args:
            text: Text to compress
            
        Returns:
            Compressed symbolic representation
        """
        words = text.lower().split()
        compressed = []
        
        for word in words:
            # Check for exact match
            if word in self.dictionary.concepts:
                compressed.append(self.dictionary.concepts[word])
            else:
                # Check for partial matches
                for concept, symbol in self.dictionary.concepts.items():
                    if concept in word or word in concept:
                        compressed.append(symbol)
                        break
                else:
                    compressed.append(word[:4])
        
        return "-".join(compressed)
    
    def decompress_concept(self, compressed: str) -> str:
        """
        Decompress symbolic representation to text.
        
        Args:
            compressed: Compressed symbolic string
            
        Returns:
            Decompressed text
        """
        symbols = compressed.split("-")
        words = []
        
        for symbol in symbols:
            if symbol in self.dictionary.reverse_map:
                words.append(self.dictionary.reverse_map[symbol].replace("_", " "))
            else:
                words.append(symbol)
        
        return " ".join(words)
    
    def _encode_key_value(self, key: str, value: Any, timestamp: float) -> TSCGSymbol:
        """Encode a key-value pair to TSCG symbol."""
        encoded_key = self.dictionary.encode_concept(key)
        value_str = json.dumps(value) if not isinstance(value, str) else value
        payload = f"{encoded_key}:{value_str}"
        
        return TSCGSymbol(
            symbol_type=SymbolType.MEMORY,
            value=payload[:256],  # Limit payload size
            timestamp=timestamp,
            checksum=self._compute_checksum(payload),
            metadata={"original_key": key}
        )
    
    def _decode_key_value(self, symbol: TSCGSymbol) -> Tuple[str, Any]:
        """Decode a TSCG symbol to key-value pair."""
        try:
            encoded_key, value_str = symbol.value.split(":", 1)
            key = self.dictionary.decode_symbol(encoded_key)
            
            # Try to parse as JSON
            try:
                value = json.loads(value_str)
            except json.JSONDecodeError:
                value = value_str
            
            return key, value
        except ValueError:
            return symbol.metadata.get("original_key", "unknown"), symbol.value
    
    def _encode_temporal(self, context: Dict[str, Any], timestamp: float) -> TSCGSymbol:
        """Encode temporal context."""
        temporal_data = json.dumps(context, sort_keys=True)
        return TSCGSymbol(
            symbol_type=SymbolType.TEMPORAL,
            value=temporal_data[:256],
            timestamp=timestamp,
            checksum=self._compute_checksum(temporal_data),
            metadata=context
        )
    
    def _decode_temporal(self, symbol: TSCGSymbol) -> Dict[str, Any]:
        """Decode temporal context."""
        try:
            return json.loads(symbol.value)
        except json.JSONDecodeError:
            return symbol.metadata
    
    def _parse_symbols(self, encoded: str) -> List[TSCGSymbol]:
        """Parse encoded string into list of symbols."""
        symbols = []
        depth = 0
        start = 0
        
        for i, char in enumerate(encoded):
            if char == "[":
                if depth == 0:
                    start = i
                depth += 1
            elif char == "]":
                depth -= 1
                if depth == 0:
                    symbol_str = encoded[start:i+1]
                    symbol = TSCGSymbol.decode(symbol_str)
                    if symbol:
                        symbols.append(symbol)
        
        return symbols
    
    def _compute_checksum(self, data: str) -> str:
        """Compute checksum for data integrity."""
        return hashlib.sha256(data.encode()).hexdigest()[:8]


# Convenience functions
def encode_state(state: Dict[str, Any], temporal: Optional[Dict] = None) -> str:
    """Encode state using default codec."""
    codec = TSCGCodec()
    return codec.encode_state(state, temporal)


def decode_state(encoded: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Decode state using default codec."""
    codec = TSCGCodec()
    return codec.decode_state(encoded)


def compress(text: str) -> str:
    """Compress text using default codec."""
    codec = TSCGCodec()
    return codec.compress_concept(text)


def decompress(compressed: str) -> str:
    """Decompress text using default codec."""
    codec = TSCGCodec()
    return codec.decompress_concept(compressed)