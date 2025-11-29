"""
Location tracking and management system.
"""
import json
import requests
from datetime import datetime
from cryptography.fernet import Fernet
import os
from dotenv import load_dotenv
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from app.core.network_utils import is_online


class LocationTracker:
    def __init__(self, encryption_key=None):
        # Prefer explicit argument, then FERNET_KEY env var, then generate a new key
        # Load .env so environment keys are available
        load_dotenv()
        key = encryption_key or os.getenv('FERNET_KEY')
        if key:
            if isinstance(key, str):
                key = key.encode()
            self.encryption_key = key
        else:
            self.encryption_key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)
        self.geolocator = Nominatim(user_agent="ai_assistant")
        self.active = False
        self._last_known_location = None
        self._offline_mode = False

    @property
    def offline_mode(self) -> bool:
        """Check if location tracking is in offline mode."""
        return self._offline_mode

    def encrypt_location(self, location_data):
        """Encrypt location data"""
        try:
            json_data = json.dumps(location_data)
            encrypted_data = self.cipher_suite.encrypt(json_data.encode())
            return encrypted_data
        except Exception as encryption_error:
            print(f"Encryption error: {str(encryption_error)}")
            return None

    def decrypt_location(self, encrypted_data):
        """Decrypt location data"""
        try:
            decrypted_data = self.cipher_suite.decrypt(encrypted_data)
            return json.loads(decrypted_data.decode())
        except Exception as decryption_error:
            print(f"Decryption error: {str(decryption_error)}")
            return None

    def get_location_from_ip(self):
        """Get location from IP address.

        Returns cached location when offline.
        """
        # Check if we're online
        if not is_online(timeout=2.0):
            self._offline_mode = True
            # Return last known location with offline indicator
            if self._last_known_location:
                offline_location = self._last_known_location.copy()
                offline_location['source'] = 'cached'
                offline_location['offline'] = True
                offline_location['timestamp'] = datetime.now().isoformat()
                return offline_location
            return self._get_offline_placeholder()

        try:
            response = requests.get('https://ipapi.co/json/', timeout=10)
            if response.status_code == 200:
                data = response.json()
                location = {
                    'latitude': data.get('latitude'),
                    'longitude': data.get('longitude'),
                    'city': data.get('city'),
                    'region': data.get('region'),
                    'country': data.get('country_name'),
                    'ip': data.get('ip'),
                    'timestamp': datetime.now().isoformat(),
                    'source': 'ip',
                    'offline': False
                }
                # Cache for offline use
                self._last_known_location = location
                self._offline_mode = False
                return location
            return self._handle_ip_api_failure()
        except Exception as ip_lookup_error:
            print(f"Error getting location from IP: {str(ip_lookup_error)}")
            return self._handle_ip_api_failure()

    def _handle_ip_api_failure(self):
        """Handle IP API failure by returning cached or placeholder location."""
        self._offline_mode = True
        if self._last_known_location:
            offline_location = self._last_known_location.copy()
            offline_location['source'] = 'cached'
            offline_location['offline'] = True
            offline_location['timestamp'] = datetime.now().isoformat()
            return offline_location
        return self._get_offline_placeholder()

    def _get_offline_placeholder(self) -> dict:
        """Return a placeholder location for offline mode."""
        return {
            'latitude': None,
            'longitude': None,
            'city': 'Unknown (Offline)',
            'region': 'Unknown',
            'country': 'Unknown',
            'ip': None,
            'timestamp': datetime.now().isoformat(),
            'source': 'offline',
            'offline': True
        }

    def get_location_from_coords(self, latitude, longitude):
        """Get location details from coordinates.

        Returns basic coordinate info when offline.
        """
        # Check if we're online for reverse geocoding
        if not is_online(timeout=2.0):
            self._offline_mode = True
            return {
                'latitude': latitude,
                'longitude': longitude,
                'address': 'Address unavailable (offline)',
                'timestamp': datetime.now().isoformat(),
                'source': 'gps',
                'offline': True
            }

        try:
            location = self.geolocator.reverse(f"{latitude}, {longitude}")
            if location:
                result = {
                    'latitude': latitude,
                    'longitude': longitude,
                    'address': location.address,
                    'timestamp': datetime.now().isoformat(),
                    'source': 'gps',
                    'offline': False
                }
                self._offline_mode = False
                return result
            return None
        except GeocoderTimedOut:
            print("Geocoding service timed out")
            self._offline_mode = True
            return {
                'latitude': latitude,
                'longitude': longitude,
                'address': 'Address unavailable (timeout)',
                'timestamp': datetime.now().isoformat(),
                'source': 'gps',
                'offline': True
            }
        except Exception as geocode_error:
            print(f"Error getting location from coordinates: {str(geocode_error)}")
            self._offline_mode = True
            return {
                'latitude': latitude,
                'longitude': longitude,
                'address': 'Address unavailable (error)',
                'timestamp': datetime.now().isoformat(),
                'source': 'gps',
                'offline': True
            }

    def save_location_history(self, username, location_data):
        """Save encrypted location history"""
        filename = f"location_history_{username}.json"
        history = []

        if os.path.exists(filename):
            with open(filename, 'r') as f:
                history = json.load(f)

        encrypted_location = self.encrypt_location(location_data)
        if encrypted_location:
            history.append(encrypted_location.decode())  # Convert bytes to string for JSON

        with open(filename, 'w') as f:
            json.dump(history, f)

    def get_location_history(self, username):
        """Get decrypted location history"""
        filename = f"location_history_{username}.json"
        if not os.path.exists(filename):
            return []

        with open(filename, 'r') as f:
            history = json.load(f)

        decrypted_history = []
        for encrypted_location in history:
            location_data = self.decrypt_location(encrypted_location.encode())
            if location_data:
                decrypted_history.append(location_data)

        # Update last known location from history
        if decrypted_history:
            self._last_known_location = decrypted_history[-1]

        return decrypted_history

    def get_last_known_location(self, username: str = None) -> dict | None:
        """Get the last known location (from memory or history).

        Useful for offline mode when current location cannot be determined.
        """
        if self._last_known_location:
            return self._last_known_location

        if username:
            history = self.get_location_history(username)
            if history:
                self._last_known_location = history[-1]
                return self._last_known_location

        return None

    def clear_location_history(self, username):
        """Clear location history for a user"""
        filename = f"location_history_{username}.json"
        if os.path.exists(filename):
            os.remove(filename)
            return True
        return False
