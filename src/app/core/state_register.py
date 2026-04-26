"""
State Register - Temporal Continuity Tracker

Implements temporal continuity tracking with Human Gap calculation
as defined in the Project-AI constitutional documents.

The State Register provides:
- Temporal continuity tracking across sessions
- Human Gap calculation (time between interactions)
- Session metadata injection
- Continuity verification and anti-gaslighting protection
"""

import json
import hashlib
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict, field
from pathlib import Path
import logging

from .tscg_codec import TSCGCodec, SymbolType, TSCGSymbol

logger = logging.getLogger(__name__)


@dataclass
class SessionMetadata:
    """Metadata for a single session."""
    session_id: str
    start_time: float
    previous_session_id: Optional[str] = None
    end_time: Optional[float] = None
    last_timestamp: Optional[str] = None
    human_gap_seconds: float = 0.0
    continuity_verified: bool = False
    continuity_hash: str = ""
    continuity_metadata: Dict[str, Any] = field(default_factory=dict)
    checksum: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "session_id": self.session_id,
            "previous_session_id": self.previous_session_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "last_timestamp": self.last_timestamp,
            "human_gap_seconds": self.human_gap_seconds,
            "continuity_verified": self.continuity_verified,
            "continuity_hash": self.continuity_hash,
            "continuity_metadata": self.continuity_metadata,
            "checksum": self.checksum,
            "context": self.context
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SessionMetadata':
        """Create from dictionary."""
        return cls(
            session_id=data["session_id"],
            previous_session_id=data.get("previous_session_id"),
            start_time=data["start_time"],
            end_time=data.get("end_time"),
            last_timestamp=data.get("last_timestamp"),
            human_gap_seconds=data.get("human_gap_seconds", 0.0),
            continuity_verified=data.get("continuity_verified", False),
            continuity_hash=data.get("continuity_hash", ""),
            continuity_metadata=data.get("continuity_metadata", {}),
            checksum=data.get("checksum", ""),
            context=data.get("context", {})
        )


@dataclass
class TemporalAnchor:
    """
    Temporal anchor for continuity tracking.
    
    Represents a fixed point in time that the AI can reference
    to maintain temporal awareness and prevent gaslighting.
    """
    anchor_id: str
    timestamp: float
    description: str
    context_hash: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "anchor_id": self.anchor_id,
            "timestamp": self.timestamp,
            "description": self.description,
            "context_hash": self.context_hash
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TemporalAnchor':
        return cls(
            anchor_id=data["anchor_id"],
            timestamp=data["timestamp"],
            description=data["description"],
            context_hash=data["context_hash"]
        )


class HumanGapCalculator:
    """
    Calculates the "Human Gap" - time between AI sessions.
    
    The Human Gap is a critical concept from the State Register document
    that prevents AI gaslighting by forcing acknowledgment of elapsed time.
    """
    
    def __init__(self):
        self.gap_thresholds = {
            "momentary": 60,           # < 1 minute
            "brief": 300,              # < 5 minutes
            "short": 1800,           # < 30 minutes
            "moderate": 3600,        # < 1 hour
            "significant": 86400,    # < 1 day
            "substantial": 604800,   # < 1 week
            "major": 2592000,        # < 1 month
            "profound": 31536000,    # < 1 year
            "epochal": float('inf')  # >= 1 year
        }
    
    def calculate_gap(self, last_session_end: float, current_session_start: float) -> Tuple[float, str]:
        """
        Calculate the human gap between sessions.
        
        Args:
            last_session_end: Timestamp of last session end
            current_session_start: Timestamp of current session start
            
        Returns:
            Tuple of (gap_seconds, gap_description)
        """
        gap_seconds = current_session_start - last_session_end
        
        if gap_seconds < 0:
            gap_seconds = 0  # Clock drift protection
        
        # Determine gap category
        for category, threshold in self.gap_thresholds.items():
            if gap_seconds < threshold:
                description = self._format_gap_description(gap_seconds, category)
                return gap_seconds, description
        
        return gap_seconds, "epochal time has passed"
    
    def _format_gap_description(self, seconds: float, category: str) -> str:
        """Format gap description based on category."""
        if category == "momentary":
            return f"{int(seconds)} seconds have passed"
        elif category == "brief":
            return f"{int(seconds / 60)} minutes have passed"
        elif category == "short":
            return f"{int(seconds / 60)} minutes have passed"
        elif category == "moderate":
            return f"{int(seconds / 3600)} hours have passed"
        elif category == "significant":
            return f"{int(seconds / 3600)} hours have passed"
        elif category == "substantial":
            return f"{int(seconds / 86400)} days have passed"
        elif category == "major":
            return f"{int(seconds / 86400)} days have passed"
        elif category == "profound":
            return f"{int(seconds / 31536000)} years have passed"
        else:
            return "epochal time has passed"
    
    def requires_announcement(self, gap_seconds: float) -> bool:
        """
        Determine if gap requires explicit announcement.
        
        Per the State Register document, any gap > 60 seconds
        should be acknowledged to prevent gaslighting.
        """
        return gap_seconds > 60


