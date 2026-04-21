# Emergency Alert Data Model

**Module**: `src/app/core/emergency_alert.py` [[src/app/core/emergency_alert.py]]  
**Storage**: `emergency_contacts_{username}.json`  
**Persistence**: JSON with email notification system  
**Schema Version**: 1.0

---

## Overview

Emergency alert system with contact management, email notifications, and SMS support (planned) for critical situations.

### Key Features

- **Contact Management**: Multiple emergency contacts per user
- **Email Notifications**: SMTP-based email alerts
- **Location Integration**: Includes location data in alerts
- **Template System**: Customizable email templates
- **Priority Levels**: Critical, high, medium, low

---

## Schema Structure

### Emergency Contacts Document

**File**: `emergency_contacts_{username}.json`

```json
{
  "contacts": [
    {
      "id": "contact_001",
      "name": "Jane Doe",
      "relationship": "Emergency Contact",
      "email": "jane.doe@example.com",
      "phone": "+1-555-0100",
      "priority": 1,
      "active": true,
      "added_at": "2024-01-01T00:00:00Z"
    },
    {
      "id": "contact_002",
      "name": "John Smith",
      "relationship": "Family",
      "email": "john.smith@example.com",
      "phone": "+1-555-0200",
      "priority": 2,
      "active": true,
      "added_at": "2024-01-01T00:00:00Z"
    }
  ],
  "alert_history": [
    {
      "alert_id": "alert_001",
      "timestamp": "2024-01-20T14:30:00Z",
      "severity": "critical",
      "message": "Emergency alert triggered by user",
      "location": {
        "latitude": 37.7749,
        "longitude": -122.4194,
        "city": "San Francisco"
      },
      "contacts_notified": ["contact_001", "contact_002"],
      "status": "sent"
    }
  ]
}
```

---

## Field Specifications

### Contact Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique contact identifier |
| `name` | string | Yes | Contact's full name |
| `relationship` | string | Yes | Relationship to user |
| `email` | string | Yes | Email address for notifications |
| `phone` | string | No | Phone number (for SMS, future) |
| `priority` | integer | Yes | Notification priority (1=highest) |
| `active` | boolean | Yes | Whether contact receives alerts |
| `added_at` | datetime | Yes | Contact registration timestamp |

### Alert History Entry

| Field | Type | Description |
|-------|------|-------------|
| `alert_id` | string | Unique alert identifier |
| `timestamp` | datetime | Alert trigger time |
| `severity` | string | "critical", "high", "medium", "low" |
| `message` | string | Alert message content |
| `location` | object | User location at time of alert |
| `contacts_notified` | array | List of contact IDs notified |
| `status` | string | "sent", "failed", "pending" |

---

## SMTP Configuration

### Environment Variables

```bash
# .env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=alerts@example.com
SMTP_PASSWORD=<app_password>
SMTP_FROM_EMAIL=alerts@example.com
SMTP_FROM_NAME=Project-AI Emergency Alerts
```

### SMTP Connection

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def _connect_smtp(self) -> smtplib.SMTP | None:
    """Connect to SMTP server."""
    try:
        smtp_host = os.getenv("SMTP_HOST")
        smtp_port = int(os.getenv("SMTP_PORT", 587))
        
        server = smtplib.SMTP(smtp_host, smtp_port, timeout=10)
        server.starttls()
        
        smtp_user = os.getenv("SMTP_USERNAME")
        smtp_pass = os.getenv("SMTP_PASSWORD")
        server.login(smtp_user, smtp_pass)
        
        return server
    except Exception as e:
        logger.error("SMTP connection error: %s", e)
        return None
```

---

## Contact Management

### Add Emergency Contact

```python
def add_contact(self, username: str, name: str, relationship: str, 
                email: str, phone: str | None = None, priority: int = 1) -> str:
    """Add emergency contact."""
    contacts = self._load_contacts(username)
    
    contact_id = f"contact_{len(contacts['contacts']) + 1:03d}"
    contact = {
        "id": contact_id,
        "name": name,
        "relationship": relationship,
        "email": email,
        "phone": phone,
        "priority": priority,
        "active": True,
        "added_at": datetime.now().isoformat()
    }
    
    contacts["contacts"].append(contact)
    self._save_contacts(username, contacts)
    
    return contact_id
