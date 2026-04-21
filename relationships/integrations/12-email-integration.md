# Email Integration Relationship Map

**Status**: 🟢 Production | **Type**: External Communication Service  
**Priority**: P2 Feature | **Governance**: SMTP Protocol

---


## Navigation

**Location**: `relationships\integrations\12-email-integration.md`

**Parent**: [[relationships\integrations\README.md]]


## Overview

Email integration provides emergency alert notifications via SMTP (Simple Mail Transfer Protocol). Primary use case: sending location data and emergency messages to pre-configured contacts.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              EMERGENCY ALERT SYSTEM                          │
│         src/app/core/emergency_alert.py                      │
│  ┌──────────────────────────────────────────┐              │
│  │ Emergency Contact Management             │              │
│  │ SMTP Email Sender                        │              │
│  │ Alert Template Builder                   │              │
│  └──────────────────────────────────────────┘              │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                     SMTP PROVIDERS                           │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐  │
│  │ Gmail SMTP    │  │ SendGrid      │  │ Custom SMTP   │  │
│  │ smtp.gmail.com│  │ (API/SMTP)    │  │ Server        │  │
│  │ Port: 587 TLS │  │               │  │               │  │
│  └───────────────┘  └───────────────┘  └───────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## Core Functionality

### Emergency Contact Management

**Data Storage**: `emergency_contacts.json` (root directory)

**Schema**:
```json
{
    "alice": {
        "name": "Alice Smith",
        "emails": ["alice.emergency@example.com", "alice.backup@example.com"],
        "phone": "+1-555-0100",
        "relationship": "primary"
    },
    "bob": {
        "name": "Bob Jones",
        "emails": ["bob@example.com"],
        "phone": "+1-555-0200",
        "relationship": "secondary"
    }
}
```

**Methods**:
```python
from app.core.emergency_alert import EmergencyAlert

alert = EmergencyAlert()

# Add contact
alert.add_emergency_contact("alice", {
    "name": "Alice Smith",
    "emails": ["alice.emergency@example.com"],
    "phone": "+1-555-0100",
    "relationship": "primary"
})

# List contacts
contacts = alert.emergency_contacts
print(contacts)  # {"alice": {...}, "bob": {...}}
```

### Send Emergency Alert

**Method**: `send_alert(username, location_data, message=None)`

**Parameters**:
- `username`: User whose contacts to notify
- `location_data`: Dict with `lat`, `lng`, `timestamp` keys
- `message`: Optional custom message

**Returns**: `(success: bool, message: str)`

**Example**:
```python
alert = EmergencyAlert()

location = {
    "lat": 37.7749,
    "lng": -122.4194,
    "timestamp": "2025-01-26T15:30:00Z"
}

success, msg = alert.send_alert(
    username="alice",
    location_data=location,
    message="Emergency situation - immediate assistance needed"
)

if success:
    print("Alert sent successfully")
else:
    print(f"Failed to send alert: {msg}")
```

---

## SMTP Configuration

### Gmail SMTP Setup

**Server**: `smtp.gmail.com`  
**Port**: 587 (TLS) or 465 (SSL)  
**Authentication**: OAuth2 or App Password

**Configuration**:
```python
smtp_config = {
    "server": "smtp.gmail.com",
    "port": 587,
    "username": os.getenv("SMTP_USERNAME"),  # your-email@gmail.com
    "password": os.getenv("SMTP_PASSWORD")   # App-specific password
}
```

**Generate App Password** (Gmail):
1. Go to https://myaccount.google.com/apppasswords
2. Select "Mail" and "Other (Custom name)"
3. Enter "Project-AI" as the name
4. Copy the 16-character password
5. Add to `.env` [[.env]] file:
   ```bash
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=abcd efgh ijkl mnop
   ```

### SendGrid API (Alternative)

**Advantage**: Higher deliverability, rate limits

**Configuration**:
```python
# Use SendGrid Python SDK instead of SMTP
import sendgrid
from sendgrid.helpers.mail import Mail

sg = sendgrid.SendGridAPIClient(api_key=os.getenv("SENDGRID_API_KEY"))

message = Mail(
    from_email="alerts@project-ai.com",
    to_emails=["recipient@example.com"],
    subject="Emergency Alert",
    html_content="<strong>Emergency alert message</strong>"
)

response = sg.send(message)
```

