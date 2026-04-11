"""
Token Storage

Persistent storage for capability tokens with support for
database and distributed cache backends.
"""

import json
import sqlite3
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging
from .token_manager import Token, TokenStatus

logger = logging.getLogger(__name__)


class TokenStorage:
    """
    Persistent storage for capability tokens
    
    Supports multiple backends:
    - SQLite (default)
    - Redis
    - PostgreSQL
    """
    
    def __init__(self, backend: str = "sqlite", connection_string: str = "tokens.db"):
        self.backend = backend
        self.connection_string = connection_string
        
        if backend == "sqlite":
            self._init_sqlite()
        elif backend == "redis":
            self._init_redis()
        elif backend == "postgresql":
            self._init_postgresql()
        else:
            raise ValueError(f"Unsupported backend: {backend}")
    
    def _init_sqlite(self):
        """Initialize SQLite storage"""
        self.conn = sqlite3.connect(self.connection_string)
        self.conn.row_factory = sqlite3.Row
        
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tokens (
                id TEXT PRIMARY KEY,
                subject TEXT NOT NULL,
                scopes TEXT NOT NULL,
                issued_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                constraints TEXT,
                status TEXT NOT NULL,
                metadata TEXT,
                signature TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_subject ON tokens(subject)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_expires_at ON tokens(expires_at)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_status ON tokens(status)
        """)
        
        self.conn.commit()
        logger.info("Initialized SQLite token storage")
    
    def _init_redis(self):
        """Initialize Redis storage"""
        try:
            import redis
            self.redis_client = redis.from_url(self.connection_string)
            self.redis_client.ping()
            logger.info("Initialized Redis token storage")
        except ImportError:
            raise ImportError("Redis library not installed. Install with: pip install redis")
        except Exception as e:
            logger.error(f"Failed to initialize Redis: {e}")
            raise
    
    def _init_postgresql(self):
        """Initialize PostgreSQL storage"""
        try:
            import psycopg2
            self.pg_conn = psycopg2.connect(self.connection_string)
            cursor = self.pg_conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tokens (
                    id TEXT PRIMARY KEY,
                    subject TEXT NOT NULL,
                    scopes JSONB NOT NULL,
                    issued_at TIMESTAMP NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    constraints JSONB,
                    status TEXT NOT NULL,
                    metadata JSONB,
                    signature TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_subject ON tokens(subject)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_expires_at ON tokens(expires_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_status ON tokens(status)")
            
            self.pg_conn.commit()
            logger.info("Initialized PostgreSQL token storage")
        except ImportError:
            raise ImportError("psycopg2 not installed. Install with: pip install psycopg2-binary")
        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL: {e}")
            raise
    
    def store_token(self, token: Token):
        """Store token in backend"""
        if self.backend == "sqlite":
            self._store_sqlite(token)
        elif self.backend == "redis":
            self._store_redis(token)
        elif self.backend == "postgresql":
            self._store_postgresql(token)
    
    def _store_sqlite(self, token: Token):
        """Store token in SQLite"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO tokens
            (id, subject, scopes, issued_at, expires_at, constraints, status, metadata, signature)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            token.id,
            token.subject,
            json.dumps(token.scopes),
            token.issued_at.isoformat(),
            token.expires_at.isoformat(),
            json.dumps(token.constraints.to_dict()),
            token.status.value,
            json.dumps(token.metadata),
            token.signature,
        ))
        self.conn.commit()
    
    def _store_redis(self, token: Token):
        """Store token in Redis"""
        key = f"token:{token.id}"
        ttl = int((token.expires_at - datetime.utcnow()).total_seconds())
        
        self.redis_client.setex(
            key,
            ttl,
            json.dumps(token.to_dict()),
        )
    
    def _store_postgresql(self, token: Token):
        """Store token in PostgreSQL"""
        cursor = self.pg_conn.cursor()
        cursor.execute("""
            INSERT INTO tokens
            (id, subject, scopes, issued_at, expires_at, constraints, status, metadata, signature)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                status = EXCLUDED.status,
                metadata = EXCLUDED.metadata
        """, (
            token.id,
            token.subject,
            json.dumps(token.scopes),
            token.issued_at,
            token.expires_at,
            json.dumps(token.constraints.to_dict()),
            token.status.value,
            json.dumps(token.metadata),
            token.signature,
        ))
        self.pg_conn.commit()
    
    def get_token(self, token_id: str) -> Optional[Token]:
        """Retrieve token from backend"""
        if self.backend == "sqlite":
            return self._get_sqlite(token_id)
        elif self.backend == "redis":
            return self._get_redis(token_id)
        elif self.backend == "postgresql":
            return self._get_postgresql(token_id)
    
    def _get_sqlite(self, token_id: str) -> Optional[Token]:
        """Get token from SQLite"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM tokens WHERE id = ?", (token_id,))
        row = cursor.fetchone()
        
        if not row:
            return None
        
        return self._row_to_token(dict(row))
    
    def _get_redis(self, token_id: str) -> Optional[Token]:
        """Get token from Redis"""
        key = f"token:{token_id}"
        data = self.redis_client.get(key)
        
        if not data:
            return None
        
        return Token.from_dict(json.loads(data))
    
    def _get_postgresql(self, token_id: str) -> Optional[Token]:
        """Get token from PostgreSQL"""
        cursor = self.pg_conn.cursor()
        cursor.execute("SELECT * FROM tokens WHERE id = %s", (token_id,))
        row = cursor.fetchone()
        
        if not row:
            return None
        
        return self._row_to_token(row)
    
    def _row_to_token(self, row: Dict) -> Token:
        """Convert database row to Token object"""
        from .token_manager import TokenConstraints
        
        return Token(
            id=row["id"],
            subject=row["subject"],
            scopes=json.loads(row["scopes"]),
            issued_at=datetime.fromisoformat(row["issued_at"]),
            expires_at=datetime.fromisoformat(row["expires_at"]),
            constraints=TokenConstraints(**json.loads(row["constraints"])),
            status=TokenStatus(row["status"]),
            metadata=json.loads(row["metadata"]),
            signature=row["signature"],
        )
    
    def revoke_token(self, token_id: str) -> bool:
        """Revoke token"""
        token = self.get_token(token_id)
        if token:
            token.status = TokenStatus.REVOKED
            self.store_token(token)
            return True
        return False
    
    def list_tokens_by_subject(self, subject: str) -> List[Token]:
        """List all tokens for a subject"""
        if self.backend == "sqlite":
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM tokens WHERE subject = ?", (subject,))
            return [self._row_to_token(dict(row)) for row in cursor.fetchall()]
        
        # For other backends, implement similar logic
        return []
    
    def cleanup_expired(self) -> int:
        """Remove expired tokens"""
        if self.backend == "sqlite":
            cursor = self.conn.cursor()
            cursor.execute(
                "DELETE FROM tokens WHERE expires_at < ?",
                (datetime.utcnow().isoformat(),)
            )
            self.conn.commit()
            return cursor.rowcount
        
        return 0
