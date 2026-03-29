# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / thirsty_audit.py
# ============================================================================ #
import os
import subprocess



               #
# COMPLIANCE: Thirsty-Lang Syntax & Substrate Audit                            #



THIRSTY_DIR = r"c:\Users\Quencher\.gemini\antigravity\scratch\sovereign-repos\Project-AI\src"
INTERPRETER = r"src\thirsty_lang\src\thirsty_interpreter.py"

def audit_thirsty():
    results = []
    files_to_check = []
    
    for root, dirs, files in os.walk(THIRSTY_DIR):
        for file in files:
            if file.endswith(".thirsty"):
                files_to_check.append(os.path.join(root, file))
                
    for path in files_to_check:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        has_substrate = "sacred substrate" in content
        
        # Test execution
        try:
            cmd = ["python", INTERPRETER, path]
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if proc.returncode == 0:
                status = "PASS"
            else:
                status = f"FAIL (Code {proc.returncode})"
        except Exception as e:
            status = f"ERROR: {str(e)}"
            
        results.append(f"FILE: {path} | SUBSTRATE: {'YES' if has_substrate else 'NO'} | STATUS: {status}")

    with open(r"c:\Users\Quencher\.gemini\antigravity\scratch\sovereign-repos\Project-AI\governance\THIRSTY_AUDIT_REPORT.txt", 'w') as f:
        f.write("\n".join(results))
    print(f"Thirsty Audit complete. Processed {len(results)} files.")

if __name__ == "__main__":
    audit_thirsty()
