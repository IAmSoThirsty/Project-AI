# Location Services Integration (IP Geolocation & GPS)

## Overview
Project-AI integrates with IP geolocation services and GPS coordinates for emergency alert location tracking via the LocationTracker class (src/app/core/location_tracker.py).

## Providers
- **IP Geolocation**: ipapi.co (free tier: 1,500 requests/day)
- **Reverse Geocoding**: Nominatim/OpenStreetMap (geopy library)
- **Encryption**: Fernet symmetric encryption for location history

## Configuration
`ash
FERNET_KEY=<generated_key>  # For location history encryption
`

## Implementation
`python
from app.core.location_tracker import LocationTracker
from cryptography.fernet import Fernet

tracker = LocationTracker(encryption_key=os.getenv('FERNET_KEY'))

# Get location from IP
location = tracker.get_location_from_ip()
# Returns: {'latitude', 'longitude', 'city', 'region', 'country', 'ip'}

# Get address from GPS coordinates
location = tracker.get_location_from_coords(40.7128, -74.0060)
# Returns: {'latitude', 'longitude', 'address', 'timestamp', 'source'}

# Save encrypted location history
tracker.save_location_history('username', location)

# Load location history (decrypted)
history = tracker.load_location_history('username')
`

## Security Features
- Encrypted storage with Fernet
- No location tracking without user consent
- Automatic location data expiration options

## References
- ipapi.co API: https://ipapi.co/api
- geopy: https://geopy.readthedocs.io
- Nominatim: https://nominatim.org


---

## Related Documentation

- **Relationship Map**: [[relationships\integrations\README.md]]
