# Location Tracking Data Model

**Module**: `src/app/core/location_tracker.py` [[src/app/core/location_tracker.py]]  
**Storage**: `location_history_{username}.json` (encrypted)  
**Persistence**: Encrypted JSON with Fernet  
**Schema Version**: 1.0

---

## Overview

Location tracking system with encrypted history storage, IP geolocation, GPS coordinate lookup, and privacy-focused design.

### Key Features

- **Dual Source Support**: IP geolocation + GPS coordinates
- **Encrypted Storage**: Fernet cipher for location history
- **Privacy-First**: User-controlled activation
- **History Management**: Clear and retrieve encrypted history
- **Timeout Protection**: 10-second timeout for API calls

---

## Schema Structure

### Location Entry (IP-Based)

```json
{
  "latitude": 37.7749,
  "longitude": -122.4194,
  "city": "San Francisco",
  "region": "California",
  "country": "United States",
  "ip": "203.0.113.42",
  "timestamp": "2024-01-20T14:30:00Z",
  "source": "ip"
}
```

### Location Entry (GPS-Based)

```json
{
  "latitude": 37.7749,
  "longitude": -122.4194,
  "address": "123 Market St, San Francisco, CA 94103, USA",
  "timestamp": "2024-01-20T14:30:00Z",
  "source": "gps"
}
```

### Location History File

**File**: `location_history_{username}.json`

**Format**: Array of **base64-encoded encrypted strings**

```json
[
  "gAAAAABl1Kj7X5Y...",  // Encrypted location entry 1
  "gAAAAABl1Kk2Z8A...",  // Encrypted location entry 2
  "gAAAAABl1Kl9B3C..."   // Encrypted location entry 3
]
```

---

## Field Specifications

### Common Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `latitude` | float | Yes | Latitude coordinate |
| `longitude` | float | Yes | Longitude coordinate |
| `timestamp` | string | Yes | ISO 8601 timestamp |
| `source` | string | Yes | "ip" or "gps" |

### IP-Based Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `city` | string | Yes | City name |
| `region` | string | Yes | State/province |
| `country` | string | Yes | Country name |
| `ip` | string | Yes | IP address |

### GPS-Based Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `address` | string | Yes | Full street address |

---

## Location Retrieval

### IP Geolocation

**API**: `https://ipapi.co/json/`

```python
def get_location_from_ip(self):
    """Get location from IP address using ipapi.co."""
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
                "source": "ip",
            }
        return None
    except requests.Timeout:
        logger.error("IP geolocation API timed out")
        return None
```

### GPS Coordinate Lookup

**Library**: `geopy.geocoders.Nominatim` (OpenStreetMap)

```python
from geopy.geocoders import Nominatim

def get_location_from_coords(self, latitude: float, longitude: float):
    """Get address from GPS coordinates using Nominatim."""
    try:
        location = self.geolocator.reverse(f"{latitude}, {longitude}")
        if location:
            return {
                "latitude": latitude,
                "longitude": longitude,
                "address": location.address,
                "timestamp": datetime.now().isoformat(),
                "source": "gps",
            }
        return None
    except GeocoderTimedOut:
        logger.error("Geocoding service timed out")
        return None
```

---

## Encryption System

### Initialization

```python
from cryptography.fernet import Fernet

# Key priority: argument > FERNET_KEY env var > generate new
key = encryption_key or os.getenv("FERNET_KEY")
if key:
    if isinstance(key, str):
        key = key.encode()
    self.encryption_key = key
else:
    self.encryption_key = Fernet.generate_key()

self.cipher_suite = Fernet(self.encryption_key)
```

### Encrypt Location

```python
def encrypt_location(self, location_data: dict) -> bytes | None:
    """Encrypt location data."""
    try:
        json_data = json.dumps(location_data)
        encrypted_data = self.cipher_suite.encrypt(json_data.encode())
        return encrypted_data
    except Exception as e:
        logger.error("Encryption error: %s", e)
        return None
```

### Decrypt Location

```python
def decrypt_location(self, encrypted_data: bytes) -> dict | None:
    """Decrypt location data."""
    try:
        decrypted_data = self.cipher_suite.decrypt(encrypted_data)
        return json.loads(decrypted_data.decode())
    except Exception as e:
        logger.error("Decryption error: %s", e)
        return None
```

---

## History Management

### Save Location History

```python
def save_location_history(self, username: str, location_data: dict):
    """Save encrypted location history."""
    filename = f"location_history_{username}.json"
    history = []
    
    # Load existing history
    if os.path.exists(filename):
        with open(filename) as f:
            history = json.load(f)
    
    # Encrypt and append
    encrypted_location = self.encrypt_location(location_data)
    if encrypted_location:
        # Convert bytes to base64 string for JSON
        history.append(encrypted_location.decode())
    
    # Save updated history
    with open(filename, "w") as f:
        json.dump(history, f)
```

### Get Location History

