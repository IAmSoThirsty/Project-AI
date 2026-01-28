#!/usr/bin/env python3
"""
Database backup script for audit logs.
Creates timestamped backups of audit data.
"""
import os
import shutil
import json
from datetime import datetime
from pathlib import Path

AUDIT_LOG = "audit.log"
BACKUP_DIR = "backups/audit"

def create_backup():
    """Create a timestamped backup of the audit log."""
    # Ensure backup directory exists
    Path(BACKUP_DIR).mkdir(parents=True, exist_ok=True)
    
    # Check if audit log exists
    if not os.path.exists(AUDIT_LOG):
        print(f"⚠️  Audit log not found: {AUDIT_LOG}")
        return False
    
    # Generate timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(BACKUP_DIR, f"audit_{timestamp}.log")
    
    # Copy file
    try:
        shutil.copy2(AUDIT_LOG, backup_file)
        
        # Get file size
        size = os.path.getsize(backup_file)
        size_mb = size / (1024 * 1024)
        
        # Count records
        with open(backup_file, 'r') as f:
            record_count = sum(1 for _ in f)
        
        print(f"✅ Backup created: {backup_file}")
        print(f"   Size: {size_mb:.2f} MB")
        print(f"   Records: {record_count}")
        
        return True
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return False

def list_backups():
    """List all available backups."""
    if not os.path.exists(BACKUP_DIR):
        print("No backups found")
        return
    
    backups = sorted(Path(BACKUP_DIR).glob("audit_*.log"), reverse=True)
    
    if not backups:
        print("No backups found")
        return
    
    print(f"\n📦 Available backups ({len(backups)}):\n")
    for backup in backups:
        size = backup.stat().st_size / (1024 * 1024)
        mtime = datetime.fromtimestamp(backup.stat().st_mtime)
        print(f"  {backup.name}")
        print(f"    Size: {size:.2f} MB")
        print(f"    Date: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
        print()

def main():
    """Main backup routine."""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "list":
        list_backups()
    else:
        print("🗄️  Creating audit log backup...\n")
        if create_backup():
            print("\n✨ Backup complete!\n")
        else:
            print("\n❌ Backup failed\n")
            sys.exit(1)

if __name__ == "__main__":
    main()
