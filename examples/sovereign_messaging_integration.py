"""
Integration example: Sovereign Messaging with Project-AI.

This example demonstrates how to integrate the sovereign messaging system
with the main Project-AI application, enabling secure communication between
users and AI agents.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.features.sovereign_messaging import (
    MessageStatus,
    ParticipantType,
    SovereignMessaging,
)


def example_user_ai_secure_conversation():
    """Example: User communicates securely with AI assistant."""
    print("=" * 60)
    print("EXAMPLE: User-AI Secure Conversation")
    print("=" * 60)

    # Initialize AI agent messaging
    ai_agent = SovereignMessaging(
        data_dir="data/sovereign_messages_ai", participant_name="ProjectAI_Assistant"
    )
    ai_agent.set_participant_type(ParticipantType.AI)

    # Initialize user messaging
    user = SovereignMessaging(
        data_dir="data/sovereign_messages_user", participant_name="Alice"
    )

    # Display pairing information
    print("\n🤖 AI Agent Information:")
    print("   Name: ProjectAI_Assistant")
    print(f"   Code: {ai_agent.get_communication_code()}")
    print("   Type: AI")

    print("\n👤 User Information:")
    print("   Name: Alice")
    print(f"   Code: {user.get_communication_code()}")
    print("   Type: USER")

    # Mutual pairing
    print("\n🔗 Pairing user and AI...")
    user.pair_with_contact(
        "ProjectAI_Assistant",
        ai_agent.get_communication_code(),
        ai_agent.get_public_key(),
        participant_type=ParticipantType.AI,
    )

    ai_agent.pair_with_contact(
        "Alice",
        user.get_communication_code(),
        user.get_public_key(),
        participant_type=ParticipantType.USER,
    )
    print("✅ Pairing complete!")

    # User sends encrypted question to AI
    print("\n📤 User sends encrypted message to AI...")
    question = "What is the meaning of life?"
    user_msg_id = user.send_message(ai_agent.get_communication_code(), question)
    print(f"   Question: '{question}'")
    print(f"   Message ID: {user_msg_id}")
    print(f"   Status: {MessageStatus.SENT.value}")

    # AI receives and decrypts the message
    print("\n📥 AI receives and decrypts message...")
    user_sent_msg = user.get_messages()[0]
    ai_received = ai_agent.receive_message(
        user.get_communication_code(),
        user_sent_msg["encrypted_aes_key"],
        user_sent_msg["iv"],
        user_sent_msg["ciphertext"],
    )
    print(f"   Decrypted: '{ai_received['content']}'")
    print(f"   Status: {ai_received['status']}")

    # AI processes and sends encrypted response
    print("\n📤 AI sends encrypted response...")
    ai_response = "42 - The answer to life, the universe, and everything!"
    ai_msg_id = ai_agent.send_message(user.get_communication_code(), ai_response)
    print(f"   Response: '{ai_response}'")
    print(f"   Message ID: {ai_msg_id}")

    # User receives AI's response
    print("\n📥 User receives AI response...")
    ai_sent_msg = ai_agent.get_messages()[-1]
    user_received = user.receive_message(
        ai_agent.get_communication_code(),
        ai_sent_msg["encrypted_aes_key"],
        ai_sent_msg["iv"],
        ai_sent_msg["ciphertext"],
    )
    print(f"   Decrypted: '{user_received['content']}'")
    print(f"   Status: {user_received['status']}")

    # User marks message as seen (starts self-destruct timer)
    print("\n👁️  User marks AI response as seen...")
    user.mark_message_seen(user_received["message_id"])
    seen_msg = user.get_messages()[-1]
    print(f"   Status: {seen_msg['status']}")
    print(f"   Self-destruct timer: 1 hour from {seen_msg['seen_at']}")
    print(f"   Will be deleted at: {seen_msg['delete_at']}")

    print("\n✅ Secure conversation complete!")
    print("\n🔐 Security Summary:")
    print("   - All messages encrypted with RSA-2048 + AES-256")
    print("   - No plaintext stored")
    print("   - Messages will auto-delete after 1 hour")
    print("   - No server involvement (P2P)")
    print("   - Complete sovereignty and privacy")


def example_integration_with_project_ai():
    """Example: Integrating sovereign messaging into Project-AI main app."""
    print("\n" + "=" * 60)
    print("EXAMPLE: Integration with Project-AI")
    print("=" * 60)

    print("""
Integration Steps:

