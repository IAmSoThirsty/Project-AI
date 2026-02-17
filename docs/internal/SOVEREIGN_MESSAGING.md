# 🔐 Sovereign Messaging System

**Secure P2P encrypted messaging for users and AI agents**

## Overview

The Sovereign Messaging System provides industry-standard end-to-end encrypted communication between users and AI agents with complete privacy and sovereignty. Messages self-destruct after being read, leaving no traces.

### Key Features

✅ **Communication Codes** - Easy pairing with XXXX-XXXX-XXXX-XXXX format ✅ **Hybrid Encryption** - RSA-2048 OAEP + AES-256-CBC ✅ **Message Lifecycle** - SENT → DELIVERED → SEEN → DELETED ✅ **Self-Destruct** - Auto-delete 1 hour after SEEN ✅ **Complete Privacy** - Local-only storage, no cloud/backup/telemetry ✅ **P2P Architecture** - No central server ✅ **User & AI Support** - Communication between humans and AI agents

## Message Lifecycle

```
📤 SENT      → Message encrypted and sent
📥 DELIVERED → Received on device
👁️  SEEN      → Opened by recipient (⏰ Timer starts: 1 hour)
🗑️  DELETED   → Auto-erased permanently ✅
```

### Timeline Example

```
14:00 - Sent
14:15 - Delivered
14:30 - Seen ← Timer starts
15:30 - Deleted ✅ (exactly 1 hour after seen)
```

## Security Architecture

### Encryption Details

**Hybrid Encryption:**

```
├── RSA-2048 OAEP
│   └── Encrypts AES key
└── AES-256-CBC
    └── Encrypts message content
```

- **Algorithm**: RSA-2048 + AES-256 hybrid
- **Strength**: Industry-standard encryption
- **Keys**: 2048-bit RSA keypair per participant
- **Message**: AES-256-CBC per message
- **Padding**: OAEP + PKCS7
- **Hashing**: SHA-256
- **Backend**: cryptography library

### Threat Protection

| Threat        | Protection                 |
| ------------- | -------------------------- |
| Interception  | End-to-end encryption      |
| Server breach | No central server          |
| Forensics     | Self-destructing messages  |
| Man-in-middle | Public key verification    |
| Brute force   | 2048-bit RSA + 256-bit AES |

## Storage

### Local-Only Data Structure

```
data/sovereign_messages/
├── identity.json    ← Your keys & code (LOCAL ONLY)
├── contacts.json    ← Your contacts (LOCAL ONLY)
└── messages.json    ← Encrypted messages (LOCAL ONLY)
```

**Privacy guarantees:**

- ✅ 100% Local Storage - No cloud
- ✅ Zero Telemetry - No tracking
- ✅ No Accounts Required
- ✅ No Cloud Sync
- ✅ Maximum Privacy

**⚠️ Important**: No backup means no disaster recovery. If you lose your device or the data directory, all messages and contacts are permanently lost. This is by design for maximum privacy, but consider the implications for your use case.

## Communication Code Format

Format: `XXXX-XXXX-XXXX-XXXX` Example: `AB3D-7F2K-9QWE-5RT8`

### Usage Flow

1. **Share your code** with contacts
1. **They share theirs** with you
1. **Secure pairing complete!**
1. **Start messaging** ✅

## Quick Start

### Python API

```python
from src.features.sovereign_messaging import SovereignMessaging, ParticipantType

# Initialize for a user

user_messaging = SovereignMessaging(participant_name="Alice")

# Initialize for an AI

ai_messaging = SovereignMessaging(participant_name="AI_Assistant")
ai_messaging.set_participant_type(ParticipantType.AI)

# Get your communication code

print(f"Your code: {user_messaging.get_communication_code()}")
print(f"Your public key: {user_messaging.get_public_key()}")

# Pair with a contact

user_messaging.pair_with_contact(
    contact_name="Bob",
    contact_code="ABCD-1234-EFGH-5678",
    contact_public_key="-----BEGIN PUBLIC KEY-----\n...",
    participant_type=ParticipantType.USER
)

# Send a message

message_id = user_messaging.send_message(
    recipient_code="ABCD-1234-EFGH-5678",
    message_content="Hello, this is a secure message!"
)

# Receive a message (Bob's side)

bob_messaging = SovereignMessaging(participant_name="Bob")
received_message = bob_messaging.receive_message(
    sender_code=user_messaging.get_communication_code(),
    encrypted_aes_key_hex="...",
    iv_hex="...",
    ciphertext_hex="..."
)

# Mark message as seen (starts 1-hour self-destruct timer)

bob_messaging.mark_message_seen(received_message["message_id"])

# Process self-destruct (call periodically)

deleted_count = bob_messaging.process_self_destruct()
```

