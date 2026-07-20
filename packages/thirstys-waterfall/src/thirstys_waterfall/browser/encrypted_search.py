"""Encrypted Search Engine - All searches are encrypted"""

import hashlib
import logging
import time
from collections.abc import Callable
from typing import Any

from cryptography.fernet import Fernet


class EncryptedSearchEngine:
    """
    Encrypted search engine that encrypts all search queries and results.
    No plaintext searches are ever stored or transmitted.
    """

    def __init__(
        self,
        cipher: Fernet,
        provider: Callable[[bytes], bytes] | None = None,
    ):
        self.logger = logging.getLogger(__name__)
        self._cipher = cipher
        self._active = False
        self._provider = provider

        # Encrypted search history (encrypted queries)
        self._encrypted_search_history = []

        # Encrypted cache (query_hash -> encrypted results)
        # Use hash as key since Fernet encryption is non-deterministic
        self._encrypted_cache: dict[str, bytes] = {}

    def start(self):
        """Start encrypted search engine"""
        self.logger.info("Starting Encrypted Search Engine - All searches encrypted")
        self._active = True

    def stop(self):
        """Stop and wipe all encrypted data"""
        self.logger.info("Stopping Encrypted Search Engine - Wiping data")
        self._encrypted_search_history.clear()
        self._encrypted_cache.clear()
        self._active = False

    def search(self, query: str) -> dict[str, Any]:
        """
        Perform encrypted search.
        Query is encrypted before processing.

        Args:
            query: Search query (will be encrypted immediately)

        Returns:
            Search results (encrypted)
        """
        if not self._active:
            raise RuntimeError("Search engine not active")

        # Encrypt query immediately
        encrypted_query = self._cipher.encrypt(query.encode())

        # Create deterministic hash for caching (from plaintext before encryption)
        query_hash = hashlib.sha256(query.encode()).hexdigest()
        self.logger.debug(f"Search hash: {query_hash[:16]}")

        # Store encrypted query in history
        self._encrypted_search_history.append(
            {
                "encrypted_query": encrypted_query,
                "timestamp": time.time(),
                "hash": query_hash[:16],
            }
        )

        # Check encrypted cache (using hash as key)
        if query_hash in self._encrypted_cache:
            self.logger.debug("Returning encrypted cached results")
            return {
                "encrypted_results": self._encrypted_cache[query_hash],
                "from_cache": True,
                "status": "ok" if self._provider is not None else "unavailable",
            }

        # Perform search (in production would use encrypted search API)
        encrypted_results = self._perform_encrypted_search(encrypted_query)

        # Cache encrypted results (using hash as key)
        self._encrypted_cache[query_hash] = encrypted_results

        return {
            "encrypted_results": encrypted_results,
            "from_cache": False,
            "status": "ok" if self._provider is not None else "unavailable",
        }

    def _perform_encrypted_search(self, encrypted_query: bytes) -> bytes:
        """
        Perform actual encrypted search.
        Query remains encrypted throughout.
        """
        if self._provider is None:
            unavailable = '{"status":"unavailable","reason":"encrypted search provider not configured","results":[]}'
            return self._cipher.encrypt(unavailable.encode())
        encrypted_results = self._provider(encrypted_query)
        if not isinstance(encrypted_results, bytes):
            raise TypeError("encrypted search provider must return bytes")
        return encrypted_results

    def decrypt_results(self, encrypted_results: bytes) -> str:
        """
        Decrypt search results for display.
        Only decrypted in memory when needed for display.
        """
        try:
            return self._cipher.decrypt(encrypted_results).decode()
        except Exception as e:
            self.logger.error(f"Failed to decrypt results: {e}")
            return ""

    def get_encrypted_history(self) -> list:
        """
        Get encrypted search history.
        History is never available in plaintext.
        """
        return self._encrypted_search_history.copy()

    def clear_history(self):
        """Securely clear encrypted search history"""
        self.logger.info("Clearing encrypted search history")
        self._encrypted_search_history.clear()
        self._encrypted_cache.clear()
