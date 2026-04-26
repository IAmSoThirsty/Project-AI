# SMS Integration Relationship Map

**Status**: 🟡 Planned | **Type**: External Communication Service  
**Priority**: P3 Future Enhancement | **Governance**: API-Based

---


## Navigation

**Location**: `relationships\integrations\13-sms-integration.md`

**Parent**: [[relationships\integrations\README.md]]


## Overview

SMS integration is a **planned feature** for sending emergency alerts, notifications, and two-factor authentication codes via SMS. This document outlines the proposed architecture and implementation.

**Current Status**: ⏳ NOT IMPLEMENTED  
**Planned For**: Phase 3 (2025 Q3-Q4)

---

## Proposed Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   SMS MANAGER (Planned)                      │
│         src/app/core/sms_manager.py (NOT CREATED)            │
│  ┌──────────────────────────────────────────┐              │
│  │ SMS Contact Management                   │              │
│  │ Emergency SMS Alerts                     │              │
│  │ 2FA Code Sender                          │              │
│  │ Delivery Status Tracking                 │              │
│  └──────────────────────────────────────────┘              │
└────────────────┬────────────────────────────────────────────┘
                 │
        ┌────────┴────────┐
        │                 │
        ▼                 ▼
┌───────────────┐  ┌───────────────┐
│ Twilio API    │  │ AWS SNS       │
│ (Primary)     │  │ (Fallback)    │
└───────────────┘  └───────────────┘
```

---

## Proposed Providers

### Option 1: Twilio (Recommended)

**Pros**:
- ✅ Easy to use, well-documented
- ✅ Global coverage (200+ countries)
- ✅ Delivery reports and status webhooks
- ✅ Python SDK available
- ✅ Phone number verification API

**Cons**:
- ❌ Cost: $0.0075 per SMS (US)
- ❌ Requires phone number purchase ($1/month)

**Pricing**:
- SMS (US): $0.0075/message
- SMS (International): $0.01-0.10/message
- Phone number rental: $1-2/month

**API Example**:
```python
from twilio.rest import Client

client = Client(
    os.getenv("TWILIO_ACCOUNT_SID"),
    os.getenv("TWILIO_AUTH_TOKEN")
)

message = client.messages.create(
    body="🚨 EMERGENCY ALERT: Alice at 37.7749, -122.4194",
    from_="+15551234567",  # Your Twilio number
    to="+15559876543"       # Recipient number
)

print(f"Message SID: {message.sid}")
print(f"Status: {message.status}")  # queued, sent, delivered, failed
```

### Option 2: AWS SNS (Simple Notification Service)

**Pros**:
- ✅ Pay-as-you-go pricing
- ✅ No monthly fees
- ✅ Integrates with AWS ecosystem
- ✅ Supports SMS, email, push notifications

**Cons**:
- ❌ Limited to 100 SMS/day (free tier)
- ❌ No phone number purchasing
- ❌ Less detailed delivery reports

**Pricing**:
- SMS (US): $0.00645/message
- SMS (International): Varies by country

**API Example**:
```python
import boto3

sns = boto3.client(
    "sns",
    region_name="us-east-1",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
)

response = sns.publish(
    PhoneNumber="+15559876543",
    Message="🚨 EMERGENCY ALERT: Alice at 37.7749, -122.4194",
    MessageAttributes={
        "AWS.SNS.SMS.SMSType": {"DataType": "String", "StringValue": "Transactional"}
    }
)

print(f"Message ID: {response['MessageId']}")
```

### Option 3: Local SMS (Android Only)

**Pros**:
- ✅ Free (uses device's SMS)
- ✅ No API keys required
- ✅ Works offline

**Cons**:
- ❌ Android-only
- ❌ Requires SMS permissions
- ❌ Limited to device's SMS plan

**Implementation** (via Android Intents):
```python
# In Android app (using Kivy or similar)
from android.permissions import request_permissions, Permission
from jnius import autoclass

request_permissions([Permission.SEND_SMS])

SmsManager = autoclass("android.telephony.SmsManager")
sms = SmsManager.getDefault()
sms.sendTextMessage(
    "+15559876543",  # Destination
    None,            # Service center (default)
    "Emergency alert from Project-AI",  # Message
    None,            # Sent intent
    None             # Delivery intent
)
```

---

## Proposed Functionality

### SMS Manager Class

```python
# src/app/core/sms_manager.py (PLANNED)
import logging
import os
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class SMSProvider(Enum):
    """SMS provider options."""
    TWILIO = "twilio"
    AWS_SNS = "aws_sns"
    LOCAL = "local"  # Android only


class SMSStatus(Enum):
    """SMS delivery status."""
    QUEUED = "queued"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    UNDELIVERED = "undelivered"


