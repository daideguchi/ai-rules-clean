#!/usr/bin/env python3
"""Reorganize and consolidate documentation structure."""

import shutil
from datetime import datetime
from pathlib import Path


class DocumentationReorganizer:
    def __init__(self):
        self.docs_dir = Path("docs")
        self.new_structure = {
            "00_quick_start": [
                "README.md",
                "startup_checklist.md",
                "COMMAND_USAGE_GUIDE.md",
            ],
            "01_architecture": [
                "AI_CONSTITUTION.md",
                "CONDUCTOR_SYSTEM.md",
                "PROJECT_STRUCTURE.md",
            ],
            "02_operations": [
                "language-usage-rules.md",
                "president-command-procedures.md",
                "mistake-prevention-system.md",
            ],
            "03_development": [
                "hooks-system-design.md",
                "memory-inheritance-system-guide.md",
                "WORKER_UI_COMMANDS.md",
            ],
            "04_governance": [
                "THINKING_REQUIREMENTS.md",
                "VIOLATION_PREVENTION.md",
                "nist_ai_rmf.md",
            ],
            "05_reference": [
                "COMPLETE_IMPLEMENTATION_REPORT.md",
                "FINAL_COMPREHENSIVE_EVALUATION.md",
            ],
            "_archived": [],  # For old/outdated docs
        }

    def create_new_structure(self):
        """Create new documentation directory structure."""
        backup_dir = (
            self.docs_dir.parent
            / f"docs_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        print(f"Creating backup at {backup_dir}")
        shutil.copytree(self.docs_dir, backup_dir)

        # Create new directories
        for new_dir in self.new_structure.keys():
            (self.docs_dir / new_dir).mkdir(exist_ok=True)

    def consolidate_archives(self):
        """Move all archived documents to single location."""
        archive_dir = self.docs_dir / "_archived"
        archive_dir.mkdir(exist_ok=True)

        # Move _archive directory contents
        old_archive = self.docs_dir / "_archive"
        if old_archive.exists():
            for item in old_archive.rglob("*"):
                if item.is_file():
                    # Create year/month subdirectory
                    rel_path = item.relative_to(old_archive)
                    new_path = archive_dir / "legacy" / rel_path
                    new_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(item), str(new_path))

            # Remove empty directories
            shutil.rmtree(old_archive)

    def create_unified_index(self):
        """Create a unified index of all documentation."""
        index_content = """# AI Safety Governance System - Documentation Index

## Quick Start
- [README](00_quick_start/README.md) - System overview and quick start
- [Startup Checklist](00_quick_start/startup_checklist.md) - Session initialization
- [Command Usage Guide](00_quick_start/COMMAND_USAGE_GUIDE.md) - Essential commands

## Architecture
- [AI Constitution](01_architecture/AI_CONSTITUTION.md) - Core AI principles
- [Conductor System](01_architecture/CONDUCTOR_SYSTEM.md) - Task orchestration
- [Project Structure](01_architecture/PROJECT_STRUCTURE.md) - Directory layout

## Operations
- [Language Usage Rules](02_operations/language-usage-rules.md) - Communication standards
- [President Commands](02_operations/president-command-procedures.md) - Authority system
- [Mistake Prevention](02_operations/mistake-prevention-system.md) - Error handling

## Development
- [Hooks System](03_development/hooks-system-design.md) - Event handling
- [Memory Inheritance](03_development/memory-inheritance-system-guide.md) - Session continuity
- [Worker UI Commands](03_development/WORKER_UI_COMMANDS.md) - Interface controls

## Governance
- [Thinking Requirements](04_governance/THINKING_REQUIREMENTS.md) - Cognitive standards
- [Violation Prevention](04_governance/VIOLATION_PREVENTION.md) - Compliance rules
- [NIST AI RMF](04_governance/nist_ai_rmf.md) - Risk management framework

## Reference
- [Implementation Report](05_reference/COMPLETE_IMPLEMENTATION_REPORT.md) - System status
- [Comprehensive Evaluation](05_reference/FINAL_COMPREHENSIVE_EVALUATION.md) - Performance metrics

## Archives
- [Legacy Documentation](_archived/index.md) - Historical documents

---
*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

        index_file = self.docs_dir / "INDEX.md"
        with open(index_file, "w") as f:
            f.write(index_content)

        print(f"Created unified index at {index_file}")

    def generate_recommendations(self):
        """Generate specific file consolidation recommendations."""
        recommendations = []

        # Find duplicate concepts
        duplicates = {
            "memory_system": [
                "CLAUDE_CODE_MEMORY_SYSTEM.md",
                "memory-inheritance-system-guide.md",
                "ai-memory-system-product.md",
                "claude-memory-system.md",
                "claude-persistent-memory-system.md",
            ],
            "status_reports": [
                "COMPLETE_IMPLEMENTATION_REPORT.md",
                "FINAL_COMPREHENSIVE_EVALUATION.md",
                "OPTIMIZATION_SUCCESS_REPORT.md",
                "FINAL_CONSOLIDATION_REPORT.md",
            ],
            "worker_guides": [
                "WORKER_UI_COMMANDS.md",
                "AI_WORKER_COMMANDS_SIMPLIFIED.md",
                "worker1-final-quality-report.md",
                "worker3-completion-report.md",
            ],
        }

        for concept, files in duplicates.items():
            recommendations.append(
                {
                    "action": "consolidate",
                    "concept": concept,
                    "files": files,
                    "target": f"consolidated_{concept}.md",
                }
            )

        return recommendations


if __name__ == "__main__":
    reorganizer = DocumentationReorganizer()

    print("=== Documentation Reorganization Plan ===")
    print("\n1. Creating new structure...")
    reorganizer.create_new_structure()

    print("\n2. Consolidating archives...")
    reorganizer.consolidate_archives()

    print("\n3. Creating unified index...")
    reorganizer.create_unified_index()

    print("\n4. Consolidation recommendations:")
    for rec in reorganizer.generate_recommendations():
        print(f"\n  {rec['concept']}:")
        print(f"  - Consolidate {len(rec['files'])} files into {rec['target']}")
        for f in rec["files"]:
            print(f"    • {f}")
