#!/usr/bin/env python3
"""
🚨 Simple Root File Limit Enforcer
================================

Simple enforcement of 12-file root directory limit without external dependencies.
"""

import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class SimpleRootEnforcer:
    """Simple root file limit enforcement"""

    MAX_ROOT_FILES = 12
    ESSENTIAL_FILES = {
        "CLAUDE.md",
        "README.md",
        "Makefile",
        "LICENSE",
        ".gitignore",
        ".gitattributes",
        "pyproject.toml",
        ".pre-commit-config.yaml",
        ".claude-project",
        ".cursorrules",
        ".env.example",
        "CHANGELOG.md",
    }

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path.cwd()

    def get_current_root_files(self) -> List[Path]:
        """Get current files in root directory"""
        try:
            return [f for f in self.project_root.iterdir() if f.is_file()]
        except Exception as e:
            print(f"Error getting root files: {e}")
            return []

    def categorize_file(self, file_path: Path) -> tuple:
        """Categorize file and return (target_dir, description)"""
        filename = file_path.name

        # Essential files stay in root
        if filename in self.ESSENTIAL_FILES:
            return ("", "Essential root file")

        # Reports
        if "_REPORT.md" in filename or "CONSOLIDATION" in filename:
            return ("docs/04_reference/", "Status report")

        # Setup guides
        if filename.startswith("SETUP_") or filename == "Index.md":
            return ("docs/02_guides/", "Setup guide")

        # Docker files
        if filename.startswith("Dockerfile") or filename.startswith("docker-compose"):
            return ("config/docker/", "Docker configuration")

        # Python files
        if (
            filename.endswith("_ui_system.py")
            or filename.startswith("demo_")
            or filename.startswith("test_")
        ):
            return ("src/ui/", "UI/Test file")

        # Requirements
        if filename.startswith("requirements-"):
            return ("config/", "Requirements file")

        # Cursor config
        if filename.startswith(".cursor") or filename.startswith(".forbidden"):
            return ("config/cursor/", "Cursor configuration")

        # Default
        return ("misc/", "Miscellaneous file")

    def move_file(self, file_path: Path, target_dir: str) -> bool:
        """Move file to target directory"""
        if not target_dir:
            return False

        try:
            target_path = self.project_root / target_dir
            target_path.mkdir(parents=True, exist_ok=True)

            destination = target_path / file_path.name

            # Avoid overwriting
            if destination.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                stem = destination.stem
                suffix = destination.suffix
                destination = target_path / f"{stem}_{timestamp}{suffix}"

            shutil.move(str(file_path), str(destination))
            print(f"✅ Moved {file_path.name} to {target_dir}")
            return True

        except Exception as e:
            print(f"❌ Error moving {file_path.name}: {e}")
            return False

    def enforce_limit(self) -> Dict:
        """Enforce the 12-file limit"""
        root_files = self.get_current_root_files()
        file_count = len(root_files)

        print(f"📊 Current root files: {file_count}/{self.MAX_ROOT_FILES}")

        if file_count <= self.MAX_ROOT_FILES:
            print("✅ Root directory compliant")
            return {"status": "COMPLIANT", "file_count": file_count, "moved_files": []}

        print(f"🚨 VIOLATION: {file_count} files exceed limit of {self.MAX_ROOT_FILES}")

        # Separate essential and non-essential
        essential_files = []
        non_essential_files = []

        for file_path in root_files:
            if file_path.name in self.ESSENTIAL_FILES:
                essential_files.append(file_path)
            else:
                non_essential_files.append(file_path)

        print(f"📋 Essential files: {len(essential_files)}")
        print(f"📋 Non-essential files: {len(non_essential_files)}")

        # Move non-essential files
        moved_files = []
        for file_path in non_essential_files:
            if (
                len(essential_files) + len(non_essential_files) - len(moved_files)
                <= self.MAX_ROOT_FILES
            ):
                break

            target_dir, description = self.categorize_file(file_path)
            if self.move_file(file_path, target_dir):
                moved_files.append(
                    {
                        "file": file_path.name,
                        "destination": target_dir,
                        "reason": description,
                    }
                )

        # Check final count
        final_count = len(self.get_current_root_files())

        if final_count <= self.MAX_ROOT_FILES:
            print(f"✅ Violation resolved: {final_count} files remaining")
            status = "RESOLVED"
        else:
            print(f"⚠️ Partial resolution: {final_count} files remaining")
            status = "PARTIAL"

        return {"status": status, "file_count": final_count, "moved_files": moved_files}

    def list_files(self):
        """List current root files"""
        root_files = self.get_current_root_files()

        print(f"\n📁 Root Directory Files ({len(root_files)}/{self.MAX_ROOT_FILES}):")
        print("=" * 50)

        for i, file_path in enumerate(sorted(root_files), 1):
            essential = "⭐" if file_path.name in self.ESSENTIAL_FILES else "📄"
            print(f"{i:2d}. {essential} {file_path.name}")

        if len(root_files) > self.MAX_ROOT_FILES:
            print(
                f"\n🚨 VIOLATION: {len(root_files) - self.MAX_ROOT_FILES} files over limit"
            )
        else:
            print(
                f"\n✅ Compliant: {self.MAX_ROOT_FILES - len(root_files)} files under limit"
            )


def main():
    """Main execution"""
    import sys

    enforcer = SimpleRootEnforcer()

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "list":
            enforcer.list_files()
        elif command == "check":
            result = enforcer.enforce_limit()
            print(f"\n📊 Status: {result['status']}")
        elif command == "fix":
            print("🔧 Fixing root directory violations...")
            result = enforcer.enforce_limit()
            if result["moved_files"]:
                print(f"\n📁 Moved {len(result['moved_files'])} files:")
                for moved in result["moved_files"]:
                    print(f"  • {moved['file']} → {moved['destination']}")
        else:
            print("Usage: python simple-root-enforcer.py [list|check|fix]")
    else:
        # Default: check and fix
        print("🚨 Root File Limit Enforcer - Production Mode")
        print("=" * 50)

        result = enforcer.enforce_limit()

        if result["moved_files"]:
            print("\n📁 Files moved:")
            for moved in result["moved_files"]:
                print(f"  • {moved['file']} → {moved['destination']}")


if __name__ == "__main__":
    main()
