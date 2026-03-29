# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / header_audit.py
# ============================================================================ #
import os
import re
from datetime import datetime



               #
# COMPLIANCE: Absolute Sovereignty Header Audit                                #



FILES_TO_AUDIT = []
SRC_DIR = r"c:\Users\Quencher\.gemini\antigravity\scratch\sovereign-repos\Project-AI\src"

HEADER_TEMPLATE = "# STATUS: ACTIVE | TIER: MASTER | DATE: {date} | TIME: {time}"
HEADER_REGEX = r"^# STATUS:.*\| TIER: MASTER.*"

def audit_files():
    results = []
    now = datetime.now()
    cur_date = now.strftime("%Y-%m-%d")
    cur_time = now.strftime("%H:%M")

    for root, dirs, files in os.walk(SRC_DIR):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                has_header = re.search(HEADER_REGEX, content, re.MULTILINE)
                has_basesubsystem = "BaseSubsystem" in content or "KernelRoutedAgent" in content
                
                if not has_header:
                    # Prepend header
                    new_header = f"
\n{HEADER_TEMPLATE.format(date=cur_date, time=cur_time)}\n
\n"
                    # Remove old-style productivity headers if present
                    content = re.sub(r"^#\s*\[\d{4}-\d{2}-\d{2}.*\]\n", "", content)
                    content = re.sub(r"^#\s*Productivity:.*\n", "", content)
                    
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(new_header + content)
                    results.append(f"UPDATED: {path}")
                else:
                    results.append(f"COMPLIANT: {path}")

    with open(r"c:\Users\Quencher\.gemini\antigravity\scratch\sovereign-repos\Project-AI\governance\HEADER_AUDIT_REPORT.txt", 'w') as f:
        f.write("\n".join(results))
    print(f"Audit complete. Processed {len(results)} files.")

if __name__ == "__main__":
    audit_files()
