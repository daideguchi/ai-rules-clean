# MCP Integration System

## Overview
This directory contains all Model Context Protocol (MCP) integration components for the AI Safety Governance System.

## Directory Structure
```
mcp_integration/
├── servers/          # MCP server implementations
│   ├── gemini_mcp_server.py
│   └── o3_mcp_server.py
├── clients/          # MCP client implementations
│   ├── mcp_database_client.py
│   └── claude_code_complete_mcp_integration.py
├── bridges/          # Integration bridges
│   └── claude_cursor_mcp_bridge.py
├── configs/          # Configuration files
│   └── postgres-mcp-server.json
├── hooks/            # MCP-related hooks
│   └── pre_mcp_logger.py
└── docs/             # Documentation
    ├── README.md
    ├── server_configuration.md
    └── client_usage.md
```

## Quick Start

### 1. Server Setup
```bash
# Start Gemini MCP server
python mcp_integration/servers/gemini_mcp_server.py

# Start o3 MCP server
python mcp_integration/servers/o3_mcp_server.py
```

### 2. Client Configuration
```python
from mcp_integration.clients import mcp_database_client

client = mcp_database_client.MCPDatabaseClient()
client.connect()
```

### 3. PostgreSQL Integration
Configure PostgreSQL MCP server using:
```bash
cat mcp_integration/configs/postgres-mcp-server.json
```

## Integration Points

### Claude Code Integration
- Full MCP support via `claude_code_complete_mcp_integration.py`
- Automatic session management
- Memory persistence through PostgreSQL

### Multi-Agent Monitoring
- Gemini server for secondary validation
- o3 server for tertiary checks
- Unified logging through MCP hooks

## Configuration

### Environment Variables
```bash
export MCP_SERVER_HOST="localhost"
export MCP_SERVER_PORT="8080"
export MCP_DATABASE_URL="postgresql://user:pass@localhost/db"
```

### Server Configuration
See `configs/postgres-mcp-server.json` for database server setup.

## Troubleshooting

### Common Issues
1. **Connection refused**: Check server is running
2. **Authentication failed**: Verify credentials in config
3. **Timeout errors**: Increase timeout in client settings

### Logs
- Server logs: `runtime/logs/mcp_server.log`
- Client logs: `runtime/logs/mcp_client.log`
- Hook logs: `runtime/logs/pre_mcp_logger.log`

## Development

### Adding New Servers
1. Create server in `servers/` directory
2. Implement MCP protocol interface
3. Add configuration in `configs/`
4. Update documentation

### Testing
```bash
python -m pytest tests/mcp/
```
