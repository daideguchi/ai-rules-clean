#!/usr/bin/env python3
# プロジェクト汚染防止
import os
from pathlib import Path


def ensure_project_isolation():
    project_root = Path(__file__).parent.parent.parent
    if not str(os.getcwd()).startswith(str(project_root)):
        print("⚠️ WARNING: Operating outside project boundary!")
        print(f"Current: {os.getcwd()}")
        print(f"Expected: {project_root}")
        return False
    return True


if __name__ == "__main__":
    ensure_project_isolation()
