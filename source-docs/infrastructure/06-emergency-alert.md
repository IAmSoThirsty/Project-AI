# Emergency Alert System

**Module:** `src/app/core/emergency_alert.py`  
**Type:** Core Infrastructure  
**Dependencies:** smtplib, email, json  
**Related Modules:** location_tracker.py, user_manager.py

---

## Overview

The Emergency Alert System provides automated emergency notifications via email with location data integration, designed for critical incident response and user safety workflows.

### Core Features

- **Email Notifications**: SMTP-based alert delivery to emergency contacts
- **Location Integration**: Automatic location data embedding
- **Contact Management**: Per-user emergency contact lists
- **Alert History**: JSON-based alert logging with timestamps
- **Gmail/SMTP Support**: Configurable SMTP server (defaults to Gmail)

---

## Architecture

```
EmergencyAlert
├── SMTP Configuration (Gmail default, customizable)
├── Contact Management (emergency_contacts.json)
├── Alert Composition (email with location data)
├── Delivery System (smtplib with TLS)
└── History Logging (emergency_alerts_{username}.json)
```

---

## Core Classes

### EmergencyAlert

```python
from app.core.emergency_alert import EmergencyAlert

# Initialize with default SMTP (Gmail)
alert_system = EmergencyAlert()

# Custom SMTP configuration
alert_system = EmergencyAlert(smtp_config={
    "server": "smtp.office365.com",
    "port": 587,
    "username": "alerts@company.com",
    "password": "secure_password"
})

# Add emergency contact for user
alert_system.add_emergency_contact("admin", {
    "emails": ["contact1@example.com", "contact2@example.com"],
    "phone": "+1-555-0100",  # Optional metadata
    "relationship": "Family"  # Optional metadata
})

# Send emergency alert
success, message = alert_system.send_alert(
    username="admin",
    location_data={
        "latitude": 40.7128,
        "longitude": -74.0060,
        "city": "New York",
        "address": "123 Main St, New York, NY"
    },
    message="User triggered emergency alert"
)

if success:
    print("Alert sent successfully")
else:
    print(f"Alert failed: {message}")

# Get alert history
history = alert_system.get_alert_history("admin")
```

---

## Contact Management

### Emergency Contacts Data Structure

```json
{
  "admin": {
    "emails": ["family@example.com", "friend@example.com"],
    "phone": "+1-555-0100",
    "relationship": "Family"
  },
  "user2": {
    "emails": ["emergency@example.com"],
    "phone": "+1-555-0200",
    "relationship": "Emergency Services"
  }
}
```

### Add/Update Contacts

```python
def add_emergency_contact(self, username, contact_info):
    """
    Add or update emergency contact for user.
    
    Args:
        username: User identifier
        contact_info: Dict with 'emails' list and optional metadata
    """
    self.emergency_contacts[username] = contact_info
    self.save_contacts()

# Usage
alert_system.add_emergency_contact("admin", {
    "emails": ["primary@example.com", "secondary@example.com"],
    "phone": "+1-555-0100",
    "relationship": "Family",
    "notes": "Call phone first, then email"
})
```

### Load/Save Contacts

```python
def load_contacts(self):
    """Load emergency contacts from emergency_contacts.json."""
    if os.path.exists(EMERGENCY_CONTACTS_FILE):
        with open(EMERGENCY_CONTACTS_FILE) as f:
            self.emergency_contacts = json.load(f)

def save_contacts(self):
    """Save emergency contacts to emergency_contacts.json."""
    with open(EMERGENCY_CONTACTS_FILE, "w") as f:
        json.dump(self.emergency_contacts, f)
```

---

## Alert Composition

### Email Structure

```python
def send_alert(self, username, location_data, message=None):
    """
    Compose and send emergency alert email.
    
    Email structure:
    - Subject: "EMERGENCY ALERT - {username}"
    - Body: User, timestamp, location data, custom message
    - Recipients: All emails in emergency contacts
    """
    # Create MIME multipart message
    msg = MIMEMultipart()
    msg["From"] = self.smtp_config["username"]
    msg["To"] = ", ".join(contacts["emails"])
    msg["Subject"] = f"EMERGENCY ALERT - {username}"
    
    # Compose body
    body = self._compose_alert_body(username, location_data, message)
    msg.attach(MIMEText(body, "plain"))
    
    # Send via SMTP
    with smtplib.SMTP(self.smtp_config["server"], self.smtp_config["port"]) as server:
        server.starttls()
        server.login(self.smtp_config["username"], self.smtp_config["password"])
        server.send_message(msg)
```

### Email Template