```

### Remove Contact

```python
def remove_contact(self, username: str, contact_id: str) -> bool:
    """Remove emergency contact."""
    contacts = self._load_contacts(username)
    
    original_count = len(contacts["contacts"])
    contacts["contacts"] = [c for c in contacts["contacts"] if c["id"] != contact_id]
    
    if len(contacts["contacts"]) < original_count:
        self._save_contacts(username, contacts)
        return True
    
    return False
```

### Update Contact Priority

```python
def update_contact_priority(self, username: str, contact_id: str, priority: int) -> bool:
    """Update contact notification priority."""
    contacts = self._load_contacts(username)
    
    for contact in contacts["contacts"]:
        if contact["id"] == contact_id:
            contact["priority"] = priority
            self._save_contacts(username, contacts)
            return True
    
    return False
```

---

## Alert Sending

### Send Emergency Alert

```python
def send_alert(self, username: str, message: str, severity: str = "high", 
               location: dict | None = None) -> dict:
    """Send emergency alert to all active contacts."""
    contacts = self._load_contacts(username)
    active_contacts = [c for c in contacts["contacts"] if c["active"]]
    
    # Sort by priority
    active_contacts.sort(key=lambda c: c["priority"])
    
    # Send emails
    results = []
    for contact in active_contacts:
        success = self._send_email_alert(contact, username, message, severity, location)
        results.append({
            "contact_id": contact["id"],
            "name": contact["name"],
            "email": contact["email"],
            "success": success
        })
    
    # Log alert
    alert_id = self._log_alert(username, message, severity, location, 
                                [r["contact_id"] for r in results if r["success"]])
    
    return {
        "alert_id": alert_id,
        "contacts_notified": len([r for r in results if r["success"]]),
        "results": results
    }
```

### Email Alert Template

```python
def _send_email_alert(self, contact: dict, username: str, message: str, 
                      severity: str, location: dict | None) -> bool:
    """Send email alert to contact."""
    try:
        server = self._connect_smtp()
        if not server:
            return False
        
        # Build email
        msg = MIMEMultipart()
        msg["From"] = f"{os.getenv('SMTP_FROM_NAME')} <{os.getenv('SMTP_FROM_EMAIL')}>"
        msg["To"] = contact["email"]
        msg["Subject"] = f"[{severity.upper()}] Emergency Alert from {username}"
        
        # Email body
        body = f"""
        Emergency Alert
        
        Severity: {severity.upper()}
        User: {username}
        Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
        
        Message:
        {message}
        """
        
        if location:
            body += f"""
        
        Location:
        - City: {location.get('city', 'Unknown')}
        - Coordinates: {location.get('latitude')}, {location.get('longitude')}
        """
        
        body += f"""
        
        Contact: {contact['name']} ({contact['relationship']})
        
        This is an automated emergency alert from Project-AI.
        """
        
        msg.attach(MIMEText(body, "plain"))
        
        # Send email
        server.sendmail(
            os.getenv("SMTP_FROM_EMAIL"),
            contact["email"],
            msg.as_string()
        )
        
        server.quit()
        return True
        
    except Exception as e:
        logger.error("Failed to send email to %s: %s", contact["email"], e)
        return False
```

---

## Alert History

### Log Alert

```python
def _log_alert(self, username: str, message: str, severity: str, 
               location: dict | None, contacts_notified: list[str]) -> str:
    """Log alert to history."""
    contacts = self._load_contacts(username)
    
    alert_id = f"alert_{len(contacts['alert_history']) + 1:03d}"
    alert_entry = {
        "alert_id": alert_id,
        "timestamp": datetime.now().isoformat(),
        "severity": severity,
        "message": message,
        "location": location,
        "contacts_notified": contacts_notified,
        "status": "sent" if contacts_notified else "failed"
    }
    
    contacts["alert_history"].append(alert_entry)
    self._save_contacts(username, contacts)
    
    return alert_id
```

### Get Alert History

```python
def get_alert_history(self, username: str, limit: int = 10) -> list[dict]:
    """Get recent alert history."""
    contacts = self._load_contacts(username)
    history = contacts.get("alert_history", [])
    
    # Sort by timestamp descending
    history.sort(key=lambda a: a["timestamp"], reverse=True)
    
    return history[:limit]
