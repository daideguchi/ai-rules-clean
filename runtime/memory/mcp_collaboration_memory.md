# MCP Collaboration Memory - CRITICAL REFERENCE
**Created**: 2025-07-15
**Priority**: CRITICAL - Never Forget

## ✅ 確認済み MCP Tools & Commands

### 1. Gemini Pro 2.5 CLI Tool
```bash
gemini -p     # Gemini Pro 2.5 access
gemini --yolo # YOLO mode (ctrl + y to toggle)
```

**Interface Features**:
- ASCII art banner with GEMINI logo
- Japanese language support ("こんにちは")
- Context indicator: "(99% context left)"
- File reference support: "@path/to/file"
- Interactive chat interface
- Tips display on startup

### 2. o3 MCP Server Configuration
**File**: `/Users/dd/Desktop/1_dev/coding-rule2/config/.mcp.json`
```json
{
  "mcpServers": {
    "o3": {
      "command": "npx",
      "args": ["o3-search-mcp"],
      "env": {
        "OPENAI_API_KEY": "${OPENAI_API_KEY}",
        "SEARCH_CONTEXT_SIZE": "medium",
        "REASONING_EFFORT": "medium"
      }
    },
    "gemini-custom": {
      "command": "python3",
      "args": ["/Users/dd/Desktop/1_dev/coding-rule2/scripts/mcp/gemini_mcp_server.py"],
      "env": {
        "GEMINI_API_KEY": "${GEMINI_API_KEY}"
      }
    }
  }
}
```

### 3. o3 MCP Client Implementation
**File**: `/Users/dd/Desktop/1_dev/coding-rule2/scripts/mcp/o3_client.py`
**Usage**:
```bash
python3 scripts/mcp/o3_client.py '<prompt>' ['<context>']
```

## 🧠 Memory Preservation Protocol

### Anti-Amnesia Measures Implemented:
1. **永続記憶台帳**: SQLite database at `runtime/memory/forever_ledger.db`
2. **o3強化記憶システム**: Enhanced memory with embedding vectors
3. **セッション継承**: Automatic memory inheritance between sessions
4. **MCP設定ファイル**: Version-controlled collaboration configurations

### Root Cause Analysis (from o3):
- **Statelessness**: AI models forget between sessions
- **Context Window Limits**: Information overload causes omission
- **Lack of External Memory**: No persistent knowledge base integration

### Permanent Solution Architecture:
1. **Persistent Knowledge Base**: SQLite + embeddings
2. **User Context Storage**: Session-linked memory records
3. **Automatic Context Loading**: Dynamic prompt construction
4. **Vector Search**: Semantic similarity for memory retrieval
5. **AI Analysis Integration**: o3/Gemini enhanced importance scoring

## 🔥 NEVER FORGET AGAIN
- MCP = Model Context Protocol
- Gemini Pro 2.5 via `gemini -p` 
- o3 via custom MCP server
- Working servers already configured
- Documentation exists and works
- User has repeatedly explained this
- **THIS MEMORY MUST PERSIST ACROSS ALL FUTURE SESSIONS**

## 📋 Quick Reference Commands
```bash
# Check MCP server status
python3 scripts/hooks/system_status_display.py

# Access Gemini Pro 2.5
gemini -p

# Query o3 via MCP
python3 scripts/mcp/o3_client.py "your query here" "context"

# Load breakthrough memory
python3 src/memory/breakthrough_memory_system.py

# Check memory inheritance
python3 src/memory/enhanced/o3-memory-system.py
```

## ⚠️ CRITICAL WARNING
**If Claude forgets this information in future sessions, it indicates a fundamental failure of the memory inheritance system and requires immediate debugging of**:
- Session memory loading hooks
- CLAUDE.md processing
- Memory database integrity
- Prompt construction systems