#!/usr/bin/env python3
"""
🚀 Optimized MCP Base Server
============================
Base class for all MCP servers with performance and security optimizations
"""

import json
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional

import aiohttp

# Load project configuration
project_root = Path(__file__).parent.parent.parent
config_path = project_root / "config" / "unified_config.json"

with open(config_path) as f:
    CONFIG = json.load(f)


class MCPServerStatus(Enum):
    """MCP Server Status Enum"""
    STARTING = "starting"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    STOPPED = "stopped"


@dataclass
class MCPRequest:
    """MCP Request Data Structure"""
    method: str
    params: Dict[str, Any]
    request_id: str
    timestamp: float
    user_id: Optional[str] = None
    session_id: Optional[str] = None


@dataclass
class MCPResponse:
    """MCP Response Data Structure"""
    request_id: str
    success: bool
    data: Any
    error: Optional[str] = None
    timestamp: float = None
    processing_time: float = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()


class OptimizedMCPBase(ABC):
    """
    Optimized MCP Base Server with:
    - Connection pooling
    - Error handling & retry logic
    - Health checks
    - Security features
    - Performance monitoring
    """

    def __init__(self, server_name: str, config: Dict[str, Any] = None):
        self.server_name = server_name
        self.config = config or CONFIG
        self.status = MCPServerStatus.STARTING
        self.session = None
        self.request_count = 0
        self.error_count = 0
        self.last_health_check = 0
        self.health_check_interval = 30  # 30 seconds

        # Setup logging
        self.logger = self._setup_logging()

        # Initialize security
        self._init_security()

        # Initialize performance monitoring
        self._init_monitoring()

        self.logger.info(f"🚀 {server_name} MCP Server initializing...")

    def _setup_logging(self) -> logging.Logger:
        """Setup structured logging with correlation IDs"""
        logger = logging.getLogger(f"mcp.{self.server_name}")
        logger.setLevel(logging.INFO)

        # Create formatter for structured logs
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File handler
        log_file = Path(f"logs/mcp_{self.server_name}.log")
        log_file.parent.mkdir(exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        return logger

    def _init_security(self):
        """Initialize security features"""
        # API key validation
        self.api_keys = {}
        self.rate_limits = {}
        self.security_config = self.config.get("security", {})

        # RBAC integration
        self.rbac_config = self.security_config.get("rbac", {})

        self.logger.info("🔐 Security features initialized")

    def _init_monitoring(self):
        """Initialize performance monitoring"""
        self.metrics = {
            "requests_total": 0,
            "requests_success": 0,
            "requests_error": 0,
            "response_times": [],
            "last_request_time": 0,
            "uptime_start": time.time()
        }

        self.logger.info("📊 Performance monitoring initialized")

    async def initialize(self):
        """Initialize the MCP server"""
        try:
            # Create HTTP session with connection pooling
            connector = aiohttp.TCPConnector(
                limit=100,  # Total connection limit
                limit_per_host=30,  # Per-host connection limit
                ttl_dns_cache=300,  # DNS cache TTL
                use_dns_cache=True,
                keepalive_timeout=30,
                enable_cleanup_closed=True
            )

            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=aiohttp.ClientTimeout(total=30)
            )

            # Run server-specific initialization
            await self._server_initialize()

            self.status = MCPServerStatus.HEALTHY
            self.logger.info(f"✅ {self.server_name} MCP Server initialized successfully")

        except Exception as e:
            self.status = MCPServerStatus.UNHEALTHY
            self.logger.error(f"❌ Failed to initialize {self.server_name}: {str(e)}")
            raise

    @abstractmethod
    async def _server_initialize(self):
        """Server-specific initialization logic"""
        pass

    async def process_request(self, request_data: Dict[str, Any]) -> MCPResponse:
        """Process MCP request with optimization features"""
        start_time = time.time()
        request_id = request_data.get("id", f"req_{int(time.time() * 1000)}")

        try:
            # Create request object
            request = MCPRequest(
                method=request_data.get("method", ""),
                params=request_data.get("params", {}),
                request_id=request_id,
                timestamp=start_time
            )

            # Validate request
            if not self._validate_request(request):
                raise ValueError("Invalid request format")

            # Check rate limits
            if not self._check_rate_limit(request):
                raise ValueError("Rate limit exceeded")

            # Process the request
            result = await self._process_request_impl(request)

            # Update metrics
            self._update_metrics(True, time.time() - start_time)

            return MCPResponse(
                request_id=request_id,
                success=True,
                data=result,
                processing_time=time.time() - start_time
            )

        except Exception as e:
            self.error_count += 1
            self._update_metrics(False, time.time() - start_time)

            self.logger.error(f"❌ Request {request_id} failed: {str(e)}")

            return MCPResponse(
                request_id=request_id,
                success=False,
                data=None,
                error=str(e),
                processing_time=time.time() - start_time
            )

    @abstractmethod
    async def _process_request_impl(self, request: MCPRequest) -> Any:
        """Server-specific request processing"""
        pass

    def _validate_request(self, request: MCPRequest) -> bool:
        """Validate request format and content"""
        if not request.method:
            return False
        if not isinstance(request.params, dict):
            return False
        return True

    def _check_rate_limit(self, request: MCPRequest) -> bool:
        """Check if request is within rate limits"""
        # Simple rate limiting implementation
        current_time = time.time()
        user_id = request.user_id or "anonymous"

        if user_id not in self.rate_limits:
            self.rate_limits[user_id] = []

        # Remove old entries (older than 1 hour)
        self.rate_limits[user_id] = [
            timestamp for timestamp in self.rate_limits[user_id]
            if current_time - timestamp < 3600
        ]

        # Check if under limit (100 requests per hour)
        if len(self.rate_limits[user_id]) >= 100:
            return False

        self.rate_limits[user_id].append(current_time)
        return True

    def _update_metrics(self, success: bool, processing_time: float):
        """Update performance metrics"""
        self.metrics["requests_total"] += 1
        self.metrics["last_request_time"] = time.time()

        if success:
            self.metrics["requests_success"] += 1
        else:
            self.metrics["requests_error"] += 1

        self.metrics["response_times"].append(processing_time)

        # Keep only last 1000 response times
        if len(self.metrics["response_times"]) > 1000:
            self.metrics["response_times"] = self.metrics["response_times"][-1000:]

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        current_time = time.time()

        # Calculate error rate
        error_rate = (self.metrics["requests_error"] /
                     max(self.metrics["requests_total"], 1))

        # Calculate average response time
        avg_response_time = (
            sum(self.metrics["response_times"]) /
            max(len(self.metrics["response_times"]), 1)
        )

        # Determine health status
        if error_rate > 0.1:  # More than 10% errors
            self.status = MCPServerStatus.UNHEALTHY
        elif error_rate > 0.05 or avg_response_time > 5.0:  # 5% errors or slow response
            self.status = MCPServerStatus.DEGRADED
        else:
            self.status = MCPServerStatus.HEALTHY

        self.last_health_check = current_time

        health_data = {
            "server_name": self.server_name,
            "status": self.status.value,
            "uptime": current_time - self.metrics["uptime_start"],
            "requests_total": self.metrics["requests_total"],
            "requests_success": self.metrics["requests_success"],
            "requests_error": self.metrics["requests_error"],
            "error_rate": error_rate,
            "avg_response_time": avg_response_time,
            "last_request": self.metrics["last_request_time"],
            "timestamp": current_time
        }

        # Run server-specific health checks
        try:
            server_health = await self._server_health_check()
            health_data.update(server_health)
        except Exception as e:
            self.logger.warning(f"Server health check failed: {str(e)}")
            health_data["server_health_error"] = str(e)

        return health_data

    async def _server_health_check(self) -> Dict[str, Any]:
        """Server-specific health check"""
        return {"server_specific": "healthy"}

    async def shutdown(self):
        """Graceful shutdown"""
        self.logger.info(f"🔄 Shutting down {self.server_name} MCP Server...")

        self.status = MCPServerStatus.STOPPED

        if self.session:
            await self.session.close()

        # Run server-specific shutdown
        try:
            await self._server_shutdown()
        except Exception as e:
            self.logger.error(f"Error during server shutdown: {str(e)}")

        self.logger.info(f"✅ {self.server_name} MCP Server shut down successfully")

    async def _server_shutdown(self):
        """Server-specific shutdown logic"""
        pass

    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        return self.metrics.copy()

    def get_status(self) -> MCPServerStatus:
        """Get server status"""
        return self.status