```

---

## Usage Examples

### Setup Emergency Contacts

```python
from app.core.emergency_alert import EmergencyAlertSystem

alert_system = EmergencyAlertSystem()

# Add primary contact
contact_id_1 = alert_system.add_contact(
    username="alice",
    name="Jane Doe",
    relationship="Emergency Contact",
    email="jane@example.com",
    phone="+1-555-0100",
    priority=1
)

# Add secondary contact
contact_id_2 = alert_system.add_contact(
    username="alice",
    name="John Smith",
    relationship="Family",
    email="john@example.com",
    priority=2
)
```

### Send Emergency Alert

```python
# Get current location
from app.core.location_tracker import LocationTracker

tracker = LocationTracker()
location = tracker.get_location_from_ip()

# Send alert
result = alert_system.send_alert(
    username="alice",
    message="Emergency alert triggered - immediate assistance needed",
    severity="critical",
    location=location
)

print(f"Alert ID: {result['alert_id']}")
print(f"Contacts notified: {result['contacts_notified']}")
```

### View Alert History

```python
history = alert_system.get_alert_history("alice", limit=5)

for alert in history:
    print(f"[{alert['timestamp']}] {alert['severity'].upper()}: {alert['message']}")
    print(f"  Contacts notified: {len(alert['contacts_notified'])}")
```

---

## Integration with Location Tracker

```python
from app.core.location_tracker import LocationTracker
from app.core.emergency_alert import EmergencyAlertSystem

def trigger_emergency_with_location(username: str, message: str):
    """Trigger emergency alert with current location."""
    tracker = LocationTracker()
    location = tracker.get_location_from_ip()
    
    alert_system = EmergencyAlertSystem()
    result = alert_system.send_alert(username, message, "critical", location)
    
    return result
```

---

## Security & Privacy

### Contact Data Encryption (Future)

**Planned**: Encrypt contact information at rest.

```python
from cryptography.fernet import Fernet

def _encrypt_contacts(self, contacts: dict) -> bytes:
    """Encrypt contacts before saving."""
    cipher = Fernet(self.encryption_key)
    json_data = json.dumps(contacts)
    return cipher.encrypt(json_data.encode())
```

### Access Control

**Recommended**: Only user can view/modify their own contacts.

```python
def authorize_contact_access(username: str, requester: str) -> bool:
    """Verify user can access contacts."""
    if username != requester:
        # Admin override check
        acl = get_access_control()
        if not acl.has_role(requester, "admin"):
            raise PermissionError("Cannot access other user's emergency contacts")
    return True
```

---

## Testing Strategy

### Unit Tests

```python
def test_add_remove_contact():
    alert_system = EmergencyAlertSystem()
    
    contact_id = alert_system.add_contact(
        "testuser", "Test Contact", "Friend", "test@example.com"
    )
    
    assert contact_id is not None
    
    success = alert_system.remove_contact("testuser", contact_id)
    assert success
```

### Mock SMTP

```python
from unittest.mock import patch, MagicMock

def test_send_alert_success():
    with patch('smtplib.SMTP') as mock_smtp:
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        alert_system = EmergencyAlertSystem()
        result = alert_system.send_alert("testuser", "Test alert", "high")
        
        assert result["contacts_notified"] >= 0
```

---

## Related Modules

| Module | Relationship |
|--------|-------------|
| `location_tracker.py` | Provides location data for alerts |
| `user_manager.py` | User authentication for contact management |
| `command_override.py` | Triggers alerts on override activation |
| `telemetry.py` | Logs alert events |

---

## Future Enhancements

1. **SMS Support**: Twilio integration for text messages
2. **Push Notifications**: Mobile app push notifications
3. **Voice Calls**: Automated voice alert calls
4. **Escalation Rules**: Auto-escalate if primary contact doesn't respond
5. **Geo-fencing Alerts**: Trigger when user enters/exits safe zones

---

**Last Updated**: 2024-01-20  
**Schema Version**: 1.0  
**Maintainer**: Project-AI Core Team


---

## Related Documentation

- **Relationship Map**: [[relationships\data\README.md]]


---

## Source Code References

- **Primary Module**: [[src/app/core/emergency_alert.py]]
