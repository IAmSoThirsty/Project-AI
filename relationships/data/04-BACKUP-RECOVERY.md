# Backup and Recovery Procedures

**Component:** Backup & Disaster Recovery  
**Agent:** AGENT-058  
**Date:** 2026-04-20

---


## Navigation

**Location**: `relationships\data\04-BACKUP-RECOVERY.md`

**Parent**: [[relationships\data\README.md]]


## Overview

The BackupManager provides automated backup creation, verification, rotation, and disaster recovery capabilities. This document details backup strategies, recovery procedures, and data integrity validation. For persistence patterns, see [[01-PERSISTENCE-PATTERNS.md|Persistence Patterns]]. For monitoring, see [[../monitoring/02-metrics-system.md|Metrics System]].

---

## Backup Architecture

```
┌───────────────────────────────────────────────────────────┐
│                   Backup System Architecture              │
├───────────────────────────────────────────────────────────┤
│                                                           │
│  Source Data (data/)                                     │
│  ┌─────────────────────────────────────────────┐         │
│  │ users.json                                  │         │
│  │ ai_persona/state.json                       │         │
│  │ memory/knowledge.json                       │         │
│  │ learning_requests/requests.json             │         │
│  │ secure.db                                   │         │
│  │ *.enc, *.meta (encrypted states)            │         │
│  └─────────────────────────────────────────────┘         │
│           │                                               │
│           ↓ BackupManager.create_backup()                │
│  ┌─────────────────────────────────────────────┐         │
│  │ Backup Archive (compressed)                 │         │
│  │ data/backups/backup_YYYYMMDD_HHMMSS.tar.gz  │         │
│  │ → [[../monitoring/02-metrics-system.md|Metrics System]]    │
│  └─────────────────────────────────────────────┘         │
│           │                                               │
│           ↓ Metadata Creation                            │
│  ┌─────────────────────────────────────────────┐         │
│  │ Backup Metadata (JSON)                      │         │
│  │ data/backups/backup_YYYYMMDD_HHMMSS.meta    │         │
│  │ - timestamp, checksum, compressed flag      │         │
│  └─────────────────────────────────────────────┘         │
│           │                                               │
│           ↓ Rotation Policy                              │
│  ┌─────────────────────────────────────────────┐         │
│  │ Keep Last N Backups (default: 7)            │         │
│  │ Delete older backups automatically          │         │
│  └─────────────────────────────────────────────┘         │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

---

## Backup Creation

### Full Backup Process

See [[01-PERSISTENCE-PATTERNS.md|Persistence Patterns]] for atomic write implementation.

```python
def create_backup(self, backup_name: str | None = None) -> bool:
    """Create a full backup of all data."""
    
    # Step 1: Generate backup name (timestamp-based)
    if backup_name is None:
        backup_name = datetime.now().strftime("backup_%Y%m%d_%H%M%S")
    
    backup_path = self.backup_dir / backup_name
    
    # Step 2: Create compressed archive
    if self.compression_enabled:
        # tar.gz format (gzip compression)
        shutil.make_archive(str(backup_path), "gztar", self.data_dir)
        backup_file = f"{backup_path}.tar.gz"
    else:
        # Uncompressed directory copy
        shutil.copytree(self.data_dir, backup_path, dirs_exist_ok=True)
        backup_file = str(backup_path)
    
    # Step 3: Calculate integrity checksum (see [[../security/01_security_system_overview.md|Security Overview]])
    checksum = self._calculate_checksum(backup_file)
    
    # Step 4: Save metadata
    metadata = {
        "backup_name": backup_name,
        "timestamp": datetime.now().isoformat(),
        "checksum": checksum,
        "compressed": self.compression_enabled,
    }
    
    metadata_file = self.backup_dir / f"{backup_name}.meta"
    with open(metadata_file, "w") as f:
        json.dump(metadata, f, indent=2)
    
    logger.info("Backup created: %s", backup_file)
    
    # Step 5: Cleanup old backups (rotation) (see [[../configuration/10_default_values_relationships.md|Default Values]])
    self._cleanup_old_backups()
    
    return True
