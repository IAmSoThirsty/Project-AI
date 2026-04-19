import subprocess
import sys
import os

def run_command(command, description):
    print(f"[*] Running {description}...")
    try:
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        print(f"[+] {description} completed successfully.")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"[!] {description} failed with return code {e.returncode}.")
        print(e.stdout)
        print(e.stderr)
        return False
    return True

def main():
    workspace_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(workspace_root)
    
    success = True
    
    # Run Bandit
    bandit_cmd = ["bandit", "-r", "src", "security", "-c", "bandit.yml", "-lll"]
    if not run_command(bandit_cmd, "Bandit Security Scan"):
        success = False
        
    # Run pip-audit
    pip_audit_cmd = ["pip-audit", "-r", "requirements.txt"]
    if not run_command(pip_audit_cmd, "pip-audit Vulnerability Scan"):
        success = False
        
    if success:
        print("[+] All security audits passed.")
        sys.exit(0)
    else:
        print("[!] Security audits found issues. Please review the output above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
