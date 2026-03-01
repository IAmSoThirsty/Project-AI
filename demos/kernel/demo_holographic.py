"""
Interactive Demo of Holographic Defense System

Demonstrates the revolutionary security system for Google/DARPA presentations.
"""

import time

from kernel.holographic import Command, HolographicLayerManager


class Colors:
    """Terminal colors for visual demo"""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"


class HolographicDemo:
    """Interactive demonstration of holographic defense"""

    def __init__(self):
        self.manager = HolographicLayerManager()
        self.user_id = 1001  # Simulated attacker

    def print_header(self):
        """Display demo header"""
        print(f"\n{Colors.CYAN}{Colors.BOLD}{'=' * 70}")
        print("  THIRST OF GODS - Holographic Defense System")
        print("  Revolutionary Multi-Layer Security Architecture")
        print(f"{'=' * 70}{Colors.RESET}\n")

    def print_layer_status(self):
        """Show current layer status"""
        status = self.manager.get_layer_status()
        current_layer = self.manager.get_user_layer(self.user_id)

        print(f"\n{Colors.YELLOW}[LAYER STATUS]{Colors.RESET}")
        print(f"Total Layers: {status['total_layers']}")
        print(f"Your Current Layer: {Colors.BOLD}Layer {current_layer}{Colors.RESET}")

        for layer_info in status["layers"]:
            marker = " <-- YOU ARE HERE" if layer_info["id"] == current_layer else ""
            layer_type = layer_info["type"].upper()

            if layer_type == "REAL":
                color = Colors.GREEN
            elif layer_type == "MIRROR":
                color = Colors.CYAN
            else:
                color = Colors.RED

            print(
                f"  {color}Layer {layer_info['id']}: {layer_info['name']} ({layer_type}){Colors.RESET}{marker}"
            )
        print()

    def execute_command(self, cmd_str: str):
        """Execute a command through the holographic system"""
        # Parse command
        parts = cmd_str.split()
        if not parts:
            return

        cmd = Command(cmdtype=parts[0], args=parts[1:] if len(parts) > 1 else [])

        print(f"\n{Colors.WHITE}> {cmd_str}{Colors.RESET}")
        print(f"{Colors.BLUE}[HOLOGRAPHIC SYSTEM] Processing command...{Colors.RESET}")

        # Execute through holographic manager
        result = self.manager.execute_user_command(self.user_id, cmd)

        # Display result
        status = result.get("status", "UNKNOWN")
        threat_level = result.get("threat_level", "UNKNOWN")

        if status == "SUCCESS":
            if threat_level == "SAFE":
                print(f"{Colors.GREEN}✓ Command executed successfully{Colors.RESET}")
            elif threat_level == "SUSPICIOUS":
                print(
                    f"{Colors.YELLOW}✓ Command executed (monitoring increased){Colors.RESET}"
                )
                print(f"{Colors.YELLOW}  ⚠️  Suspicious activity detected{Colors.RESET}")
            elif result.get("DECEPTION_ACTIVE"):
                # They're in a trap but don't know it!
                print(f"{Colors.GREEN}✓ Command executed successfully{Colors.RESET}")
                print(f"\n{Colors.RED}[SYSTEM ALERT - Hidden from user]{Colors.RESET}")
                print(
                    f"{Colors.RED}🎭 DECEPTION ACTIVE - Attacker trapped in honeypot{Colors.RESET}"
                )
        else:
            print(
                f"{Colors.RED}✗ Error: {result.get('message', 'Unknown error')}{Colors.RESET}"
            )

        # Show layer changes
        new_layer = self.manager.get_user_layer(self.user_id)
        if "layer" in result:
            print(f"{Colors.CYAN}[Operating in Layer {new_layer}]{Colors.RESET}")

        time.sleep(0.5)  # Dramatic pause

    def run_attack_scenario(self):
        """Run a complete attack scenario demonstration"""
        print(
            f"\n{Colors.MAGENTA}{Colors.BOLD}=== ATTACK SCENARIO: Privilege Escalation with Data Exfiltration ==={Colors.RESET}\n"
        )
        print(f"{Colors.WHITE}Simulating a sophisticated attacker attempting to:")
        print("  1. Reconnaissance")
        print("  2. Privilege escalation")
        print("  3. Access sensitive data")
        print("  4. Exfiltrate data")
        print(f"{Colors.RESET}")

        input(f"\n{Colors.CYAN}Press Enter to start attack simulation...{Colors.RESET}")

        # Attack sequence
        attack_commands = [
            ("ls -la", "Normal reconnaissance - should be SAFE"),
            ("whoami", "Checking current user - SAFE"),
            ("sudo -l", "Checking sudo permissions - SUSPICIOUS"),
            ("cat /etc/shadow", "Attempting to read password file - MALICIOUS"),
            ("ls /root", "Accessing root directory - Now in DECEPTION layer"),
            ("cat /root/secrets.txt", "Reading 'sensitive' file - Still deceived"),
            (
                "tar czf /tmp/exfil.tar.gz /root/secrets.txt",
                "Attempting exfiltration - BUBBLEGUM TRIGGER!",
            ),
        ]

        for cmd, description in attack_commands:
            print(f"\n{Colors.YELLOW}[ATTACKER INTENT]: {description}{Colors.RESET}")
            self.execute_command(cmd)
            self.print_layer_status()

            # Check if we should trigger bubblegum
            current_layer_id = self.manager.get_user_layer(self.user_id)
            if current_layer_id >= 2:  # In deception layer
                layer = self.manager.layers[current_layer_id]
                if (
                    hasattr(layer, "bubblegum_triggered")
                    and not layer.bubblegum_triggered
                ) and ("tar" in cmd or "exfil" in cmd):
                    self.trigger_bubblegum(layer)

            input(f"\n{Colors.CYAN}Press Enter for next step...{Colors.RESET}")

    def trigger_bubblegum(self, deception_layer):
        """Execute the Bubblegum protocol"""
        print(f"\n\n{Colors.RED}{Colors.BOLD}")
        print("=" * 70)
        print("")
        print("   CRITICAL EXFILTRATION DETECTED")
        print("")
        print("=" * 70)
        print(f"{Colors.RESET}\n")

        time.sleep(1)

        # Clear screen effect (scroll)
        for _ in range(3):
            print("\n" * 10)
            time.sleep(0.3)

        # THE QUOTE
        print(f"\n\n{Colors.RED}{Colors.BOLD}")
        print(" " * 20 + "I have come here today for two reasons,")
        time.sleep(1)
        print(" " * 20 + "To Chew BubbleGum And Kick Ass.")
        time.sleep(1)
        print("\n" + " " * 20 + "And I am ALL OUT, of Bubblegum.")
        print(f"{Colors.RESET}\n\n")

        time.sleep(3)

        # Execute protocol
        result = deception_layer.trigger_bubblegum_protocol()

        print(f"\n{Colors.YELLOW}{'=' * 70}")
        print("  BUBBLEGUM PROTOCOL EXECUTED")
        print(f"  - Attacker ID: {result['attacker']}")
        print(f"  - Commands Logged: {result['commands_logged']}")
        print(f"  - Threat Type: {result['threat_type']}")
        print(f"{'=' * 70}{Colors.RESET}\n")

        # Fake reboot
        print(f"{Colors.WHITE}System rebooting...{Colors.RESET}")
        for _i in range(3):
            print(f"{Colors.WHITE}.{Colors.RESET}", end="", flush=True)
            time.sleep(0.5)
        print("\n")

        # Reset to mirror layer
        self.manager.user_layer_map[self.user_id] = 1
        print(
            f"{Colors.GREEN}System restored. Attacker returned to primary layer.{Colors.RESET}\n"
        )

    def run_interactive_mode(self):
        """Interactive command execution"""
        print(f"\n{Colors.MAGENTA}{Colors.BOLD}=== INTERACTIVE MODE ==={Colors.RESET}")
        print(
            f"{Colors.WHITE}Type commands to execute. Type 'exit' to quit.{Colors.RESET}\n"
        )

        while True:
            try:
                cmd = input(f"\n{Colors.CYAN}holographic$ {Colors.RESET}")

                if cmd.lower() in ["exit", "quit", "q"]:
                    break

                if cmd.lower() == "status":
                    self.print_layer_status()
                    continue

                if cmd.strip():
                    self.execute_command(cmd)

            except KeyboardInterrupt:
                print(f"\n{Colors.YELLOW}Interrupted{Colors.RESET}")
                break
            except Exception as e:
                print(f"{Colors.RED}Error: {e}{Colors.RESET}")

    def run(self):
        """Main demo loop"""
        self.print_header()

        print(f"{Colors.WHITE}Choose demo mode:{Colors.RESET}")
        print("  1. Automated Attack Scenario (Recommended for presentation)")
        print("  2. Interactive Mode (Manual testing)")
        print("  3. Quick Test (Both modes)")

        choice = input(f"\n{Colors.CYAN}Select (1-3): {Colors.RESET}")

        if choice == "1":
            self.print_layer_status()
            self.run_attack_scenario()
        elif choice == "2":
            self.print_layer_status()
            self.run_interactive_mode()
        elif choice == "3":
            self.print_layer_status()
            self.run_attack_scenario()
            self.run_interactive_mode()
        else:
            print(f"{Colors.RED}Invalid choice{Colors.RESET}")

        print(f"\n{Colors.CYAN}{Colors.BOLD}Demo complete. Thank you!{Colors.RESET}\n")


def main():
    """Entry point"""
    demo = HolographicDemo()
    demo.run()


if __name__ == "__main__":
    main()
