# Date & Time Utilities

## Overview

Common date and time manipulation utilities for consistent temporal operations across Project-AI, including formatting, parsing, timezone handling, and duration calculations.

**Purpose**: Centralized datetime operations, timezone management, formatting  
**Dependencies**: datetime, time, zoneinfo (Python 3.9+)

---

## Core Utilities

### 1. Current Time Operations

#### now_utc()
```python
from datetime import datetime, timezone

def now_utc() -> datetime:
    """Get current UTC time with timezone info."""
    return datetime.now(timezone.utc)
```

**Usage**:
```python
timestamp = now_utc()
print(timestamp)  # 2025-01-24 15:30:45.123456+00:00
```

---

#### now_iso()
```python
def now_iso() -> str:
    """Get current UTC time as ISO 8601 string."""
    return now_utc().isoformat()
```

**Usage**:
```python
timestamp_str = now_iso()
# "2025-01-24T15:30:45.123456+00:00"
```

---

#### unix_timestamp()
```python
def unix_timestamp() -> float:
    """Get current Unix timestamp (seconds since epoch)."""
    import time
    return time.time()
```

---

### 2. Formatting

#### format_datetime()
```python
def format_datetime(
    dt: datetime,
    format_string: str = "%Y-%m-%d %H:%M:%S"
) -> str:
    """
    Format datetime with custom format.
    
    Common formats:
    - "%Y-%m-%d" = "2025-01-24"
    - "%Y-%m-%d %H:%M:%S" = "2025-01-24 15:30:45"
    - "%B %d, %Y" = "January 24, 2025"
    - "%I:%M %p" = "03:30 PM"
    """
    return dt.strftime(format_string)
```

**Usage**:
```python
now = now_utc()

print(format_datetime(now, "%Y-%m-%d"))  # "2025-01-24"
print(format_datetime(now, "%B %d, %Y"))  # "January 24, 2025"
print(format_datetime(now, "%I:%M %p"))   # "03:30 PM"
```

---

#### format_relative_time()
```python
def format_relative_time(dt: datetime) -> str:
    """
    Format datetime as relative time (e.g., "5 minutes ago").
    
    Returns:
        Human-readable relative time string
    """
    now = now_utc()
    
    # Ensure dt is timezone-aware
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    delta = now - dt
    seconds = delta.total_seconds()
    
    if seconds < 60:
        return f"{int(seconds)} seconds ago"
    elif seconds < 3600:
        return f"{int(seconds / 60)} minutes ago"
    elif seconds < 86400:
        return f"{int(seconds / 3600)} hours ago"
    elif seconds < 604800:
        return f"{int(seconds / 86400)} days ago"
    else:
        return f"{int(seconds / 604800)} weeks ago"
```

**Usage**:
```python
past_time = now_utc() - timedelta(minutes=30)
print(format_relative_time(past_time))  # "30 minutes ago"
```

---

### 3. Parsing

#### parse_iso_datetime()
```python
from datetime import datetime

def parse_iso_datetime(iso_string: str) -> datetime:
    """
    Parse ISO 8601 datetime string.
    
    Handles:
    - "2025-01-24T15:30:45"
    - "2025-01-24T15:30:45.123456"
    - "2025-01-24T15:30:45+00:00"
    - "2025-01-24T15:30:45.123456+00:00"
    """
    return datetime.fromisoformat(iso_string)
```

---

#### parse_flexible_datetime()
```python
from dateutil import parser

def parse_flexible_datetime(date_string: str) -> datetime:
    """
    Parse datetime from various formats.
    
    Handles:
    - "2025-01-24"
    - "January 24, 2025"
    - "24/01/2025"
    - "01-24-2025 3:30 PM"
    
    Requires: python-dateutil package
    """
    return parser.parse(date_string)
```

---

### 4. Timezone Operations

#### convert_timezone()
```python
from zoneinfo import ZoneInfo

def convert_timezone(
    dt: datetime,
    to_tz: str = "UTC"
) -> datetime:
    """
    Convert datetime to different timezone.
    
    Args:
        dt: Datetime to convert
        to_tz: Target timezone (e.g., "UTC", "America/New_York")
    
    Returns:
        Datetime in target timezone
    """
    # Ensure datetime is timezone-aware
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    target_tz = ZoneInfo(to_tz)
    return dt.astimezone(target_tz)
```

**Usage**:
```python
utc_time = now_utc()
ny_time = convert_timezone(utc_time, "America/New_York")
tokyo_time = convert_timezone(utc_time, "Asia/Tokyo")

print(f"UTC: {format_datetime(utc_time)}")
print(f"New York: {format_datetime(ny_time)}")
print(f"Tokyo: {format_datetime(tokyo_time)}")
```

---