```

### Backup Naming Convention

```
Format: backup_YYYYMMDD_HHMMSS
Examples:
  backup_20260420_143000.tar.gz
  backup_20260419_090000.tar.gz
  backup_20260418_170000.tar.gz
```

**Benefits:**
- ✅ Lexicographically sorted
- ✅ Human-readable timestamp
- ✅ No collisions (second precision)
- ✅ Easy to find latest backup

---

### Compression Strategy

**Enabled (Default):**
```python
# tar.gz format using shutil.make_archive
shutil.make_archive(str(backup_path), "gztar", self.data_dir)
```

**Output:**
```
backup_20260420_143000.tar.gz (compressed)
Original size: 10 MB
Compressed size: 2-4 MB (60-80% reduction)
```

**Disabled (Optional):**
```python
# Plain directory copy
shutil.copytree(self.data_dir, backup_path, dirs_exist_ok=True)
```

**Output:**
```
backup_20260420_143000/ (directory)
└── (full directory structure)
```

**Trade-offs:**

| Feature | Compressed | Uncompressed |
|---------|-----------|--------------|
| **Size** | 20-40% of original | 100% of original |
| **Speed** | Slower (compression time) | Faster (direct copy) |
| **Portability** | Single file | Directory |
| **Random access** | No (must extract) | Yes (direct file access) |

**Recommendation:** Use compression (default) for production

---

### Checksum Calculation

See [[../security/01_security_system_overview.md|Security Overview]] for integrity verification and [[../monitoring/02-metrics-system.md|Metrics System]] for checksum tracking.

```python
def _calculate_checksum(self, file_path: str) -> str:
    """Calculate SHA-256 checksum."""
    sha256 = hashlib.sha256()
    
    if os.path.isfile(file_path):
        # Single file (compressed backup)
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
    
    elif os.path.isdir(file_path):
        # Directory (uncompressed backup)
        for root, _dirs, files in os.walk(file_path):
            for file in sorted(files):  # Deterministic order
                file_path_full = os.path.join(root, file)
                with open(file_path_full, "rb") as f:
                    for chunk in iter(lambda: f.read(8192), b""):
                        sha256.update(chunk)
    
    return sha256.hexdigest()
