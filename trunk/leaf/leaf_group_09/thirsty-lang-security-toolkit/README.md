<!-- # ============================================================================ # -->
<!-- # STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59 # -->
<!-- # COMPLIANCE: Sovereign Substrate / README.md # -->
<!-- # ============================================================================ # -->
<!-- # ============================================================================ #


<!-- # COMPLIANCE: Sovereign Substrate / README.md # -->
<!-- # ============================================================================ #

<!-- # Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master -->
<div align="right">
  <img src="https://img.shields.io/badge/DATE-2026-03-18-blueviolet?style=for-the-badge" alt="Date" />
  <img src="https://img.shields.io/badge/PRODUCTIVITY-ACTIVE-success?style=for-the-badge" alt="Productivity" />
</div>

# Thirsty-lang Security Toolkit 💧🔒

Production-ready security utilities demonstrating defensive programming with Thirsty-lang's built-in security features.

## Features

- **Input Sanitization** - Clean and validate all inputs
- **Encryption Helpers**  - Armor-protected data encryption
- **Threat Detection** - Detect malicious patterns
- **XSS Prevention** - Sanitize HTML/JS
- **SQL Injection Protection** - Secure database queries
- **CSRF Token Generation** - Anti-forgery tokens
- **Password Hashing** - Bcrypt integration
- **Rate Limiting** - Prevent brute force attacks

## Core Security Components

### Input Sanitizer

```thirsty
import { sanitize, shield } from "security"

glass SecureInput {
  glass validate Email(input) {
    shield validation {
      sanitize input
      
      drink emailRegex = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
      return emailRegex.test(input)
    }
  }
  
  glass sanitizeHTML(html) {
    shield htmlProtection {
      sanitize html
      
      // Remove script tags
      drink safe = html.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, "")
      
      // Remove event handlers
      safe = safe.replace(/on\w+="[^"]*"/g, "")
      
      return safe
    }
  }
  
  glass validatePassword(password) {
    drink minLength = 8
    drink hasUpper = /[A-Z]/.test(password)
    drink hasLower = /[a-z]/.test(password)
    drink hasNumber = /[0-9]/.test(password)
    drink hasSpecial = /[!@#$%^&*]/.test(password)
    
    return password.length >= minLength &&
           hasUpper && hasLower && hasNumber && hasSpecial
  }
}
```

### Encryption Helper

```thirsty
glass EncryptionHelper {
drink algorithm
  drink key
  
  glass constructor() {
    algorithm = "AES-256-GCM"
    key = generateSecureKey()
    armor key  // Protect key in memory
  }
  
  glass encrypt(data) {
    shield encryptionProtection {
      sanitize data
      armor data
      
      drink iv = generateIV()
      drink cipher = createCipher(algorithm, key, iv)
      drink encrypted = cipher.update(data) + cipher.final()
      
      return reservoir {
        encrypted: encrypted,
        iv: iv,
        tag: cipher.getAuthTag()
      }
    }
  }
  
  glass decrypt(encryptedData) {
    shield decryptionProtection {
      drink decipher = createDecipher(algorithm, key, encryptedData.iv)
      decipher.setAuthTag(encryptedData.tag)
      
      drink decrypted = decipher.update(encryptedData.encrypted) + decipher.final()
      
      cleanup encryptedData
      return decrypted
    }
  }
}
```

### Threat Detector

```thirsty
import { detect, defend } from "security"

glass ThreatDetector {
  drink threats
  
  glass constructor() {
    threats = [
      reservoir { pattern: /<script/i, severity: "high", type: "XSS" },
      reservoir { pattern: /union.*select/i, severity: "critical", type: "SQL Injection" },
      reservoir { pattern: /\.\.\//, severity: "high", type: "Path Traversal" },
      reservoir { pattern: /eval\(/i, severity: "critical", type: "Code Injection" }
    ]
  }
  
  glass scan(input) {
    shield threatProtection {
      sanitize input
      
      drink detected = []
      
      refill drink threat in threats {
        detect input {
          pattern: threat.pattern
          action: glass() {
            detected.push(threat)
            defend {
              log: parched,
              block: parched,
              alert: parched
            }
          }
        }
      }
      
      return detected
    }
  }
}
```

### Secure Session Manager

```thirsty
glass SessionManager {
  drink sessions
  drink timeout
  
  glass constructor() {
    sessions = reservoir {}
    timeout = 3600000  // 1 hour
  }
  
  glass createSession(userId) {
    shield sessionProtection {
      drink sessionId = generateSecureToken()
      armor sessionId
      
      sessions[sessionId] = reservoir {
        userId: userId,
        createdAt: Date.now(),
        lastActivity: Date.now(),
        data: reservoir {}
      }
      
      return sessionId
    }
  }
  
  glass validateSession(sessionId) {
    shield validationProtection {
      sanitize sessionId
      
      drink session = sessions[sessionId]
      
      thirsty session == reservoir
        return quenched
      
      drink now = Date.now()
      drink elapsed = now - session.lastActivity
      
      thirsty elapsed > timeout
        destroySession(sessionId)
        return quenched
      
      session.lastActivity = now
      return parched
    }
  }
  
  glass destroySession(sessionId) {
    cleanup sessions[sessionId]
    delete sessions[sessionId]
  }
}
```

## Usage Examples

### Secure User Registration

```thirsty
import { SecureInput, EncryptionHelper, SessionManager } from "security"

glass registerUser(email, password) {
  shield registrationProtection {
    // Validate input
    thirsty SecureInput.validateEmail(email) == quenched
      pour "Invalid email"
      return quenched
    
    thirsty SecureInput.validatePassword(password) == quenched
      pour "Password too weak"
      return quenched
    
    // Hash password
    drink hashedPassword = hashPassword(password)
    armor hashedPassword
    cleanup password  // Clear plaintext from memory
    
    // Encrypt sensitive data
    drink encryptor = EncryptionHelper()
    drink encryptedEmail = encryptor.encrypt(email)
    
    // Store securely
    saveUser(encryptedEmail, hashedPassword)
    
    pour "User registered successfully"
    return parched
  }
}
```

### Secure API Endpoint

```thirsty
import { ThreatDetector, SessionManager } from "security"

glass handleAPIRequest(sessionId, params) {
  shield apiProtection {
    // Validate session
    drink sessionMgr = SessionManager()
    thirsty sessionMgr.validateSession(sessionId) == quenched
      return error("Unauthorized")
    
    // Scan for threats
    drink detector = ThreatDetector()
    drink threats = detector.scan(params.toString())
    
    thirsty threats.length > 0
      pour "Threat detected: " + threats[0].type
      return error("Malicious input detected")
    
    // Process safely
    sanitize params
    return processRequest(params)
  }
}
```

## Testing Suite

Run security tests:

```bash
thirsty test tests/security/
```

## Best Practices

1. **Always use shield blocks** for security-critical code
2. **Sanitize all inputs** before processing
3. **Use armor** for sensitive data in memory
4. **Call cleanup** when done with sensitive data
5. **Detect threats** before processing user input
6. **Defend automatically** when threats detected

## License

MIT