### CLI Interface

```bash

# Run standalone CLI

python src/features/sovereign_messaging.py

# Or with a specific name

python src/features/sovereign_messaging.py Alice
```

#### CLI Menu

```
🔐 SOVEREIGN MESSAGING SYSTEM
==================================================
For Users and AI Agents
==================================================

MENU:

1. Show my communication code
2. Pair with contact
3. Send message
4. View messages
5. Mark message as seen
6. Process self-destruct
7. Show contacts
8. Set participant type (USER/AI)
9. Exit

```

## Use Cases

✅ Confidential business communication ✅ Sensitive personal messages ✅ Whistleblowing & journalism ✅ Privacy-conscious users ✅ Medical/legal professionals ✅ Human rights activists ✅ AI-human secure interaction ✅ Anyone valuing digital sovereignty

## Integration with Project-AI

The sovereign messaging system can be integrated into the main Project-AI application:

```python

# In your Project-AI code

from src.features.sovereign_messaging import SovereignMessaging, ParticipantType

# Initialize messaging for the AI persona

ai_messaging = SovereignMessaging(
    data_dir="data/sovereign_messages",
    participant_name="Project-AI"
)
ai_messaging.set_participant_type(ParticipantType.AI)

# Enable users to pair with the AI

ai_code = ai_messaging.get_communication_code()
ai_public_key = ai_messaging.get_public_key()

# User pairs with AI

# AI can now send/receive encrypted messages with users

```

## Testing

Comprehensive test suite with 27 tests covering:

- Communication code generation and validation
- RSA-2048 keypair generation
- AES-256-CBC encryption/decryption
- Hybrid encryption workflow
- Contact pairing
- Message sending/receiving
- Message lifecycle and status tracking
- Self-destruct timer functionality
- Data persistence
- User-AI conversation flows

```bash

# Run tests

python -m pytest tests/test_sovereign_messaging.py -v

# All 27 tests should pass

```

## Future Enhancements

Potential additions (not yet implemented):

- ☐ QR code scanning for easy code exchange
- ☐ Group messaging support
- ☐ Voice/video calls
- ☐ File attachments
- ☐ Optional read receipts
- ☐ Message pinning
- ☐ Contact verification badges

## Security Considerations

### What This System Provides

✅ **Forward secrecy through per-message AES keys** - Each message uses a unique encryption key ✅ **No server-side storage** - All data stays on your device ✅ **Self-destructing messages** - Auto-deletion after reading ✅ **Local-only data storage** - Never transmitted to third parties ✅ **PKCS7 padding validation** - Protects against padding oracle attacks ✅ **File permission protection** - Private keys stored with 0o600 permissions on Unix systems

### What This System Does NOT Provide

❌ **Network transport** - You must implement message delivery (P2P, local network, etc.) ❌ **Key rotation** - RSA keys are static per identity (consider creating new identities periodically) ❌ **Multi-device sync** - Each device has its own identity ❌ **Backup/recovery** - Data loss is permanent by design ❌ **Message authentication codes** - Relies on encryption for integrity ❌ **Password-protected private keys** - Private keys are stored unencrypted locally (ensure device security)

### Best Practices

1. **Secure key exchange** - Exchange communication codes and public keys through secure channels
1. **Verify contacts** - Confirm identity before pairing
1. **Regular self-destruct** - Call `process_self_destruct()` regularly
1. **Protect identity.json** - This file contains your private key
1. **No screenshots** - Respect message privacy
1. **Device security** - Keep your device secure (encrypted disk, strong password)

## License

This module is part of Project-AI and follows the same MIT license.

## Support

For issues or questions:

- GitHub Issues: https://github.com/IAmSoThirsty/Project-AI/issues
- Review code: `src/features/sovereign_messaging.py`
- Review tests: `tests/test_sovereign_messaging.py`

______________________________________________________________________

**Remember**: With great privacy comes great responsibility. Use this system ethically and legally.