```

**Properties:**
- ✅ **Integrity:** Detects corruption (bit flips, partial writes)
- ✅ **Deterministic:** Same content → same checksum
- ✅ **Fast:** ~100-200 MB/s on SSD
- ⚠️ **Not encrypted:** Checksum stored in plaintext metadata

**Checksum Format:**
```
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
(64 hex characters = 256 bits = 32 bytes)
```

---

### Backup Metadata

**File:** `data/backups/backup_20260420_143000.meta`

```json
{
  "backup_name": "backup_20260420_143000",
  "timestamp": "2026-04-20T14:30:00.123456",
  "checksum": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "compressed": true,
  "original_size": 10485760,
  "compressed_size": 2621440,
  "compression_ratio": 0.25,
  "data_dir": "data",
  "files_count": 42
}
```

**Enhanced Metadata (Future):**
```json
{
  "backup_name": "backup_20260420_143000",
  "timestamp": "2026-04-20T14:30:00.123456",
  "checksum": "e3b0c442...",
  "compressed": true,
  "files": [
    {"path": "users.json", "size": 1024, "checksum": "abc123..."},
    {"path": "ai_persona/state.json", "size": 512, "checksum": "def456..."}
  ],
  "tags": ["auto", "daily"],
  "retention": "7d"
}
```

---

## Backup Restoration

### Full Restore Process

See [[../monitoring/06-error-tracking.md|Error Tracking]] for restore error logging.

```python
def restore_backup(self, backup_name: str) -> bool:
    """Restore from a backup with verification."""
    
    # Step 1: Load and verify metadata
    metadata_file = self.backup_dir / f"{backup_name}.meta"
    if not metadata_file.exists():
        logger.error("Backup metadata not found: %s", backup_name)
        return False
    
    with open(metadata_file) as f:
        metadata = json.load(f)
    
    # Step 2: Locate backup file
    if metadata["compressed"]:
        backup_file = self.backup_dir / f"{backup_name}.tar.gz"
    else:
        backup_file = self.backup_dir / backup_name
    
    if not backup_file.exists():
        logger.error("Backup file not found: %s", backup_file)
        return False
    
    # Step 3: Verify checksum (integrity check) (see [[../security/01_security_system_overview.md|Security Overview]])
    checksum = self._calculate_checksum(str(backup_file))
    if checksum != metadata["checksum"]:
        logger.error("Checksum mismatch for backup %s", backup_name)
        logger.error("Expected: %s", metadata["checksum"])
        logger.error("Actual:   %s", checksum)
        return False
    
    # Step 4: Create pre-restore safety backup
    logger.info("Creating pre-restore safety backup...")
    self.create_backup("pre_restore_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
    
    # Step 5: Remove current data directory
    if self.data_dir.exists():
        logger.info("Removing current data directory...")
        shutil.rmtree(self.data_dir)
    
    # Step 6: Extract backup
    if metadata["compressed"]:
        logger.info("Extracting compressed backup...")
        shutil.unpack_archive(str(backup_file), self.data_dir)
    else:
        logger.info("Copying uncompressed backup...")
        shutil.copytree(backup_file, self.data_dir)
    
    logger.info("Backup restored successfully: %s", backup_name)
    return True
```

### Restore Sequence Diagram

```
User Request
   ↓
BackupManager.restore_backup("backup_20260420_143000")
   ↓
Load metadata (.meta file)
   ↓
Verify metadata exists? → No → Return False (error)
   ↓ Yes
Locate backup file
   ↓
Verify file exists? → No → Return False (error)
   ↓ Yes
Calculate checksum
   ↓
Verify checksum matches? → No → Return False (corrupted)
   ↓ Yes
Create pre-restore backup (safety)
   ↓
Remove current data/ directory
   ↓
Extract backup archive
   ↓
Return True (success)
   ↓
Application reloads state from restored data/
```

---

### Verification Checks

See [[../monitoring/02-metrics-system.md|Metrics System]] for verification tracking and [[../monitoring/06-error-tracking.md|Error Tracking]] for failure logging.

**Pre-restore Checks:**
```python
def verify_backup(self, backup_name: str) -> tuple[bool, str]:
    """Verify backup integrity without restoring."""
    
    # Check 1: Metadata exists
    metadata_file = self.backup_dir / f"{backup_name}.meta"
    if not metadata_file.exists():
        return False, "Metadata file not found"
    
    # Check 2: Backup file exists
    metadata = json.load(open(metadata_file))
    if metadata["compressed"]:
        backup_file = self.backup_dir / f"{backup_name}.tar.gz"
    else:
        backup_file = self.backup_dir / backup_name
    
    if not backup_file.exists():
        return False, "Backup file not found"
    
    # Check 3: Checksum matches
    checksum = self._calculate_checksum(str(backup_file))
    if checksum != metadata["checksum"]:
        return False, f"Checksum mismatch (expected {metadata['checksum']}, got {checksum})"
    
    # Check 4: Test extraction (compressed only)
    if metadata["compressed"]:
        try:
            # Extract to temp directory
            with tempfile.TemporaryDirectory() as tmpdir:
                shutil.unpack_archive(str(backup_file), tmpdir)
        except Exception as e:
            return False, f"Extraction failed: {e}"
    
    return True, "Backup verified successfully"
```

---

## Backup Rotation

### Rotation Policy

See [[../configuration/10_default_values_relationships.md|Default Values]] for default retention configuration (max_backups=7).

```python
def _cleanup_old_backups(self):
    """Remove old backups exceeding max_backups limit."""
    backups = self.list_backups()
    
    # Sort by timestamp (newest first)
    backups.sort(key=lambda x: x["timestamp"], reverse=True)
    
    if len(backups) > self.max_backups:
        to_remove = backups[self.max_backups:]
        
        for backup in to_remove:
            backup_name = backup["backup_name"]
            
            # Remove backup file
            if backup["compressed"]:
                backup_file = self.backup_dir / f"{backup_name}.tar.gz"
            else:
                backup_file = self.backup_dir / backup_name
            
            if backup_file.exists():
                if backup_file.is_file():
                    backup_file.unlink()
                else:
                    shutil.rmtree(backup_file)
            
            # Remove metadata
            meta_file = self.backup_dir / f"{backup_name}.meta"
            if meta_file.exists():
                meta_file.unlink()
            
            logger.info("Removed old backup: %s", backup_name)
```

**Default Policy:** Keep last 7 backups

**Example Timeline:**
```
Day 1:  backup_20260420_143000 (kept)
Day 2:  backup_20260421_143000 (kept)
Day 3:  backup_20260422_143000 (kept)
Day 4:  backup_20260423_143000 (kept)
Day 5:  backup_20260424_143000 (kept)
Day 6:  backup_20260425_143000 (kept)
Day 7:  backup_20260426_143000 (kept)
Day 8:  backup_20260427_143000 (kept) ← Day 1 backup deleted
```

---

### Custom Retention Policies (Future)

**Grandfather-Father-Son Strategy:**
```python
class GFSBackupManager(BackupManager):
    """Grandfather-Father-Son backup retention."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.daily_backups = 7      # Keep 7 daily
        self.weekly_backups = 4     # Keep 4 weekly
        self.monthly_backups = 12   # Keep 12 monthly
    
    def _cleanup_old_backups(self):
        backups = self.list_backups()
        now = datetime.now()
        
        # Categorize backups
        daily = []
        weekly = []
        monthly = []
        
        for backup in backups:
            ts = datetime.fromisoformat(backup["timestamp"])
            age_days = (now - ts).days
            
            if age_days < 7:
                daily.append(backup)
            elif age_days < 30 and ts.weekday() == 6:  # Sunday
                weekly.append(backup)
            elif ts.day == 1:  # First of month
                monthly.append(backup)
        
        # Keep N most recent from each category
        to_keep = (
            daily[-self.daily_backups:] +
            weekly[-self.weekly_backups:] +
            monthly[-self.monthly_backups:]
        )
        
        # Remove backups not in keep list
        to_remove = [b for b in backups if b not in to_keep]
        # ... removal logic
```

**Benefits:**
- ✅ Longer retention for old data
- ✅ Efficient storage (fewer old backups)
- ✅ Meets compliance requirements

---

## Backup Validation

### Integrity Testing

```python
def test_backup_integrity(backup_name: str) -> dict:
    """Comprehensive backup integrity test."""
    results = {
        "backup_name": backup_name,
        "timestamp": datetime.now().isoformat(),
        "checks": [],
    }
    
    # Check 1: Metadata exists and valid JSON
    try:
        metadata_file = Path(f"data/backups/{backup_name}.meta")
        with open(metadata_file) as f:
            metadata = json.load(f)
        results["checks"].append({"name": "metadata_valid", "status": "PASS"})
    except Exception as e:
        results["checks"].append({"name": "metadata_valid", "status": "FAIL", "error": str(e)})
        return results
    
    # Check 2: Backup file exists
    if metadata["compressed"]:
        backup_file = Path(f"data/backups/{backup_name}.tar.gz")
    else:
        backup_file = Path(f"data/backups/{backup_name}")
    
    if backup_file.exists():
        results["checks"].append({"name": "file_exists", "status": "PASS"})
    else:
        results["checks"].append({"name": "file_exists", "status": "FAIL"})
        return results
    
    # Check 3: Checksum verification
    calculated_checksum = _calculate_checksum(str(backup_file))
    if calculated_checksum == metadata["checksum"]:
        results["checks"].append({"name": "checksum_match", "status": "PASS"})
    else:
        results["checks"].append({
            "name": "checksum_match",
            "status": "FAIL",
            "expected": metadata["checksum"],
            "actual": calculated_checksum,
        })
        return results
    
    # Check 4: Test extraction (compressed only)
    if metadata["compressed"]:
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                shutil.unpack_archive(str(backup_file), tmpdir)
                
                # Verify critical files exist
                critical_files = ["users.json", "ai_persona/state.json"]
                for file in critical_files:
                    if not Path(tmpdir, file).exists():
                        raise FileNotFoundError(f"Critical file missing: {file}")
                
                results["checks"].append({"name": "extraction_test", "status": "PASS"})
        except Exception as e:
            results["checks"].append({"name": "extraction_test", "status": "FAIL", "error": str(e)})
            return results
    
    # Check 5: JSON validity (all .json files)
    if metadata["compressed"]:
        with tempfile.TemporaryDirectory() as tmpdir:
            shutil.unpack_archive(str(backup_file), tmpdir)
            json_files = Path(tmpdir).rglob("*.json")
            
            for json_file in json_files:
                try:
                    with open(json_file) as f:
                        json.load(f)
                except Exception as e:
                    results["checks"].append({
                        "name": f"json_valid_{json_file.name}",
                        "status": "FAIL",
                        "error": str(e),
                    })
                    return results
            
            results["checks"].append({"name": "json_validity", "status": "PASS"})
    
    # All checks passed
    results["overall_status"] = "PASS"
    return results
```

**Example Output:**
```json
{
  "backup_name": "backup_20260420_143000",
  "timestamp": "2026-04-20T14:35:00",
  "checks": [
    {"name": "metadata_valid", "status": "PASS"},
    {"name": "file_exists", "status": "PASS"},
    {"name": "checksum_match", "status": "PASS"},
    {"name": "extraction_test", "status": "PASS"},
    {"name": "json_validity", "status": "PASS"}
  ],
  "overall_status": "PASS"
}
```

---

## Disaster Recovery Procedures

See [[../monitoring/06-error-tracking.md|Error Tracking]] for disaster detection and [[03-SYNC-STRATEGIES.md|Sync Strategies]] for cloud-based recovery options.

### Scenario 1: Complete Data Loss

**Symptoms:**
- `data/` directory deleted or corrupted
- All state files missing

**Recovery Steps:**
```bash
# 1. List available backups
backup_manager = BackupManager()
backups = backup_manager.list_backups()
print(backups)

# 2. Verify latest backup
is_valid, message = backup_manager.verify_backup(backups[0]["backup_name"])
print(f"Verification: {message}")

# 3. Restore latest backup
success = backup_manager.restore_backup(backups[0]["backup_name"])

# 4. Restart application
# Application will reload state from restored data/
```

**Automation:**

See [[../monitoring/06-error-tracking.md|Error Tracking]] for automatic failure detection.

```python
def auto_recover():
    """Automatic recovery from latest backup."""
    backup_manager = BackupManager()
    
    # Check if data directory is empty or corrupted
    if not Path("data").exists() or not any(Path("data").iterdir()):
        logger.warning("Data directory missing, attempting auto-recovery...")
        
        backups = backup_manager.list_backups()
        if backups:
            latest = backups[0]["backup_name"]
            logger.info("Restoring from latest backup: %s", latest)
            
            if backup_manager.restore_backup(latest):
                logger.info("Auto-recovery successful")
                return True
        
        logger.error("Auto-recovery failed: No backups available")
        return False
    
    return True
```

---

### Scenario 2: Partial File Corruption

**Symptoms:**
- Specific JSON file corrupted (e.g., `users.json`)
- Other files intact

**Recovery Steps:**
```python
def restore_single_file(backup_name: str, file_path: str):
    """Restore a single file from backup."""
    backup_file = Path(f"data/backups/{backup_name}.tar.gz")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Extract backup to temp directory
        shutil.unpack_archive(str(backup_file), tmpdir)
        
        # Copy specific file to data directory
        source = Path(tmpdir, file_path)
        dest = Path("data", file_path)
        
        if source.exists():
            shutil.copy(source, dest)
            logger.info("Restored %s from %s", file_path, backup_name)
            return True
        else:
            logger.error("File %s not found in backup", file_path)
            return False

# Usage
restore_single_file("backup_20260420_143000", "users.json")
```

---

### Scenario 3: Accidental Data Modification

**Symptoms:**
- User accidentally deleted important data
- Want to rollback to previous state

**Recovery Steps:**
```python
def list_backups_with_timestamps():
    """Show backups with human-readable timestamps."""
    backup_manager = BackupManager()
    backups = backup_manager.list_backups()
    
    print("Available Backups:")
    for i, backup in enumerate(backups):
        ts = datetime.fromisoformat(backup["timestamp"])
        print(f"{i+1}. {backup['backup_name']} - {ts.strftime('%Y-%m-%d %H:%M:%S')}")
    
    return backups

def restore_by_timestamp(target_time: datetime):
    """Restore backup closest to target time."""
    backups = list_backups_with_timestamps()
    
    # Find closest backup before target time
    closest = None
    min_diff = float('inf')
    
    for backup in backups:
        ts = datetime.fromisoformat(backup["timestamp"])
        if ts <= target_time:
            diff = (target_time - ts).total_seconds()
            if diff < min_diff:
                min_diff = diff
                closest = backup
    
    if closest:
        return backup_manager.restore_backup(closest["backup_name"])
    
    return False

# Usage: Restore to state from 2 hours ago
target = datetime.now() - timedelta(hours=2)
restore_by_timestamp(target)
```

---

## Backup Scheduling

### Manual Backup

See [[../configuration/01_config_loader_relationships.md|Config Loader]] for backup configuration.

```python
# Trigger backup manually
backup_manager = BackupManager()
backup_manager.create_backup()
```

### Event-Driven Backup

See [[../monitoring/04-telemetry-system.md|Telemetry System]] for change tracking events.

```python
class BackupTrigger:
    def __init__(self, backup_manager):
        self.backup_manager = backup_manager
        self.changes_since_backup = 0
        self.backup_threshold = 100  # Backup after 100 changes
    
    def on_data_change(self):
        """Called whenever data is modified."""
        self.changes_since_backup += 1
        
        if self.changes_since_backup >= self.backup_threshold:
            logger.info("Change threshold reached, creating backup...")
            self.backup_manager.create_backup()
            self.changes_since_backup = 0

# Usage
trigger = BackupTrigger(backup_manager)

# In state modification functions
def _save_state(self):
    _atomic_write_json(self.state_file, self.state)
    trigger.on_data_change()  # Notify trigger
```

### Scheduled Backup (Cron-style)

See [[../configuration/10_default_values_relationships.md|Default Values]] for backup schedule configuration.

```python
import schedule
import time

def scheduled_backup_job():
    """Daily backup at 2 AM."""
    backup_manager = BackupManager()
    backup_manager.create_backup()
    logger.info("Scheduled backup completed")

# Schedule daily backup
schedule.every().day.at("02:00").do(scheduled_backup_job)

# Run scheduler in background thread
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(60)

threading.Thread(target=run_scheduler, daemon=True).start()
```

---

## Backup Best Practices

### 3-2-1 Backup Rule

```
3 copies of data:
  1. Production data (data/ directory)
  2. Local backup (data/backups/)
  3. Remote backup (cloud storage)

2 different media types:
  - SSD (local)
  - Cloud storage (remote)

1 copy off-site:
  - Cloud backup (different geographic location)
```

**Implementation:**

See [[03-SYNC-STRATEGIES.md|Sync Strategies]] for cloud upload implementation and [[../security/06_data_flow_diagrams.md|Data Flow Diagrams]] for secure transfer flows.

```python
class ThreeTwoOneBackup(BackupManager):
    def create_backup(self, backup_name=None):
        # 1. Create local backup
        success = super().create_backup(backup_name)
        
        if success:
            # 2. Upload to cloud storage (off-site)
            self._upload_to_cloud(backup_name)
        
        return success
    
    def _upload_to_cloud(self, backup_name: str):
        """Upload backup to cloud storage."""
        backup_file = self.backup_dir / f"{backup_name}.tar.gz"
        
        # Example: Upload to AWS S3
        import boto3
        s3 = boto3.client('s3')
        
        with open(backup_file, 'rb') as f:
            s3.upload_fileobj(
                f,
                'my-backup-bucket',
                f'backups/{backup_name}.tar.gz'
            )
        
        logger.info("Backup uploaded to cloud: %s", backup_name)
```

---

### Backup Testing

See [[../monitoring/02-metrics-system.md|Metrics System]] for backup drill tracking.

**Monthly Backup Drill:**
```python
def backup_drill():
    """Test backup/restore process monthly."""
    backup_manager = BackupManager()
    
    # 1. Create test backup
    test_backup = "drill_" + datetime.now().strftime("%Y%m%d")
    backup_manager.create_backup(test_backup)
    
    # 2. Verify backup
    is_valid, message = backup_manager.verify_backup(test_backup)
    assert is_valid, f"Backup verification failed: {message}"
    
    # 3. Test extraction to temp directory
    with tempfile.TemporaryDirectory() as tmpdir:
        backup_file = Path(f"data/backups/{test_backup}.tar.gz")
        shutil.unpack_archive(str(backup_file), tmpdir)
        
        # Verify critical files
        assert Path(tmpdir, "users.json").exists()
        assert Path(tmpdir, "ai_persona", "state.json").exists()
    
    # 4. Cleanup test backup
    backup_manager._remove_backup(test_backup)
    
    logger.info("Backup drill completed successfully")

# Schedule monthly drill
schedule.every().month.at("01:00").do(backup_drill)
```

---

### Backup Documentation

See [[../monitoring/04-telemetry-system.md|Telemetry System]] for backup event logging.

**Backup Log:**
```json
{
  "backups": [
    {
      "name": "backup_20260420_143000",
      "timestamp": "2026-04-20T14:30:00",
      "type": "auto",
      "trigger": "daily_schedule",
      "size_mb": 2.5,
      "duration_seconds": 3.2,
      "status": "success"
    }
  ],
  "restores": [
    {
      "backup_name": "backup_20260419_143000",
      "timestamp": "2026-04-20T09:00:00",
      "reason": "data_corruption",
      "status": "success",
      "duration_seconds": 5.1
    }
  ]
}
```

---

## Related Documentation

### Data Layer Documentation
- **[[00-DATA-INFRASTRUCTURE-OVERVIEW.md|Data Infrastructure Overview]]** - Complete architecture
- **[[01-PERSISTENCE-PATTERNS.md|Persistence Patterns]]** - Atomic write patterns
- **[[02-ENCRYPTION-CHAINS.md|Encryption Chains]]** - Backup encryption
- **[[03-SYNC-STRATEGIES.md|Sync Strategies]]** - Cloud backup strategies
- **[05-DATA-MODELS.md](./05-DATA-MODELS.md)** - Schema definitions

### Cross-System Documentation
- **[[../security/01_security_system_overview.md|Security Overview]]** - Checksum verification
- **[[../security/06_data_flow_diagrams.md|Data Flow Diagrams]]** - Secure backup flows
- **[[../monitoring/02-metrics-system.md|Metrics System]]** - Backup verification metrics
- **[[../monitoring/04-telemetry-system.md|Telemetry System]]** - Backup event tracking
- **[[../monitoring/06-error-tracking.md|Error Tracking]]** - Disaster detection and recovery
- **[[../configuration/01_config_loader_relationships.md|Config Loader]]** - Backup configuration
- **[[../configuration/10_default_values_relationships.md|Default Values]]** - Retention defaults

---

**Document Version:** 1.0.0  
**Related:** [[03-SYNC-STRATEGIES.md|Sync Strategies]]  
**Next:** [05-DATA-MODELS.md](./05-DATA-MODELS.md)
