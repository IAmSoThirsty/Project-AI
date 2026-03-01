"""
Rainbow CSV Visualizer
Reads a CSV file and converts rows into VR visual events (e.g., colored lights).
"""

import csv
import hashlib
import json
import time
from pathlib import Path

# Real Bridge logic
import requests

API_URL = "http://localhost:8001/vr/command"


def send_vr_action(action_type, params):
    payload = {"type": action_type, "params": params}
    try:
        # Print for local debug
        print(f"[VR BRIDGE] >> EXECUTING: {json.dumps(payload)}")

        # Send to actual backend
        response = requests.post(API_URL, json=payload, timeout=2)
        response.raise_for_status()
    except Exception as e:
        print(f"[WARN] Failed to send to VR Backend: {e}")


def string_to_color(text):
    """Generate a consistent hex color from a string."""
    hash_object = hashlib.md5(text.encode())
    hex_hash = hash_object.hexdigest()
    return f"#{hex_hash[:6]}"


def visualize_csv(file_path):
    print(f"--- RAINBOW CSV VISUALIZATION: {file_path} ---\n")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row in reader:
                # Extract interesting fields
                username = row.get("Username", "Unknown")
                computer = row.get("Computer Name", "Unknown")
                timestamp = row.get("Activated", "")

                # Generate visual logic
                color = string_to_color(username)

                print(
                    f"[DATA] Processing Activation: {username} on {computer} at {timestamp}"
                )

                # 1. Announce event
                send_vr_action(
                    "DisplayText",
                    {
                        "content": f"New Activation: {username}",
                        "position": "HUD",
                        "duration": 3.0,
                    },
                )

                # 2. Pulse Light based on user
                send_vr_action(
                    "ChangeLighting",
                    {
                        "color": color,
                        "intensity": 1.2,
                        "duration": 0.5,
                        "reason": f"Activation by {username}",
                    },
                )

                # 3. Spawn 'Data Orb'
                send_vr_action(
                    "SpawnObject", {"id": "DataOrb", "color": color, "label": computer}
                )

                print("")
                time.sleep(1.5)  # Pause for effect

    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
    except Exception as e:
        print(f"Error processing CSV: {e}")


if __name__ == "__main__":
    # Default to the user's downloaded file
    csv_path = r"c:\Users\Quencher\Downloads\activations.csv"
    visualize_csv(csv_path)
