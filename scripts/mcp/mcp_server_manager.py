#!/usr/bin/env python3
"""
🎛️ MCP Server Manager
=====================
Centralized management for all MCP servers with monitoring and optimization
"""

import asyncio
import json
import logging
import os
import signal
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import psutil

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.mcp.optimized_mcp_base import MCPServerStatus  # noqa: E402


class MCPServerManager:
    """
    Centralized MCP Server Manager with:
    - Multi-server orchestration
    - Health monitoring
    - Performance optimization
    - Centralized logging
    - Graceful shutdown
    """

    def __init__(self):
        self.servers = {}
        self.processes = {}
        self.config = self._load_config()
        self.logger = self._setup_logging()
        self.running = False
        self.monitoring_interval = 30  # 30 seconds
        self.last_health_check = 0

        # Performance metrics
        self.metrics = {
            "total_requests": 0,
            "total_errors": 0,
            "avg_response_time": 0,
            "servers_healthy": 0,
            "servers_total": 0,
            "uptime_start": time.time()
        }

        self.logger.info("🎛️ MCP Server Manager initialized")

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from unified config"""
        config_path = project_root / "config" / "unified_config.json"

        try:
            with open(config_path) as f:
                config = json.load(f)
            return config
        except Exception as e:
            print(f"❌ Failed to load config: {str(e)}")
            return {}

    def _setup_logging(self) -> logging.Logger:
        """Setup centralized logging"""
        logger = logging.getLogger("mcp.manager")
        logger.setLevel(logging.INFO)

        # Create logs directory
        log_dir = project_root / "logs"
        log_dir.mkdir(exist_ok=True)

        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File handler
        file_handler = logging.FileHandler(log_dir / "mcp_manager.log")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        return logger

    async def start_all_servers(self):
        """Start all configured MCP servers"""
        self.logger.info("🚀 Starting all MCP servers...")
        self.running = True

        mcp_config = self.config.get("mcp", {}).get("mcpServers", {})

        for server_name, server_config in mcp_config.items():
            try:
                await self._start_server(server_name, server_config)
            except Exception as e:
                self.logger.error(f"❌ Failed to start server {server_name}: {str(e)}")

        # Start monitoring
        asyncio.create_task(self._monitoring_loop())

        self.logger.info(f"✅ Started {len(self.servers)} MCP servers")

    async def _start_server(self, server_name: str, config: Dict[str, Any]):
        """Start a specific MCP server"""
        self.logger.info(f"🔄 Starting server: {server_name}")

        command = config.get("command", "")
        args = config.get("args", [])
        env = config.get("env", {})

        try:
            # Prepare environment
            server_env = os.environ.copy()
            server_env.update(env)

            # Start the server process
            process = await asyncio.create_subprocess_exec(
                command,
                *args,
                env=server_env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(project_root)
            )

            self.processes[server_name] = {
                "process": process,
                "config": config,
                "start_time": time.time(),
                "status": MCPServerStatus.STARTING,
                "restart_count": 0
            }

            # Monitor process output
            asyncio.create_task(self._monitor_process_output(server_name, process))

            self.logger.info(f"✅ Server {server_name} started with PID {process.pid}")

        except Exception as e:
            self.logger.error(f"❌ Failed to start server {server_name}: {str(e)}")
            raise

    async def _monitor_process_output(self, server_name: str, process: asyncio.subprocess.Process):
        """Monitor process output for logging"""
        try:
            async for line in process.stdout:
                line_str = line.decode().strip()
                if line_str:
                    self.logger.info(f"[{server_name}] {line_str}")

            async for line in process.stderr:
                line_str = line.decode().strip()
                if line_str:
                    self.logger.error(f"[{server_name}] {line_str}")

        except Exception as e:
            self.logger.error(f"❌ Error monitoring {server_name} output: {str(e)}")

    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                await self._perform_health_checks()
                await self._collect_metrics()
                await self._handle_failed_servers()

                await asyncio.sleep(self.monitoring_interval)

            except Exception as e:
                self.logger.error(f"❌ Monitoring error: {str(e)}")
                await asyncio.sleep(5)

    async def _perform_health_checks(self):
        """Perform health checks on all servers"""
        self.logger.debug("🔍 Performing health checks...")

        healthy_count = 0
        total_count = len(self.processes)

        for server_name, server_info in self.processes.items():
            try:
                process = server_info["process"]

                # Check if process is still running
                if process.returncode is not None:
                    server_info["status"] = MCPServerStatus.UNHEALTHY
                    self.logger.warning(f"⚠️ Server {server_name} process died")
                    continue

                # Check system resources
                try:
                    proc = psutil.Process(process.pid)
                    cpu_percent = proc.cpu_percent()
                    memory_percent = proc.memory_percent()

                    # Log resource usage
                    self.logger.debug(f"📊 {server_name} - CPU: {cpu_percent:.1f}%, Memory: {memory_percent:.1f}%")

                    # Check for resource issues
                    if cpu_percent > 80 or memory_percent > 80:
                        server_info["status"] = MCPServerStatus.DEGRADED
                        self.logger.warning(f"⚠️ Server {server_name} high resource usage")
                    else:
                        server_info["status"] = MCPServerStatus.HEALTHY
                        healthy_count += 1

                except psutil.NoSuchProcess:
                    server_info["status"] = MCPServerStatus.UNHEALTHY
                    self.logger.error(f"❌ Server {server_name} process not found")

            except Exception as e:
                self.logger.error(f"❌ Health check failed for {server_name}: {str(e)}")
                server_info["status"] = MCPServerStatus.UNHEALTHY

        # Update global metrics
        self.metrics["servers_healthy"] = healthy_count
        self.metrics["servers_total"] = total_count

        self.logger.info(f"📊 Health check: {healthy_count}/{total_count} servers healthy")

    async def _collect_metrics(self):
        """Collect performance metrics"""
        # This would typically integrate with individual server metrics
        uptime = time.time() - self.metrics["uptime_start"]

        metrics_summary = {
            "timestamp": datetime.now().isoformat(),
            "uptime": uptime,
            "servers_healthy": self.metrics["servers_healthy"],
            "servers_total": self.metrics["servers_total"],
            "total_requests": self.metrics["total_requests"],
            "total_errors": self.metrics["total_errors"]
        }

        # Save metrics to file
        metrics_file = project_root / "runtime" / "mcp_metrics.json"
        metrics_file.parent.mkdir(exist_ok=True)

        with open(metrics_file, 'w') as f:
            json.dump(metrics_summary, f, indent=2)

    async def _handle_failed_servers(self):
        """Handle failed servers with restart logic"""
        for server_name, server_info in self.processes.items():
            if server_info["status"] == MCPServerStatus.UNHEALTHY:

                # Check if we should restart
                if server_info["restart_count"] < 3:  # Max 3 restarts
                    self.logger.info(f"🔄 Restarting failed server: {server_name}")

                    try:
                        # Stop the old process
                        if server_info["process"].returncode is None:
                            server_info["process"].terminate()
                            await asyncio.sleep(2)
                            if server_info["process"].returncode is None:
                                server_info["process"].kill()

                        # Start new process
                        await self._start_server(server_name, server_info["config"])
                        server_info["restart_count"] += 1

                        self.logger.info(f"✅ Server {server_name} restarted")

                    except Exception as e:
                        self.logger.error(f"❌ Failed to restart server {server_name}: {str(e)}")

                else:
                    self.logger.error(f"❌ Server {server_name} failed too many times, not restarting")

    async def stop_all_servers(self):
        """Stop all MCP servers gracefully"""
        self.logger.info("🔄 Stopping all MCP servers...")
        self.running = False

        for server_name, server_info in self.processes.items():
            try:
                process = server_info["process"]

                if process.returncode is None:
                    self.logger.info(f"🔄 Stopping server: {server_name}")

                    # Send SIGTERM first
                    process.terminate()

                    # Wait for graceful shutdown
                    try:
                        await asyncio.wait_for(process.wait(), timeout=10)
                    except asyncio.TimeoutError:
                        # Force kill if not responding
                        self.logger.warning(f"⚠️ Force killing server: {server_name}")
                        process.kill()
                        await process.wait()

                    self.logger.info(f"✅ Server {server_name} stopped")

            except Exception as e:
                self.logger.error(f"❌ Error stopping server {server_name}: {str(e)}")

        self.logger.info("✅ All MCP servers stopped")

    async def get_server_status(self) -> Dict[str, Any]:
        """Get status of all servers"""
        status = {
            "timestamp": datetime.now().isoformat(),
            "manager_status": "running" if self.running else "stopped",
            "metrics": self.metrics,
            "servers": {}
        }

        for server_name, server_info in self.processes.items():
            status["servers"][server_name] = {
                "status": server_info["status"].value,
                "start_time": server_info["start_time"],
                "restart_count": server_info["restart_count"],
                "pid": server_info["process"].pid if server_info["process"].returncode is None else None
            }

        return status

    async def restart_server(self, server_name: str):
        """Restart a specific server"""
        if server_name not in self.processes:
            raise ValueError(f"Server {server_name} not found")

        self.logger.info(f"🔄 Restarting server: {server_name}")

        server_info = self.processes[server_name]

        # Stop the current process
        if server_info["process"].returncode is None:
            server_info["process"].terminate()
            await asyncio.sleep(2)
            if server_info["process"].returncode is None:
                server_info["process"].kill()

        # Start new process
        await self._start_server(server_name, server_info["config"])

        self.logger.info(f"✅ Server {server_name} restarted")

    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            self.logger.info(f"🔄 Received signal {signum}, shutting down...")
            asyncio.create_task(self.stop_all_servers())

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)


async def main():
    """Main function"""
    manager = MCPServerManager()

    try:
        manager._setup_signal_handlers()
        await manager.start_all_servers()

        # Keep running until shutdown
        while manager.running:
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        manager.logger.info("🔄 Received shutdown signal")
    except Exception as e:
        manager.logger.error(f"❌ Manager error: {str(e)}")
    finally:
        await manager.stop_all_servers()


if __name__ == "__main__":
    asyncio.run(main())
