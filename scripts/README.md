# 📁 Scripts Directory Organization

**Status**: PRESIDENT承認済み・Gemini推奨構造実装完了  
**Last Updated**: 2025-07-08T11:30:00+09:00  
**Organization**: Function-based hierarchy following Unix conventions

## 🎯 Directory Structure

### `bin/` - Critical Entry Points
**Purpose**: User-facing commands and critical system entry points  
**Contents**:
- `start-president` - Primary AI system launcher
- `start-ai-workers` - Multi-agent worker system
- `task` - Task management command

**Rules**:
- ✅ Must be executable by end users
- ✅ No `.sh` extension (user commands)
- ❌ No library functions here

### `lib/` - Shared Libraries
**Purpose**: Reusable functions sourced by other scripts  
**Contents**:
- `utils.sh` - Common utility functions

**Rules**:
- ✅ Functions only, not standalone scripts
- ✅ Must use `.sh` extension
- ❌ Not directly executable

### `rules/` - Rules Management
**Purpose**: Configuration rule management and synchronization  
**Contents**:
- `check-cursor-rules` - Cursor rules validation
- `sync-cursor-rules.sh` - Rules synchronization
- `analyze-rule-duplicates.py` - Duplicate detection

**Rules**:
- ✅ Rule validation and management only
- ✅ IDE configuration related
- ❌ No general utilities here

### `maintenance/` - System Maintenance
**Purpose**: System health, cleanup, and structural maintenance

#### `maintenance/structure/`
- `analyze-internal-structure.py` - Project structure analysis
- `comprehensive-structure-evaluation.py` - Complete evaluation
- `one-command-structure-optimization.py` - Automated optimization

**Rules**:
- ✅ System health and organization
- ✅ Automated maintenance tasks
- ❌ No user-facing features

### `tools/` - Specialized Tools
**Purpose**: Focused utility tools organized by domain

#### `tools/memory/`
- `quick-memory-check.sh` - Memory system validation
- `test-memory-inheritance.sh` - Inheritance testing

#### `tools/monitoring/`
- Monitoring and observability tools

#### `tools/validation/`
- `validate-file-creation.py` - File creation validation

**Rules**:
- ✅ Domain-specific tooling
- ✅ Organized by functional area
- ❌ No general-purpose scripts

### `automation/` - Setup and Configuration
**Purpose**: Environment setup and automated configuration  
**Contents**: Setup scripts for development environment

### `cleanup/` - Cleanup Operations
**Purpose**: System cleanup and maintenance operations

### `hooks/` - Git and System Hooks
**Purpose**: Pre/post execution hooks for various triggers

### `startup/` - Startup Scripts
**Purpose**: System initialization scripts

## 🔧 Enforcement Mechanisms

### Automated Validation
```bash
# Organization check (run on commit)
scripts/tests/check-script-organization.sh

# Directory size limits
# bin/: Max 10 files
# lib/: Max 5 files  
# utilities/: DEPRECATED - use tools/
```

### Naming Conventions
- **User commands**: No extension (e.g., `start-president`)
- **Libraries**: `.sh` extension (e.g., `utils.sh`)
- **Python tools**: `.py` extension with descriptive names
- **Format**: `verb-noun` pattern (e.g., `check-cursor-rules`)

### File Placement Rules

#### ✅ ALLOWED in each directory:
- `bin/`: Executable user commands only
- `lib/`: Shared functions only  
- `rules/`: Rule management only
- `maintenance/structure/`: Structure analysis only
- `tools/{domain}/`: Domain-specific tools only

#### ❌ FORBIDDEN:
- New files in `scripts/` root
- General utilities in specialized directories
- User commands outside `bin/`
- Library functions outside `lib/`

## 📊 Migration Status

### ✅ Completed Moves
- Critical scripts → `bin/`
- Rules scripts → `rules/`
- Structure scripts → `maintenance/structure/`
- Memory tools → `tools/memory/`
- Validation tools → `tools/validation/`
- Shared libraries → `lib/`

### 🔄 Remaining Cleanup
- Break down remaining `utilities/` scripts by domain
- Implement automated organization validation
- Create comprehensive tests

## 🚨 Violation Prevention

### Pre-commit Hook Integration
```python
# scripts/hooks/script_organization_enforcer.py
def validate_script_placement(file_path):
    if file_path.startswith('scripts/') and not categorized_properly(file_path):
        return BLOCK_COMMIT_WITH_ORGANIZATION_ERROR
```

### CI/CD Pipeline Check
```bash
# .github/workflows/organization-check.yml
- name: Validate Script Organization
  run: scripts/tests/check-script-organization.sh
```

---

**Important**: This organization follows industry best practices from Linux Kernel, Docker, and Kubernetes projects. Any deviation requires PRESIDENT approval and documentation update.