# SMTP/Email Integration

## Overview

Project-AI integrates with SMTP servers for email delivery, primarily used by the Emergency Alert System (`src/app/core/emergency_alert.py` [[src/app/core/emergency_alert.py]]) to send location-based emergency notifications to registered contacts.

## Architecture

```
Application Layer (Emergency Alert System)
    ↓
EmergencyAlert Class (SMTP Integration)
    ↓
Python smtplib (SMTP Protocol)
    ↓
SMTP Server (Gmail, SendGrid, etc.)
```

## Configuration

### Environment Variables

```bash
# Required for email functionality
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password       # Gmail App Password, not regular password

# Optional SMTP server configuration
SMTP_SERVER=smtp.gmail.com            # Default
SMTP_PORT=587                          # Default (TLS)
SMTP_USE_TLS=true                      # Default
```

### Gmail Setup Instructions

1. **Enable 2-Factor Authentication**
   ```
   Visit: https://myaccount.google.com/security
   Enable: 2-Step Verification
   ```

2. **Generate App Password**
   ```
   Visit: https://myaccount.google.com/apppasswords
   Select: Mail → Other (Custom name: Project-AI)
   Copy generated password to .env as SMTP_PASSWORD
   ```

3. **Test Configuration**
   ```python
   import smtplib
   
   server = smtplib.SMTP("smtp.gmail.com", 587)
   server.starttls()
   server.login(os.getenv("SMTP_USERNAME"), os.getenv("SMTP_PASSWORD"))
   server.quit()
   print("SMTP configuration valid")
   ```

## Implementation

### Emergency Alert System

```python
# src/app/core/emergency_alert.py

import json
import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

EMERGENCY_CONTACTS_FILE = "data/emergency_contacts.json"

class EmergencyAlert:
    """Emergency alert system with SMTP email delivery."""
    
    def __init__(self, smtp_config=None):
        """Initialize with SMTP configuration."""
        self.smtp_config = smtp_config or {
            "server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
            "port": int(os.getenv("SMTP_PORT", "587")),
            "username": os.getenv("SMTP_USERNAME"),
            "password": os.getenv("SMTP_PASSWORD"),
        }
        
        self.emergency_contacts = {}
        self.load_contacts()
    
    def load_contacts(self):
        """Load emergency contacts from JSON file."""
        if os.path.exists(EMERGENCY_CONTACTS_FILE):
            with open(EMERGENCY_CONTACTS_FILE) as f:
                self.emergency_contacts = json.load(f)
    
    def save_contacts(self):
        """Save emergency contacts to JSON file."""
        os.makedirs(os.path.dirname(EMERGENCY_CONTACTS_FILE), exist_ok=True)
        with open(EMERGENCY_CONTACTS_FILE, 'w') as f:
            json.dump(self.emergency_contacts, f, indent=2)
    
    def add_emergency_contact(self, username: str, contact_info: dict):
        """Register emergency contacts for a user."""
        self.emergency_contacts[username] = contact_info
        self.save_contacts()
    
    def send_alert(self, username: str, location_data: dict, message: str = None) -> tuple[bool, str]:
        """Send emergency alert via SMTP."""
        if username not in self.emergency_contacts:
            return False, "No emergency contacts registered for user"
        
        contacts = self.emergency_contacts[username]
        
        try:
            # Create email message
            msg = MIMEMultipart()
            msg["From"] = self.smtp_config["username"]
            msg["To"] = ", ".join(contacts["emails"])
            msg["Subject"] = f"EMERGENCY ALERT - {username}"
            
            # Build message body
            body = self._build_alert_body(username, location_data, message)
            msg.attach(MIMEText(body, "plain"))
            
            # Connect to SMTP server and send
            with smtplib.SMTP(self.smtp_config["server"], self.smtp_config["port"]) as server:
                server.starttls()
                server.login(self.smtp_config["username"], self.smtp_config["password"])
                server.send_message(msg)
            
            return True, "Alert sent successfully"
        
        except smtplib.SMTPAuthenticationError:
            return False, "SMTP authentication failed - check credentials"
        except smtplib.SMTPException as e:
            return False, f"SMTP error: {str(e)}"
        except Exception as e:
            return False, f"Failed to send alert: {str(e)}"
    
    def _build_alert_body(self, username: str, location_data: dict, message: str) -> str:
        """Build formatted email body for emergency alert."""
        lines = [
            "EMERGENCY ALERT",
            "",
            f"User: {username}",
            f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "Location Information:",
        ]
        
        if location_data:
            lines.extend([
                f"Latitude: {location_data.get('latitude', 'N/A')}",
                f"Longitude: {location_data.get('longitude', 'N/A')}",
                f"Address: {location_data.get('address', 'Not available')}",
                f"City: {location_data.get('city', 'Not available')}",
                f"Region: {location_data.get('region', 'Not available')}",
                f"Country: {location_data.get('country', 'Not available')}",
            ])
        else:
            lines.append("Location not available")
        
        lines.extend([
            "",
            "Additional Message:",
            message or "No additional message provided",
            "",
            "This is an automated emergency alert. Please attempt to contact the user",
            "and alert appropriate authorities if necessary.",
        ])
        
        return "\n".join(lines)
```

