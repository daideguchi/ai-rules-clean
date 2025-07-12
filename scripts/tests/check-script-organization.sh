#!/bin/bash
set -euo pipefail

# Script Organization Validation
# Enforces directory structure rules established in scripts/README.md

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SCRIPTS_DIR="$PROJECT_ROOT/scripts"
VIOLATIONS=()
EXIT_CODE=0

echo "🔍 Validating script organization..."

# Check bin/ directory rules
echo "Checking bin/ directory..."
if [[ -d "$SCRIPTS_DIR/bin" ]]; then
    BIN_COUNT=$(find "$SCRIPTS_DIR/bin" -maxdepth 1 -type f | wc -l)
    if [[ $BIN_COUNT -gt 10 ]]; then
        VIOLATIONS+=("bin/ directory has $BIN_COUNT files (max 10 allowed)")
        EXIT_CODE=1
    fi
    
    # Check for library functions in bin/
    while IFS= read -r -d '' file; do
        if grep -q "^function\|^[a-zA-Z_][a-zA-Z0-9_]*() {" "$file"; then
            VIOLATIONS+=("bin/$(basename "$file") contains function definitions (move to lib/)")
            EXIT_CODE=1
        fi
    done < <(find "$SCRIPTS_DIR/bin" -type f -print0)
fi

# Check lib/ directory rules
echo "Checking lib/ directory..."
if [[ -d "$SCRIPTS_DIR/lib" ]]; then
    LIB_COUNT=$(find "$SCRIPTS_DIR/lib" -maxdepth 1 -type f | wc -l)
    if [[ $LIB_COUNT -gt 5 ]]; then
        VIOLATIONS+=("lib/ directory has $LIB_COUNT files (max 5 allowed)")
        EXIT_CODE=1
    fi
    
    # Check for executable files in lib/
    while IFS= read -r -d '' file; do
        if [[ -x "$file" ]]; then
            VIOLATIONS+=("lib/$(basename "$file") is executable (libraries should not be executable)")
            EXIT_CODE=1
        fi
    done < <(find "$SCRIPTS_DIR/lib" -type f -print0)
fi

# Check for files in scripts/ root (forbidden)
echo "Checking scripts/ root directory..."
ROOT_FILES=$(find "$SCRIPTS_DIR" -maxdepth 1 -type f -not -name "README.md" -not -name "DEPENDENCIES.md" | wc -l)
if [[ $ROOT_FILES -gt 0 ]]; then
    while IFS= read -r file; do
        if [[ "$(basename "$file")" != "README.md" && "$(basename "$file")" != "DEPENDENCIES.md" ]]; then
            VIOLATIONS+=("File in scripts/ root: $(basename "$file") (move to appropriate subdirectory)")
            EXIT_CODE=1
        fi
    done < <(find "$SCRIPTS_DIR" -maxdepth 1 -type f)
fi

# Check naming conventions
echo "Checking naming conventions..."
while IFS= read -r -d '' file; do
    basename_file=$(basename "$file")
    
    # Check bin/ files (no .sh extension)
    if [[ "$file" == *"/bin/"* && "$basename_file" == *.sh ]]; then
        VIOLATIONS+=("bin/$basename_file has .sh extension (user commands should not have extensions)")
        EXIT_CODE=1
    fi
    
    # Check lib/ files (must have .sh extension)
    if [[ "$file" == *"/lib/"* && "$basename_file" != *.sh ]]; then
        VIOLATIONS+=("lib/$basename_file missing .sh extension (libraries must have .sh extension)")
        EXIT_CODE=1
    fi
    
    # Check hyphen-separated naming
    if [[ "$basename_file" =~ [A-Z] && "$file" != *"/hooks/"* ]]; then
        VIOLATIONS+=("$basename_file uses uppercase (prefer hyphen-separated lowercase)")
        EXIT_CODE=1
    fi
done < <(find "$SCRIPTS_DIR" -type f -executable -print0)

# Check utilities/ deprecation
if [[ -d "$SCRIPTS_DIR/utilities" ]]; then
    UTIL_COUNT=$(find "$SCRIPTS_DIR/utilities" -type f | wc -l)
    if [[ $UTIL_COUNT -gt 0 ]]; then
        VIOLATIONS+=("utilities/ directory is deprecated (move scripts to tools/ subdirectories)")
        EXIT_CODE=1
    fi
fi

# Report results
echo ""
if [[ ${#VIOLATIONS[@]} -eq 0 ]]; then
    echo "✅ Script organization validation passed!"
    echo "📊 Summary:"
    echo "   - bin/ files: $(find "$SCRIPTS_DIR/bin" -type f 2>/dev/null | wc -l)"
    echo "   - lib/ files: $(find "$SCRIPTS_DIR/lib" -type f 2>/dev/null | wc -l)"
    echo "   - rules/ files: $(find "$SCRIPTS_DIR/rules" -type f 2>/dev/null | wc -l)"
    echo "   - tools/ files: $(find "$SCRIPTS_DIR/tools" -type f 2>/dev/null | wc -l)"
else
    echo "❌ Script organization validation failed!"
    echo ""
    echo "Violations found:"
    for violation in "${VIOLATIONS[@]}"; do
        echo "  • $violation"
    done
    echo ""
    echo "📖 See scripts/README.md for organization rules"
fi

exit $EXIT_CODE