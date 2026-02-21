"""
Emergency alert system implementation.
"""

import json
import logging
import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.utils.path_validator import validate_path
from app.core.utils.secure_storage import SecureStorage

EMERGENCY_CONTACTS_FILE = "emergency_contacts.json"
logger = logging.getLogger(__name__)


class EmergencyAlert:
    def __init__(self, smtp_config=None):
        self.smtp_config = smtp_config or {
            "server": "smtp.gmail.com",
            "port": 587,
            "username": os.getenv("SMTP_USERNAME"),
            "password": os.getenv("SMTP_PASSWORD"),
        }
        self.emergency_contacts = {}
        self.storage = SecureStorage()
        self.contacts_file = (
            validate_path(EMERGENCY_CONTACTS_FILE, os.getcwd())
            or EMERGENCY_CONTACTS_FILE
        )
        self.load_contacts()

    def load_contacts(self):
        """Load emergency contacts from file (encrypted or plain)"""
        if not os.path.exists(self.contacts_file):
            return

        self.emergency_contacts = self.storage.load_encrypted_json(self.contacts_file)
        if self.emergency_contacts is None:
            # Migration
            try:
                with open(self.contacts_file) as f:
                    self.emergency_contacts = json.load(f)
                self.save_contacts()
            except Exception:
                self.emergency_contacts = {}

    def save_contacts(self):
        """Save emergency contacts to file securely"""
        try:
            self.storage.save_encrypted_json(
                self.contacts_file, self.emergency_contacts
            )
        except Exception as e:
            logger.error(f"Failed to save contacts securely: {e}")
            raise

    def add_emergency_contact(self, username, contact_info):
        """Add or update emergency contact for a user"""
        self.emergency_contacts[username] = contact_info
        self.save_contacts()

    def send_alert(self, username, location_data, message=None):
        """Send emergency alert to registered contacts"""
        if username not in self.emergency_contacts:
            return False, "No emergency contacts registered for user"

        contacts = self.emergency_contacts[username]

        try:
            # Create message
            msg = MIMEMultipart()
            msg["From"] = self.smtp_config["username"]
            msg["To"] = ", ".join(contacts["emails"])
            msg["Subject"] = f"EMERGENCY ALERT - {username}"

            # Create message body (built as lines to avoid long inline
            # literals)
            if not location_data:
                loc_text = "Location not available"
            else:
                loc_lines = [
                    f"Latitude: {location_data.get('latitude')}",
                    f"Longitude: {location_data.get('longitude')}",
                    f"Address: {location_data.get('address', 'Not available')}",
                    f"City: {location_data.get('city', 'Not available')}",
                    f"Region: {location_data.get('region', 'Not available')}",
                    f"Country: {location_data.get('country', 'Not available')}",
                ]
                loc_text = "\n".join(loc_lines)

            body_lines = [
                "EMERGENCY ALERT",
                "",
                f"User: {username}",
                f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "",
                "Location Information:",
                loc_text,
                "",
                "Additional Message:",
                message or "No additional message provided",
                "",
                (
                    "This is an automated emergency alert. Please attempt to "
                    "contact the user"
                ),
                "and alert appropriate authorities if necessary.",
            ]

            body = "\n".join(body_lines)

            msg.attach(MIMEText(body, "plain"))

            # Connect to SMTP server and send
            with smtplib.SMTP(
                self.smtp_config["server"], self.smtp_config["port"]
            ) as server:
                server.starttls()
                server.login(self.smtp_config["username"], self.smtp_config["password"])
                server.send_message(msg)

            # Log alert
            self.log_alert(username, location_data, message)
            return True, "Alert sent successfully"

        except Exception as e:
            return False, f"Error sending alert: {str(e)}"

    def log_alert(self, username, location_data, message):
        """Log emergency alert details securely"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "username": username,
            "location_data": location_data,
            "message": message,
        }

        filename = (
            validate_path(f"emergency_alerts_{username}.json", os.getcwd())
            or f"emergency_alerts_{username}.json"
        )

        # Load existing (encrypted or plain)
        logs = self.storage.load_encrypted_json(filename)
        if logs is None:
            if os.path.exists(filename):
                try:
                    with open(filename) as f:
                        logs = json.load(f)
                except Exception:
                    logs = []
            else:
                logs = []

        logs.append(log_entry)

        try:
            self.storage.save_encrypted_json(filename, logs)
        except Exception as e:
            logger.error(f"Failed to log alert securely: {e}")
            raise

    def get_alert_history(self, username):
        """Get history of emergency alerts for a user (securely)"""
        filename = (
            validate_path(f"emergency_alerts_{username}.json", os.getcwd())
            or f"emergency_alerts_{username}.json"
        )

        # Try encrypted first
        logs = self.storage.load_encrypted_json(filename)
        if logs is not None:
            return logs

        # Fallback to plain if it exists (migration)
        if os.path.exists(filename):
            try:
                with open(filename) as f:
                    return json.load(f)
            except Exception:
                return []
        return []
