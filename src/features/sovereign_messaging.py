"""
Sovereign Messaging System - Secure P2P encrypted messaging for users and AI agents.

Features:
- Communication codes (XXXX-XXXX-XXXX-XXXX format) for secure pairing
- RSA-2048 + AES-256-CBC hybrid encryption
- Message lifecycle: SENT → DELIVERED → SEEN → DELETED
- Self-destruct: Auto-delete 1 hour after SEEN
- Complete privacy: Local-only storage, no cloud/backup/telemetry
- P2P architecture: No central server
"""

import hashlib
import json
import secrets
import string
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


class MessageStatus(Enum):
    """Message lifecycle states."""

    SENT = "📤 SENT"
    DELIVERED = "📥 DELIVERED"
    SEEN = "👁️ SEEN"
    DELETED = "🗑️ DELETED"


class ParticipantType(Enum):
    """Type of messaging participant."""

    USER = "user"
    AI = "ai"


class SovereignMessaging:
    """
    Sovereign messaging system with military-grade encryption.

    Supports secure communication between:
    - User ↔ User
    - User ↔ AI
    - AI ↔ AI
    """

    def __init__(self, data_dir: str | None = None, participant_name: str = "default"):
        """
        Initialize sovereign messaging system.

        Args:
            data_dir: Directory for storing encrypted data (default: data/sovereign_messages/)
            participant_name: Name identifier for this participant (user or AI)
        """
        if data_dir is None:
            base_dir = Path(__file__).parent.parent.parent
            data_dir = base_dir / "data" / "sovereign_messages"
        else:
            data_dir = Path(data_dir)

        self.data_dir = Path(data_dir)
        self.participant_name = participant_name

        # Create data directory structure
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # File paths for local storage
        self.identity_file = self.data_dir / "identity.json"
        self.contacts_file = self.data_dir / "contacts.json"
        self.messages_file = self.data_dir / "messages.json"

        # Initialize or load identity
        self.identity = self._load_or_create_identity()
        self.contacts = self._load_contacts()
        self.messages = self._load_messages()

    def _generate_communication_code(self) -> str:
        """
        Generate a communication code in format XXXX-XXXX-XXXX-XXXX.

        Returns:
            Communication code string
        """
        # Use alphanumeric characters (uppercase + digits) for clarity
        chars = string.ascii_uppercase + string.digits
        # Generate 4 groups of 4 characters
        groups = []
        for _ in range(4):
            group = "".join(secrets.choice(chars) for _ in range(4))
            groups.append(group)
        return "-".join(groups)

    def _generate_rsa_keypair(self) -> tuple[bytes, bytes]:
        """
        Generate RSA-2048 keypair.

        Returns:
            Tuple of (private_key_pem, public_key_pem)
        """
        # Generate RSA-2048 private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )

        # Serialize private key to PEM format
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        # Serialize public key to PEM format
        public_key = private_key.public_key()
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        return private_pem, public_pem

    def _load_or_create_identity(self) -> dict:
        """
        Load existing identity or create new one.

        Returns:
            Identity dictionary with keys, code, and metadata
        """
        if self.identity_file.exists():
            with open(self.identity_file) as f:
                return json.load(f)

        # Create new identity
        private_key, public_key = self._generate_rsa_keypair()
        communication_code = self._generate_communication_code()

        identity = {
            "participant_name": self.participant_name,
            "communication_code": communication_code,
            "private_key": private_key.decode("utf-8"),
            "public_key": public_key.decode("utf-8"),
            "created_at": datetime.now().isoformat(),
            "participant_type": ParticipantType.USER.value  # Can be changed to AI
        }

        # Save identity
        with open(self.identity_file, "w") as f:
            json.dump(identity, f, indent=2)

        return identity

    def _load_contacts(self) -> dict:
        """Load contacts from file."""
        if self.contacts_file.exists():
            with open(self.contacts_file) as f:
                return json.load(f)
        # Create empty contacts file
        with open(self.contacts_file, "w") as f:
            json.dump({}, f)
        return {}

    def _save_contacts(self):
        """Save contacts to file."""
        with open(self.contacts_file, "w") as f:
            json.dump(self.contacts, f, indent=2)

    def _load_messages(self) -> list[dict]:
        """Load messages from file."""
        if self.messages_file.exists():
            with open(self.messages_file) as f:
                return json.load(f)
        # Create empty messages file
        with open(self.messages_file, "w") as f:
            json.dump([], f)
        return []

    def _save_messages(self):
        """Save messages to file."""
        with open(self.messages_file, "w") as f:
            json.dump(self.messages, f, indent=2)

    def get_communication_code(self) -> str:
        """
        Get this participant's communication code for sharing.

        Returns:
            Communication code string (XXXX-XXXX-XXXX-XXXX)
        """
        return self.identity["communication_code"]

    def get_public_key(self) -> str:
        """
        Get this participant's public key for sharing.

        Returns:
            Public key PEM string
        """
        return self.identity["public_key"]

    def validate_communication_code(self, code: str) -> bool:
        """
        Validate communication code format.

        Args:
            code: Communication code to validate

        Returns:
            True if valid format, False otherwise
        """
        # Check format: XXXX-XXXX-XXXX-XXXX
        parts = code.split("-")
        if len(parts) != 4:
            return False

        # Each part should be 4 alphanumeric characters
        chars = string.ascii_uppercase + string.digits
        for part in parts:
            if len(part) != 4:
                return False
            if not all(c in chars for c in part):
                return False

        return True

    def pair_with_contact(
        self,
        contact_name: str,
        contact_code: str,
        contact_public_key: str,
        participant_type: ParticipantType = ParticipantType.USER
    ) -> bool:
        """
        Pair with a contact using their communication code and public key.

        Args:
            contact_name: Name of the contact
            contact_code: Contact's communication code
            contact_public_key: Contact's public key PEM
            participant_type: Type of participant (USER or AI)

        Returns:
            True if pairing successful, False otherwise
        """
        # Validate communication code
        if not self.validate_communication_code(contact_code):
            return False

        # Store contact
        self.contacts[contact_code] = {
            "name": contact_name,
            "code": contact_code,
            "public_key": contact_public_key,
            "participant_type": participant_type.value,
            "paired_at": datetime.now().isoformat()
        }

        self._save_contacts()
        return True

    def _encrypt_with_rsa(self, data: bytes, public_key_pem: str) -> bytes:
        """
        Encrypt data with RSA-2048 OAEP.

        Args:
            data: Data to encrypt
            public_key_pem: Public key PEM string

        Returns:
            Encrypted data bytes
        """
        # Load public key
        public_key = serialization.load_pem_public_key(
            public_key_pem.encode("utf-8"),
            backend=default_backend()
        )

        # Encrypt with RSA OAEP
        encrypted = public_key.encrypt(
            data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        return encrypted

    def _decrypt_with_rsa(self, encrypted_data: bytes) -> bytes:
        """
        Decrypt data with RSA-2048 OAEP.

        Args:
            encrypted_data: Encrypted data bytes

        Returns:
            Decrypted data bytes
        """
        # Load private key
        private_key = serialization.load_pem_private_key(
            self.identity["private_key"].encode("utf-8"),
            password=None,
            backend=default_backend()
        )

        # Decrypt with RSA OAEP
        decrypted = private_key.decrypt(
            encrypted_data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        return decrypted

    def _encrypt_with_aes(self, plaintext: str) -> tuple[bytes, bytes, bytes]:
        """
        Encrypt message content with AES-256-CBC.

        Args:
            plaintext: Message content to encrypt

        Returns:
            Tuple of (aes_key, iv, ciphertext)
        """
        # Generate random AES-256 key
        aes_key = secrets.token_bytes(32)  # 256 bits

        # Generate random IV
        iv = secrets.token_bytes(16)  # 128 bits

        # Pad plaintext to multiple of 16 bytes (PKCS7)
        plaintext_bytes = plaintext.encode("utf-8")
        padding_length = 16 - (len(plaintext_bytes) % 16)
        padded_plaintext = plaintext_bytes + bytes([padding_length] * padding_length)

        # Encrypt with AES-256-CBC
        cipher = Cipher(
            algorithms.AES(aes_key),
            modes.CBC(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()

        return aes_key, iv, ciphertext

    def _decrypt_with_aes(self, aes_key: bytes, iv: bytes, ciphertext: bytes) -> str:
        """
        Decrypt message content with AES-256-CBC.

        Args:
            aes_key: AES key
            iv: Initialization vector
            ciphertext: Encrypted message

        Returns:
            Decrypted plaintext string
        """
        # Decrypt with AES-256-CBC
        cipher = Cipher(
            algorithms.AES(aes_key),
            modes.CBC(iv),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()

        # Remove PKCS7 padding
        padding_length = padded_plaintext[-1]
        plaintext_bytes = padded_plaintext[:-padding_length]

        return plaintext_bytes.decode("utf-8")

    def send_message(self, recipient_code: str, message_content: str) -> str | None:
        """
        Send encrypted message to a contact.

        Uses hybrid encryption:
        1. Encrypt message with AES-256-CBC
        2. Encrypt AES key with recipient's RSA-2048 public key

        Args:
            recipient_code: Recipient's communication code
            message_content: Message text to send

        Returns:
            Message ID if successful, None otherwise
        """
        # Check if contact exists
        if recipient_code not in self.contacts:
            return None

        contact = self.contacts[recipient_code]

        # Hybrid encryption
        # Step 1: Encrypt message with AES-256-CBC
        aes_key, iv, ciphertext = self._encrypt_with_aes(message_content)

        # Step 2: Encrypt AES key with recipient's RSA public key
        encrypted_aes_key = self._encrypt_with_rsa(aes_key, contact["public_key"])

        # Generate message ID
        message_id = hashlib.sha256(
            f"{self.identity['communication_code']}{recipient_code}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]

        # Create message record
        message = {
            "message_id": message_id,
            "sender_code": self.identity["communication_code"],
            "sender_name": self.participant_name,
            "recipient_code": recipient_code,
            "recipient_name": contact["name"],
            "encrypted_aes_key": encrypted_aes_key.hex(),
            "iv": iv.hex(),
            "ciphertext": ciphertext.hex(),
            "status": MessageStatus.SENT.value,
            "sent_at": datetime.now().isoformat(),
            "delivered_at": None,
            "seen_at": None,
            "delete_at": None
        }

        # Save message
        self.messages.append(message)
        self._save_messages()

        return message_id

    def receive_message(
        self,
        sender_code: str,
        encrypted_aes_key_hex: str,
        iv_hex: str,
        ciphertext_hex: str
    ) -> dict | None:
        """
        Receive and decrypt message from a contact.

        Args:
            sender_code: Sender's communication code
            encrypted_aes_key_hex: Hex-encoded encrypted AES key
            iv_hex: Hex-encoded IV
            ciphertext_hex: Hex-encoded ciphertext

        Returns:
            Message dict with decrypted content, or None if failed
        """
        # Check if sender is a contact
        if sender_code not in self.contacts:
            return None

        contact = self.contacts[sender_code]

        try:
            # Step 1: Decrypt AES key with our RSA private key
            encrypted_aes_key = bytes.fromhex(encrypted_aes_key_hex)
            aes_key = self._decrypt_with_rsa(encrypted_aes_key)

            # Step 2: Decrypt message with AES key
            iv = bytes.fromhex(iv_hex)
            ciphertext = bytes.fromhex(ciphertext_hex)
            plaintext = self._decrypt_with_aes(aes_key, iv, ciphertext)

            # Generate message ID
            message_id = hashlib.sha256(
                f"{sender_code}{self.identity['communication_code']}{datetime.now().isoformat()}".encode()
            ).hexdigest()[:16]

            # Create received message record
            message = {
                "message_id": message_id,
                "sender_code": sender_code,
                "sender_name": contact["name"],
                "recipient_code": self.identity["communication_code"],
                "recipient_name": self.participant_name,
                "content": plaintext,
                "status": MessageStatus.DELIVERED.value,
                "sent_at": None,  # Unknown from sender's perspective
                "delivered_at": datetime.now().isoformat(),
                "seen_at": None,
                "delete_at": None
            }

            # Save message
            self.messages.append(message)
            self._save_messages()

            return message

        except Exception:
            return None

    def mark_message_seen(self, message_id: str) -> bool:
        """
        Mark message as seen and start self-destruct timer (1 hour).

        Args:
            message_id: ID of message to mark as seen

        Returns:
            True if successful, False otherwise
        """
        for message in self.messages:
            if message["message_id"] == message_id and message["status"] != MessageStatus.DELETED.value:
                message["status"] = MessageStatus.SEEN.value
                message["seen_at"] = datetime.now().isoformat()
                # Set delete time to 1 hour from now
                delete_time = datetime.now() + timedelta(hours=1)
                message["delete_at"] = delete_time.isoformat()
                self._save_messages()
                return True
        return False

    def process_self_destruct(self) -> int:
        """
        Process self-destruct for messages past their delete time.

        Returns:
            Number of messages deleted
        """
        deleted_count = 0
        now = datetime.now()

        for message in self.messages:
            if message.get("delete_at"):
                delete_time = datetime.fromisoformat(message["delete_at"])
                if now >= delete_time and message["status"] != MessageStatus.DELETED.value:
                    message["status"] = MessageStatus.DELETED.value
                    # Clear sensitive data
                    if "content" in message:
                        message["content"] = "[DELETED]"
                    if "ciphertext" in message:
                        message["ciphertext"] = ""
                    if "encrypted_aes_key" in message:
                        message["encrypted_aes_key"] = ""
                    if "iv" in message:
                        message["iv"] = ""
                    deleted_count += 1

        if deleted_count > 0:
            self._save_messages()

        return deleted_count

    def get_messages(self, include_deleted: bool = False) -> list[dict]:
        """
        Get all messages.

        Args:
            include_deleted: Whether to include deleted messages

        Returns:
            List of message dictionaries
        """
        if include_deleted:
            return self.messages

        return [
            msg for msg in self.messages
            if msg["status"] != MessageStatus.DELETED.value
        ]

    def get_contacts(self) -> dict:
        """
        Get all paired contacts.

        Returns:
            Dictionary of contacts
        """
        return self.contacts

    def set_participant_type(self, participant_type: ParticipantType):
        """
        Set the participant type (USER or AI).

        Args:
            participant_type: Type of participant
        """
        self.identity["participant_type"] = participant_type.value
        with open(self.identity_file, "w") as f:
            json.dump(self.identity, f, indent=2)


def main():
    """CLI interface for sovereign messaging."""
    import sys

    print("🔐 SOVEREIGN MESSAGING SYSTEM")
    print("=" * 50)
    print("For Users and AI Agents")
    print("=" * 50)

    # Initialize messaging system
    if len(sys.argv) > 1:
        participant_name = sys.argv[1]
    else:
        participant_name = input("Enter your name: ").strip()

    messaging = SovereignMessaging(participant_name=participant_name)

    print(f"\n✅ Identity loaded/created for: {participant_name}")
    print(f"📋 Your communication code: {messaging.get_communication_code()}")
    print(f"🔑 Your public key: {messaging.get_public_key()[:50]}...")

    while True:
        print("\n" + "=" * 50)
        print("MENU:")
        print("1. Show my communication code")
        print("2. Pair with contact")
        print("3. Send message")
        print("4. View messages")
        print("5. Mark message as seen")
        print("6. Process self-destruct")
        print("7. Show contacts")
        print("8. Set participant type (USER/AI)")
        print("9. Exit")
        print("=" * 50)

        choice = input("Choose option: ").strip()

        if choice == "1":
            print(f"\n📋 Your communication code: {messaging.get_communication_code()}")
            print(f"🔑 Your public key:\n{messaging.get_public_key()}")

        elif choice == "2":
            print("\n👥 PAIR WITH CONTACT")
            name = input("Contact name: ").strip()
            code = input("Contact code (XXXX-XXXX-XXXX-XXXX): ").strip()
            print("Paste contact's public key (end with empty line):")
            key_lines = []
            while True:
                line = input()
                if not line:
                    break
                key_lines.append(line)
            public_key = "\n".join(key_lines)

            ptype = input("Participant type (user/ai) [user]: ").strip().lower()
            participant_type = ParticipantType.AI if ptype == "ai" else ParticipantType.USER

            if messaging.pair_with_contact(name, code, public_key, participant_type):
                print("✅ Contact paired successfully!")
            else:
                print("❌ Failed to pair contact (invalid code format)")

        elif choice == "3":
            print("\n📤 SEND MESSAGE")
            contacts = messaging.get_contacts()
            if not contacts:
                print("❌ No contacts available. Pair with someone first.")
                continue

            print("Available contacts:")
            for code, contact in contacts.items():
                print(f"  - {contact['name']} ({code}) [{contact['participant_type']}]")

            recipient_code = input("Recipient code: ").strip()
            message = input("Message: ").strip()

            message_id = messaging.send_message(recipient_code, message)
            if message_id:
                print(f"✅ Message sent! ID: {message_id}")
            else:
                print("❌ Failed to send message (contact not found)")

        elif choice == "4":
            print("\n📬 MESSAGES")
            messages = messaging.get_messages(include_deleted=False)
            if not messages:
                print("No messages.")
            else:
                for msg in messages:
                    print(f"\n{'=' * 40}")
                    print(f"ID: {msg['message_id']}")
                    print(f"From: {msg['sender_name']} ({msg['sender_code']})")
                    print(f"To: {msg['recipient_name']} ({msg['recipient_code']})")
                    print(f"Status: {msg['status']}")
                    if "content" in msg:
                        print(f"Content: {msg['content']}")
                    if msg.get('seen_at'):
                        print(f"Seen at: {msg['seen_at']}")
                        print(f"Delete at: {msg['delete_at']}")

        elif choice == "5":
            message_id = input("Message ID to mark as seen: ").strip()
            if messaging.mark_message_seen(message_id):
                print("✅ Message marked as seen. Self-destruct timer started (1 hour).")
            else:
                print("❌ Message not found.")

        elif choice == "6":
            deleted = messaging.process_self_destruct()
            print(f"🗑️ Processed self-destruct: {deleted} messages deleted.")

        elif choice == "7":
            print("\n👥 CONTACTS")
            contacts = messaging.get_contacts()
            if not contacts:
                print("No contacts.")
            else:
                for code, contact in contacts.items():
                    print(f"\n{contact['name']} ({code})")
                    print(f"  Type: {contact['participant_type']}")
                    print(f"  Paired: {contact['paired_at']}")

        elif choice == "8":
            print("\nCurrent type:", messaging.identity.get("participant_type", "user"))
            ptype = input("New participant type (user/ai): ").strip().lower()
            if ptype in ["user", "ai"]:
                participant_type = ParticipantType.AI if ptype == "ai" else ParticipantType.USER
                messaging.set_participant_type(participant_type)
                print(f"✅ Participant type set to: {participant_type.value}")
            else:
                print("❌ Invalid type")

        elif choice == "9":
            print("\n👋 Goodbye!")
            break

        else:
            print("❌ Invalid option")


if __name__ == "__main__":
    main()
