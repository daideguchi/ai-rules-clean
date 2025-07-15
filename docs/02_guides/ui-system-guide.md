# 🎯 AI Organization UI System - Complete Guide

## Overview

The AI Organization UI System provides a comprehensive visual interface for monitoring and managing the 8-role AI organization system. It features real-time monitoring, interactive command interfaces, and professional CLI dashboards.

## Key Features

### 🎨 Visual Dashboard
- **Real-time monitoring** of 8 AI workers
- **Color-coded status indicators** (Active/Idle/Processing/Error/Offline)
- **Performance metrics** with live updates
- **Task queue visualization**
- **System health monitoring**
- **Responsive layout** for different terminal sizes

### 🎮 Interactive Command Interface
- **Type commands** to control workers
- **Assign tasks** and manage queues
- **View detailed** worker information
- **Command history** and shortcuts
- **Context-sensitive help**
- **Auto-completion** support

### 👥 Worker Management
- **8 AI Workers** with distinct roles:
  - 👑 **PRESIDENT** - Strategic leadership (Authority: 10)
  - 🔄 **COORDINATOR** - Task coordination (Authority: 8)
  - 🔧 **BACKEND_DEV** - Backend development (Authority: 7)
  - 💻 **FRONTEND_DEV** - Frontend development (Authority: 7)
  - ⚙️ **DEVOPS** - Infrastructure management (Authority: 8)
  - 🔒 **SECURITY** - Security specialist (Authority: 9)
  - ✅ **QA** - Quality assurance (Authority: 6)
  - 🤖 **AI_SPECIALIST** - AI development (Authority: 9)

## Installation

### Prerequisites
```bash
# Install Python dependencies
pip install -r requirements-ui.txt

# Key dependencies
pip install rich>=13.0.0
pip install textual>=0.41.0
pip install asyncio-mqtt>=0.13.0
pip install psutil>=5.9.0
```

### System Requirements
- **Python 3.8+**
- **Terminal** with 256 color support
- **Rich library** for professional CLI interface
- **Asyncio** for real-time updates

## Usage

### Quick Start
```bash
# Launch the main UI menu
python src/ui/ai_org_ui.py

# Or use the launcher script
./scripts/ui/launch-dashboard.sh
```

### Direct Launch Options
```bash
# Launch full dashboard
python src/ui/ai_org_ui.py --mode dashboard

# Launch command interface
python src/ui/ai_org_ui.py --mode command

# Launch worker management
python src/ui/ai_org_ui.py --mode worker

# Show specific worker status
python src/ui/visual_dashboard.py worker PRESIDENT

# Show system metrics
python src/ui/visual_dashboard.py metrics
```

## Interface Components

### 1. Visual Dashboard

#### Layout Structure
```
┌─────────────────────────────────────────────────────────────┐
│                      System Header                         │
├─────────────────────────────────────────────────────────────┤
│  Worker Grid (2x4)              │     System Metrics       │
│  ┌─────────┬─────────┬─────────┐ │  ┌─────────────────────┐ │
│  │ PRESIDENT│COORDINAT│BACKEND │ │  │ Uptime: 02:15:23    │ │
│  │ 👑 ACTIVE│🔄 IDLE  │🔧 PROC │ │  │ Active: 3/8         │ │
│  │ Task: ..│         │Task: ..│ │  │ Tasks: 156          │ │
│  └─────────┴─────────┴─────────┘ │  │ Errors: 2           │ │
│  ┌─────────┬─────────┬─────────┐ │  │ Memory: 45.2%       │ │
│  │FRONTEND │ DEVOPS  │SECURITY│ │  │ CPU: 23.1%          │ │
│  │💻 ERROR │⚙️ ACTIVE│🔒 IDLE │ │  └─────────────────────┘ │
│  │         │Task: .. │        │ │                         │
│  └─────────┴─────────┴─────────┘ │     Command Panel       │
│  ┌─────────┬─────────┬─────────┐ │  ┌─────────────────────┐ │
│  │   QA    │AI_SPEC  │        │ │  │ Commands:           │ │
│  │✅ IDLE  │🤖 ACTIVE│        │ │  │ • w - Workers       │ │
│  │         │Task: .. │        │ │  │ • m - Metrics       │ │
│  └─────────┴─────────┴─────────┘ │  │ • t - Tasks         │ │
├─────────────────────────────────────────────────────────────┤
│                        Footer                               │
└─────────────────────────────────────────────────────────────┘
```

