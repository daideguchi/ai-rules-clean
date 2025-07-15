# Project Local Memory - Coding Rule 2

@./CLAUDE.md
@~/.claude/CLAUDE.md

## Project-Specific Settings

### Language Usage Rules (Enforced)
- 宣言: 日本語 (## 🎯 これから行うこと)
- 処理: English (Technical implementation)  
- 報告: 日本語 (## ✅ 完遂報告)

### System Status Display (Mandatory)
- **Every response must include**: DB connection, API status, active todos, task level
- **Auto-display hook**: `python3 scripts/hooks/system_status_display.py`
- **Format**: Compact 4-line status at start of each response
- **No exceptions**: Even for simple tasks

### Autonomous Growth Protocol
- **No Apologies**: Technical analysis and system improvements instead
- **Mistake Pattern Learning**: Record to runtime/memory/forever_ledger.db
- **System-Level Fixes**: Implement preventive mechanisms
- **Continuous Monitoring**: Automatic detection and correction

### Status Bar Configuration
- Language: Japanese (default)
- Role display: Dynamic translation
- Task display: Real-time detection and translation

### Task Complexity & AI Collaboration System
- **Automatic complexity classification**: SIMPLE/STANDARD/COMPLEX/CRITICAL
- **Level-based file confirmation**: Efficient resource usage
- **AI collaboration triggers**: COMPLEX+ tasks automatically route to multiagent
- **Adaptive execution flow**: Right approach for right task

### 🎯 Cursor Rules Integration - CRITICAL
**基本的にCursorも使って開発を行う - Cursor Rules準拠必須**:
- .cursor/rules/globals.mdc: 180行の詳細開発ルール確認必須
- 絶対禁止ルール: 推測報告禁止、職務放棄禁止、手抜き禁止、虚偽報告禁止
- PRESIDENT必須確認プロトコル: globals.mdc確認完了必須
- Function-Based Grouping準拠: 8ディレクトリ制限遵守
- 作業記録システム: .cursor/rules/work-log.mdc記録必須
- 5分検索ルール: 推測前に5分間の検索実行
- 品質指標: 推測回答率0%、手順遵守率100%

### 📋 要件定義・仕様書重視 - CRITICAL  
**要件定義や仕様書に関してはとても重要**:
- AI Compliance Engine要件定義: docs/developer/specs/ai-compliance-engine-requirements-specification.md
- THINKING要件: docs/governance/THINKING_REQUIREMENTS.md
- 記憶継承要件: docs/memory/INHERITANCE_REQUIREMENTS.md
- AgentWeaver仕様: docs/developer/agentweaver/requirements-spec.md
- 実装前必須確認: 関連する要件定義・仕様書の精査
- 仕様準拠確認: 実装完了後の仕様書照合必須
- 要件トレーサビリティ: 実装と要件の対応関係明確化

### Adaptive Execution Algorithm
```
Claude Code startup
↓
【Auto-loading (Claude Code Standard)】
1. ./CLAUDE.md (Project memory) ← Auto-loaded
2. ~/.claude/CLAUDE.md (User memory) ← Auto-loaded  
3. ./.claude/claude.md (Project local) ← Auto-loaded
4. @import files recursively ← Auto-loaded (max 5 levels)
↓
【Cursor Rules Validation】
- .cursor/rules/globals.mdc validation
- 絶対禁止ルール extraction
- PRESIDENT必須確認プロトコル
↓
【Task Complexity Analysis】
- Automatic task classification (SIMPLE/STANDARD/COMPLEX/CRITICAL)
- Determine required confirmation level
- Check AI collaboration need
↓
【Level-based File Reading】
LEVEL 1 (SIMPLE): CLAUDE.md + cursor rules only
LEVEL 2 (STANDARD): + related docs + recent logs  
LEVEL 3 (COMPLEX): + full system docs + AI collaboration
LEVEL 4 (CRITICAL): + complete audit + multi-AI + user confirmation
↓
【Execution Method Selection】
SIMPLE: Direct execution
STANDARD: Planned execution  
COMPLEX: AI organization consultation
CRITICAL: Full collaboration + user approval
↓
【Work Execution Phase】
- Execute work based on determined approach
- Monitor and log collaborative decisions
```

### Memory Hierarchy (Claude Code Standard)
1. **User Memory**: `~/.claude/CLAUDE.md` - Global settings
2. **Project Memory**: `./CLAUDE.md` - Team-shared project instructions  
3. **Project Local Memory**: `./.claude/claude.md` - Local project-specific settings

### Auto-loading System
- Files are automatically loaded when Claude Code starts
- Recursive reading from current directory to root
- Maximum 5-level recursion depth
- Nested files read only when specific subtrees accessed

### Claude Code Best Practices Integration
- **Start Simple**: Begin with basic operations, increase complexity gradually
- **Batch Operations**: Group related changes for efficiency
- **Iterative Development**: Small incremental changes over large modifications
- **Strategic Memory**: Place CLAUDE.md files at appropriate hierarchy levels
- **Context-Aware Instructions**: Tailor to specific project areas
- **Focused Sessions**: Work on related tasks together
- **Parallel Processing**: Use concurrent operations when possible
- **Smart Caching**: Leverage Claude Code's memory and context caching

### Security & Safety (Never Compromise)
- **No Secrets in Memory**: Never include API keys or sensitive data
- **Access Control**: Be mindful of shared memory access
- **Backup Strategies**: Implement proper backup procedures
- **Code Review**: Maintain quality through regular reviews

### Reference Documentation
- Claude Code Memory System: https://docs.anthropic.com/ja/docs/claude-code/memory
- Claude Code Best Practices: https://www.anthropic.com/engineering/claude-code-best-practices
- Memory inheritance confirmation code: 7749
- File reference proof numbers: 8274, 6139, 7562

---
**Project Local Memory established for Coding Rule 2 - AI Safety Governance System**