class SMSManager:
    """Manage SMS sending and delivery tracking."""
    
    def __init__(self, provider: SMSProvider = SMSProvider.TWILIO):
        """
        Initialize SMS manager.
        
        Args:
            provider: SMS provider to use (Twilio, AWS SNS, Local)
        """
        self.provider = provider
        self._client = self._init_provider()
        self.sms_contacts = self._load_sms_contacts()
    
    def _init_provider(self):
        """Initialize provider client."""
        if self.provider == SMSProvider.TWILIO:
            from twilio.rest import Client
            return Client(
                os.getenv("TWILIO_ACCOUNT_SID"),
                os.getenv("TWILIO_AUTH_TOKEN")
            )
        elif self.provider == SMSProvider.AWS_SNS:
            import boto3
            return boto3.client("sns", region_name="us-east-1")
        else:
            # Local SMS (Android)
            return None
    
    def send_sms(self, to_number: str, message: str) -> tuple[bool, str]:
        """
        Send SMS message.
        
        Args:
            to_number: Recipient phone number (E.164 format: +15551234567)
            message: Message body (max 160 chars for single SMS)
        
        Returns:
            (success: bool, message_id: str)
        """
        try:
            if self.provider == SMSProvider.TWILIO:
                return self._send_via_twilio(to_number, message)
            elif self.provider == SMSProvider.AWS_SNS:
                return self._send_via_sns(to_number, message)
            else:
                return self._send_via_local(to_number, message)
        except Exception as e:
            logger.error(f"Failed to send SMS: {e}")
            return False, str(e)
    
    def _send_via_twilio(self, to_number, message):
        """Send via Twilio API."""
        response = self._client.messages.create(
            body=message,
            from_=os.getenv("TWILIO_PHONE_NUMBER"),
            to=to_number
        )
        return True, response.sid
    
    def _send_via_sns(self, to_number, message):
        """Send via AWS SNS."""
        response = self._client.publish(
            PhoneNumber=to_number,
            Message=message,
            MessageAttributes={
                "AWS.SNS.SMS.SMSType": {
                    "DataType": "String",
                    "StringValue": "Transactional"
                }
            }
        )
        return True, response["MessageId"]
    
    def send_emergency_alert(self, username: str, location_data: dict, message: str = None):
        """
        Send emergency alert via SMS.
        
        Args:
            username: User whose SMS contacts to notify
            location_data: Dict with 'lat', 'lng', 'timestamp' keys
            message: Optional custom message
        
        Returns:
            (success: bool, message: str)
        """
        if username not in self.sms_contacts:
            return False, "No SMS contacts registered"
        
        contact_numbers = self.sms_contacts[username].get("phone_numbers", [])
        
        if not contact_numbers:
            return False, "No phone numbers configured"
        
        # Build alert message
        lat = location_data.get("lat", "Unknown")
        lng = location_data.get("lng", "Unknown")
        maps_link = f"https://maps.google.com/?q={lat},{lng}"
        
        sms_body = (
            f"🚨 EMERGENCY ALERT\n"
            f"User: {username}\n"
            f"Location: {lat}, {lng}\n"
            f"Map: {maps_link}"
        )
        
        if message:
            sms_body += f"\nMessage: {message}"
        
        # Send to all contacts
        sent_count = 0
        for number in contact_numbers:
            success, msg_id = self.send_sms(number, sms_body)
            if success:
                sent_count += 1
                logger.info(f"SMS sent to {number}: {msg_id}")
        
        if sent_count > 0:
            return True, f"Alert sent to {sent_count} recipients"
        else:
            return False, "Failed to send SMS to any recipient"
    
    def send_2fa_code(self, phone_number: str, code: str) -> tuple[bool, str]:
        """
        Send 2FA verification code via SMS.
        
        Args:
            phone_number: Recipient phone number
            code: 6-digit verification code
        
        Returns:
            (success: bool, message_id: str)
        """
        message = f"Your Project-AI verification code is: {code}\nValid for 5 minutes."
        return self.send_sms(phone_number, message)
    
    def check_delivery_status(self, message_id: str) -> SMSStatus:
        """
        Check SMS delivery status (Twilio only).
        
        Args:
            message_id: Message SID from send_sms()
        
        Returns:
            SMSStatus enum value
        """
        if self.provider != SMSProvider.TWILIO:
            logger.warning("Delivery status check only supported for Twilio")
            return SMSStatus.SENT
        
        try:
            message = self._client.messages(message_id).fetch()
            status_map = {
                "queued": SMSStatus.QUEUED,
                "sent": SMSStatus.SENT,
                "delivered": SMSStatus.DELIVERED,
                "failed": SMSStatus.FAILED,
                "undelivered": SMSStatus.UNDELIVERED
            }
            return status_map.get(message.status, SMSStatus.SENT)
        except Exception as e:
            logger.error(f"Failed to check status: {e}")
            return SMSStatus.FAILED
```

---

## Configuration

### Environment Variables

```bash
# Twilio Configuration
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+15551234567  # Your Twilio number