## Usage Patterns

### 1. Register Emergency Contacts

```python
from app.core.emergency_alert import EmergencyAlert

alert_system = EmergencyAlert()

# Add emergency contacts for user
alert_system.add_emergency_contact(
    username="john_doe",
    contact_info={
        "emails": [
            "friend@example.com",
            "family@example.com"
        ],
        "phones": ["+1-555-0100"],  # Optional: for future SMS integration
        "relationship": "Emergency Contacts"
    }
)
```

### 2. Send Emergency Alert

```python
from app.core.location_tracker import LocationTracker

# Get user's location
tracker = LocationTracker()
location = tracker.get_location_from_ip()

# Send emergency alert
success, message = alert_system.send_alert(
    username="john_doe",
    location_data=location,
    message="User triggered emergency alert via panic button"
)

if success:
    logger.info(f"Emergency alert sent: {message}")
else:
    logger.error(f"Failed to send alert: {message}")
```

### 3. Bulk Alert Sending

```python
def send_bulk_alerts(usernames: list[str], incident_message: str):
    """Send emergency alerts to multiple users."""
    alert_system = EmergencyAlert()
    results = {}
    
    for username in usernames:
        success, message = alert_system.send_alert(
            username=username,
            location_data=None,
            message=incident_message
        )
        results[username] = {"success": success, "message": message}
    
    return results

# Usage
incident_users = ["user1", "user2", "user3"]
results = send_bulk_alerts(incident_users, "System security incident detected")
```

### 4. Custom SMTP Configuration

```python
# Use custom SMTP server (e.g., SendGrid, Mailgun)
custom_config = {
    "server": "smtp.sendgrid.net",
    "port": 587,
    "username": "apikey",
    "password": os.getenv("SENDGRID_API_KEY")
}

alert_system = EmergencyAlert(smtp_config=custom_config)
```

## Supported SMTP Providers

### Gmail

```python
smtp_config = {
    "server": "smtp.gmail.com",
    "port": 587,  # TLS
    "username": "your-email@gmail.com",
    "password": "your-app-password"
}
```

**Requirements:**
- 2FA enabled
- App-specific password generated
- "Less secure app access" NOT recommended (use App Passwords)

### SendGrid

```python
smtp_config = {
    "server": "smtp.sendgrid.net",
    "port": 587,
    "username": "apikey",
    "password": os.getenv("SENDGRID_API_KEY")
}
```

**Benefits:**
- 100 emails/day free tier
- Better deliverability
- Detailed analytics

### Mailgun

```python
smtp_config = {
    "server": "smtp.mailgun.org",
    "port": 587,
    "username": "postmaster@your-domain.mailgun.org",
    "password": os.getenv("MAILGUN_PASSWORD")
}
```

### Office 365

```python
smtp_config = {
    "server": "smtp.office365.com",
    "port": 587,
    "username": "your-email@outlook.com",
    "password": "your-password"
}
```

## Security Best Practices

### 1. Use App-Specific Passwords

```python
# NEVER store actual email password in code
# Use app-specific passwords or API keys

# ❌ BAD
smtp_password = "MyRealPassword123"

# ✅ GOOD
smtp_password = os.getenv("SMTP_PASSWORD")  # App password from .env
```

### 2. TLS Encryption