1. **Initialize Sovereign Messaging in main.py:**

   from src.features.sovereign_messaging import SovereignMessaging, ParticipantType
   
   # In your Project-AI initialization
   self.messaging = SovereignMessaging(
       data_dir="data/sovereign_messages",
       participant_name="ProjectAI"
   )
   self.messaging.set_participant_type(ParticipantType.AI)

2. **Display Communication Code in UI:**

   # In your GUI or CLI
   code = self.messaging.get_communication_code()
   print(f"AI Communication Code: {code}")
   print("Share this code with users to establish secure messaging")

3. **Handle User Pairing Requests:**

   def pair_with_user(self, user_name, user_code, user_public_key):
       success = self.messaging.pair_with_contact(
           user_name,
           user_code,
           user_public_key,
           participant_type=ParticipantType.USER
       )
       return success

4. **Receive and Process Encrypted Messages:**

   def receive_encrypted_message(self, sender_code, encrypted_data):
       # Decrypt message
       message = self.messaging.receive_message(
           sender_code,
           encrypted_data["encrypted_aes_key"],
           encrypted_data["iv"],
           encrypted_data["ciphertext"]
       )
       
       if message:
           # Process the decrypted message
           response = self.process_user_query(message["content"])
           
           # Send encrypted response
           self.messaging.send_message(sender_code, response)

5. **Periodic Self-Destruct Processing:**

   # Run this periodically (e.g., every hour)
   def cleanup_old_messages(self):
       deleted = self.messaging.process_self_destruct()
       if deleted > 0:
           print(f"Auto-deleted {deleted} expired messages")

6. **Display Secure Messaging Status:**

   contacts = self.messaging.get_contacts()
   messages = self.messaging.get_messages(include_deleted=False)
   
   print(f"Paired contacts: {len(contacts)}")
   print(f"Active messages: {len(messages)}")
""")


def example_multi_user_scenario():
    """Example: Multiple users communicating with AI."""
    print("\n" + "=" * 60)
    print("EXAMPLE: Multi-User Scenario")
    print("=" * 60)

    # Initialize AI agent
    ai = SovereignMessaging(
        data_dir="data/sovereign_messages_multi_ai", participant_name="ProjectAI_Hub"
    )
    ai.set_participant_type(ParticipantType.AI)

    # Initialize multiple users
    users = []
    for name in ["Alice", "Bob", "Charlie"]:
        user = SovereignMessaging(
            data_dir=f"data/sovereign_messages_multi_{name.lower()}",
            participant_name=name,
        )
        users.append((name, user))

    print(f"\n🤖 AI Hub: {ai.get_communication_code()}")

    # Pair all users with AI
    print("\n🔗 Pairing users with AI...")
    for name, user in users:
        # User pairs with AI
        user.pair_with_contact(
            "ProjectAI_Hub",
            ai.get_communication_code(),
            ai.get_public_key(),
            participant_type=ParticipantType.AI,
        )

        # AI pairs with user
        ai.pair_with_contact(
            name,
            user.get_communication_code(),
            user.get_public_key(),
            participant_type=ParticipantType.USER,
        )

        print(f"   ✅ {name} ({user.get_communication_code()}) paired with AI")

    # Each user sends a message to AI
    print("\n📤 Users send messages to AI...")
    for name, user in users:
        message = f"Hello from {name}! This is a secure test."
        user.send_message(ai.get_communication_code(), message)
        print(f"   {name}: '{message}'")

    # AI receives all messages
    print("\n📥 AI receives and processes messages...")
    for name, user in users:
        user_msg = user.get_messages()[0]
        ai_received = ai.receive_message(
            user.get_communication_code(),
            user_msg["encrypted_aes_key"],
            user_msg["iv"],
            user_msg["ciphertext"],
        )
        print(f"   From {name}: '{ai_received['content']}'")

        # AI responds to each user
        response = f"Hello {name}, I received your secure message!"
        ai.send_message(user.get_communication_code(), response)

    print("\n✅ Multi-user secure messaging complete!")
    print(f"   Total contacts: {len(ai.get_contacts())}")
    print(f"   Total messages: {len(ai.get_messages())}")


def main():
    """Run all integration examples."""
    print("\n" + "🔐" * 30)
    print("SOVEREIGN MESSAGING - PROJECT-AI INTEGRATION EXAMPLES")
    print("🔐" * 30)

    # Example 1: Basic user-AI conversation
    example_user_ai_secure_conversation()

    # Example 2: Integration guide
    example_integration_with_project_ai()

    # Example 3: Multi-user scenario
    example_multi_user_scenario()

    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
