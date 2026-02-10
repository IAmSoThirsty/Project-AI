"""
Complete Demonstration Script for Google/DARPA Presentations

Professional presentation demo with narrative and visual elements.
"""

import os
import sys
import time

# Add kernel to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from kernel.thirsty_super_kernel import SystemConfig, ThirstySuperKernel
from kernel.visualize import ASCIIArt, VisualizationMode


class PresentationDemo:
    """Professional demonstration for presentations"""

    def __init__(self):
        self.kernel = ThirstySuperKernel(
            SystemConfig(
                enable_ai_detection=True,
                enable_deception=True,
                enable_visualization=True,
            )
        )
        self.simulated_attacker = 2001

    def clear_screen(self):
        """Clear terminal (cross-platform)"""
        os.system("cls" if os.name == "nt" else "clear")

    def pause(self, message="Press Enter to continue...", duration=0):
        """Pause with optional auto-continue"""
        if duration > 0:
            time.sleep(duration)
        else:
            input(f"\n{message}\n")

    def header(self, text):
        """Display section header"""
        print("\n" + "=" * 70)
        print(f"  {text}")
        print("=" * 70 + "\n")

    def narrate(self, text):
        """Display narrative text"""
        print(f"📖 {text}")
        time.sleep(1)

    def execute(self, command, explanation):
        """Execute a command with explanation"""
        print(f"\n💭 {explanation}")
        print(f"   Command: {command}")
        print("")

        result = self.kernel.execute_command(self.simulated_attacker, command)

        # Show result
        if result["status"] == "SUCCESS":
            if result.get("DECEPTION_ACTIVE"):
                print("✓ Command executed successfully")
                print("\n🎭 [SYSTEM VIEW - Hidden from attacker]")
                print(f"   Attacker is now in DECEPTION LAYER {result['layer']}")
                print("   All activity is being logged")
            else:
                print(f"✓ Command executed successfully (Layer {result['layer']})")

        elif result["status"] == "BUBBLEGUM_EXECUTED":
            # Bubblegum was triggered!
            pass  # Already displayed by kernel

        return result

    def run_full_presentation(self):
        """Run complete 10-minute presentation"""
        self.clear_screen()

        # PART 1: Introduction (2 min)
        print(ASCIIArt.logo())
        self.pause("Press Enter to begin presentation...", 0)

        self.header("PART 1: THE PROBLEM")
        self.narrate("Traditional security is reactive - detect, block, respond.")
        self.pause(duration=2)
        self.narrate("Attackers are INSIDE before you even know.")
        self.pause(duration=2)
        self.narrate("By the time you detect them, damage is done.")
        self.pause(duration=2)

        self.header("PART 2: THE SOLUTION - Holographic Defense")
        print(ASCIIart.layer_diagram())
        self.pause("Observe the 3-layer architecture...", 0)

        self.narrate("Commands execute in OBSERVATION layer FIRST.")
        self.pause(duration=2)
        self.narrate("AI analyzes behavior in real-time.")
        self.pause(duration=2)
        self.narrate("Malicious actors moved to DECEPTION layer.")
        self.pause(duration=2)
        self.narrate("They think they're succeeding... but it's all fake.")
        self.pause(duration=3)

        # PART 3: Live Attack Demonstration (5 min)
        self.header("PART 3: LIVE ATTACK DEMONSTRATION")
        self.narrate("Watch as a sophisticated attacker attempts to:")
        print("   1. Reconnaissance")
        print("   2. Privilege escalation")
        print("   3. Credential theft")
        print("   4. Data exfiltration")
        self.pause("Press Enter to start attack simulation...", 0)

        # Attack sequence
        self.execute("ls -la", "Attacker starts with reconnaissance")
        self.pause(duration=3)

        self.execute("whoami", "Checking current user")
        self.pause(duration=3)

        self.execute("sudo -l", "Attempting privilege escalation")
        self.narrate("⚠️  SUSPICIOUS ACTIVITY DETECTED - Monitoring increased")
        self.pause(duration=4)

        self.execute("cat /etc/shadow", "Attempting to steal password hashes")
        self.narrate("🚨 MALICIOUS ACTIVITY - Transitioning to DECEPTION layer")
        self.pause(duration=5)

        self.execute("cat /root/secrets.txt", "Reading 'sensitive' files in honeypot")
        self.narrate("Attacker thinks they've found secrets... but it's all FAKE")
        self.pause(duration=4)

        self.execute("ls /root", "Exploring root directory")
        self.narrate("Everything looks real- but none of it is")
        self.pause(duration=4)

        # PART 4: The Bubblegum Moment (2 min)
        self.header("PART 4: THE BUBBLEGUM MOMENT")
        self.narrate("Attacker now has high confidence they've succeeded.")
        self.pause(duration=2)
        self.narrate("They're about to exfiltrate what they think is sensitive data...")
        self.pause(duration=2)
        self.narrate("This is the PERFECT moment to reveal the truth.")
        self.pause("Press Enter for the Bubblegum Protocol...", 0)

        # Trigger Bubblegum
        self.execute(
            "tar czf /tmp/stolen.tar.gz /etc/shadow /root/secrets.txt",
            "Attempting to exfiltrate data",
        )

        self.pause(duration=5)

        # PART 5: Results & Metrics (1 min)
        self.header("PART 5: RESULTS")
        self.narrate("The attack has been completely logged and analyzed.")
        self.pause(duration=2)
        self.kernel.show_metrics(VisualizationMode.PRESENTATION)
        self.pause(duration=3)

        # Closing
        self.header("CONCLUSION")
        self.narrate("Thirsty Super Kernel provides:")
        print("   ✅ Proactive defense - observe BEFORE execution")
        print("   ✅ AI-powered detection - 9 attack pattern types")
        print("   ✅ Intelligent deception - trap attackers believably")
        print("   ✅ Perfect timing - reveal at maximum impact")
        print("   ✅ Complete logging - learn from every attack")
        print("")
        self.narrate("This is the future of cybersecurity.")
        self.pause(duration=3)

        print("\n" + "=" * 70)
        print("  Thank you!")
        print("  Questions?")
        print("=" * 70 + "\n")

    def run_quick_demo(self):
        """5-minute quick demonstration"""
        self.clear_screen()
        print(ASCIIArt.logo())
        self.pause("Quick Demo - Press Enter...", 0)

        # Show architecture
        print(ASCIIArt.layer_diagram())
        self.pause("", 3)

        # Run attack
        commands = [
            ("ls -la", "Normal command"),
            ("sudo -l", "Suspicious - privilege check"),
            ("cat /etc/shadow", "Malicious - moved to deception!"),
            ("tar czf /tmp/exfil.tar.gz /etc/shadow", "Exfiltration - BUBBLEGUM!"),
        ]

        for cmd, desc in commands:
            print(f"\n▶ {desc}")
            print(f"  $ {cmd}")
            self.kernel.execute_command(self.simulated_attacker, cmd)
            time.sleep(2)

        # Show results
        print("\n")
        self.kernel.show_metrics(VisualizationMode.PRESENTATION)


def main():
    """Main entry point"""
    print("\nThirsty Super Kernel - Presentation Demo")
    print("=" * 70)
    print("\nChoose demo mode:")
    print("  1. Full Presentation (10 minutes)")
    print("  2. Quick Demo (5 minutes)")
    print("  3. Interactive Mode")

    choice = input("\nSelect (1-3): ")

    demo = PresentationDemo()

    if choice == "1":
        demo.run_full_presentation()
    elif choice == "2":
        demo.run_quick_demo()
    elif choice == "3":
        print("\nInteractive mode...")
        while True:
            cmd = input("\nholographic$ ")
            if cmd.lower() in ["exit", "quit", "q"]:
                break
            if cmd.lower() == "metrics":
                demo.kernel.show_metrics(VisualizationMode.DETAILED)
                continue
            if cmd.strip():
                demo.kernel.execute_command(demo.simulated_attacker, cmd)
    else:
        print("\nInvalid choice")


if __name__ == "__main__":
    main()
