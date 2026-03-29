import datetime

try:
    # Python 3.11+
    UTC = datetime.UTC
except AttributeError:
    # Python < 3.11
    UTC = datetime.timezone.utc
