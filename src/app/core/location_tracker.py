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

    def encrypt_location(self, location_data):
        """Encrypt location data"""
        try:
            json_data = json.dumps(location_data)
            encrypted_data = self.cipher_suite.encrypt(json_data.encode())
            return encrypted_data
        except Exception as e:
            print(f"Encryption error: {str(e)}")
            return None

    def decrypt_location(self, encrypted_data):
        """Decrypt location data"""
        try:
            decrypted_data = self.cipher_suite.decrypt(encrypted_data)
            return json.loads(decrypted_data.decode())
        except Exception as e:
            print(f"Decryption error: {str(e)}")
            return None

    def get_location_from_ip(self):
        """Get location from IP address"""
        try:
            response = requests.get('https://ipapi.co/json/', timeout=10)
            if response.status_code == 200:
                data = response.json()
                return {
                    'latitude': data.get('latitude'),
                    'longitude': data.get('longitude'),
                    'city': data.get('city'),
                    'region': data.get('region'),
                    'country': data.get('country_name'),
                    'ip': data.get('ip'),
                    'timestamp': datetime.now().isoformat(),
                    'source': 'ip'
                }
            return None
        except Exception as e:
            print(f"Error getting location from IP: {str(e)}")
            return None

    def get_location_from_coords(self, latitude, longitude):
        """Get location details from coordinates"""
        try:
            location = self.geolocator.reverse(f"{latitude}, {longitude}")
            if location:
                return {
                    'latitude': latitude,
                    'longitude': longitude,
                    'address': location.address,
                    'timestamp': datetime.now().isoformat(),
                    'source': 'gps'
                }
            return None
        except GeocoderTimedOut:
            print("Geocoding service timed out")
            return None
        except Exception as e:
            print(f"Error getting location from coordinates: {str(e)}")
            return None

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
            # Convert string back to bytes
            location_data = self.decrypt_location(encrypted_location.encode())
            if location_data:
                decrypted_history.append(location_data)

        return decrypted_history

    def clear_location_history(self, username):
        """Clear location history for a user"""
        filename = f"location_history_{username}.json"
        if os.path.exists(filename):
            os.remove(filename)
            return True
        return False
