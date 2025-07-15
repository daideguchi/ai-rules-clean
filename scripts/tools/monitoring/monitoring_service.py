#!/usr/bin/env python3
"""
🔧 Monitoring Service Management
===============================

Service management for 24/7 real-time monitoring system:
- Start/stop monitoring service
- Health checks and status monitoring
- Service configuration management
- Auto-restart on failures
- Integration with systemd
"""

import argparse
import json
import logging
import os
import signal
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from monitoring.realtime_monitoring_system import RealTimeMonitoringSystem
except ImportError:
    print("❌ Error: Could not import RealTimeMonitoringSystem")
    print("Make sure you're running from the project root directory")
    sys.exit(1)


class MonitoringService:
    """Service management for real-time monitoring system"""

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent
        self.service_name = "coding-rule2-monitoring"
        self.pid_file = self.project_root / "runtime" / "monitoring.pid"
        self.log_file = (
            self.project_root / "runtime" / "logs" / "monitoring_service.log"
        )
        self.config_file = self.project_root / "runtime" / "monitoring_config.json"

        # Ensure directories exist
        self.pid_file.parent.mkdir(parents=True, exist_ok=True)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

        # Setup logging
        self.logger = self._setup_logging()

        # Load configuration
        self.config = self._load_config()

        # Initialize monitoring system
        self.monitoring_system = None

    def _setup_logging(self) -> logging.Logger:
        """Setup service logging"""
        logger = logging.getLogger("monitoring_service")
        logger.setLevel(logging.INFO)

        # File handler
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.INFO)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return logger

    def _load_config(self) -> Dict[str, Any]:
        """Load service configuration"""
        default_config = {
            "auto_restart": True,
            "max_restart_attempts": 5,
            "restart_delay": 30,
            "health_check_interval": 60,
            "log_level": "INFO",
            "monitoring_rules": {
                "root_file_limit": True,
                "constitutional_ai_violations": True,
                "memory_integrity": True,
                "database_consistency": True,
                "ai_organization_health": True,
            },
        }

        try:
            if self.config_file.exists():
                with open(self.config_file) as f:
                    config = json.load(f)
                    # Merge with defaults
                    default_config.update(config)
        except Exception as e:
            self.logger.warning(f"Config load failed, using defaults: {e}")

        return default_config

    def _save_config(self):
        """Save service configuration"""
        try:
            with open(self.config_file, "w") as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            self.logger.error(f"Config save failed: {e}")

    def start(self, daemon: bool = False) -> bool:
        """Start monitoring service"""
        try:
            # Check if already running
            if self.is_running():
                self.logger.info("Monitoring service is already running")
                return True

            self.logger.info("Starting monitoring service...")

            if daemon:
                # Daemonize process
                self._daemonize()

            # Initialize monitoring system
            self.monitoring_system = RealTimeMonitoringSystem(self.project_root)

            # Write PID file
            self._write_pid_file()

            # Setup signal handlers
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)

            self.logger.info("✅ Monitoring service started successfully")

            # Start monitoring with auto-restart
            self._run_with_restart()

            return True

        except Exception as e:
            self.logger.error(f"Failed to start monitoring service: {e}")
            return False

    def stop(self) -> bool:
        """Stop monitoring service"""
        try:
            if not self.is_running():
                self.logger.info("Monitoring service is not running")
                return True

            # Get PID
            pid = self._get_pid()
            if pid:
                self.logger.info(f"Stopping monitoring service (PID: {pid})")

                # Send termination signal
                os.kill(pid, signal.SIGTERM)

                # Wait for graceful shutdown
                for _ in range(30):  # Wait up to 30 seconds
                    if not self.is_running():
                        break
                    time.sleep(1)

                # Force kill if still running
                if self.is_running():
                    self.logger.warning("Forcing service termination")
                    os.kill(pid, signal.SIGKILL)

                # Remove PID file
                self._remove_pid_file()

                self.logger.info("✅ Monitoring service stopped successfully")
                return True

        except Exception as e:
            self.logger.error(f"Failed to stop monitoring service: {e}")
            return False

    def restart(self) -> bool:
        """Restart monitoring service"""
        self.logger.info("Restarting monitoring service...")

        if not self.stop():
            return False

        time.sleep(2)  # Brief pause

        return self.start()

    def status(self) -> Dict[str, Any]:
        """Get service status"""
        try:
            is_running = self.is_running()
            pid = self._get_pid() if is_running else None

            status = {
                "service_name": self.service_name,
                "is_running": is_running,
                "pid": pid,
                "config_file": str(self.config_file),
                "log_file": str(self.log_file),
                "pid_file": str(self.pid_file),
            }

            if is_running and self.monitoring_system:
                # Get monitoring system status
                monitoring_status = self.monitoring_system.get_monitoring_status()
                status.update(monitoring_status)

            return status

        except Exception as e:
            self.logger.error(f"Status check failed: {e}")
            return {"error": str(e)}

    def is_running(self) -> bool:
        """Check if service is running"""
        try:
            pid = self._get_pid()
            if pid:
                # Check if process exists
                os.kill(pid, 0)
                return True
        except (OSError, ProcessLookupError):
            # Process doesn't exist
            self._remove_pid_file()

        return False

    def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        try:
            if not self.is_running():
                return {"status": "stopped", "healthy": False}

            if not self.monitoring_system:
                return {
                    "status": "error",
                    "healthy": False,
                    "message": "Monitoring system not initialized",
                }

            # Get monitoring status
            monitoring_status = self.monitoring_system.get_monitoring_status()

            # Check system health
            healthy = True
            issues = []

            # Check uptime
            uptime = monitoring_status.get("uptime_seconds", 0)
            if uptime < 60:  # Less than 1 minute
                issues.append("Short uptime")

            # Check integrations
            integrations = monitoring_status.get("system_integration", {})
            if not integrations.get("constitutional_ai"):
                issues.append("Constitutional AI not available")

            if not integrations.get("memory_manager"):
                issues.append("Memory manager not available")

            if not integrations.get("database"):
                issues.append("Database not available")

            if issues:
                healthy = False

            return {
                "status": "running",
                "healthy": healthy,
                "issues": issues,
                "uptime_seconds": uptime,
                "violations_detected": monitoring_status.get("violations_detected", 0),
                "auto_corrections_applied": monitoring_status.get(
                    "auto_corrections_applied", 0
                ),
            }

        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {"status": "error", "healthy": False, "message": str(e)}

    def _run_with_restart(self):
        """Run monitoring with auto-restart capability"""
        restart_count = 0
        max_restarts = self.config.get("max_restart_attempts", 5)
        restart_delay = self.config.get("restart_delay", 30)

        while restart_count < max_restarts:
            try:
                self.logger.info(f"Starting monitoring (attempt {restart_count + 1})")

                # Run monitoring system
                import asyncio

                asyncio.run(self.monitoring_system.start_monitoring())

                # If we get here, monitoring stopped normally
                self.logger.info("Monitoring stopped normally")
                break

            except Exception as e:
                restart_count += 1
                self.logger.error(f"Monitoring failed (attempt {restart_count}): {e}")

                if restart_count < max_restarts:
                    self.logger.info(f"Restarting in {restart_delay} seconds...")
                    time.sleep(restart_delay)
                else:
                    self.logger.error("Max restart attempts reached, stopping service")
                    break

        # Clean up
        self._remove_pid_file()

    def _daemonize(self):
        """Daemonize the service process"""
        try:
            # Fork first child
            pid = os.fork()
            if pid > 0:
                sys.exit(0)

            # Decouple from parent environment
            os.chdir("/")
            os.setsid()
            os.umask(0)

            # Fork second child
            pid = os.fork()
            if pid > 0:
                sys.exit(0)

            # Redirect standard file descriptors
            sys.stdout.flush()
            sys.stderr.flush()

            with open("/dev/null") as stdin:
                os.dup2(stdin.fileno(), sys.stdin.fileno())

            with open(self.log_file, "a") as stdout:
                os.dup2(stdout.fileno(), sys.stdout.fileno())

            with open(self.log_file, "a") as stderr:
                os.dup2(stderr.fileno(), sys.stderr.fileno())

        except OSError as e:
            self.logger.error(f"Daemonization failed: {e}")
            sys.exit(1)

    def _write_pid_file(self):
        """Write PID file"""
        try:
            with open(self.pid_file, "w") as f:
                f.write(str(os.getpid()))
        except Exception as e:
            self.logger.error(f"PID file write failed: {e}")

    def _get_pid(self) -> Optional[int]:
        """Get PID from file"""
        try:
            if self.pid_file.exists():
                with open(self.pid_file) as f:
                    return int(f.read().strip())
        except Exception:
            pass
        return None

    def _remove_pid_file(self):
        """Remove PID file"""
        try:
            if self.pid_file.exists():
                self.pid_file.unlink()
        except Exception as e:
            self.logger.debug(f"PID file removal failed: {e}")

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, shutting down...")

        if self.monitoring_system:
            self.monitoring_system.is_running = False

        sys.exit(0)

    def create_systemd_service(self) -> bool:
        """Create systemd service file"""
        try:
            service_content = f"""[Unit]
Description=Coding Rule2 Real-time Monitoring Service
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=forking
User={os.getenv("USER", "root")}
Group={os.getenv("USER", "root")}
WorkingDirectory={self.project_root}
ExecStart={sys.executable} {__file__} start --daemon
ExecStop={sys.executable} {__file__} stop
ExecReload={sys.executable} {__file__} restart
PIDFile={self.pid_file}
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
"""

            service_file = Path(f"/etc/systemd/system/{self.service_name}.service")

            # Write service file (requires sudo)
            print(f"Creating systemd service file at {service_file}")
            print("Note: This requires sudo privileges")
            print("\nService file content:")
            print(service_content)
            print("\nTo install manually:")
            print(f"sudo tee {service_file} > /dev/null << 'EOF'")
            print(service_content)
            print("EOF")
            print("sudo systemctl daemon-reload")
            print(f"sudo systemctl enable {self.service_name}")
            print(f"sudo systemctl start {self.service_name}")

            return True

        except Exception as e:
            self.logger.error(f"Systemd service creation failed: {e}")
            return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Monitoring Service Management")
    parser.add_argument(
        "action",
        choices=["start", "stop", "restart", "status", "health", "systemd"],
        help="Service action",
    )
    parser.add_argument("--daemon", action="store_true", help="Run as daemon")
    parser.add_argument("--config", help="Configuration file path")

    args = parser.parse_args()

    # Initialize service
    service = MonitoringService()

    if args.action == "start":
        success = service.start(daemon=args.daemon)
        sys.exit(0 if success else 1)

    elif args.action == "stop":
        success = service.stop()
        sys.exit(0 if success else 1)

    elif args.action == "restart":
        success = service.restart()
        sys.exit(0 if success else 1)

    elif args.action == "status":
        status = service.status()
        print(json.dumps(status, indent=2, default=str))

        if status.get("is_running"):
            print(f"\n✅ Service is running (PID: {status.get('pid')})")
        else:
            print("\n❌ Service is not running")

    elif args.action == "health":
        health = service.health_check()
        print(json.dumps(health, indent=2, default=str))

        if health.get("healthy"):
            print("\n✅ Service is healthy")
        else:
            print(f"\n❌ Service health issues: {health.get('issues', [])}")

    elif args.action == "systemd":
        service.create_systemd_service()


if __name__ == "__main__":
    main()