```
EMERGENCY ALERT

User: admin
Time: 2026-04-20 14:30:00

Location Information:
Latitude: 40.7128
Longitude: -74.0060
Address: 123 Main St, New York, NY
City: New York
Region: New York
Country: United States

Additional Message:
User triggered emergency alert via panic button

This is an automated emergency alert. Please attempt to contact the user
and alert appropriate authorities if necessary.
```

---

## Alert History

### History Data Structure

```json
[
  {
    "timestamp": "2026-04-20T14:30:00",
    "username": "admin",
    "location_data": {
      "latitude": 40.7128,
      "longitude": -74.0060,
      "city": "New York"
    },
    "message": "User triggered emergency alert"
  }
]
```

### Log Alert

```python
def log_alert(self, username, location_data, message):
    """
    Log emergency alert to history file.
    
    File: emergency_alerts_{username}.json
    """
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "username": username,
        "location_data": location_data,
        "message": message
    }
    
    filename = f"emergency_alerts_{username}.json"
    logs = []
    
    if os.path.exists(filename):
        with open(filename) as f:
            logs = json.load(f)
    
    logs.append(log_entry)
    
    with open(filename, "w") as f:
        json.dump(logs, f)
```

### Retrieve History

```python
def get_alert_history(self, username):
    """
    Get history of emergency alerts for user.
    
    Returns: List of alert log entries (chronological)
    """
    filename = f"emergency_alerts_{username}.json"
    if os.path.exists(filename):
        with open(filename) as f:
            return json.load(f)
    return []

# Usage
history = alert_system.get_alert_history("admin")
print(f"Total alerts: {len(history)}")
for alert in history:
    print(f"Alert at {alert['timestamp']}: {alert['message']}")
```

---

## SMTP Configuration

### Gmail Configuration

```python
# Default configuration (Gmail)
smtp_config = {
    "server": "smtp.gmail.com",
    "port": 587,
    "username": os.getenv("SMTP_USERNAME"),
    "password": os.getenv("SMTP_PASSWORD")
}

# Gmail App Password Setup:
# 1. Enable 2FA on Google Account
# 2. Go to https://myaccount.google.com/apppasswords
# 3. Generate App Password for "Mail"
# 4. Use App Password as SMTP_PASSWORD
```

### Alternative SMTP Servers

```python
# Outlook/Office 365
alert_system = EmergencyAlert(smtp_config={
    "server": "smtp.office365.com",
    "port": 587,
    "username": "user@outlook.com",
    "password": "password"
})

# Yahoo Mail
alert_system = EmergencyAlert(smtp_config={
    "server": "smtp.mail.yahoo.com",
    "port": 587,
    "username": "user@yahoo.com",
    "password": "app_password"
})

# SendGrid (transactional email service)
alert_system = EmergencyAlert(smtp_config={
    "server": "smtp.sendgrid.net",
    "port": 587,
    "username": "apikey",
    "password": "SG.xxxxxxxxxxxxxxxxxxxx"
})

# Custom SMTP server
alert_system = EmergencyAlert(smtp_config={
    "server": "mail.company.com",
    "port": 25,
    "username": "alerts@company.com",
    "password": "secure_password"
})
```

---

## Integration Examples

### With Location Tracker

```python
from app.core.location_tracker import LocationTracker
from app.core.emergency_alert import EmergencyAlert

tracker = LocationTracker()
alert_system = EmergencyAlert()

# Get current location
location = tracker.get_location_from_ip()

# Send emergency alert with location
alert_system.send_alert(
    username="admin",
    location_data=location,
    message="Panic button activated - immediate assistance required"
)
```

### With GUI Panic Button

```python
from PyQt6.QtWidgets import QPushButton
from app.core.location_tracker import LocationTracker
from app.core.emergency_alert import EmergencyAlert

class EmergencyPanicButton(QPushButton):
    def __init__(self, username):
        super().__init__("🚨 EMERGENCY")
        self.username = username
        self.tracker = LocationTracker()
        self.alert_system = EmergencyAlert()
        self.clicked.connect(self.trigger_emergency_alert)
        self.setStyleSheet("background-color: red; color: white; font-size: 18px; padding: 15px;")
    
    def trigger_emergency_alert(self):
        # Get location
        location = self.tracker.get_location_from_ip()
        
        # Send alert
        success, message = self.alert_system.send_alert(
            self.username,
            location,
            "User activated emergency panic button"
        )
        
        if success:
            self.setText("✅ Alert Sent")
            QTimer.singleShot(2000, lambda: self.setText("🚨 EMERGENCY"))
        else:
            self.setText("❌ Alert Failed")
            print(f"Alert failed: {message}")
```

### Automated Alert Triggers