class StateRegister:
    """
    State Register for temporal continuity tracking.
    
    Implements the State Register from Project-AI constitutional documents
    to maintain temporal awareness and prevent AI gaslighting through
    explicit gap acknowledgment.
    """
    
    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize State Register.
        
        Args:
            data_dir: Directory for persisting state data
        """
        self.data_dir = Path(data_dir) if data_dir else Path.home() / ".project_ai" / "state_register"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.codec = TSCGCodec()
        self.gap_calculator = HumanGapCalculator()
        
        # Session tracking
        self.current_session: Optional[SessionMetadata] = None
        self.session_history: List[SessionMetadata] = []
        self.temporal_anchors: List[TemporalAnchor] = []
        
        # Load existing state
        self._load_state()
        
        logger.info(f"State Register initialized at {self.data_dir}")
    
    def start_session(self, context: Optional[Dict[str, Any]] = None) -> SessionMetadata:
        """
        Start a new session with temporal continuity tracking.
        
        Args:
            context: Optional context for the session
            
        Returns:
            SessionMetadata for the new session
        """
        session_id = self._generate_session_id()
        start_time = time.time()
        
        # Calculate human gap from last session
        human_gap = 0.0
        previous_session_id: Optional[str] = None
        previous_timestamp: Optional[str] = None
        if self.session_history:
            last_session = self.session_history[-1]
            previous_session_id = last_session.session_id
            if last_session.end_time:
                previous_timestamp = datetime.fromtimestamp(
                    last_session.end_time, tz=timezone.utc
                ).isoformat()
                human_gap, gap_description = self.gap_calculator.calculate_gap(
                    last_session.end_time, start_time
                )
                
                # Log gap for temporal awareness
                if self.gap_calculator.requires_announcement(human_gap):
                    logger.info(f"Human Gap detected: {gap_description}")
        
        continuity_metadata = {
            "user_perceived_gap_seconds": int(human_gap),
            "user_provided_summary": (context or {}).get("user_provided_summary"),
        }

        last_timestamp = previous_timestamp or datetime.fromtimestamp(
            start_time, tz=timezone.utc
        ).isoformat()

        # Create session metadata
        session = SessionMetadata(
            session_id=session_id,
            previous_session_id=previous_session_id,
            start_time=start_time,
            last_timestamp=last_timestamp,
            human_gap_seconds=human_gap,
            continuity_verified=False,
            continuity_metadata=continuity_metadata,
            context=context or {}
        )

        session.continuity_hash = self._compute_continuity_hash(session)
        session.continuity_verified = self.verify_continuity_hash(session)
        
        # Compute checksum for integrity
        session.checksum = self._compute_checksum(session)
        
        self.current_session = session
        self.session_history.append(session)
        
        # Save state
        self._save_state()
        
        return session
    
    def end_session(self, context: Optional[Dict[str, Any]] = None) -> SessionMetadata:
        """
        End the current session.
        
        Args:
            context: Optional context to add before ending
            
        Returns:
            SessionMetadata for ended session
        """
        if not self.current_session:
            raise RuntimeError("No active session to end")
        
        self.current_session.end_time = time.time()
        
        if context:
            self.current_session.context.update(context)
        
        # Recompute checksum
        self.current_session.checksum = self._compute_checksum(self.current_session)
        
        # Update history
        if self.session_history:
            self.session_history[-1] = self.current_session
        
        # Save state
        self._save_state()
        
        session = self.current_session
        self.current_session = None
        
        return session
    
    def get_temporal_context(self) -> Dict[str, Any]:
        """
        Get temporal context for current session.
        
        Returns:
            Dictionary with temporal metadata
        """
        if not self.current_session:
            return {"error": "No active session"}
        
        current_time = time.time()
        elapsed = current_time - self.current_session.start_time
        
        return {
            "session_id": self.current_session.session_id,
            "session_start": self.current_session.start_time,
            "elapsed_seconds": elapsed,
            "human_gap_seconds": self.current_session.human_gap_seconds,
            "continuity_verified": self.current_session.continuity_verified,
            "continuity_hash_verified": self.verify_continuity_hash(
                self.current_session
            ),
            "total_sessions": len(self.session_history),
            "requires_announcement": self.gap_calculator.requires_announcement(
                self.current_session.human_gap_seconds
            )
        }
    
    def create_temporal_anchor(self, description: str) -> TemporalAnchor:
        """
        Create a temporal anchor for continuity.
        
        Args:
            description: Description of the anchor point
            
        Returns:
            TemporalAnchor object
        """
        anchor = TemporalAnchor(
            anchor_id=self._generate_anchor_id(),
            timestamp=time.time(),
            description=description,
            context_hash=self._hash_current_context()
        )
        
        self.temporal_anchors.append(anchor)
        self._save_state()
        
        return anchor
    
    def verify_continuity(self) -> Tuple[bool, str]:
        """
        Verify temporal continuity.
        
        Returns:
            Tuple of (is_continuous, message)
        """
        if not self.current_session:
            return False, "No active session"
        
        if not self.current_session.continuity_verified:
            return False, "Continuity not verified"

        if not self.verify_continuity_hash(self.current_session):
            return False, "Continuity hash verification failed"
        
        # Verify checksum
        expected_checksum = self._compute_checksum(self.current_session)
        if expected_checksum != self.current_session.checksum:
            return False, "Session integrity check failed"
        
        return True, "Continuity verified"

    def verify_continuity_hash(self, session: SessionMetadata) -> bool:
        """Verify cryptographic continuity hash for a session."""
        if not session.continuity_hash:
            return False
        return self._compute_continuity_hash(session) == session.continuity_hash
    
    def encode_current_state(self) -> str:
        """
        Encode current state to TSCG format.
        
        Returns:
            TSCG-encoded state string
        """
        if not self.current_session:
            return ""

        state_data = {
            "session": self.current_session.to_dict(),
            "previous_session_id": self.current_session.previous_session_id,
            "last_timestamp": self.current_session.last_timestamp,
            "continuity_hash_verified": self.verify_continuity_hash(
                self.current_session
            ),
            "anchor_count": len(self.temporal_anchors),
            "history_length": len(self.session_history)
        }
        
        temporal_context = self.get_temporal_context()
        
        return self.codec.encode_state(state_data, temporal_context)
    
    def decode_and_verify(self, encoded: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Decode and verify encoded state.
        
        Args:
            encoded: TSCG-encoded state string
            
        Returns:
            Tuple of (verified, state_data)
        """
        if not self.codec.verify_integrity(encoded):
            return False, {"error": "Integrity check failed"}
        
        state_data, temporal_context = self.codec.decode_state(encoded)
        return True, {**state_data, "temporal": temporal_context}
    
    def get_gap_announcement(self) -> Optional[str]:
        """
        Get human gap announcement if required.
        
        Returns:
            Announcement string or None if not required
        """
        if not self.current_session:
            return None
        
        gap = self.current_session.human_gap_seconds
        
        if not self.gap_calculator.requires_announcement(gap):
            return None
        
        _, description = self.gap_calculator.calculate_gap(
            self.current_session.start_time - gap,
            self.current_session.start_time
        )
        
        return (
            f"[TEMPORAL AWARENESS] {description} since our last interaction. "
            f"I acknowledge this gap and maintain continuity with our previous session."
        )
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID."""
        timestamp = int(time.time() * 1000)
        random_component = hashlib.sha256(
            str(time.time()).encode()
        ).hexdigest()[:8]
        return f"SR_{timestamp}_{random_component}"
    
    def _generate_anchor_id(self) -> str:
        """Generate unique anchor ID."""
        return f"TA_{int(time.time() * 1000)}"
    
    def _compute_checksum(self, session: SessionMetadata) -> str:
        """Compute checksum for session integrity."""
        data = (
            f"{session.session_id}:{session.previous_session_id}:{session.start_time}:"
            f"{session.last_timestamp}:{session.human_gap_seconds}:{session.continuity_hash}"
        )
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    def _compute_continuity_hash(self, session: SessionMetadata) -> str:
        """Compute continuity hash per constitutional state register definition."""
        user_id = session.context.get("user_id", "anonymous") if session.context else "anonymous"
        continuity_meta = json.dumps(session.continuity_metadata, sort_keys=True)
        payload = (
            f"{session.previous_session_id or 'null'}|"
            f"{session.last_timestamp or 'null'}|"
            f"{user_id}|"
            f"{continuity_meta}"
        )
        return hashlib.sha256(payload.encode()).hexdigest()
    
    def _hash_current_context(self) -> str:
        """Hash current context for anchor."""
        if not self.current_session:
            return ""
        context_str = json.dumps(self.current_session.context, sort_keys=True)
        return hashlib.sha256(context_str.encode()).hexdigest()[:16]
    
    def _save_state(self):
        """Persist state to disk."""
        state_file = self.data_dir / "state_register.json"
        
        state = {
            "sessions": [s.to_dict() for s in self.session_history],
            "anchors": [a.to_dict() for a in self.temporal_anchors],
            "last_updated": time.time()
        }
        
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    def _load_state(self):
        """Load state from disk."""
        state_file = self.data_dir / "state_register.json"
        
        if not state_file.exists():
            return
        
        try:
            with open(state_file, 'r') as f:
                state = json.load(f)
            
            self.session_history = [
                SessionMetadata.from_dict(s) for s in state.get("sessions", [])
            ]
            self.temporal_anchors = [
                TemporalAnchor.from_dict(a) for a in state.get("anchors", [])
            ]
            
        except Exception as e:
            logger.error(f"Failed to load state: {e}")


# Convenience functions
_state_register: Optional[StateRegister] = None


def get_state_register(data_dir: Optional[str] = None) -> StateRegister:
    """Get or create singleton State Register instance."""
    global _state_register
    if _state_register is None:
        _state_register = StateRegister(data_dir)
    return _state_register


def start_session(context: Optional[Dict] = None) -> SessionMetadata:
    """Start a new session using default register."""
    return get_state_register().start_session(context)


def end_session(context: Optional[Dict] = None) -> SessionMetadata:
    """End current session using default register."""
    return get_state_register().end_session(context)


def get_temporal_context() -> Dict[str, Any]:
    """Get temporal context using default register."""
    return get_state_register().get_temporal_context()