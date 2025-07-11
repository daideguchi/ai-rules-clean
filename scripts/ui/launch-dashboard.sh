#!/bin/bash
# 🎯 AI Organization Dashboard Launcher
# ====================================

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$PROJECT_ROOT"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🎯 AI Organization Dashboard Launcher${NC}"
echo "===================================="

# Check if running in proper environment
if [[ -z "$VIRTUAL_ENV" ]] && [[ ! -f "venv/bin/activate" ]]; then
    echo -e "${YELLOW}⚠️  Virtual environment not detected${NC}"
    echo "Consider running: python -m venv venv && source venv/bin/activate"
fi

# Check dependencies
echo -e "${BLUE}📦 Checking dependencies...${NC}"

if ! python -c "import rich" 2>/dev/null; then
    echo -e "${RED}❌ Rich library not installed${NC}"
    echo "Installing UI dependencies..."
    pip install -r requirements-ui.txt
fi

# Check core systems
echo -e "${BLUE}🔍 Checking core systems...${NC}"

# Check AI organization system
if [[ -f "src/ai/ai_organization_system.py" ]]; then
    echo -e "${GREEN}✅ AI Organization System found${NC}"
else
    echo -e "${YELLOW}⚠️  AI Organization System not found${NC}"
fi

# Check memory manager
if [[ -f "src/memory/unified_memory_manager.py" ]]; then
    echo -e "${GREEN}✅ Memory Manager found${NC}"
else
    echo -e "${YELLOW}⚠️  Memory Manager not found${NC}"
fi

# Check conductor
if [[ -f "src/conductor/core.py" ]]; then
    echo -e "${GREEN}✅ Conductor System found${NC}"
else
    echo -e "${YELLOW}⚠️  Conductor System not found${NC}"
fi

# Launch mode selection
echo -e "${BLUE}🚀 Launch Options:${NC}"
echo "1. Full Dashboard (default)"
echo "2. Command Interface"
echo "3. Worker Management"
echo "4. System Metrics"
echo "5. Main Menu"

read -p "Select launch mode [1-5]: " choice

case $choice in
    1|"")
        echo -e "${GREEN}🎯 Launching Full Dashboard...${NC}"
        python src/ui/ai_org_ui.py --mode dashboard
        ;;
    2)
        echo -e "${GREEN}🎮 Launching Command Interface...${NC}"
        python src/ui/ai_org_ui.py --mode command
        ;;
    3)
        echo -e "${GREEN}👥 Launching Worker Management...${NC}"
        python src/ui/ai_org_ui.py --mode worker
        ;;
    4)
        echo -e "${GREEN}📈 Showing System Metrics...${NC}"
        python src/ui/visual_dashboard.py metrics
        ;;
    5)
        echo -e "${GREEN}📋 Launching Main Menu...${NC}"
        python src/ui/ai_org_ui.py
        ;;
    *)
        echo -e "${RED}❌ Invalid choice. Launching main menu...${NC}"
        python src/ui/ai_org_ui.py
        ;;
esac

echo -e "${BLUE}👋 Dashboard closed${NC}"