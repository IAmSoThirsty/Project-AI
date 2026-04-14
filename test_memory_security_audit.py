"""Security audit test for MemoryExpansionSystem vulnerabilities."""

import os
import tempfile
import json
from app.core.ai_systems import MemoryExpansionSystem

def test_injection_vulnerabilities():
    """Test for injection vulnerabilities in memory system."""
    print("\n=== Testing Injection Vulnerabilities ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        mem = MemoryExpansionSystem(data_dir=tmpdir)
        
        # Test 1: SQL-like injection in category/key
        print("\n1. SQL-like injection in category:")
        mem.add_knowledge("'; DROP TABLE--", "test", "value")
        result = mem.get_knowledge("'; DROP TABLE--", "test")
        print(f"   Result: {result}")
        
        # Test 2: Path traversal in category
        print("\n2. Path traversal in category:")
        mem.add_knowledge("../../etc", "passwd", "hacked")
        result = mem.get_knowledge("../../etc", "passwd")
        print(f"   Result: {result}")
        
        # Test 3: XSS in knowledge value
        print("\n3. XSS payload in value:")
        xss_payload = '<script>alert("XSS")</script>'
        mem.add_knowledge("test", "xss", xss_payload)
        result = mem.get_knowledge("test", "xss")
        print(f"   Stored value: {result}")
        print(f"   XSS preserved: {result == xss_payload}")
        
        # Test 4: JSON injection
        print("\n4. JSON injection:")
        mem.add_knowledge("test", '","hack":"yes"},"real":{', "payload")
        
        # Check if file was corrupted
        kb_file = os.path.join(tmpdir, "memory", "knowledge.json")
        with open(kb_file, 'r') as f:
            content = f.read()
            print(f"   File content valid: {content is not None}")
            try:
                json.loads(content)
                print("   JSON valid: True")
            except:
                print("   JSON valid: False - VULNERABILITY!")

def test_cross_user_isolation():
    """Test for cross-user memory isolation."""
    print("\n=== Testing Cross-User Isolation ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create two users
        user1_mem = MemoryExpansionSystem(data_dir=tmpdir, user_name="user1")
        user2_mem = MemoryExpansionSystem(data_dir=tmpdir, user_name="user2")
        
        # User 1 stores sensitive data
        user1_mem.add_knowledge("private", "ssn", "123-45-6789")
        user1_mem.log_conversation("What's my password?", "Your password is secret123")
        
        # User 2 tries to access
        user2_data = user2_mem.get_knowledge("private", "ssn")
        print(f"\n1. User 2 can access User 1 knowledge: {user2_data is not None}")
        print(f"   Value: {user2_data}")
        
        user2_convs = user2_mem.conversations
        print(f"\n2. User 2 can access User 1 conversations: {len(user2_convs) > 0}")
        if user2_convs:
            print(f"   Leaked conversations: {user2_convs}")
        
        # Check file paths
        print(f"\n3. Memory directory paths:")
        print(f"   User 1: {user1_mem.memory_dir}")
        print(f"   User 2: {user2_mem.memory_dir}")
        print(f"   Same directory: {user1_mem.memory_dir == user2_mem.memory_dir}")

def test_sensitive_data_filtering():
    """Test for sensitive data filtering."""
    print("\n=== Testing Sensitive Data Filtering ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        mem = MemoryExpansionSystem(data_dir=tmpdir)
        
        # Store sensitive data types
        sensitive_items = {
            "password": "myPassword123!",
            "api_key": "sk-1234567890abcdef",
            "credit_card": "4532-1234-5678-9010",
            "ssn": "123-45-6789",
            "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        }
        
        for key, value in sensitive_items.items():
            mem.add_knowledge("sensitive", key, value)
        
        # Check if data is stored as-is
        kb_file = os.path.join(tmpdir, "memory", "knowledge.json")
        with open(kb_file, 'r') as f:
            content = f.read()
            
        print("\n1. Sensitive data found in storage:")
        for key, value in sensitive_items.items():
            found = value in content
            print(f"   {key}: {'EXPOSED' if found else 'Protected'}")

def test_memory_export_security():
    """Test memory export for data leaks."""
    print("\n=== Testing Memory Export Security ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        mem = MemoryExpansionSystem(data_dir=tmpdir)
        
        # Add sensitive data
        mem.add_knowledge("auth", "password", "secretPassword")
        mem.log_conversation("User login", "Login successful with password: admin123")
        
        # Check statistics export
        stats = mem.get_statistics()
        print(f"\n1. Statistics expose data: {stats}")
        
        # Check conversation export
        convs = mem.get_conversations()
        print(f"\n2. Conversation export includes sensitive data:")
        print(f"   {convs}")
        
        # Check if all_categories leaks structure
        categories = mem.get_all_categories()
        print(f"\n3. Categories exposed: {categories}")
        
        # Check category summary
        if "auth" in categories:
            summary = mem.get_category_summary("auth")
            print(f"\n4. Category summary exposes keys: {summary}")

def test_input_sanitization():
    """Test input sanitization for memory entries."""
    print("\n=== Testing Input Sanitization ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        mem = MemoryExpansionSystem(data_dir=tmpdir)
        
        # Test various malicious inputs
        malicious_inputs = [
            ("", "", "empty"),  # Empty strings
            (None, None, "null"),  # None values
            ("a" * 10000, "b" * 10000, "c" * 10000),  # Very long strings
            ("\x00\x01\x02", "control", "chars"),  # Control characters
            ("unicode\u0000test", "key", "value"),  # Null bytes
        ]
        
        for i, (cat, key, val) in enumerate(malicious_inputs):
            try:
                mem.add_knowledge(cat, key, val)
                result = mem.get_knowledge(cat, key)
                print(f"\n{i+1}. Input {i+1}: Accepted, returned: {result is not None}")
            except Exception as e:
                print(f"\n{i+1}. Input {i+1}: Rejected with: {type(e).__name__}")

if __name__ == "__main__":
    test_injection_vulnerabilities()
    test_cross_user_isolation()
    test_sensitive_data_filtering()
    test_memory_export_security()
    test_input_sanitization()
    print("\n=== Audit Complete ===")