---

## Email Implementation

### Build Alert Email

**Template**:
```python
def _build_alert_email(self, username, location_data, message):
    """Build HTML email with location data."""
    user_info = self.emergency_contacts.get(username, {})
    name = user_info.get("name", username)
    
    lat = location_data.get("lat", "Unknown")
    lng = location_data.get("lng", "Unknown")
    timestamp = location_data.get("timestamp", "Unknown")
    
    # Build Google Maps link
    maps_link = f"https://www.google.com/maps?q={lat},{lng}"
    
    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif;">
        <h2 style="color: #d32f2f;">🚨 EMERGENCY ALERT</h2>
        <p><strong>User:</strong> {name} ({username})</p>
        <p><strong>Time:</strong> {timestamp}</p>
        
        <h3>Location:</h3>
        <ul>
            <li><strong>Latitude:</strong> {lat}</li>
            <li><strong>Longitude:</strong> {lng}</li>
            <li><a href="{maps_link}">View on Google Maps</a></li>
        </ul>
        
        {f"<h3>Message:</h3><p>{message}</p>" if message else ""}
        
        <hr>
        <p style="color: #666; font-size: 12px;">
            This alert was sent automatically by Project-AI Emergency Alert System.
        </p>
    </body>
    </html>
    """
    
    return html
```

### Send Email via SMTP

```python
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_alert(self, username, location_data, message=None):
    """Send emergency alert via SMTP."""
    # Get emergency contacts
    if username not in self.emergency_contacts:
        return False, "No emergency contacts registered"
    
    contact_info = self.emergency_contacts[username]
    recipient_emails = contact_info.get("emails", [])
    
    if not recipient_emails:
        return False, "No email addresses configured"
    
    try:
        # Build email
        msg = MIMEMultipart("alternative")
        msg["From"] = self.smtp_config["username"]
        msg["To"] = ", ".join(recipient_emails)
        msg["Subject"] = f"🚨 EMERGENCY ALERT: {username}"
        
        # Add HTML body
        html_body = self._build_alert_email(username, location_data, message)
        msg.attach(MIMEText(html_body, "html"))
        
        # Send via SMTP
        with smtplib.SMTP(self.smtp_config["server"], self.smtp_config["port"]) as server:
            server.starttls()  # Upgrade to TLS
            server.login(self.smtp_config["username"], self.smtp_config["password"])
            server.send_message(msg)
        
        logger.info(f"Emergency alert sent to {len(recipient_emails)} recipients")
        return True, "Alert sent successfully"
    
    except smtplib.SMTPAuthenticationError:
        logger.error("SMTP authentication failed - check username/password")
        return False, "Email authentication failed"
    
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error: {e}")
        return False, f"Failed to send email: {str(e)}"
    
    except Exception as e:
        logger.error(f"Unexpected error sending alert: {e}")
        return False, f"Unexpected error: {str(e)}"
```

---

## Configuration

### Environment Variables

```bash
# SMTP Configuration (Gmail example)
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-specific-password
SMTP_SERVER=smtp.gmail.com  # Optional (default: smtp.gmail.com)
SMTP_PORT=587  # Optional (default: 587)

# SendGrid Alternative
SENDGRID_API_KEY=SG.xxxxxxxxxxxxx
SENDGRID_FROM_EMAIL=alerts@your-domain.com
```

---

## Error Handling

### Common Errors

1. **SMTPAuthenticationError**: Invalid username/password
   - **Check**: Correct credentials, app password (not account password)

2. **SMTPRecipientsRefused**: Invalid recipient email
   - **Check**: Email addresses are valid

3. **SMTPServerDisconnected**: Connection lost
   - **Retry**: Implement retry logic with exponential backoff

4. **Timeout**: SMTP server unreachable
   - **Check**: Network connectivity, firewall rules

### Retry Logic

