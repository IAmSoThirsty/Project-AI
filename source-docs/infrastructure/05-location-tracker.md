# Location Tracking System

**Module:** `src/app/core/location_tracker.py`  
**Type:** Core Infrastructure  
**Dependencies:** requests, geopy, cryptography (Fernet)  
**Related Modules:** emergency_alert.py, user_manager.py

---

## Overview

The Location Tracking System provides encrypted location tracking with IP geolocation and GPS coordinate resolution, designed for emergency services integration and privacy-first data storage.

### Core Features

- **Dual-Source Location**: IP-based geolocation + GPS coordinates
- **Encrypted History Storage**: Fernet-encrypted location logs
- **Emergency Integration**: Real-time location for emergency alerts
- **Privacy Controls**: User consent required (via user_manager)
- **Offline History**: Local encrypted storage with JSON persistence

---

## Architecture

```
LocationTracker
├── IP Geolocation (ipapi.co API)
├── GPS Geocoding (Nominatim/OpenStreetMap)
├── Encryption Layer (Fernet cipher)
├── History Management (encrypted JSON logs)
└── Emergency Integration (EmergencyAlert compatibility)
```

---

## Core Classes

### LocationTracker

```python
from app.core.location_tracker import LocationTracker

# Initialize (auto-loads FERNET_KEY from env)
tracker = LocationTracker()

# Custom encryption key
from cryptography.fernet import Fernet
custom_key = Fernet.generate_key()
tracker = LocationTracker(encryption_key=custom_key)

# Get location from IP address (no GPS required)
location = tracker.get_location_from_ip()
# Returns: {
#     "latitude": 40.7128,
#     "longitude": -74.0060,
#     "city": "New York",
#     "region": "New York",
#     "country": "United States",
#     "ip": "203.0.113.45",
#     "timestamp": "2026-04-20T14:00:00",
#     "source": "ip"
# }

# Get location from GPS coordinates (reverse geocoding)
location = tracker.get_location_from_coords(
    latitude=40.7128,
    longitude=-74.0060
)
# Returns: {
#     "latitude": 40.7128,
#     "longitude": -74.0060,
#     "address": "New York, NY, United States",
#     "timestamp": "2026-04-20T14:00:00",
#     "source": "gps"
# }

# Save encrypted location history
tracker.save_location_history("admin", location)

# Retrieve location history (decrypted)
history = tracker.get_location_history("admin")
# Returns: [location1, location2, ...]

# Clear history (GDPR compliance)
tracker.clear_location_history("admin")
```

---

## IP Geolocation

### API: ipapi.co

```python
def get_location_from_ip(self):
    """
    Get location from public IP address using ipapi.co API.
    
    Free tier: 1,000 requests/day
    No authentication required
    """
    try:
        response = requests.get("https://ipapi.co/json/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return {
                "latitude": data.get("latitude"),
                "longitude": data.get("longitude"),
                "city": data.get("city"),
                "region": data.get("region"),
                "country": data.get("country_name"),
                "ip": data.get("ip"),
                "timestamp": datetime.now().isoformat(),
                "source": "ip"
            }
    except requests.Timeout:
        print("Request to IP geolocation API timed out")
        return None
```

**Example Response:**
```json
{
  "latitude": 37.7749,
  "longitude": -122.4194,
  "city": "San Francisco",
  "region": "California",
  "country": "United States",
  "ip": "203.0.113.45",
  "timestamp": "2026-04-20T14:00:00.123456",
  "source": "ip"
}
```

**Rate Limits:**
- Free: 1,000 requests/day
- Pro: 50,000 requests/day ($10/month)
- Business: 250,000 requests/day ($50/month)

---

## GPS Geocoding

### API: Nominatim (OpenStreetMap)

```python
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

def get_location_from_coords(self, latitude, longitude):
    """
    Reverse geocode GPS coordinates to address.
    
    API: Nominatim (OpenStreetMap)
    Rate Limit: 1 request/second
    """
    try:
        geolocator = Nominatim(user_agent="ai_assistant")
        location = geolocator.reverse(f"{latitude}, {longitude}")
        
        if location:
            return {
                "latitude": latitude,
                "longitude": longitude,
                "address": location.address,
                "timestamp": datetime.now().isoformat(),
                "source": "gps"
            }
    except GeocoderTimedOut:
        print("Geocoding service timed out")
        return None
```

**Example Response:**
```json
{
  "latitude": 40.7128,
  "longitude": -74.0060,
  "address": "New York City Hall, Broadway, Manhattan, New York County, New York, 10007, United States",
  "timestamp": "2026-04-20T14:00:00.123456",
  "source": "gps"
}
```

