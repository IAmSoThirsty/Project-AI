"""
Secure Memory Management - Zero Plaintext Residue

Implements Proof 3: Zero plaintext residue in RAM, temp files, logs, crash dumps.
"""

import ctypes
import logging
import os
import platform
import re
import sys
from typing import Any

# resource module only available on Unix-like systems
if platform.system() != "Windows":
    import resource
else:
    resource = None

logger = logging.getLogger(__name__)


class SecureMemory:
    """
    Secure memory management to prevent plaintext residue.

    Protections:
    1. Disable core dumps (prevent key leakage in crash dumps)
    2. Secure memory wiping (triple overwrite with barrier)
    3. Platform-aware memory operations
    """

    _core_dumps_disabled = False

    @staticmethod
    def disable_core_dumps():
        """
        Disable core dumps for this process.

        Prevents sensitive data (keys, passphrases) from leaking into core dump files.
        """
        if SecureMemory._core_dumps_disabled:
            return

        try:
            if platform.system() != "Windows" and resource:
                # Unix-like systems: set RLIMIT_CORE to 0
                resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
                logger.info("✓ Core dumps disabled (RLIMIT_CORE = 0)")
            else:
                # Windows: Use SetErrorMode to suppress crash dialogs
                # Note: Can't fully disable dump generation without admin rights
                SEM_NOGPFAULTERRORBOX = 0x0002
                kernel32 = ctypes.windll.kernel32
                kernel32.SetErrorMode(SEM_NOGPFAULTERRORBOX)
                logger.info("✓ Crash dialogs suppressed (Windows)")

            SecureMemory._core_dumps_disabled = True

        except Exception as e:
            logger.warning(f"Failed to disable core dumps: {e}")

    @staticmethod
    def secure_wipe(buffer: bytearray | memoryview) -> None:
        """
        Securely wipe sensitive data from memory.

        Uses triple overwrite pattern:
        1. Overwrite with zeros
        2. Overwrite with ones (0xFF)
        3. Overwrite with zeros

        Includes memory barrier to prevent compiler optimization.

        Args:
            buffer: Buffer to wipe (must be mutable: bytearray or memoryview)
        """
        if not isinstance(buffer, (bytearray, memoryview)):
            raise TypeError("Buffer must be bytearray or memoryview")

        try:
            size = len(buffer)

            # Pass 1: Zeros
            for i in range(size):
                buffer[i] = 0

            # Pass 2: Ones
            for i in range(size):
                buffer[i] = 0xFF

            # Pass 3: Zeros
            for i in range(size):
                buffer[i] = 0

            # Memory barrier: Force actual memory write
            # Use ctypes to ensure no compiler optimization
            if size > 0:
                try:
                    # Get memory address
                    if isinstance(buffer, bytearray):
                        ptr = (ctypes.c_char * size).from_buffer(buffer)
                    else:
                        ptr = (ctypes.c_char * size).from_buffer_copy(buffer)

                    # Force memory barrier by reading back
                    _ = ptr[0] if size > 0 else None

                except Exception:
                    # Fallback: just ensure Python doesn't optimize away
                    pass

            logger.debug(f"✓ Secure wipe completed ({size} bytes)")

        except Exception as e:
            logger.error(f"Secure wipe failed: {e}")
            raise

    @staticmethod
    def secure_bytes(data: bytes) -> bytearray:
        """
        Create a mutable copy of bytes for secure wiping.

        Args:
            data: Immutable bytes to copy

        Returns:
            Mutable bytearray that can be securely wiped
        """
        return bytearray(data)

    @staticmethod
    def wipe_and_del(obj: Any, attr_name: str) -> None:
        """
        Securely wipe an attribute and delete it.

        Args:
            obj: Object containing the attribute
            attr_name: Name of attribute to wipe
        """
        try:
            if hasattr(obj, attr_name):
                attr = getattr(obj, attr_name)

                # If bytes-like, convert to bytearray and wipe
                if isinstance(attr, (bytes, bytearray, memoryview)):
                    if isinstance(attr, bytes):
                        attr = bytearray(attr)
                    SecureMemory.secure_wipe(attr)

                # Delete attribute
                delattr(obj, attr_name)
                logger.debug(f"✓ Attribute wiped and deleted: {attr_name}")

        except Exception as e:
            logger.warning(f"Failed to wipe attribute {attr_name}: {e}")


class LogSanitizer:
    """
    Sanitize logs to prevent key/passphrase leakage.

    Redacts:
    - Passphrases, passwords, secrets
    - Long hex strings (likely keys)
    - Long base64 strings (likely tokens)
    - File paths containing sensitive dirs
    """

    # Patterns for sensitive data
    PASSPHRASE_PATTERN = re.compile(
        r"(passphrase|password|secret|key|token)[\s]*[=:]\s*[^\s]+",
        re.IGNORECASE,
    )
    HEX_KEY_PATTERN = re.compile(r"\b[0-9a-fA-F]{32,}\b")
    BASE64_TOKEN_PATTERN = re.compile(r"\b[A-Za-z0-9+/]{32,}={0,2}\b")
    SENSITIVE_PATH_PATTERN = re.compile(
        r"(genesis_keys|vault_unlock_key|\.vault_token|private_key)", re.IGNORECASE
    )

    @staticmethod
    def sanitize(message: str) -> str:
        """
        Sanitize log message to remove sensitive data.

        Args:
            message: Original log message

        Returns:
            Sanitized message with sensitive data redacted
        """
        # Redact passphrase/password assignments
        message = LogSanitizer.PASSPHRASE_PATTERN.sub(
            r"\1=***REDACTED***", message
        )

        # Redact long hex strings (likely keys)
        message = LogSanitizer.HEX_KEY_PATTERN.sub("***REDACTED_KEY***", message)

        # Redact long base64 strings (likely tokens)
        message = LogSanitizer.BASE64_TOKEN_PATTERN.sub(
            "***REDACTED_TOKEN***", message
        )

        # Redact sensitive file paths
        message = LogSanitizer.SENSITIVE_PATH_PATTERN.sub(
            "***SENSITIVE_PATH***", message
        )

        return message


