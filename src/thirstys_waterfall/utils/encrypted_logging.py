"""Encrypted Logging System - All logs encrypted"""

import logging
from typing import Optional
from cryptography.fernet import Fernet
import time
import os


class EncryptedLogger:
    """
    Encrypted logging system.
    All logs are encrypted before writing to disk or memory.
    """

    def __init__(self, cipher: Fernet, log_file: Optional[str] = None):
        self._cipher = cipher
        self._log_file = log_file
        self._encrypted_logs = []
        self._active = False

    def start(self):
        """Start encrypted logging"""
        self._active = True

    def stop(self):
        """Stop encrypted logging and wipe"""
        if self._log_file and os.path.exists(self._log_file):
            # Overwrite log file before deletion
            with open(self._log_file, "wb") as f:
                f.write(os.urandom(1024))
            os.remove(self._log_file)

        self._encrypted_logs.clear()
        self._active = False

    def log(self, level: str, message: str):
        """
        Log message with encryption.
        Message is encrypted immediately.
        """
        if not self._active:
            return

        # Encrypt log message
        encrypted_msg = self._cipher.encrypt(
            f"{time.time()}|{level}|{message}".encode()
        )

        # Store encrypted
        self._encrypted_logs.append(encrypted_msg)

        # Write encrypted to file if configured
        if self._log_file:
            with open(self._log_file, "ab") as f:
                f.write(encrypted_msg + b"\n")

    def get_encrypted_logs(self) -> list:
        """Get encrypted logs"""
        return self._encrypted_logs.copy()

    def decrypt_log(self, encrypted_log: bytes) -> str:
        """Decrypt single log entry for viewing"""
        try:
            return self._cipher.decrypt(encrypted_log).decode()
        except Exception:
            return "encrypted_log_entry"


class EncryptedLogHandler(logging.Handler):
    """
    Custom logging handler that encrypts all log messages.
    """

    def __init__(self, cipher: Fernet):
        super().__init__()
        self._cipher = cipher
        self._encrypted_logs = []

    def emit(self, record):
        """Emit encrypted log record"""
        try:
            msg = self.format(record)
            encrypted_msg = self._cipher.encrypt(msg.encode())
            self._encrypted_logs.append(encrypted_msg)
        except Exception:
            self.handleError(record)

    def get_encrypted_logs(self) -> list:
        """Get all encrypted logs"""
        return self._encrypted_logs.copy()
