#!/bin/sh
set -eu

# Restore a backup_audit_data.sh archive into an explicitly named empty target.
# Usage: restore_audit_data.sh ARCHIVE TARGET_DIR

ARCHIVE="${1:-}"
TARGET_DIR="${2:-}"

if [ -z "$ARCHIVE" ] || [ -z "$TARGET_DIR" ]; then
  echo "Usage: restore_audit_data.sh ARCHIVE TARGET_DIR" >&2
  exit 2
fi
if [ ! -f "$ARCHIVE" ]; then
  echo "ERROR: archive does not exist: $ARCHIVE" >&2
  exit 1
fi
case "$TARGET_DIR" in
  ""|/|.)
    echo "ERROR: restore target must be an explicit directory, not $TARGET_DIR" >&2
    exit 1
    ;;
esac
if [ -L "$TARGET_DIR" ]; then
  echo "ERROR: restore target must not be a symbolic link: $TARGET_DIR" >&2
  exit 1
fi

mkdir -p "$TARGET_DIR"
if [ -n "$(find "$TARGET_DIR" -mindepth 1 -print -quit)" ]; then
  echo "ERROR: restore target is not empty: $TARGET_DIR" >&2
  exit 1
fi

# Reject absolute paths and parent traversal before extraction.
tar -tzf "$ARCHIVE" | while IFS= read -r entry; do
  case "$entry" in
    /*|../*|*/../*|..)
      echo "ERROR: unsafe archive path: $entry" >&2
      exit 1
      ;;
  esac
done

tar -xzf "$ARCHIVE" -C "$TARGET_DIR"
echo "Restore completed: $ARCHIVE -> $TARGET_DIR"
