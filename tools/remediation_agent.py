# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / remediation_agent.py
# ============================================================================ #
import os
import re
import logging
from datetime import datetime



               #
# COMPLIANCE: Sovereign Substrate / Remediation Agent                          #



ROOT_DIR = r"c:\Users\Quencher\.gemini\antigravity\scratch\sovereign-repos\Project-AI"
TARGET_DIRS = [
    os.path.join(ROOT_DIR, "api"),
    os.path.join(ROOT_DIR, "src", "app", "core"),
    os.path.join(ROOT_DIR, "src", "app", "agents"),
    os.path.join(ROOT_DIR, "src", "security"),
    os.path.join(ROOT_DIR, "src", "app", "gui"),
    os.path.join(ROOT_DIR, "src", "services"),
    os.path.join(ROOT_DIR, "src", "thirsty_lang"),
]

HEADER_TEMPLATE = """

# STATUS: ACTIVE | TIER: MASTER | DATE: {date} | TIME: {time}               #
# COMPLIANCE: Sovereign Substrate / {purpose}


"""

# Matches both divided and un-divided Master-Tier headers
HEADER_REGEX = r"(# =+ #\n)?# STATUS: ACTIVE \| TIER: MASTER.*?(# =+ #\n)?"
OLD_PRODUCTIVITY_REGEX = r"^#\s*\[\d{4}-\d{2}-\d{2}.*\]\n|#\s*Productivity:.*\n"

def get_purpose(path, content):
    """Derive component purpose from path or docstring."""
    if "api" in path:
        return "Governance Host API"
    if "core/council" in path:
        return "Council Runtime Contract"
    if "cognition" in path:
        return "Cognition Kernel"
    if "security" in path:
        return "Zero-Trust Substrate"
    if "thirsty_lang" in path:
        return "Thirsty-Lang Substrate"
    
    match = re.search(r'"""(.*?)"""', content, re.DOTALL)
    if match:
        first_line = match.group(1).strip().split('\n')[0]
        if len(first_line) < 50:
            return first_line
        
    return "Core Component"

def remediate_file(path):
    """Apply header and fix pass stubs."""
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    now = datetime.now()
    cur_date = now.strftime("%Y-%m-%d")
    cur_time = now.strftime("%H:%M")
    
    modified = False
    
    # 1. Apply/Update Header
    if not re.search(r"^
", content):
        purpose = get_purpose(path, content)
        header = HEADER_TEMPLATE.format(date=cur_date, time=cur_time, purpose=purpose)
        
        # Remove old headers (all variants)
        content = re.sub(HEADER_REGEX, "", content, flags=re.DOTALL)
        content = re.sub(OLD_PRODUCTIVITY_REGEX, "", content)
        content = header + content.lstrip()
        modified = True
    
    # 2. Remediate 'except... pass'
    # First, fix pass stubs
    if "pass" in content:
        content = re.sub(
            r"(^([ \t]*)except.*?:)\s*\n[ \t]*pass", 
            r"\1\n\2    logger.warning('Encountered non-terminal exception in %s' % __name__)", 
            content,
            flags=re.MULTILINE
        )
        modified = True

    # Second, repair previous broken indentation regressions
    if "Encountered non-terminal exception" in content:
        def repair_indent(match):
            exc_line = match.group(1)
            exc_indent = match.group(2)
            warning_indent = match.group(3)
            # If warning is not indented at least 4 spaces more than except, fix it
            if len(warning_indent) < len(exc_indent) + 4:
                return f"{exc_line}\n{exc_indent}    logger.warning('Encountered non-terminal exception in %s' % __name__)"
            return match.group(0)

        new_content = re.sub(
            r"(^([ \t]*)except.*?:)\s*\n([ \t]*)logger\.warning\('Encountered non-terminal exception in %s' % __name__\)",
            repair_indent,
            content,
            flags=re.MULTILINE
        )
        if new_content != content:
            content = new_content
            modified = True

    if modified:
        if "import logging" not in content and "from logging" not in content:
            content = "import logging\nlogger = logging.getLogger(__name__)\n" + content

    if modified:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def run_sweep():
    """Execute remediation across target directories."""
    count = 0
    for tdir in TARGET_DIRS:
        print(f"Sweeping {tdir}...")
        for root, _, files in os.walk(tdir):
            for file in files:
                if file.endswith(".py"):
                    path = os.path.join(root, file)
                    try:
                        if remediate_file(path):
                            count += 1
                            if count % 20 == 0:
                                print(f"Remediated {count} files...")
                    except Exception as e:
                        print(f"Error remediating {path}: {e}")
    print(f"Sweep complete. Total files remediated: {count}")

if __name__ == "__main__":
    run_sweep()
