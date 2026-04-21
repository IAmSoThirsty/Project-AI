# User Login Sequence Diagram

## Overview
This diagram illustrates the complete user authentication flow in Project-AI, from initial login request through password verification, lockout protection, session establishment, and governance validation.

## Sequence Flow

```mermaid
sequenceDiagram
    autonumber
    participant User
    participant GUI as LeatherBookInterface
    participant UserMgr as UserManager
    participant Cipher as Fernet Cipher
    participant Gov as Triumvirate
    participant FS as File System
    
    Note over User,FS: User Authentication Flow
    
    %% Login Initiation
    User->>GUI: Enter credentials
    GUI->>GUI: Validate input format
    
    %% Account Lockout Check
    GUI->>UserMgr: login(username, password)
    activate UserMgr
    UserMgr->>UserMgr: Check account lockout
    
    alt Account Locked
        UserMgr->>UserMgr: Check lockout duration
        alt Still Locked
            UserMgr-->>GUI: Login failed (account locked)
            GUI-->>User: Display lockout message
        else Lockout Expired
            UserMgr->>UserMgr: Reset failed attempts
            Note over UserMgr: Continue to password verification
        end
    end
    
    %% Password Verification
    UserMgr->>FS: Load users.json
    activate FS
    FS-->>UserMgr: User data
    deactivate FS
    
    UserMgr->>UserMgr: pwd_context.verify(password, hash)
    
    alt Invalid Password
        UserMgr->>UserMgr: Increment failed attempts
        UserMgr->>UserMgr: Check if max attempts reached
        
        alt Max Attempts Reached (5)
            UserMgr->>UserMgr: Lock account (30 min)
            UserMgr->>FS: Save lockout state
            UserMgr-->>GUI: Login failed (account locked)
            GUI-->>User: Account locked notification
        else Below Max Attempts
            UserMgr-->>GUI: Login failed (invalid credentials)
            GUI-->>User: Display error (attempts remaining)
        end
    else Valid Password
        %% Successful Authentication
        UserMgr->>UserMgr: Reset failed attempts
        UserMgr->>UserMgr: Set current_user
        UserMgr->>FS: Save user state
        UserMgr-->>GUI: Login successful
        deactivate UserMgr
        
        %% Governance Validation
        GUI->>Gov: Validate login action
        activate Gov
        Gov->>Gov: Galahad: Check relational integrity
        Gov->>Gov: Cerberus: Check security bounds
        Gov->>Gov: Codex: Check logical consistency
        Gov-->>GUI: Action approved
        deactivate Gov
        
        %% Session Initialization
        GUI->>Cipher: Generate session token
        activate Cipher
        Cipher-->>GUI: Encrypted token
        deactivate Cipher
        
        GUI->>GUI: Switch to dashboard
        GUI-->>User: Display dashboard
        
        Note over User,FS: User authenticated and session established
    end
```

## Key Components

### UserManager (`src/app/core/user_manager.py`)
- **Password Hashing**: Uses `passlib` with pbkdf2_sha256 (primary) and bcrypt (fallback)
- **Account Lockout**: 5 failed attempts → 30-minute lockout
- **State Persistence**: JSON file storage with atomic writes
- **Migration Support**: Auto-migrates plaintext passwords to hashes

### LeatherBookInterface (`src/app/gui/leather_book_interface.py`)
- **Login UI**: Tron-themed login page with input validation
- **Error Handling**: Displays remaining attempts and lockout duration
- **Session Management**: Stores encrypted session tokens
- **Page Switching**: Transitions from login (page 0) to dashboard (page 1)

### Triumvirate Governance (`src/app/core/governance.py`)
- **Galahad**: Validates user welfare and relationship health
- **Cerberus**: Ensures security boundaries and data protection
- **Codex Deus Maximus**: Checks logical consistency and prior commitments

### Fernet Cipher (`cryptography.fernet`)
- **Key Management**: Loads FERNET_KEY from environment
- **Token Generation**: Creates encrypted session identifiers
- **Secure Storage**: Encrypts sensitive user data

## Security Features

1. **Timing Attack Protection**: Constant-time password comparison via passlib
2. **Path Traversal Protection**: Validates filenames before file operations
3. **Rate Limiting**: Account lockout prevents brute-force attacks
4. **Secure Hashing**: pbkdf2_sha256 with automatic salt generation
5. **Audit Logging**: All login attempts logged with timestamps

## Error Handling

| Error Condition | Response | User Feedback |
|----------------|----------|---------------|
| Invalid credentials | Increment failed attempts | "Invalid username or password (X attempts remaining)" |
| Account locked | Reject login | "Account locked. Try again in X minutes" |
| Lockout expired | Reset attempts, allow login | Normal login flow |
| Missing user file | Create new users.json | Onboarding flow |
| Corrupted data | Fallback to empty state | Error message + admin contact |

## Usage in Documentation

This diagram is referenced in:
- **User Authentication Flow** (`docs/security/authentication.md`)
- **Security Architecture** (`docs/architecture/security.md`)
- **User Management Guide** (`docs/user-guide/authentication.md`)

## Testing

Covered by:
- `tests/test_user_manager.py::TestUserManager::test_login_success`
- `tests/test_user_manager.py::TestUserManager::test_login_failure`
- `tests/test_user_manager.py::TestUserManager::test_account_lockout`
- `tests/integration/test_auth_flow.py`

## Related Diagrams

- [Governance Validation Sequence](./03-governance-validation-sequence.md) - Details the Triumvirate decision process
- [Security Alert Sequence](./04-security-alert-sequence.md) - Shows automated security responses
- [API Request/Response Sequence](./06-api-request-response-sequence.md) - Web API authentication flow