#### get_timezone_offset()
```python
def get_timezone_offset(tz_name: str) -> int:
    """
    Get timezone offset in hours from UTC.
    
    Returns:
        Offset in hours (can be negative)
    """
    tz = ZoneInfo(tz_name)
    now = datetime.now(tz)
    offset_seconds = now.utcoffset().total_seconds()
    return int(offset_seconds / 3600)

# Usage
print(get_timezone_offset("America/New_York"))  # -5 or -4 (depending on DST)
print(get_timezone_offset("Asia/Tokyo"))        # +9
```

---

### 5. Duration Calculations

#### time_delta()
```python
from datetime import timedelta

def time_delta(
    days: int = 0,
    hours: int = 0,
    minutes: int = 0,
    seconds: int = 0
) -> timedelta:
    """Create time delta."""
    return timedelta(
        days=days,
        hours=hours,
        minutes=minutes,
        seconds=seconds
    )
```

---

#### format_duration()
```python
def format_duration(seconds: float, precision: int = 2) -> str:
    """
    Format duration in human-readable format.
    
    Args:
        seconds: Duration in seconds
        precision: Number of units to show
    
    Returns:
        Formatted string (e.g., "2h 30m", "1d 5h 30m")
    """
    if seconds < 0:
        return "0s"
    
    units = [
        ("d", 86400),  # days
        ("h", 3600),   # hours
        ("m", 60),     # minutes
        ("s", 1),      # seconds
    ]
    
    parts = []
    remaining = seconds
    
    for unit_name, unit_seconds in units:
        if remaining >= unit_seconds:
            value = int(remaining / unit_seconds)
            parts.append(f"{value}{unit_name}")
            remaining %= unit_seconds
        
        if len(parts) >= precision:
            break
    
    return " ".join(parts) if parts else "0s"
```

**Usage**:
```python
print(format_duration(90))        # "1m 30s"
print(format_duration(3665))      # "1h 1m"
print(format_duration(90000, 3))  # "1d 1h 0m"
```

---

### 6. Date Arithmetic

#### add_business_days()
```python
def add_business_days(date: datetime, days: int) -> datetime:
    """
    Add business days (excluding weekends).
    
    Args:
        date: Starting date
        days: Number of business days to add
    
    Returns:
        Date after adding business days
    """
    current = date
    added = 0
    
    while added < days:
        current += timedelta(days=1)
        # Skip weekends (Saturday=5, Sunday=6)
        if current.weekday() < 5:
            added += 1
    
    return current

# Usage
start_date = datetime(2025, 1, 24)  # Friday
future_date = add_business_days(start_date, 5)
# Skips weekend, lands on following Friday
```

---

#### is_business_day()
```python
def is_business_day(date: datetime) -> bool:
    """Check if date is a business day (weekday)."""
    return date.weekday() < 5  # Monday=0, Friday=4
```

---

### 7. Date Range Operations

#### date_range()
```python
from typing import Generator

def date_range(
    start: datetime,
    end: datetime,
    step: timedelta = timedelta(days=1)
) -> Generator[datetime, None, None]:
    """
    Generate dates in range.
    
    Args:
        start: Start date
        end: End date
        step: Step size (default: 1 day)
    
    Yields:
        Dates in range
    """
    current = start
    while current < end:
        yield current
        current += step

# Usage
start = datetime(2025, 1, 1)
end = datetime(2025, 1, 8)

for date in date_range(start, end):
    print(format_datetime(date, "%Y-%m-%d"))
# 2025-01-01
# 2025-01-02
# ...
# 2025-01-07
```

---

#### business_days_between()
```python
def business_days_between(start: datetime, end: datetime) -> int:
    """Calculate number of business days between dates."""
    count = 0
    current = start
    
    while current < end:
        if is_business_day(current):
            count += 1
        current += timedelta(days=1)
    
    return count
```

---

### 8. Scheduling Utilities

#### next_occurrence()
```python
def next_occurrence(
    from_date: datetime,
    hour: int,
    minute: int = 0
) -> datetime:
    """
    Find next occurrence of time.
    
    Args:
        from_date: Starting datetime
        hour: Target hour (0-23)
        minute: Target minute (0-59)
    
    Returns:
        Next occurrence of specified time
    """
    target = from_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
    
    if target <= from_date:
        # Already passed today, use tomorrow
        target += timedelta(days=1)
    
    return target

# Usage
now = now_utc()
next_run = next_occurrence(now, hour=3, minute=0)  # Next 3:00 AM
```

---

#### cron_next_run()
```python
from croniter import croniter

def cron_next_run(cron_expression: str, base_time: datetime = None) -> datetime:
    """
    Calculate next run time from cron expression.
    
    Args:
        cron_expression: Cron expression (e.g., "0 3 * * *")
        base_time: Base time (default: now)
    
    Returns:
        Next run datetime
    
    Requires: croniter package
    """
    if base_time is None:
        base_time = now_utc()
    
    cron = croniter(cron_expression, base_time)
    return cron.get_next(datetime)

# Usage
# Run daily at 3 AM
next_run = cron_next_run("0 3 * * *")

# Run every 15 minutes
next_run = cron_next_run("*/15 * * * *")
```