```python
import smtplib

def send_secure_email():
    """Always use TLS for SMTP connections."""
    server = smtplib.SMTP("smtp.gmail.com", 587)
    
    # Enable TLS encryption
    server.starttls()
    
    # Authenticate
    server.login(username, password)
    
    # Send email
    server.send_message(msg)
    server.quit()
```

### 3. Rate Limiting

```python
from datetime import datetime, timedelta
from collections import defaultdict

class RateLimitedEmailSender:
    """Email sender with rate limiting to prevent abuse."""
    
    def __init__(self, max_emails_per_hour: int = 10):
        self.max_emails_per_hour = max_emails_per_hour
        self.send_history = defaultdict(list)
    
    def can_send_email(self, username: str) -> bool:
        """Check if user can send another email."""
        now = datetime.now()
        cutoff = now - timedelta(hours=1)
        
        # Remove old entries
        self.send_history[username] = [
            ts for ts in self.send_history[username] if ts > cutoff
        ]
        
        return len(self.send_history[username]) < self.max_emails_per_hour
    
    def record_email_sent(self, username: str):
        """Record email send timestamp."""
        self.send_history[username].append(datetime.now())
```

### 4. Input Validation

```python
import re

def validate_email(email: str) -> bool:
    """Validate email address format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def sanitize_email_content(content: str) -> str:
    """Sanitize email content to prevent injection attacks."""
    # Remove CRLF injection attempts
    content = content.replace('\r', '').replace('\n', ' ')
    
    # Remove potentially dangerous HTML
    content = content.replace('<', '&lt;').replace('>', '&gt;')
    
    return content
```

## Error Handling

### Common SMTP Errors

```python
import smtplib

def send_email_with_error_handling(msg: MIMEMultipart):
    """Send email with comprehensive error handling."""
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(username, password)
        server.send_message(msg)
        server.quit()
        return True, "Email sent successfully"
    
    except smtplib.SMTPAuthenticationError:
        return False, "Authentication failed - check username/password"
    
    except smtplib.SMTPRecipientsRefused:
        return False, "All recipients were refused"
    
    except smtplib.SMTPSenderRefused:
        return False, "Sender address was refused"
    
    except smtplib.SMTPDataError:
        return False, "SMTP server refused to accept message data"
    
    except smtplib.SMTPConnectError:
        return False, "Could not connect to SMTP server"
    
    except smtplib.SMTPHeloError:
        return False, "Server refused HELO/EHLO command"
    
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"
```

### Retry Logic

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def send_email_with_retry(msg: MIMEMultipart):
    """Send email with automatic retry on transient failures."""
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(username, password)
    server.send_message(msg)
    server.quit()
```

## Testing

### Mock SMTP Server

```python
import pytest
from unittest.mock import patch, MagicMock

class TestEmergencyAlert:
    @patch('smtplib.SMTP')
    def test_send_alert_success(self, mock_smtp):
        """Test successful alert sending."""
        # Mock SMTP server
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        # Test alert sending
        alert = EmergencyAlert()
        alert.add_emergency_contact("test_user", {"emails": ["test@example.com"]})
        
        success, message = alert.send_alert(
            username="test_user",
            location_data={"latitude": 40.7128, "longitude": -74.0060},
            message="Test alert"
        )
        
        assert success
        assert message == "Alert sent successfully"
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once()
        mock_server.send_message.assert_called_once()
    
    @patch('smtplib.SMTP')
    def test_send_alert_auth_failure(self, mock_smtp):
        """Test alert sending with authentication failure."""
        mock_smtp.return_value.__enter__.return_value.login.side_effect = \
            smtplib.SMTPAuthenticationError(535, b'Invalid credentials')
        
        alert = EmergencyAlert()
        alert.add_emergency_contact("test_user", {"emails": ["test@example.com"]})
        
        success, message = alert.send_alert("test_user", {})
        
        assert not success
        assert "authentication failed" in message.lower()
```

### Integration Test with Real SMTP

```python
@pytest.mark.integration
@pytest.mark.skipif(not os.getenv("SMTP_PASSWORD"), reason="SMTP credentials not set")
def test_real_email_sending():
    """Test actual email delivery (requires valid credentials)."""
    alert = EmergencyAlert()
    
    # Use test email address
    test_email = os.getenv("TEST_EMAIL_ADDRESS")
    alert.add_emergency_contact("test_user", {"emails": [test_email]})
    
    # Send test alert
    success, message = alert.send_alert(
        username="test_user",
        location_data={"latitude": 40.7128, "longitude": -74.0060, "city": "New York"},
        message="Integration test alert - please ignore"
    )
    
    assert success, f"Failed to send email: {message}"