```python
def get_location_history(self, username: str) -> list[dict]:
    """Get decrypted location history."""
    filename = f"location_history_{username}.json"
    if not os.path.exists(filename):
        return []
    
    with open(filename) as f:
        history = json.load(f)
    
    decrypted_history = []
    for encrypted_location in history:
        # Convert base64 string back to bytes
        location_data = self.decrypt_location(encrypted_location.encode())
        if location_data:
            decrypted_history.append(location_data)
    
    return decrypted_history
```

### Clear Location History

```python
def clear_location_history(self, username: str) -> bool:
    """Clear location history for a user."""
    filename = f"location_history_{username}.json"
    if os.path.exists(filename):
        os.remove(filename)
        return True
    return False
```

---

## Usage Examples

### Track Current Location (IP)

```python
from app.core.location_tracker import LocationTracker

tracker = LocationTracker()
tracker.active = True

# Get location from IP
location = tracker.get_location_from_ip()
if location:
    print(f"City: {location['city']}")
    print(f"Coordinates: {location['latitude']}, {location['longitude']}")
    
    # Save to history
    tracker.save_location_history("alice", location)
```

### Track Location (GPS Coordinates)

```python
# User provides GPS coordinates
latitude = 37.7749
longitude = -122.4194

location = tracker.get_location_from_coords(latitude, longitude)
if location:
    print(f"Address: {location['address']}")
    
    # Save to history
    tracker.save_location_history("alice", location)
```

### View Location History

```python
history = tracker.get_location_history("alice")

for entry in history:
    print(f"[{entry['timestamp']}] {entry['source']}: {entry.get('city', entry.get('address'))}")
```

### Clear History (Privacy)

```python
# User requests data deletion
success = tracker.clear_location_history("alice")
if success:
    print("Location history cleared")
```

---

## Privacy & Security

### User Control

```python
# Location tracking is opt-in
tracker.active = False  # Default: disabled

# User must explicitly enable
tracker.active = True
```

### Data Minimization

**Only Store Essential Data**:
- ✅ Coordinates, city, timestamp
- ❌ Full street address (unless GPS-based)
- ❌ ISP information
- ❌ Network details

### Encryption Key Management

```bash
# .env
FERNET_KEY=<base64-encoded-32-byte-key>
```

**Best Practices**:
1. Use environment variable for key
2. Never commit key to version control
3. Rotate key periodically (requires decryption/re-encryption)

---

## GDPR Compliance

### Right to Access

```python
def export_location_data(self, username: str) -> dict:
    """Export all location data for user (GDPR compliance)."""
    history = self.get_location_history(username)
    return {
        "username": username,
        "location_history": history,
        "total_entries": len(history),
        "exported_at": datetime.now().isoformat()
    }
```

### Right to Erasure

```python
def delete_user_location_data(self, username: str) -> bool:
    """Delete all location data (GDPR right to erasure)."""
    return self.clear_location_history(username)
```

---

## Error Handling

### Timeout Protection

```python
# IP geolocation with timeout
response = requests.get("https://ipapi.co/json/", timeout=10)

# Geocoding with timeout
try:
    location = self.geolocator.reverse(f"{lat}, {lon}")
except GeocoderTimedOut:
    logger.error("Geocoding service timed out")
    return None
```

### Graceful Degradation

```python
def get_location_safe(self):
    """Get location with graceful fallback."""
    # Try IP-based first
    location = self.get_location_from_ip()
    if location:
        return location
    
    # Fallback: Return None (no location)
    logger.warning("Location tracking failed")
    return None
```

---

## Testing Strategy

### Unit Tests

```python
def test_encrypt_decrypt_location():
    tracker = LocationTracker()
    
    location = {
        "latitude": 37.7749,
        "longitude": -122.4194,
        "city": "San Francisco"
    }
    
    encrypted = tracker.encrypt_location(location)
    decrypted = tracker.decrypt_location(encrypted)
    
    assert decrypted == location

def test_location_history():
    tracker = LocationTracker()
    
    location = {"latitude": 37.7749, "longitude": -122.4194}
    tracker.save_location_history("testuser", location)
    
    history = tracker.get_location_history("testuser")
    assert len(history) == 1
    
    tracker.clear_location_history("testuser")
    history = tracker.get_location_history("testuser")
    assert len(history) == 0
```

---

## Related Modules

| Module | Relationship |
|--------|-------------|
| `emergency_alert.py` | Uses location for emergency alerts |
| `data_persistence.py` | Provides encryption primitives |
| `cloud_sync.py` | Syncs location history across devices |

---

## Future Enhancements

1. **Geofencing**: Alert when user enters/exits defined areas
2. **Location Clustering**: Identify frequently visited locations
3. **Privacy Zones**: Exclude home/work locations from history
4. **Offline Mode**: Queue location updates when offline
5. **Battery-Aware Tracking**: Adjust frequency based on battery level

---

**Last Updated**: 2024-01-20  
**Schema Version**: 1.0  
**Maintainer**: Project-AI Core Team


---

## Related Documentation

- **Relationship Map**: [[relationships\data\README.md]]


---

## Source Code References

- **Primary Module**: [[src/app/core/location_tracker.py]]
