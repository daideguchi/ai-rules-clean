#!/usr/bin/env python3
"""Organize MCP integration files and configurations."""

import json
import os
from pathlib import Path


class MCPOrganizer:
    def __init__(self):
        self.project_root = Path(".")
        self.mcp_dir = Path("mcp_integration")

    def create_mcp_structure(self):
        """Create organized MCP directory structure."""

        # Create directories
        for category in ["servers", "clients", "bridges", "configs", "hooks", "docs"]:
            (self.mcp_dir / category).mkdir(parents=True, exist_ok=True)

        # Generate MCP organization plan
        plan = {"current_files": {}, "proposed_moves": [], "new_documentation": []}

        # Find all MCP-related files
        mcp_files = []
        for pattern in ["*mcp*.py", "*mcp*.json", "*MCP*"]:
            mcp_files.extend(self.project_root.rglob(pattern))

        # Categorize files
        for file_path in mcp_files:
            if (
                "__pycache__" in str(file_path)
                or ".venv" in str(file_path)
                or "venv" in str(file_path)
            ):
                continue

            category = self.categorize_mcp_file(file_path)
            plan["current_files"][str(file_path)] = category

            if category:
                new_path = self.mcp_dir / category / file_path.name
                plan["proposed_moves"].append(
                    {"from": str(file_path), "to": str(new_path), "category": category}
                )

        # Add documentation needs
        plan["new_documentation"] = [
            {
                "file": "mcp_integration/docs/README.md",
                "content": "MCP Integration Overview and Setup Guide",
            },
            {
                "file": "mcp_integration/docs/server_configuration.md",
                "content": "MCP Server Configuration Guide",
            },
            {
                "file": "mcp_integration/docs/client_usage.md",
                "content": "MCP Client Usage Examples",
            },
        ]

        return plan

    def categorize_mcp_file(self, file_path):
        """Categorize MCP file based on name and location."""
        name = file_path.name.lower()
        path_str = str(file_path).lower()

        if "server" in name:
            return "servers"
        elif "client" in name:
            return "clients"
        elif "bridge" in name:
            return "bridges"
        elif name.endswith(".json"):
            return "configs"
        elif "hook" in path_str:
            return "hooks"
        elif name.endswith(".md"):
            return "docs"
        else:
            return None

    def create_mcp_documentation(self):
        """Create comprehensive MCP documentation."""
        readme_content = """# MCP Integration System

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
"""

        docs_dir = self.mcp_dir / "docs"
        docs_dir.mkdir(parents=True, exist_ok=True)

        with open(docs_dir / "README.md", "w") as f:
            f.write(readme_content)

        print(f"Created MCP documentation at {docs_dir}/README.md")

    def generate_migration_script(self, plan):
        """Generate script to migrate MCP files."""
        script_content = """#!/usr/bin/env python3
\"\"\"Migrate MCP files to organized structure.\"\"\"

import shutil
from pathlib import Path

migrations = {}

def migrate_files():
    for migration in migrations:
        src = Path(migration["from"])
        dst = Path(migration["to"])

        if src.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            print(f"Moving {{src}} -> {{dst}}")
            shutil.move(str(src), str(dst))
        else:
            print(f"Source not found: {{src}}")

if __name__ == "__main__":
    print("Starting MCP file migration...")
    migrate_files()
    print("Migration complete!")
""".format(json.dumps(plan["proposed_moves"], indent=4))

        script_path = self.project_root / "migrate_mcp_files.py"
        with open(script_path, "w") as f:
            f.write(script_content)

        os.chmod(script_path, 0o755)
        print(f"Created migration script at {script_path}")


if __name__ == "__main__":
    organizer = MCPOrganizer()

    print("=== MCP File Organization ===")

    # Analyze current state
    plan = organizer.create_mcp_structure()

    print(f"\nFound {len(plan['current_files'])} MCP-related files")

    print("\nProposed reorganization:")
    for category in ["servers", "clients", "bridges", "configs", "hooks"]:
        files = [m for m in plan["proposed_moves"] if m["category"] == category]
        if files:
            print(f"\n{category}:")
            for f in files:
                print(f"  - {Path(f['from']).name}")

    # Create documentation
    organizer.create_mcp_documentation()

    # Generate migration script
    organizer.generate_migration_script(plan)

    print("\n✅ MCP organization plan complete!")
    print("Run ./migrate_mcp_files.py to execute the migration")