#### Worker Panel Details
Each worker panel shows:
- **Icon and name** (e.g., 👑 PRESIDENT)
- **Status indicator** with color coding
- **Current task** (truncated if long)
- **Tasks completed** count
- **Error count** with red highlighting
- **Performance bar** (0-100%)
- **Queue length** indicator

#### Status Colors
- 🟢 **Green** - Active (working on tasks)
- 🟡 **Yellow** - Idle (waiting for tasks)
- 🔵 **Blue** - Processing (executing tasks)
- 🔴 **Red** - Error (failed tasks)
- ⚫ **Gray** - Offline (not responding)

### 2. Interactive Command Interface

#### Available Commands

##### System Commands
```bash
help [command]     # Show help information
quit               # Exit the interface
clear              # Clear the screen
refresh            # Refresh dashboard data
```

##### View Commands
```bash
dashboard          # Launch full dashboard
workers            # Show worker status
metrics            # Show system metrics
status             # Show overall system status
logs               # Show activity logs
```

##### Worker Commands
```bash
select <worker_id>        # Select a worker
worker [worker_id]        # Show worker details
reset <worker_id>         # Reset worker state
```

##### Task Commands
```bash
assign <worker_id> <task>      # Assign task to worker
tasks                          # Show task queues
complete <worker_id> <task_id> # Mark task as complete
cancel <worker_id> <task_id>   # Cancel a task
```

#### Command Shortcuts
- `q` → quit
- `h` → help
- `w` → workers
- `m` → metrics
- `s` → status
- `t` → tasks
- `l` → logs
- `r` → refresh
- `c` → clear
- `d` → dashboard

#### Command Examples
```bash
# Show all workers
ai-org$ workers

# Select and assign task to PRESIDENT
ai-org$ select PRESIDENT
ai-org:PRESIDENT$ assign PRESIDENT "Strategic planning review"

# View task queues
ai-org$ tasks

# Show system metrics
ai-org$ metrics

# Reset a worker
ai-org$ reset BACKEND_DEV
```

### 3. Worker Management

#### Worker Properties
Each worker has:
- **ID**: Unique identifier (e.g., PRESIDENT)
- **Display Name**: Human-readable name
- **Icon**: Visual identifier
- **Status**: Current state (Active/Idle/Processing/Error/Offline)
- **Specialization**: Area of expertise
- **Authority Level**: Decision-making power (1-10)
- **Performance Score**: Efficiency rating (0.0-1.0)
- **Task Queue**: Pending tasks list
- **Resource Usage**: CPU and memory consumption

#### Task Assignment
```bash
# Assign task to specific worker
python src/ui/visual_dashboard.py assign PRESIDENT "System architecture review"

# Assign to backend developer
python src/ui/visual_dashboard.py assign BACKEND_DEV "Database optimization"

# Assign to AI specialist
python src/ui/visual_dashboard.py assign AI_SPECIALIST "Model training evaluation"
```

#### Worker Status Monitoring
```bash
# Show all workers
python src/ui/visual_dashboard.py worker

# Show specific worker
python src/ui/visual_dashboard.py worker PRESIDENT

# Show system metrics
python src/ui/visual_dashboard.py metrics
```

## Integration with AI Organization System

### Dynamic Role Generation
The UI automatically detects and displays workers from the AI Organization System:
- **Reads role definitions** from `ai_organization_system.py`
- **Displays specialized workers** based on project requirements
- **Updates worker capabilities** dynamically
- **Integrates with memory system** for persistent state

### Real-time Updates
- **Live status monitoring** with 1-second refresh rate
- **Task completion tracking** with immediate updates
- **Error detection and highlighting** for failed tasks
- **Performance metrics** updated continuously

