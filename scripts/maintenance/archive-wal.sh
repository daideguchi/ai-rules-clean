#!/bin/bash
# WAL archiving script for PITR
set -euo pipefail

WAL_PATH="$1"
WAL_FILE="$2"
ARCHIVE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/runtime/wal_archives"

# Ensure archive directory exists
mkdir -p "$ARCHIVE_DIR"

# Copy WAL file to archive
cp "$WAL_PATH" "$ARCHIVE_DIR/$WAL_FILE"

# Verify copy
if [[ -f "$ARCHIVE_DIR/$WAL_FILE" ]]; then
    echo "$(date): Archived $WAL_FILE" >> "$ARCHIVE_DIR/archive.log"
    exit 0
else
    echo "$(date): Failed to archive $WAL_FILE" >> "$ARCHIVE_DIR/archive.log"
    exit 1
fi