**Usage Policy:**
- Rate Limit: 1 request/second
- User Agent: Required (identifies your app)
- Caching: Recommended for repeated queries
- No bulk geocoding (use Nominatim server or commercial API)

---

## Encryption System

### Location Data Encryption

```python
# Encrypt location data (Fernet cipher)
location_data = {
    "latitude": 40.7128,
    "longitude": -74.0060,
    "city": "New York",
    "timestamp": "2026-04-20T14:00:00"
}

encrypted_bytes = tracker.encrypt_location(location_data)
# Returns: b'gAAAAABmY3RpMjAyNi0wNC0y...' (Fernet token)

# Decrypt location data
decrypted_data = tracker.decrypt_location(encrypted_bytes)
# Returns: {"latitude": 40.7128, "longitude": -74.0060, ...}
```

**Encryption Details:**
- Algorithm: Fernet (AES-128-CBC + HMAC-SHA256)
- Key Source: `FERNET_KEY` environment variable or auto-generated
- Format: Base64-encoded Fernet token
- Security: Authenticated encryption (tamper-proof)

---

## History Management

### Storage Format

```python
# File: location_history_admin.json
[
  "gAAAAABmY3RpMjAyNi0wNC0y...",  // Encrypted location 1
  "gAAAAABmY3RpMjAyNi0wNC0z...",  // Encrypted location 2
  "gAAAAABmY3RpMjAyNi0wNC00..."   // Encrypted location 3
]
```

### Save Location History

```python
def save_location_history(self, username, location_data):
    """
    Save encrypted location to history file.
    
    File: location_history_{username}.json
    Format: Array of base64-encoded Fernet tokens
    """
    filename = f"location_history_{username}.json"
    history = []
    
    if os.path.exists(filename):
        with open(filename) as f:
            history = json.load(f)
    
    # Encrypt and append
    encrypted_location = self.encrypt_location(location_data)
    if encrypted_location:
        history.append(encrypted_location.decode())  # bytes → string
    
    with open(filename, "w") as f:
        json.dump(history, f)
```

### Retrieve Location History

```python
def get_location_history(self, username):
    """
    Get decrypted location history for user.
    
    Returns: List of location dictionaries (chronological order)
    """
    filename = f"location_history_{username}.json"
    if not os.path.exists(filename):
        return []
    
    with open(filename) as f:
        history = json.load(f)
    
    decrypted_history = []
    for encrypted_location in history:
        location_data = self.decrypt_location(encrypted_location.encode())
        if location_data:
            decrypted_history.append(location_data)
    
    return decrypted_history
```

### Clear Location History

```python
def clear_location_history(self, username):
    """
    Delete location history for user (GDPR compliance).
    
    Returns: True if deleted, False if not found
    """
    filename = f"location_history_{username}.json"
    if os.path.exists(filename):
        os.remove(filename)
        return True
    return False
```

---

## Integration Examples

### With Emergency Alert System

```python
from app.core.location_tracker import LocationTracker
from app.core.emergency_alert import EmergencyAlert

tracker = LocationTracker()
alert_system = EmergencyAlert()

# Enable location tracking for user
tracker.active = True

# Get current location
location = tracker.get_location_from_ip()

# Send emergency alert with location
alert_system.send_alert(
    username="admin",
    location_data=location,
    message="Emergency assistance needed"
)
```

### With User Manager (Consent Checking)

```python
from app.core.location_tracker import LocationTracker
from app.core.user_manager import UserManager

tracker = LocationTracker()
user_manager = UserManager()

# Check user consent before tracking
user_data = user_manager.get_user_data("admin")
if user_data.get("location_active", False):
    location = tracker.get_location_from_ip()
    tracker.save_location_history("admin", location)
else:
    print("Location tracking disabled for user")
```

### Location Heatmap Generation

```python
import folium
from collections import Counter

def generate_location_heatmap(username):
    """Generate HTML heatmap from location history."""
    tracker = LocationTracker()
    history = tracker.get_location_history(username)
    
    if not history:
        return None
    
    # Extract coordinates
    coords = [(loc["latitude"], loc["longitude"]) for loc in history]
    
    # Create map centered on average location
    avg_lat = sum(lat for lat, _ in coords) / len(coords)
    avg_lon = sum(lon for _, lon in coords) / len(coords)
    
    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=10)
    
    # Add markers for each location
    for loc in history:
        folium.Marker(
            location=[loc["latitude"], loc["longitude"]],
            popup=f"{loc['city']}, {loc['country']}<br>{loc['timestamp']}",
            icon=folium.Icon(color="red", icon="info-sign")
        ).add_to(m)
    
    # Save to HTML
    m.save(f"location_heatmap_{username}.html")
    return f"location_heatmap_{username}.html"

# Usage
heatmap_file = generate_location_heatmap("admin")
```

---