---

## Advanced Patterns

### 1. Timestamp Context Manager

```python
from contextlib import contextmanager

@contextmanager
def timed_operation(operation_name: str):
    """Context manager for timing operations."""
    start_time = unix_timestamp()
    print(f"Starting {operation_name}...")
    
    try:
        yield start_time
    finally:
        duration = unix_timestamp() - start_time
        print(f"{operation_name} completed in {format_duration(duration)}")

# Usage
with timed_operation("data_processing"):
    process_large_dataset()
# "Starting data_processing..."
# "data_processing completed in 2m 34s"
```

---

### 2. Rate Limiter with Time Windows

```python
from collections import deque

class TimeWindowRateLimiter:
    """Rate limiter using sliding time window."""
    
    def __init__(self, max_calls: int, window_seconds: int):
        self.max_calls = max_calls
        self.window_seconds = window_seconds
        self.calls = deque()
    
    def can_proceed(self) -> bool:
        """Check if action is allowed."""
        now = unix_timestamp()
        
        # Remove old calls
        cutoff = now - self.window_seconds
        while self.calls and self.calls[0] < cutoff:
            self.calls.popleft()
        
        # Check limit
        if len(self.calls) < self.max_calls:
            self.calls.append(now)
            return True
        
        return False
    
    def time_until_next_call(self) -> float:
        """Get seconds until next call allowed."""
        if len(self.calls) < self.max_calls:
            return 0.0
        
        oldest_call = self.calls[0]
        now = unix_timestamp()
        wait_time = (oldest_call + self.window_seconds) - now
        
        return max(0.0, wait_time)

# Usage
limiter = TimeWindowRateLimiter(max_calls=10, window_seconds=60)

if limiter.can_proceed():
    make_api_call()
else:
    wait_time = limiter.time_until_next_call()
    print(f"Rate limited. Wait {wait_time:.1f}s")
```

---

### 3. Scheduler

```python
import schedule
import time

class Scheduler:
    """Simple task scheduler."""
    
    def __init__(self):
        self.jobs = []
    
    def every_day_at(self, time_str: str, func: Callable):
        """Schedule daily task."""
        schedule.every().day.at(time_str).do(func)
        self.jobs.append((f"daily_{time_str}", func))
    
    def every_hour(self, func: Callable):
        """Schedule hourly task."""
        schedule.every().hour.do(func)
        self.jobs.append(("hourly", func))
    
    def run_pending(self):
        """Run pending tasks."""
        schedule.run_pending()
    
    def run_forever(self):
        """Run scheduler loop."""
        while True:
            self.run_pending()
            time.sleep(60)  # Check every minute

# Usage
scheduler = Scheduler()
scheduler.every_day_at("03:00", backup_database)
scheduler.every_hour(check_system_health)
scheduler.run_forever()
```

---

## Testing

```python
import unittest
from datetime import datetime, timedelta, timezone

class TestDateTimeUtils(unittest.TestCase):
    def test_format_relative_time(self):
        now = now_utc()
        
        # 5 minutes ago
        past = now - timedelta(minutes=5)
        self.assertEqual(format_relative_time(past), "5 minutes ago")
        
        # 2 hours ago
        past = now - timedelta(hours=2)
        self.assertEqual(format_relative_time(past), "2 hours ago")
    
    def test_convert_timezone(self):
        utc_time = datetime(2025, 1, 24, 15, 30, tzinfo=timezone.utc)
        ny_time = convert_timezone(utc_time, "America/New_York")
        
        # New York is UTC-5 (or -4 during DST)
        self.assertNotEqual(utc_time.hour, ny_time.hour)
    
    def test_business_days(self):
        friday = datetime(2025, 1, 24)  # Friday
        monday = add_business_days(friday, 1)
        
        self.assertEqual(monday.weekday(), 0)  # Monday
```

---

## Best Practices

### DO ✅

- Always use timezone-aware datetimes
- Store timestamps in UTC
- Convert to local timezone only for display
- Use ISO 8601 format for string representation
- Handle DST transitions properly
- Use `timedelta` for time arithmetic

### DON'T ❌

- Use naive datetimes (without timezone)
- Store local time without timezone info
- Hardcode timezone offsets
- Ignore DST
- Use string concatenation for formatting
- Assume 24-hour days (DST changes)

---

## Related Documentation

- **Configuration Management**: `source-docs/utilities/008-configuration-management.md`
- **Test Helpers**: `source-docs/utilities/007-test-helpers.md`

---

**Last Updated**: 2025-01-24  
**Status**: Best Practices Guide  
**Maintainer**: Utilities Team