```python
from app.core.emergency_alert import EmergencyAlert

def setup_automated_alerts(username):
    """Setup automated emergency alert triggers."""
    alert_system = EmergencyAlert()
    tracker = LocationTracker()
    
    # Trigger 1: User inactivity (24 hours)
    def check_inactivity():
        last_activity = get_last_activity_time(username)
        if time.time() - last_activity > 86400:  # 24 hours
            location = tracker.get_location_from_ip()
            alert_system.send_alert(
                username,
                location,
                "Automated alert: User inactive for 24 hours"
            )
    
    # Trigger 2: Unusual location (geofencing)
    def check_geofence_violation():
        location = tracker.get_location_from_ip()
        if not is_within_safe_zone(location):
            alert_system.send_alert(
                username,
                location,
                "Automated alert: User outside safe zone"
            )
    
    # Trigger 3: Biometric anomaly (requires hardware integration)
    def check_biometric_alert():
        heart_rate = get_heart_rate(username)  # Smartwatch API
        if heart_rate > 120 or heart_rate < 40:
            location = tracker.get_location_from_ip()
            alert_system.send_alert(
                username,
                location,
                f"Automated alert: Abnormal heart rate detected ({heart_rate} bpm)"
            )
```

---

## Error Handling

```python
from app.core.emergency_alert import EmergencyAlert
import smtplib

alert_system = EmergencyAlert()

try:
    success, message = alert_system.send_alert("admin", location, "Emergency")
    if not success:
        print(f"Alert failed: {message}")
except smtplib.SMTPAuthenticationError:
    print("SMTP authentication failed - check username/password")
except smtplib.SMTPServerDisconnected:
    print("SMTP server disconnected - check server/port configuration")
except smtplib.SMTPException as e:
    print(f"SMTP error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

---

## Testing

```python
import unittest
from unittest.mock import Mock, patch
from app.core.emergency_alert import EmergencyAlert

class TestEmergencyAlert(unittest.TestCase):
    def setUp(self):
        self.alert_system = EmergencyAlert(smtp_config={
            "server": "smtp.gmail.com",
            "port": 587,
            "username": "test@example.com",
            "password": "test_password"
        })
    
    def test_add_contact(self):
        """Test adding emergency contact."""
        self.alert_system.add_emergency_contact("test_user", {
            "emails": ["contact@example.com"]
        })
        self.assertIn("test_user", self.alert_system.emergency_contacts)
    
    @patch('smtplib.SMTP')
    def test_send_alert(self, mock_smtp):
        """Test alert sending."""
        self.alert_system.add_emergency_contact("test_user", {
            "emails": ["contact@example.com"]
        })
        
        success, message = self.alert_system.send_alert(
            "test_user",
            {"latitude": 40.7128, "longitude": -74.0060},
            "Test alert"
        )
        
        self.assertTrue(success)
        mock_smtp.assert_called_once()
```

---

## Configuration

```bash
# Environment variables
export SMTP_USERNAME="your-email@gmail.com"
export SMTP_PASSWORD="your-app-password"  # Gmail App Password

# Optional: Custom SMTP server
export SMTP_SERVER="smtp.office365.com"
export SMTP_PORT=587
```

---

## Security Considerations

1. **Never Commit SMTP Credentials**
   ```bash
   # Add to .gitignore
   .env
   emergency_contacts.json
   emergency_alerts_*.json
   ```

2. **Use App Passwords (Gmail)**
   ```python
   # Don't use main Google account password
   # Generate App Password: https://myaccount.google.com/apppasswords
   ```

3. **Encrypt Contact Data**
   ```python
   from app.core.data_persistence import EncryptedStateManager
   
   state_manager = EncryptedStateManager()
   state_manager.save_encrypted_state("emergency_contacts", contacts)
   ```

---

## Troubleshooting

### "SMTPAuthenticationError: Username and Password not accepted"
```python
# Gmail: Enable "Less secure app access" or use App Password
# https://myaccount.google.com/lesssecureapps
# https://myaccount.google.com/apppasswords
```

### "No emergency contacts registered for user"
```python
# Add contacts first
alert_system.add_emergency_contact("username", {
    "emails": ["contact@example.com"]
})
```

### Email Delivery Issues
```python
# Check spam folder
# Verify SMTP server/port configuration
# Test SMTP connection manually:
import smtplib
with smtplib.SMTP("smtp.gmail.com", 587) as server:
    server.starttls()
    server.login("user@gmail.com", "password")
    print("SMTP connection successful")
```

---

**Last Updated:** 2026-04-20  
**Module Version:** 1.0.0  
**Author:** AGENT-036 (Data & Infrastructure Documentation Specialist)
