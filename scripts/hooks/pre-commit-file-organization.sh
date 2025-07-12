#!/bin/bash
# Pre-commit Hook: File Organization Enforcement (coding-rule2 specific)
# ファイル組織強制プリコミットフック (coding-rule2専用)
#
# Prevents commits when file organization rules are violated.
# ⚠️ WARNING: These rules are designed for coding-rule2 project only!
# When copying to other projects, customize the rules accordingly.

set -e

PROJECT_ROOT="$(git rev-parse --show-toplevel)"
cd "$PROJECT_ROOT"

echo "🔍 Checking file organization compliance..."

# Count files in root directory (only files, not directories)
ROOT_FILES=$(ls -la | grep "^-" | wc -l | tr -d ' ')
MAX_FILES=12

echo "📊 Root directory files: $ROOT_FILES/$MAX_FILES"

# Check if over limit
if [ "$ROOT_FILES" -gt "$MAX_FILES" ]; then
    echo ""
    echo "❌ COMMIT BLOCKED: Too many files in root directory"
    echo "🔴 Current: $ROOT_FILES files"
    echo "🔴 Maximum: $MAX_FILES files"
    echo ""
    echo "🔧 To fix this issue:"
    echo "   make enforce-file-organization"
    echo ""
    echo "📋 Files that should be moved:"
    
    # Show files that should be moved
    python3 scripts/automation/strict-file-organizer.py --check-only 2>/dev/null || {
        echo "   Run 'make check-file-organization' for details"
    }
    
    echo ""
    echo "🚨 COMMIT REJECTED - Fix file organization first"
    exit 1
fi

# Check for specific violations
VIOLATIONS_FOUND=false

# Check for editor config files in root (exclude .cursor directory which should stay)
EDITOR_FILES=$(ls .claude-project .forbidden-move .cursorrules .cursorignore .cursorindexignore 2>/dev/null || true)
if [ -n "$EDITOR_FILES" ]; then
    echo "❌ Editor config files found in root - should be in config/editor/"
    echo "$EDITOR_FILES" | sed 's/^/   /'
    echo "   (Note: .cursor/ directory should stay in root)"
    VIOLATIONS_FOUND=true
fi

# Check for git config files in root  
if ls .gitattributes .pre-commit-config.yaml 2>/dev/null | grep -q .; then
    echo "❌ Git config files found in root - should be in config/git/"
    VIOLATIONS_FOUND=true
fi

# Check for .env.example in root
if [ -f ".env.example" ]; then
    echo "❌ .env.example found in root - should be in scripts/setup/"
    VIOLATIONS_FOUND=true
fi

# Check for markdown files (except allowed ones)
FORBIDDEN_MD=$(ls *.md 2>/dev/null | grep -v -E "^(README|CLAUDE|Index)\.md$" || true)
if [ -n "$FORBIDDEN_MD" ]; then
    echo "❌ Markdown files found in root (except README.md, CLAUDE.md, Index.md):"
    echo "$FORBIDDEN_MD" | sed 's/^/   /'
    echo "   → Should be in docs/"
    VIOLATIONS_FOUND=true
fi

if [ "$VIOLATIONS_FOUND" = true ]; then
    echo ""
    echo "🔧 Quick fix: make enforce-file-organization"
    echo "🔍 Preview: make dry-run-organization"
    echo ""
    echo "🚨 COMMIT REJECTED - Fix violations first"
    exit 1
fi

echo "✅ File organization compliance check passed"
echo "✅ Commit allowed to proceed"
exit 0