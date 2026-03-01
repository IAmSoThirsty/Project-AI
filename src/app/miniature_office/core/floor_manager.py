"""
Multi-Language Floor Manager

Manages the spawning and communication with department floors
implemented in different programming languages.
"""

import json
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional


class FloorProcess:
    """Represents a running floor process"""

    def __init__(self, floor_number: int, language: str, process: subprocess.Popen):
        self.floor_number = floor_number
        self.language = language
        self.process = process

    def send_request(
        self, method: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Send a JSON-RPC request to the floor process"""
        request = {"method": method}
        if params:
            request["params"] = params

        request_json = json.dumps(request) + "\n"
        self.process.stdin.write(request_json.encode())
        self.process.stdin.flush()

        # Read response
        response_line = self.process.stdout.readline().decode().strip()
        return json.loads(response_line)

    def is_running(self) -> bool:
        """Check if the floor process is still running"""
        return self.process.poll() is None

    def stop(self):
        """Stop the floor process"""
        if self.is_running():
            self.process.stdin.close()
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()


class MultiLanguageFloorManager:
    """
    Manages multiple department floors implemented in different languages.

    Demonstrates "displayed and transparent Diversity flexibility" by:
    - Spawning floor processes in their native languages
    - Providing a unified interface for communication
    - Managing the lifecycle of multi-language floors
    """

    def __init__(self, floors_dir: str = "floors"):
        self.floors_dir = Path(floors_dir)
        self.active_floors: Dict[str, FloorProcess] = {}
        self.floor_configs = {
            "python": {
                "floor_number": 1,
                "executable": ["python3", "department_floor.py"],
                "path": self.floors_dir / "python",
            },
            "javascript": {
                "floor_number": 4,
                "executable": ["node", "department_floor.js"],
                "path": self.floors_dir / "javascript",
            },
            "rust": {
                "floor_number": 2,
                "executable": ["./target/debug/department_floor"],
                "path": self.floors_dir / "rust",
                "needs_build": True,
                "build_cmd": ["cargo", "build"],
            },
            "go": {
                "floor_number": 5,
                "executable": ["go", "run", "department_floor.go"],
                "path": self.floors_dir / "go",
            },
            "shell": {
                "floor_number": 7,
                "executable": ["bash", "department_floor.sh"],
                "path": self.floors_dir / "shell",
            },
        }

    def start_floor(self, language: str) -> bool:
        """Start a floor process for the given language"""
        if language in self.active_floors:
            print(f"Floor {language} is already running")
            return True

        config = self.floor_configs.get(language)
        if not config:
            print(f"No configuration found for language: {language}")
            return False

        floor_path = config["path"]
        if not floor_path.exists():
            print(f"Floor directory not found: {floor_path}")
            return False

        # Build if needed
        if config.get("needs_build"):
            print(f"Building {language} floor...")
            try:
                result = subprocess.run(
                    config["build_cmd"], cwd=floor_path, capture_output=True, timeout=60
                )
                if result.returncode != 0:
                    print(f"Build failed for {language}: {result.stderr.decode()}")
                    return False
            except Exception as e:
                print(f"Build error for {language}: {e}")
                return False

        # Start the floor process
        try:
            process = subprocess.Popen(
                config["executable"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=floor_path,
            )

            floor_process = FloorProcess(config["floor_number"], language, process)

            self.active_floors[language] = floor_process
            print(f"Started {language} floor (Floor {config['floor_number']})")
            return True

        except Exception as e:
            print(f"Failed to start {language} floor: {e}")
            return False

    def stop_floor(self, language: str):
        """Stop a running floor process"""
        if language in self.active_floors:
            self.active_floors[language].stop()
            del self.active_floors[language]
            print(f"Stopped {language} floor")

    def stop_all_floors(self):
        """Stop all running floor processes"""
        for language in list(self.active_floors.keys()):
            self.stop_floor(language)

    def get_floor_info(self, language: str) -> Optional[Dict[str, Any]]:
        """Get information about a floor"""
        if language not in self.active_floors:
            return None

        return self.active_floors[language].send_request("get_info")

    def send_request_to_floor(
        self, language: str, method: str, params: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Send a request to a specific floor"""
        if language not in self.active_floors:
            print(f"Floor {language} is not running")
            return None

        return self.active_floors[language].send_request(method, params)

    def get_all_floor_info(self) -> Dict[str, Any]:
        """Get information about all running floors"""
        info = {}
        for language, floor in self.active_floors.items():
            try:
                info[language] = floor.send_request("get_info")
            except Exception as e:
                info[language] = {"error": str(e)}
        return info


def demo():
    """Demonstration of multi-language floor management"""
    print("=" * 60)
    print("Multi-Language Department Floor Demonstration")
    print("=" * 60)
    print()

    manager = MultiLanguageFloorManager()

    # Start multiple floors
    languages = ["python", "javascript", "go"]
    print("Starting floors in different languages...\n")

    for lang in languages:
        success = manager.start_floor(lang)
        if not success:
            print(f"  ⚠️  Could not start {lang} floor")
        else:
            print(f"  ✓ {lang.capitalize()} floor started")

    print("\n" + "=" * 60)
    print("Getting information from all floors...")
    print("=" * 60 + "\n")

    # Get info from all floors
    all_info = manager.get_all_floor_info()
    for language, info in all_info.items():
        if "error" in info:
            print(f"\n{language.upper()} Floor: Error - {info['error']}")
        else:
            print(f"\n{language.upper()} Floor:")
            print(f"  Floor Number: {info.get('floor_number')}")
            print(f"  Language: {info.get('language')}")
            print(f"  Domain: {info.get('domain')}")
            print(f"  Offices: {', '.join(info.get('offices', []))}")
            print(f"  Agents: {info.get('agent_count')}")
            print(f"  Tasks: {info.get('task_count')}")

    print("\n" + "=" * 60)
    print("Testing code processing across languages...")
    print("=" * 60 + "\n")

    # Test code processing
    test_cases = [
        ("python", "def hello():\n    print('Hello')\n", "analyze"),
        ("javascript", "function hello() { console.log('Hello'); }", "analyze"),
        ("go", 'func hello() {\n    fmt.Println("Hello")\n}', "analyze"),
    ]

    for lang, code, operation in test_cases:
        if lang in manager.active_floors:
            result = manager.send_request_to_floor(
                lang, "process_code", {"code": code, "operation": operation}
            )
            if result:
                print(f"{lang.upper()} code analysis:")
                if "analysis" in result:
                    analysis = result["analysis"]
                    print(f"  Lines: {analysis.get('lines')}")
                    print(f"  Functions: {analysis.get('functions')}")
                print()

    print("=" * 60)
    print("Shutting down all floors...")
    print("=" * 60)
    manager.stop_all_floors()
    print("\nDemo complete!")


if __name__ == "__main__":
    demo()