```

## Advanced Features

### HTML Email Templates

```python
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_html_alert(username: str, location_data: dict):
    """Send emergency alert with HTML formatting."""
    msg = MIMEMultipart('alternative')
    
    # Plain text version
    text_body = f"Emergency Alert for {username}\nLocation: {location_data.get('city', 'Unknown')}"
    
    # HTML version
    html_body = f"""
    <html>
        <head></head>
        <body style="font-family: Arial, sans-serif;">
            <div style="background-color: #ff0000; color: white; padding: 20px;">
                <h1>🚨 EMERGENCY ALERT</h1>
            </div>
            <div style="padding: 20px;">
                <p><strong>User:</strong> {username}</p>
                <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <h2>Location Information</h2>
                <ul>
                    <li><strong>City:</strong> {location_data.get('city', 'N/A')}</li>
                    <li><strong>Coordinates:</strong> {location_data.get('latitude', 'N/A')}, {location_data.get('longitude', 'N/A')}</li>
                    <li><strong>Address:</strong> {location_data.get('address', 'Not available')}</li>
                </ul>
                <p style="color: red;"><strong>Please contact the user immediately and alert authorities if necessary.</strong></p>
            </div>
        </body>
    </html>
    """
    
    # Attach both versions
    msg.attach(MIMEText(text_body, 'plain'))
    msg.attach(MIMEText(html_body, 'html'))
    
    return msg
```

### Email with Attachments

```python
from email.mime.base import MIMEBase
from email import encoders

def attach_location_map(msg: MIMEMultipart, location_data: dict):
    """Attach static map image to email."""
    # Generate map image (e.g., via Google Static Maps API)
    map_image = generate_map_image(location_data)
    
    # Create attachment
    attachment = MIMEBase('image', 'png')
    attachment.set_payload(map_image)
    encoders.encode_base64(attachment)
    attachment.add_header('Content-Disposition', 'attachment', filename='location_map.png')
    
    msg.attach(attachment)
```

## Monitoring

### Email Delivery Tracking

```python
import json
from datetime import datetime

class EmailDeliveryTracker:
    """Track email delivery status and metrics."""
    
    def __init__(self, log_file="data/email_delivery_log.json"):
        self.log_file = log_file
        self.delivery_log = []
        self._load_log()
    
    def _load_log(self):
        if os.path.exists(self.log_file):
            with open(self.log_file) as f:
                self.delivery_log = json.load(f)
    
    def _save_log(self):
        with open(self.log_file, 'w') as f:
            json.dump(self.delivery_log, f, indent=2)
    
    def log_delivery(self, username: str, recipients: list[str], success: bool, error: str = None):
        """Log email delivery attempt."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "username": username,
            "recipients": recipients,
            "success": success,
            "error": error
        }
        
        self.delivery_log.append(entry)
        self._save_log()
    
    def get_delivery_stats(self, days: int = 7) -> dict:
        """Get delivery statistics for recent period."""
        cutoff = datetime.now() - timedelta(days=days)
        recent_deliveries = [
            entry for entry in self.delivery_log
            if datetime.fromisoformat(entry["timestamp"]) > cutoff
        ]
        
        total = len(recent_deliveries)
        successful = sum(1 for entry in recent_deliveries if entry["success"])
        
        return {
            "total_attempts": total,
            "successful": successful,
            "failed": total - successful,
            "success_rate": successful / total if total > 0 else 0
        }
```

## References

- **Python smtplib**: https://docs.python.org/3/library/smtplib.html
- **Email MIME**: https://docs.python.org/3/library/email.html
- **Gmail SMTP**: https://support.google.com/mail/answer/7126229
- **SendGrid SMTP**: https://docs.sendgrid.com/for-developers/sending-email/integrating-with-the-smtp-api

## Related Documentation

- [Emergency Alert System](../features/emergency-alerts.md)
- [Location Tracking](./08-location-services.md)
- [Security](../architecture/security.md)
