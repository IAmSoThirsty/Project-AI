"""
Emergency alert system implementation.
"""

import json
import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class EmergencyAlert:
    def __init__(self, smtp_config=None):
        self.smtp_config = smtp_config or {
            "server": "smtp.gmail.com",
            "port": 587,
            "username": os.getenv("SMTP_USERNAME"),
            "password": os.getenv("SMTP_PASSWORD"),
        }
        self.emergency_contacts = {}
        self.load_contacts()

    def load_contacts(self):
        """Load emergency contacts from file"""
        if os.path.exists("emergency_contacts.json"):
            with open("emergency_contacts.json", "r") as f:
                self.emergency_contacts = json.load(f)

    def save_contacts(self):
        """Save emergency contacts to file"""
        with open("emergency_contacts.json", "w") as f:
            json.dump(self.emergency_contacts, f)

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
                    (f"Longitude: " f"{location_data.get('longitude')}"),
                    (f"Address: " f"{location_data.get('address', 'Not available')}"),
                    (f"City: " f"{location_data.get('city', 'Not available')}"),
                    (f"Region: " f"{location_data.get('region', 'Not available')}"),
                    (f"Country: " f"{location_data.get('country', 'Not available')}"),
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
        """Log emergency alert details"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "username": username,
            "location_data": location_data,
            "message": message,
        }

        filename = f"emergency_alerts_{username}.json"
        logs = []

        if os.path.exists(filename):
            with open(filename, "r") as f:
                logs = json.load(f)

        logs.append(log_entry)

        with open(filename, "w") as f:
            json.dump(logs, f)

    def get_alert_history(self, username):
        """Get history of emergency alerts for a user"""
        filename = f"emergency_alerts_{username}.json"
        if os.path.exists(filename):
            with open(filename, "r") as f:
                return json.load(f)
        return []