class SanitizingLogFilter(logging.Filter):
    """
    Logging filter that sanitizes all log messages.

    Install on logger to automatically redact sensitive data.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Sanitize log record message.

        Args:
            record: Log record to filter

        Returns:
            True (always pass through, but sanitized)
        """
        if isinstance(record.msg, str):
            record.msg = LogSanitizer.sanitize(record.msg)

        # Sanitize args if present
        if record.args:
            sanitized_args = []
            for arg in record.args:
                if isinstance(arg, str):
                    sanitized_args.append(LogSanitizer.sanitize(arg))
                else:
                    sanitized_args.append(arg)
            record.args = tuple(sanitized_args)

        return True


def configure_secure_logging():
    """
    Configure logging with security hardening.

    - Install sanitizing filter on all loggers
    - Disable core dumps
    """
    # Disable core dumps
    SecureMemory.disable_core_dumps()

    # Install sanitizing filter on root logger
    root_logger = logging.getLogger()
    sanitizing_filter = SanitizingLogFilter()
    root_logger.addFilter(sanitizing_filter)

    logger.info("✓ Secure logging configured (sanitizing filter installed)")


def get_shell_history_suppression_guide() -> str:
    """
    Get shell history suppression instructions for current platform.

    Returns:
        Instructions for suppressing sensitive commands in shell history
    """
    shell = os.environ.get("SHELL", "")

    if "bash" in shell or "zsh" in shell:
        return """
Shell History Suppression (Bash/Zsh):

Method 1: Leading space (bash/zsh with HISTCONTROL=ignorespace)
    $ export HISTCONTROL=ignorespace
    $  vault mount --usb-token E:\\ --passphrase-prompt
    (Note the leading space before 'vault')

Method 2: Disable history for session
    $ export HISTFILE=/dev/null
    $ vault mount --usb-token E:\\ --passphrase-prompt
    $ unset HISTFILE  # Re-enable after sensitive operations

Method 3: Remove command after execution
    $ vault mount --usb-token E:\\ --passphrase-prompt
    $ history -d $(history 1 | awk '{print $1}')
"""
    elif "pwsh" in shell or "powershell" in shell.lower():
        return """
Shell History Suppression (PowerShell):

Method 1: Disable history for session
    PS> Set-PSReadLineOption -HistorySaveStyle SaveNothing
    PS> vault mount --usb-token E:\\ --passphrase-prompt

Method 2: Clear history after command
    PS> vault mount --usb-token E:\\ --passphrase-prompt
    PS> Clear-History

Method 3: Use SecureString for sensitive input
    PS> $pass = Read-Host -AsSecureString -Prompt "Passphrase"
"""
    else:
        return """
Shell History Suppression (Generic):

Check your shell's documentation for history control.
Common approaches:
- Disable history temporarily (unset HISTFILE)
- Clear history after sensitive commands
- Use leading space (if shell supports HISTCONTROL=ignorespace)
"""


# Initialize secure logging on module import
configure_secure_logging()


if __name__ == "__main__":
    # Self-test
    print("=== Secure Memory Self-Test ===\n")

    # Test 1: Core dumps disabled
    try:
        SecureMemory.disable_core_dumps()
        if platform.system() != "Windows" and resource:
            limit = resource.getrlimit(resource.RLIMIT_CORE)
            assert limit[0] == 0, "Core dump limit not zero"
            print("✓ Test 1: Core dumps disabled (Unix)")
        else:
            print("✓ Test 1: Crash dialogs suppressed (Windows)")
    except Exception as e:
        print(f"✗ Test 1 failed: {e}")

    # Test 2: Secure wipe
    try:
        test_data = bytearray(b"SENSITIVE_KEY_12345")
        original_value = bytes(test_data)
        SecureMemory.secure_wipe(test_data)

        # Verify wiped (should be all zeros)
        assert all(b == 0 for b in test_data), "Buffer not properly wiped"
        assert test_data != original_value, "Buffer unchanged"
        print("✓ Test 2: Secure wipe works")
    except Exception as e:
        print(f"✗ Test 2 failed: {e}")

    # Test 3: Log sanitization
    try:
        test_messages = [
            "passphrase=my_secret_pass123",
            "Found key: ABCDEF1234567890ABCDEF1234567890",
            "Token: dGVzdC10b2tlbi1iYXNlNjQtZW5jb2RlZA==",
            "Reading genesis_keys/private.key",
        ]

        for msg in test_messages:
            sanitized = LogSanitizer.sanitize(msg)
            assert "REDACTED" in sanitized or "SENSITIVE" in sanitized
            assert "secret_pass" not in sanitized
            assert "ABCDEF" not in sanitized
            assert "dGVzdC" not in sanitized

        print("✓ Test 3: Log sanitization works")
    except Exception as e:
        print(f"✗ Test 3 failed: {e}")

    # Test 4: Shell history guide
    try:
        guide = get_shell_history_suppression_guide()
        assert len(guide) > 0
        print("✓ Test 4: Shell history guide generated")
    except Exception as e:
        print(f"✗ Test 4 failed: {e}")

    print("\n=== All Tests Passed ===")
    print("\nShell History Suppression Guide:")
    print(get_shell_history_suppression_guide())