# AWS SNS Configuration
AWS_ACCESS_KEY_ID=AKIAxxxxxxxxxxxxx
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
```

### SMS Contacts Storage

**File**: `emergency_contacts.json` (extend existing file)

```json
{
    "alice": {
        "name": "Alice Smith",
        "emails": ["alice@example.com"],
        "phone_numbers": ["+15551234567", "+15559876543"],
        "sms_enabled": true
    }
}
```

---

## Security

### Phone Number Validation

```python
import re

def validate_phone_number(phone: str) -> bool:
    """Validate E.164 phone number format."""
    # E.164: +[country code][subscriber number]
    # Example: +15551234567 (US)
    pattern = r"^\+[1-9]\d{1,14}$"
    return bool(re.match(pattern, phone))
```

### Rate Limiting

```python
from datetime import datetime, timedelta

class RateLimiter:
    """Prevent SMS spam."""
    
    def __init__(self, max_sms_per_hour=10):
        self.max_sms_per_hour = max_sms_per_hour
        self.sms_log = []
    
    def can_send_sms(self) -> bool:
        """Check if SMS can be sent within rate limit."""
        now = datetime.now()
        one_hour_ago = now - timedelta(hours=1)
        
        # Remove old entries
        self.sms_log = [t for t in self.sms_log if t > one_hour_ago]
        
        if len(self.sms_log) >= self.max_sms_per_hour:
            return False
        
        self.sms_log.append(now)
        return True
```

---

## Cost Estimation

### Monthly Cost (Twilio)

**Assumptions**:
- 100 users
- 2 SMS/user/month (emergency alerts, 2FA)
- $0.0075 per SMS (US)

**Calculation**:
- SMS cost: 100 users × 2 SMS × $0.0075 = **$1.50/month**
- Phone number: **$1/month**
- **Total: $2.50/month**

**Scaling**:
- 1,000 users: **$16/month**
- 10,000 users: **$151/month**

---

## Testing

```python
# tests/test_sms_integration.py (PLANNED)
def test_send_sms():
    # Mock Twilio client
    with patch("twilio.rest.Client") as mock_client:
        manager = SMSManager(provider=SMSProvider.TWILIO)
        
        success, msg_id = manager.send_sms("+15551234567", "Test message")
        
        assert success is True
        mock_client.assert_called_once()

def test_send_emergency_alert():
    manager = SMSManager()
    manager.sms_contacts = {
        "alice": {"phone_numbers": ["+15551234567"]}
    }
    
    success, msg = manager.send_emergency_alert(
        "alice",
        {"lat": 37.7749, "lng": -122.4194, "timestamp": "2025-01-26T12:00:00Z"}
    )
    
    assert success is True
```

---

## Implementation Roadmap

### Phase 1: Core SMS (Q3 2025) ⏳ PLANNED
- [ ] Twilio integration
- [ ] SMS contact management
- [ ] Emergency alert sending
- [ ] Delivery status tracking

### Phase 2: 2FA (Q4 2025) 🔮 FUTURE
- [ ] Generate 6-digit codes
- [ ] SMS code delivery
- [ ] Code verification
- [ ] Rate limiting

### Phase 3: Rich Messaging (2026) 🔮 FUTURE
- [ ] MMS support (images, videos)
- [ ] WhatsApp integration
- [ ] Two-way messaging
- [ ] Group SMS

---

## Alternative: Push Notifications

**Note**: For mobile apps, push notifications (Firebase Cloud Messaging, Apple Push Notification Service) are more cost-effective than SMS.

**Comparison**:

| Feature | SMS | Push Notification |
|---------|-----|-------------------|
| Cost | $0.0075/message | Free |
| Delivery rate | 95% | 90% (requires app) |
| Character limit | 160 chars | Unlimited |
| Rich media | MMS only ($0.02) | Images, buttons, actions |
| Requires app | ❌ No | ✅ Yes |

---

## Related Systems

- **[12-email-integration.md](12-email-integration.md)**: Email as primary alert channel
- **[05-external-apis.md](05-external-apis.md)**: External API patterns
- Location Tracker: Provides location for alerts

---

**Last Updated**: 2025-01-26  
**Maintained By**: AGENT-060  
**Review Cycle**: Quarterly  
**Status**: 📝 Design Document (Not Implemented)


---

## See Also

### Related Source Documentation

- **01 Openai Integration**: [[source-docs\integrations\01-openai-integration.md]]
- **02 Huggingface Integration**: [[source-docs\integrations\02-huggingface-integration.md]]
- **05 Database Integrations**: [[source-docs\integrations\05-database-integrations.md]]
- **11 Openrouter Integration**: [[source-docs\integrations\11-openrouter-integration.md]]
- **12 Perplexity Integration**: [[source-docs\integrations\12-perplexity-integration.md]]
- **Documentation Index**: [[source-docs\integrations\README.md]]
