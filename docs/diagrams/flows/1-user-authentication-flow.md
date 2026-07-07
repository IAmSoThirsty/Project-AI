# User Authentication Flow

## Overview
This diagram illustrates the complete user authentication workflow in Project-AI, including password hashing, lockout protection, session management, and Fernet encryption setup.

## Flow Diagram

```mermaid
flowchart TD
    Start([User Login Request]) --> LoadEnv[Load Environment Variables<br/>dotenv.load_dotenv]
    LoadEnv --> SetupCipher[Setup Fernet Cipher<br/>from FERNET_KEY]
    SetupCipher --> CheckFile{users.json<br/>exists?}
    
    CheckFile -->|No| FirstUser[First Time Setup<br/>Onboarding Flow]
    FirstUser --> CreateAdmin[Create Admin User<br/>via create_user]
    
    CheckFile -->|Yes| LoadUsers[Load Users from JSON]
    LoadUsers --> MigratePwd[Migrate Plaintext Passwords<br/>to pbkdf2_sha256]
    MigratePwd --> EnsureLockout[Ensure Lockout Fields<br/>failed_attempts, locked_until]
    
    CreateAdmin --> ValidateAuth
    EnsureLockout --> ValidateAuth{Validate<br/>Credentials}
    
    ValidateAuth --> CheckLockout{Account<br/>Locked?}
    CheckLockout -->|Yes| LockoutError[❌ Account Locked<br/>Return Error]
    CheckLockout -->|No| VerifyPassword[Verify Password<br/>pwd_context.verify]
    
    VerifyPassword --> PasswordMatch{Password<br/>Matches?}
    PasswordMatch -->|No| IncrementFail[Increment Failed Attempts]
    IncrementFail --> CheckThreshold{Attempts >= 5?}
    CheckThreshold -->|Yes| LockAccount[Lock Account<br/>30 min lockout]
    CheckThreshold -->|No| AuthFail[❌ Authentication Failed]
    LockAccount --> AuthFail
    
    PasswordMatch -->|Yes| ResetAttempts[Reset Failed Attempts<br/>failed_attempts = 0]
    ResetAttempts --> SetCurrentUser[Set current_user<br/>Session established]
    SetCurrentUser --> UpdateLastLogin[Update last_login_at<br/>timestamp]
    UpdateLastLogin --> SaveUsers[Persist to users.json<br/>save_users]
    
    SaveUsers --> Success([✅ Authentication Success<br/>Return user profile])
    AuthFail --> End([❌ Authentication Failed])
    LockoutError --> End
    
    style Start fill:#00ff00,stroke:#00ffff,stroke-width:3px,color:#000
    style Success fill:#00ff00,stroke:#00ffff,stroke-width:3px,color:#000
    style AuthFail fill:#ff0000,stroke:#ff00ff,stroke-width:2px,color:#fff
    style LockoutError fill:#ff0000,stroke:#ff00ff,stroke-width:2px,color:#fff
    style VerifyPassword fill:#ffff00,stroke:#ff8800,stroke-width:2px,color:#000
    style SaveUsers fill:#00ffff,stroke:#0088ff,stroke-width:2px,color:#000
```

## Key Security Features

### Password Hashing
- **Primary**: pbkdf2_sha256 (PBKDF2 with SHA-256)
- **Legacy Support**: bcrypt (for backward compatibility)
- **Migration**: Automatic plaintext → hash conversion on load
- **Library**: passlib.context.CryptContext

### Lockout Protection
- **Failed Attempt Threshold**: 5 attempts
- **Lockout Duration**: 30 minutes
- **Persistence**: Lockout state saved to users.json
- **Reset**: Automatic on successful login

### Encryption
- **Cipher**: Fernet (symmetric encryption)
- **Key Source**: Environment variable FERNET_KEY
- **Fallback**: Runtime key generation if not configured
- **Usage**: Sensitive user data encryption

### Path Security
- **Validation**: validate_filename() prevents path traversal
- **Safe Joins**: safe_path_join() for secure file paths
- **Data Directory**: Isolated data/ directory with permissions

## State Persistence

All user state persists to `data/users.json`:

```json
{
  "username": {
    "password_hash": "$pbkdf2-sha256$...",
    "failed_attempts": 0,
    "locked_until": null,
    "last_login_at": "2024-01-15T10:30:00",
    "profile": {
      "email": "user@example.com",
      "role": "admin"
    }
  }
}
```

## Related Systems
- **Command Override**: Extended password system with SHA-256
- **Emergency Alert**: Email-based emergency contact system
- **Cloud Sync**: Encrypted backup with Fernet

## Error Handling
- **File Not Found**: Creates default empty users dict
- **Invalid JSON**: Logs error, uses empty dict
- **Encryption Failure**: Falls back to runtime key
- **Migration Errors**: Logs warning, continues with unmigrated users

## Performance Considerations
- **Hash Verification**: ~100-300ms per attempt (intentional slowdown)
- **File I/O**: Synchronous JSON read/write
- **Memory**: In-memory user dict (loaded once)
- **Concurrency**: Not thread-safe (GUI runs on main thread)