## Privacy and Compliance

### GDPR Compliance

```python
# Right to Erasure (Article 17)
def gdpr_delete_user_data(username):
    """Delete all location data for user."""
    tracker = LocationTracker()
    success = tracker.clear_location_history(username)
    if success:
        print(f"Deleted location history for {username}")
    return success

# Right to Data Portability (Article 20)
def gdpr_export_user_data(username, output_file):
    """Export user location data to JSON."""
    tracker = LocationTracker()
    history = tracker.get_location_history(username)
    
    with open(output_file, 'w') as f:
        json.dump({
            "username": username,
            "export_date": datetime.now().isoformat(),
            "location_history": history
        }, f, indent=2)
    
    return output_file

# Usage
gdpr_export_user_data("admin", "admin_location_export.json")
```

### Consent Management

```python
from app.core.user_manager import UserManager

def enable_location_tracking(username):
    """Enable location tracking with user consent."""
    user_manager = UserManager()
    user_manager.update_user(username, location_active=True)
    print(f"Location tracking enabled for {username}")

def disable_location_tracking(username):
    """Disable location tracking."""
    user_manager = UserManager()
    user_manager.update_user(username, location_active=False)
    
    # Optionally clear history
    tracker = LocationTracker()
    tracker.clear_location_history(username)
    print(f"Location tracking disabled for {username}")
```

---

## Error Handling

```python
from app.core.location_tracker import LocationTracker
from requests import Timeout, RequestException
from geopy.exc import GeocoderTimedOut

tracker = LocationTracker()

try:
    location = tracker.get_location_from_ip()
    if location is None:
        print("Failed to get location from IP")
except Timeout:
    print("IP geolocation service timed out")
except RequestException as e:
    print(f"Network error: {e}")

try:
    location = tracker.get_location_from_coords(40.7128, -74.0060)
    if location is None:
        print("Failed to geocode coordinates")
except GeocoderTimedOut:
    print("Geocoding service timed out (rate limit or network issue)")
except Exception as e:
    print(f"Geocoding error: {e}")
```

---

## Testing

```python
import unittest
from app.core.location_tracker import LocationTracker

class TestLocationTracker(unittest.TestCase):
    def setUp(self):
        self.tracker = LocationTracker()
    
    def test_encryption_decryption(self):
        """Test location encryption cycle."""
        location = {"latitude": 40.7128, "longitude": -74.0060}
        encrypted = self.tracker.encrypt_location(location)
        decrypted = self.tracker.decrypt_location(encrypted)
        self.assertEqual(decrypted, location)
    
    def test_get_location_from_ip(self):
        """Test IP geolocation."""
        location = self.tracker.get_location_from_ip()
        if location:  # May fail in test environment
            self.assertIn("latitude", location)
            self.assertIn("longitude", location)
            self.assertEqual(location["source"], "ip")
    
    def test_save_load_history(self):
        """Test location history persistence."""
        location = {"latitude": 40.7128, "longitude": -74.0060, "timestamp": "2026-04-20T14:00:00"}
        self.tracker.save_location_history("test_user", location)
        history = self.tracker.get_location_history("test_user")
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["latitude"], 40.7128)
        
        # Cleanup
        self.tracker.clear_location_history("test_user")
```

---

## Configuration

```bash
# Environment variables
export FERNET_KEY="your-base64-fernet-key"  # Encryption key

# Nominatim configuration (optional)
export NOMINATIM_USER_AGENT="project-ai-assistant"  # Custom user agent
export NOMINATIM_TIMEOUT=10  # Geocoding timeout (seconds)

# IP geolocation API (optional)
export IPAPI_KEY="your-api-key"  # For paid tier (higher rate limits)
```

---

## Troubleshooting

### "Request to IP geolocation API timed out"
```python
# Increase timeout or retry
tracker.get_location_from_ip()  # Default: 10 seconds

# Or use alternative API
# https://ipgeolocation.io/
# https://ip-api.com/
```

### "Geocoding service timed out"
```python
# Nominatim rate limit: 1 request/second
# Add delay between requests
import time
location1 = tracker.get_location_from_coords(40.7128, -74.0060)
time.sleep(1)  # Wait 1 second
location2 = tracker.get_location_from_coords(34.0522, -118.2437)
```

### "InvalidToken: Decryption failed"
```python
# Key mismatch - verify FERNET_KEY
print(os.getenv("FERNET_KEY"))

# Or regenerate key (loses existing history)
from cryptography.fernet import Fernet
new_key = Fernet.generate_key()
tracker = LocationTracker(encryption_key=new_key)
```

---

**Last Updated:** 2026-04-20  
**Module Version:** 1.0.0  
**Author:** AGENT-036 (Data & Infrastructure Documentation Specialist)
