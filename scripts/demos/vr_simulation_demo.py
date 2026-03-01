"""
VR Backend Simulation Demo
Simulates the communication between the VR Bridge and the AI Core.
"""

import json
import time
import uuid
from datetime import datetime


class MockVRBridge:
    def __init__(self):
        self.connected = False
        print("[SYSTEM] Initializing VR Bridge Client...")
        time.sleep(1)
        self.connected = True
        print("[SYSTEM] Connected to AI Core (localhost:5000) ✓")

    def send_user_input(self, user_id, text, role="guest"):
        print(f"\n[USER:{user_id}] '{text}'")
        self._process_request(user_id, text, role)

    def _process_request(self, user_id, text, role):
        print(f"[AI CORE] processing intent for role='{role}'...")
        time.sleep(1)

        # Simulate Logic
        if "light" in text.lower():
            self._trigger_action(
                "ChangeLighting", {"intensity": 1.0, "color": "WarmWhite"}
            )
            self._ai_respond("I've adjusted the lighting for you.")
        elif "hello" in text.lower():
            self._trigger_action("UpdateEmotion", {"state": "Happy", "intensity": 0.8})
            self._ai_respond(f"Hello {user_id}. Systems are online.")
        elif "genesis" in text.lower():
            self._run_genesis(user_id)
        else:
            self._trigger_action("Listen", {"state": "Active"})
            self._ai_respond("I heard you, but I'm not sure what to do with that yet.")

    def _trigger_action(self, action_type, params):
        packet = {
            "id": str(uuid.uuid4())[:8],
            "timestamp": datetime.now().isoformat(),
            "type": action_type,
            "params": params,
        }
        print(f"[VR BRIDGE] >> EXECUTING: {json.dumps(packet, indent=2)}")

    def _ai_respond(self, text):
        print(f'[AI VOICE] "{text}"')

    def _run_genesis(self, user_id):
        print(f"\n[GENESIS] Initiating Genesis Sequence for {user_id}...")
        stages = [
            ("OrbForming", 1),
            ("SubsystemsIgniting", 1),
            ("PresenceStabilizing", 1),
            ("RoomAwakening", 1),
            ("Acknowledgement", 1),
        ]

        for stage, duration in stages:
            print(f"[GENESIS] > Stage: {stage}...")
            time.sleep(duration)
            if stage == "OrbForming":
                self._trigger_action("SpawnObject", {"id": "AI_Orb", "scale": 0.1})
            elif stage == "RoomAwakening":
                self._trigger_action("ChangeLighting", {"room": "All", "state": "On"})

        print("[GENESIS] Sequence Complete. AI is present.\n")


def run_demo():
    bridge = MockVRBridge()

    # Scene 1: First Login (Genesis)
    print("\n--- SCENE 1: FIRST LOGIN ---")
    bridge.send_user_input("GuestUser", "System start genesis", role="guest")

    # Scene 2: Interaction
    print("\n--- SCENE 2: INTERACTION ---")
    bridge.send_user_input("GuestUser", "Hello there!")
    time.sleep(1)
    bridge.send_user_input("GuestUser", "Please turn on the lights.")

    print("\n[SYSTEM] Simulation Complete.")


if __name__ == "__main__":
    run_demo()
