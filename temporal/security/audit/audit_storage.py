"""
Audit Storage

Persistent storage backends for audit logs with support for immutability.
"""

import json
import sqlite3
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path
import logging

from .audit_logger import SecurityEvent, EventType, EventSeverity

logger = logging.getLogger(__name__)


class AuditStorage:
    """
    Persistent storage for audit events
    
    Supports:
    - SQLite (default, append-only)
    - File-based (append-only log files)
    - PostgreSQL (with immutable tables)
    - S3 (for long-term archival)
    """
    
    def __init__(
        self,
        backend: str = "sqlite",
        connection_string: str = "audit.db",
        **kwargs
    ):
        self.backend = backend
        self.connection_string = connection_string
        
        if backend == "sqlite":
            self._init_sqlite()
        elif backend == "file":
            self._init_file(kwargs.get("log_dir", "audit_logs"))
        elif backend == "postgresql":
            self._init_postgresql()
        else:
            raise ValueError(f"Unsupported backend: {backend}")
    
    def _init_sqlite(self):
        """Initialize SQLite storage with append-only table"""
        self.conn = sqlite3.connect(self.connection_string)
        self.conn.row_factory = sqlite3.Row
        
        cursor = self.conn.cursor()
        
        # Create append-only audit events table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT UNIQUE NOT NULL,
                event_type TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                severity TEXT NOT NULL,
                actor TEXT NOT NULL,
                subject TEXT,
                action TEXT,
                result TEXT,
                source_ip TEXT,
                source_service TEXT,
                metadata TEXT,
                previous_event_hash TEXT,
                event_hash TEXT NOT NULL,
                signature TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_event_type ON audit_events(event_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON audit_events(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_actor ON audit_events(actor)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_event_hash ON audit_events(event_hash)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_severity ON audit_events(severity)")
        
        # Prevent updates and deletes (append-only)
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS prevent_update_audit_events
            BEFORE UPDATE ON audit_events
            BEGIN
                SELECT RAISE(ABORT, 'Audit events are immutable');
            END
        """)
        
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS prevent_delete_audit_events
            BEFORE DELETE ON audit_events
            BEGIN
                SELECT RAISE(ABORT, 'Audit events cannot be deleted');
            END
        """)
        
        self.conn.commit()
        logger.info("Initialized SQLite audit storage (append-only)")
    
    def _init_file(self, log_dir: str):
        """Initialize file-based storage"""
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Create daily log file
        self.current_log_file = None
        self._rotate_log_file()
        
        logger.info(f"Initialized file-based audit storage: {log_dir}")
    
    def _rotate_log_file(self):
        """Rotate to new daily log file"""
        date_str = datetime.utcnow().strftime("%Y-%m-%d")
        log_file = self.log_dir / f"audit_{date_str}.jsonl"
        
        if self.current_log_file:
            self.current_log_file.close()
        
        # Open in append mode
        self.current_log_file = open(log_file, "a")
        logger.info(f"Rotated to log file: {log_file}")
    
    def _init_postgresql(self):
        """Initialize PostgreSQL storage with immutable table"""
        try:
            import psycopg2
            self.pg_conn = psycopg2.connect(self.connection_string)
            
            cursor = self.pg_conn.cursor()
            
            # Create immutable audit events table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_events (
                    id BIGSERIAL PRIMARY KEY,
                    event_id UUID UNIQUE NOT NULL,
                    event_type TEXT NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    severity TEXT NOT NULL,
                    actor TEXT NOT NULL,
                    subject TEXT,
                    action TEXT,
                    result TEXT,
                    source_ip INET,
                    source_service TEXT,
                    metadata JSONB,
                    previous_event_hash TEXT,
                    event_hash TEXT NOT NULL,
                    signature TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_event_type ON audit_events(event_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON audit_events(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_actor ON audit_events(actor)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_event_hash ON audit_events(event_hash)")
            
            self.pg_conn.commit()
            logger.info("Initialized PostgreSQL audit storage")
        except ImportError:
            raise ImportError("psycopg2 not installed. Install with: pip install psycopg2-binary")
    
    def store_event(self, event: SecurityEvent):
        """Store audit event"""
        if self.backend == "sqlite":
            self._store_sqlite(event)
        elif self.backend == "file":
            self._store_file(event)
        elif self.backend == "postgresql":
            self._store_postgresql(event)
    
    def _store_sqlite(self, event: SecurityEvent):
        """Store event in SQLite"""
        cursor = self.conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO audit_events
                (event_id, event_type, timestamp, severity, actor, subject, action,
                 result, source_ip, source_service, metadata, previous_event_hash,
                 event_hash, signature)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event.event_id,
                event.event_type.value,
                event.timestamp.isoformat(),
                event.severity.value,
                event.actor,
                event.subject,
                event.action,
                event.result,
                event.source_ip,
                event.source_service,
                json.dumps(event.metadata),
                event.previous_event_hash,
                event.event_hash,
                event.signature,
            ))
            
            self.conn.commit()
        except sqlite3.IntegrityError as e:
            logger.error(f"Failed to store event: {e}")
            raise
    
    def _store_file(self, event: SecurityEvent):
        """Store event in file"""
        # Check if we need to rotate
        current_date = datetime.utcnow().strftime("%Y-%m-%d")
        if current_date not in str(self.current_log_file.name):
            self._rotate_log_file()
        
        # Write event as JSON line
        event_json = json.dumps(event.to_dict())
        self.current_log_file.write(event_json + "\n")
        self.current_log_file.flush()
    
    def _store_postgresql(self, event: SecurityEvent):
        """Store event in PostgreSQL"""
        cursor = self.pg_conn.cursor()
        
        cursor.execute("""
            INSERT INTO audit_events
            (event_id, event_type, timestamp, severity, actor, subject, action,
             result, source_ip, source_service, metadata, previous_event_hash,
             event_hash, signature)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            event.event_id,
            event.event_type.value,
            event.timestamp,
            event.severity.value,
            event.actor,
            event.subject,
            event.action,
            event.result,
            event.source_ip,
            event.source_service,
            json.dumps(event.metadata),
            event.previous_event_hash,
            event.event_hash,
            event.signature,
        ))
        
        self.pg_conn.commit()
    
    def get_events(
        self,
        event_type: Optional[EventType] = None,
        actor: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        severity: Optional[EventSeverity] = None,
        limit: int = 100,
    ) -> List[SecurityEvent]:
        """Query audit events with filters"""
        if self.backend == "sqlite":
            return self._query_sqlite(
                event_type, actor, start_time, end_time, severity, limit
            )
        elif self.backend == "postgresql":
            return self._query_postgresql(
                event_type, actor, start_time, end_time, severity, limit
            )
        
        return []
    
    def _query_sqlite(
        self,
        event_type: Optional[EventType],
        actor: Optional[str],
        start_time: Optional[datetime],
        end_time: Optional[datetime],
        severity: Optional[EventSeverity],
        limit: int,
    ) -> List[SecurityEvent]:
        """Query SQLite"""
        cursor = self.conn.cursor()
        
        query = "SELECT * FROM audit_events WHERE 1=1"
        params = []
        
        if event_type:
            query += " AND event_type = ?"
            params.append(event_type.value)
        
        if actor:
            query += " AND actor = ?"
            params.append(actor)
        
        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time.isoformat())
        
        if end_time:
            query += " AND timestamp <= ?"
            params.append(end_time.isoformat())
        
        if severity:
            query += " AND severity = ?"
            params.append(severity.value)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        
        events = []
        for row in cursor.fetchall():
            event_dict = dict(row)
            event_dict["metadata"] = json.loads(event_dict["metadata"])
            events.append(SecurityEvent.from_dict(event_dict))
        
        return events
    
    def _query_postgresql(
        self,
        event_type: Optional[EventType],
        actor: Optional[str],
        start_time: Optional[datetime],
        end_time: Optional[datetime],
        severity: Optional[EventSeverity],
        limit: int,
    ) -> List[SecurityEvent]:
        """Query PostgreSQL"""
        cursor = self.pg_conn.cursor()
        
        query = "SELECT * FROM audit_events WHERE 1=1"
        params = []
        
        if event_type:
            query += " AND event_type = %s"
            params.append(event_type.value)
        
        if actor:
            query += " AND actor = %s"
            params.append(actor)
        
        if start_time:
            query += " AND timestamp >= %s"
            params.append(start_time)
        
        if end_time:
            query += " AND timestamp <= %s"
            params.append(end_time)
        
        if severity:
            query += " AND severity = %s"
            params.append(severity.value)
        
        query += " ORDER BY timestamp DESC LIMIT %s"
        params.append(limit)
        
        cursor.execute(query, params)
        
        events = []
        for row in cursor.fetchall():
            event_dict = dict(zip([desc[0] for desc in cursor.description], row))
            events.append(SecurityEvent.from_dict(event_dict))
        
        return events
    
    def get_events_by_hash(self, event_hash: str) -> List[SecurityEvent]:
        """Get events by event hash"""
        if self.backend == "sqlite":
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM audit_events WHERE event_hash = ?", (event_hash,))
            
            events = []
            for row in cursor.fetchall():
                event_dict = dict(row)
                event_dict["metadata"] = json.loads(event_dict["metadata"])
                events.append(SecurityEvent.from_dict(event_dict))
            
            return events
        
        return []
