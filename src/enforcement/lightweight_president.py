#!/usr/bin/env python3
"""
⚡ Lightweight PRESIDENT Recognition System
==========================================

Fast, cached PRESIDENT declaration validation for real-time task gating.
Optimized for sub-second response times with security integrity.

Usage:
    from src.enforcement.lightweight_president import LightweightPresident
    president = LightweightPresident()
    is_valid = president.quick_check()  # < 100ms
"""

import json
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass
class PresidentStatus:
    """PRESIDENT declaration status"""

    is_valid: bool
    declared_at: Optional[datetime]
    expires_at: Optional[datetime]
    session_id: Optional[str]
    version: str
    last_checked: datetime


class LightweightPresident:
    """Lightweight PRESIDENT recognition with caching"""

    def __init__(self, cache_duration: int = 300):  # 5 minutes cache
        self.project_root = Path(__file__).parent.parent.parent
        self.cache_duration = cache_duration
        self.cache_file = self.project_root / "runtime" / "president_cache.json"
        self.log_file = self.project_root / "runtime" / "president_declaration.log"

        # Thread-safe cache
        self._cache_lock = threading.Lock()
        self._cached_status: Optional[PresidentStatus] = None
        self._cache_timestamp: Optional[float] = None

        # Initialize cache directory
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)

    def quick_check(self) -> bool:
        """
        Ultra-fast PRESIDENT declaration check (< 100ms target)
        Uses cached status when possible, falls back to file check
        """

        # Check memory cache first (fastest)
        if self._is_cache_valid():
            return self._cached_status.is_valid

        # Check file cache (fast)
        cached_status = self._load_cache()
        if cached_status and self._is_status_current(cached_status):
            self._update_memory_cache(cached_status)
            return cached_status.is_valid

        # Perform quick file validation (fallback)
        status = self._quick_file_check()
        self._save_cache(status)
        self._update_memory_cache(status)

        return status.is_valid

    def full_validation(self) -> PresidentStatus:
        """
        Complete PRESIDENT validation with detailed status
        Use for initial setup or when quick_check fails
        """

        # Check if log file exists
        if not self.log_file.exists():
            return PresidentStatus(
                is_valid=False,
                declared_at=None,
                expires_at=None,
                session_id=None,
                version="unknown",
                last_checked=datetime.now(),
            )

        try:
            # Read log file
            content = self.log_file.read_text()

            # Parse timestamp from log
            declared_at = None
            session_id = None
            version = "1.0"

            for line in content.splitlines():
                if "Timestamp:" in line:
                    timestamp_str = line.split("Timestamp:")[1].strip()
                    try:
                        declared_at = datetime.fromisoformat(timestamp_str)
                    except ValueError:
                        # Try different timestamp formats
                        try:
                            declared_at = datetime.strptime(
                                timestamp_str, "%Y-%m-%d %H:%M:%S"
                            )
                        except ValueError:
                            pass

                elif "Session:" in line:
                    session_id = line.split("Session:")[1].strip()

                elif "Version:" in line:
                    version = line.split("Version:")[1].strip()

            # No expiration concept - always valid if declared
            if declared_at:
                is_valid = True
                expires_at = None
            else:
                is_valid = False
                expires_at = None

            return PresidentStatus(
                is_valid=is_valid,
                declared_at=declared_at,
                expires_at=expires_at,
                session_id=session_id,
                version=version,
                last_checked=datetime.now(),
            )

        except Exception:
            # Fail securely - assume invalid on error
            return PresidentStatus(
                is_valid=False,
                declared_at=None,
                expires_at=None,
                session_id=None,
                version="error",
                last_checked=datetime.now(),
            )

    def _quick_file_check(self) -> PresidentStatus:
        """Quick file-based validation (optimized for speed)"""

        try:
            # Check file existence and modification time
            if not self.log_file.exists():
                return PresidentStatus(
                    False, None, None, None, "missing", datetime.now()
                )

            # Get file modification time (very fast)
            stat = self.log_file.stat()
            mod_time = datetime.fromtimestamp(stat.st_mtime)

            # No expiration concept - file existence indicates valid declaration
            # (Removed expiration check - file-based verification always required)

            # File exists - assume valid for quick check (no expiration)
            return PresidentStatus(
                True, mod_time, None, "quick", "2.0", datetime.now()
            )

        except Exception:
            # Fail securely
            return PresidentStatus(False, None, None, None, "error", datetime.now())

    def _is_cache_valid(self) -> bool:
        """Check if memory cache is still valid"""

        with self._cache_lock:
            if not self._cached_status or not self._cache_timestamp:
                return False

            # Check cache age
            age = time.time() - self._cache_timestamp
            if age > self.cache_duration:
                return False

            # No expiration concept - cache always valid
            # (Removed expiration check)

            return True

    def _update_memory_cache(self, status: PresidentStatus):
        """Update memory cache thread-safely"""

        with self._cache_lock:
            self._cached_status = status
            self._cache_timestamp = time.time()

    def _load_cache(self) -> Optional[PresidentStatus]:
        """Load status from file cache"""

        try:
            if not self.cache_file.exists():
                return None

            with open(self.cache_file) as f:
                data = json.load(f)

            # Parse datetime fields
            declared_at = None
            expires_at = None
            last_checked = datetime.now()

            if data.get("declared_at"):
                declared_at = datetime.fromisoformat(data["declared_at"])
            # Legacy expires_at field ignored (no expiration concept)
            if data.get("last_checked"):
                last_checked = datetime.fromisoformat(data["last_checked"])

            return PresidentStatus(
                is_valid=data.get("is_valid", False),
                declared_at=declared_at,
                expires_at=expires_at,
                session_id=data.get("session_id"),
                version=data.get("version", "unknown"),
                last_checked=last_checked,
            )

        except Exception:
            return None

    def _save_cache(self, status: PresidentStatus):
        """Save status to file cache"""

        try:
            data = {
                "is_valid": status.is_valid,
                "declared_at": status.declared_at.isoformat()
                if status.declared_at
                else None,
                # expires_at field removed (no expiration concept)
                "session_id": status.session_id,
                "version": status.version,
                "last_checked": status.last_checked.isoformat(),
            }

            with open(self.cache_file, "w") as f:
                json.dump(data, f, indent=2)

        except Exception:
            # Cache save failure is non-critical
            pass

    def _is_status_current(self, status: PresidentStatus) -> bool:
        """Check if cached status is still current"""

        # Check age of cache entry
        age = datetime.now() - status.last_checked
        if age > timedelta(seconds=self.cache_duration):
            return False

        # No expiration concept - status always valid
        # (Removed expiration check)

        return True

    def invalidate_cache(self):
        """Force cache invalidation (use after new PRESIDENT declaration)"""

        with self._cache_lock:
            self._cached_status = None
            self._cache_timestamp = None

        # Remove file cache
        try:
            if self.cache_file.exists():
                self.cache_file.unlink()
        except Exception:
            pass

    def get_detailed_status(self) -> Dict[str, Any]:
        """Get detailed status for debugging/monitoring"""

        full_status = self.full_validation()

        return {
            "quick_check": self.quick_check(),
            "is_valid": full_status.is_valid,
            "declared_at": full_status.declared_at.isoformat()
            if full_status.declared_at
            else None,
            # expires_at field removed (no expiration concept)
            "session_id": full_status.session_id,
            "version": full_status.version,
            "cache_active": self._is_cache_valid(),
            "cache_file_exists": self.cache_file.exists(),
            "log_file_exists": self.log_file.exists(),
        }


def main():
    """Test lightweight PRESIDENT recognition"""

    print("⚡ Lightweight PRESIDENT Recognition Test")
    print("=" * 45)

    president = LightweightPresident()

    # Timing test
    start_time = time.time()
    quick_result = president.quick_check()
    quick_time = (time.time() - start_time) * 1000

    start_time = time.time()
    full_status = president.full_validation()
    full_time = (time.time() - start_time) * 1000

    print(f"🚀 Quick Check: {quick_result} ({quick_time:.1f}ms)")
    print(f"🔍 Full Validation: {full_status.is_valid} ({full_time:.1f}ms)")
    print(f"⚡ Speed Improvement: {full_time / quick_time:.1f}x faster")

    # Detailed status
    print("\n📊 Detailed Status:")
    status = president.get_detailed_status()
    for key, value in status.items():
        print(f"   {key}: {value}")

    # Cache test
    print("\n🧪 Cache Test (5 iterations):")
    for i in range(5):
        start_time = time.time()
        result = president.quick_check()
        elapsed = (time.time() - start_time) * 1000
        print(f"   Iteration {i + 1}: {result} ({elapsed:.1f}ms)")


if __name__ == "__main__":
    main()