### Command Integration
- **Execute tasks** through AI organization system
- **Track results** in memory manager
- **Log activities** for audit trail
- **Integrate with conductor** for task orchestration

## Advanced Features

### 1. Performance Monitoring
```bash
# Monitor system performance
python src/ui/visual_dashboard.py metrics

# View detailed worker performance
python src/ui/visual_dashboard.py worker PRESIDENT
```

### 2. Task Queue Management
- **Visual queue indicators** in dashboard
- **Task prioritization** based on worker authority
- **Queue length monitoring** with alerts
- **Task completion tracking** with statistics

### 3. Error Handling
- **Error detection** with red status indicators
- **Error count tracking** per worker
- **Error rate calculation** for system health
- **Automatic error recovery** suggestions

### 4. System Health Monitoring
- **CPU and memory usage** per worker
- **System uptime** tracking
- **Performance degradation** detection
- **Resource allocation** optimization

## Configuration

### Environment Variables
```bash
# Database connection (if using PostgreSQL)
DB_HOST=localhost
DB_NAME=coding_rule2_ai
DB_USER=dd
DB_PASSWORD=

# UI refresh rate (seconds)
UI_REFRESH_RATE=1.0

# Terminal size detection
TERM_COLS=80
TERM_ROWS=24
```

### Customization Options
- **Color schemes** for different terminal types
- **Layout configuration** for screen sizes
- **Refresh rates** for performance tuning
- **Command aliases** for personal preferences

## Troubleshooting

### Common Issues

#### 1. Rich Library Not Available
```bash
# Install rich library
pip install rich>=13.0.0

# Verify installation
python -c "import rich; print('Rich available')"
```

#### 2. Terminal Compatibility
```bash
# Check terminal colors
python -c "import rich.console; rich.console.Console().print('Test', style='red')"

# Use compatible terminal
# - Terminal.app (macOS)
# - iTerm2 (macOS)
# - Windows Terminal (Windows)
# - GNOME Terminal (Linux)
```

#### 3. Permission Issues
```bash
# Make scripts executable
chmod +x scripts/ui/launch-dashboard.sh

# Check file permissions
ls -la src/ui/
```

#### 4. Import Errors
```bash
# Add project root to Python path
export PYTHONPATH="$PYTHONPATH:/path/to/coding-rule2"

# Or use absolute imports
cd /path/to/coding-rule2
python -m src.ui.ai_org_ui
```

### Performance Issues
- **Reduce refresh rate** if system is slow
- **Limit worker count** for smaller systems
- **Disable animations** for better performance
- **Use simpler layouts** for older terminals

## API Reference

### VisualDashboard Class
```python
from src.ui.visual_dashboard import VisualDashboard

dashboard = VisualDashboard()

# Get worker details
details = dashboard.get_worker_details("PRESIDENT")

# Assign task
result = dashboard.assign_task_to_worker("PRESIDENT", "Strategic review")

# Get system status
status = dashboard.get_system_status()
```

### InteractiveCommandInterface Class
```python
from src.ui.command_interface import InteractiveCommandInterface

interface = InteractiveCommandInterface()

# Run interactive interface
interface.run()
```

### AIOrganizationUI Class
```python
from src.ui.ai_org_ui import AIOrganizationUI

ui = AIOrganizationUI()

# Run main menu
ui.run()
```

## Development

### Adding New Features
1. **Extend worker capabilities** in `visual_dashboard.py`
2. **Add new commands** in `command_interface.py`
3. **Update UI layouts** for new functionality
4. **Test with different terminals** and screen sizes

### Testing
```bash
# Run UI tests
python -m pytest tests/ui/

# Test dashboard functionality
python src/ui/visual_dashboard.py

# Test command interface
python src/ui/command_interface.py
```

### Contributing
- Follow existing code style
- Add comprehensive documentation
- Test on multiple terminal types
- Ensure responsive design

## Support

For issues and questions:
- Check troubleshooting section
- Review system requirements
- Verify dependencies are installed
- Test with recommended terminals

## License

This UI system is part of the AI Organization project and follows the same licensing terms.