```python
import time

def send_with_retry(self, username, location_data, message=None, max_retries=3):
    """Send alert with retry logic."""
    for attempt in range(max_retries):
        success, msg = self.send_alert(username, location_data, message)
        
        if success:
            return True, msg
        
        # Exponential backoff
        if attempt < max_retries - 1:
            wait_time = 2 ** attempt  # 1s, 2s, 4s
            logger.warning(f"Retry {attempt + 1}/{max_retries} in {wait_time}s")
            time.sleep(wait_time)
    
    return False, f"Failed after {max_retries} attempts"
```

---

## Security

### Credential Protection

```python
# NEVER hardcode credentials
smtp_config = {
    "username": os.getenv("SMTP_USERNAME"),  # ✅ From environment
    "password": os.getenv("SMTP_PASSWORD")
}

# NEVER log passwords
logger.debug(f"SMTP user: {smtp_config['username']}")  # ✅ Safe
logger.debug(f"SMTP pass: {smtp_config['password']}")  # ❌ DANGEROUS
```

### Email Injection Prevention

```python
import re

def sanitize_email(email: str) -> str:
    """Validate and sanitize email address."""
    # Basic email regex
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    
    if not re.match(pattern, email):
        raise ValueError(f"Invalid email address: {email}")
    
    return email.strip()
```

---

## Performance

### Benchmarks

| Operation | Latency | Notes |
|-----------|---------|-------|
| Send email (Gmail) | 1-3s | Network dependent |
| Send email (SendGrid) | 0.5-1s | Faster API |
| Add contact | <1ms | JSON file write |

---

## Testing

```python
# tests/test_emergency_alert.py
def test_add_emergency_contact():
    alert = EmergencyAlert()
    alert.add_emergency_contact("alice", {
        "emails": ["alice@example.com"],
        "phone": "+1-555-0100"
    })
    
    assert "alice" in alert.emergency_contacts

def test_send_alert():
    # Mock SMTP
    with patch("smtplib.SMTP") as mock_smtp:
        alert = EmergencyAlert()
        alert.add_emergency_contact("alice", {"emails": ["alice@example.com"]})
        
        success, msg = alert.send_alert(
            "alice",
            {"lat": 37.7749, "lng": -122.4194, "timestamp": "2025-01-26T12:00:00Z"}
        )
        
        assert success is True
        mock_smtp.assert_called_once()
```

---

## GUI Integration

**Location**: Emergency alert button in dashboard

**Flow**:
1. User clicks "Send Emergency Alert" button
2. Confirm dialog: "Send alert to emergency contacts?"
3. Get current location (from `LocationTracker`)
4. Send alert via `EmergencyAlert.send_alert()`
5. Show success/failure toast notification

---

## Future Enhancements

### Phase 1: Email Templates ⏳ PLANNED
- Customizable HTML templates
- Multi-language support
- Branding (logo, colors)

### Phase 2: Email Verification 🔮 FUTURE
- Send verification emails to contacts
- Require confirmation before activating

### Phase 3: Rich Alerts 🔮 FUTURE
- Attach photos, audio
- Real-time location tracking link
- Two-way communication

---

## Related Systems

- **[05-external-apis.md](05-external-apis.md)**: External API patterns
- **[12-sms-integration.md](12-sms-integration.md)**: SMS as alternative alert channel
- Location Tracker: Provides location data for alerts

---

**Last Updated**: 2025-01-26  
**Maintained By**: AGENT-060  
**Review Cycle**: Quarterly


---

## See Also

### Related Source Documentation

- **01 Openai Integration**: [[source-docs\integrations\01-openai-integration.md]]
- **02 Huggingface Integration**: [[source-docs\integrations\02-huggingface-integration.md]]
- **05 Database Integrations**: [[source-docs\integrations\05-database-integrations.md]]
- **07 Smtp Email**: [[source-docs\integrations\07-smtp-email.md]]
- **11 Openrouter Integration**: [[source-docs\integrations\11-openrouter-integration.md]]
- **12 Perplexity Integration**: [[source-docs\integrations\12-perplexity-integration.md]]
- **Documentation Index**: [[source-docs\integrations\README.md]]
