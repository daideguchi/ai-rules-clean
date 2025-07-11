#!/usr/bin/env python3
"""
Basic test suite for AI Safety Governance Template
"""

import pytest


def test_basic_functionality():
    """Basic test to ensure pytest runs successfully"""
    assert True


def test_imports():
    """Test that core modules can be imported"""
    try:
        import os
        import sys
        from pathlib import Path

        assert Path("./").exists()
        assert os.path.exists(".")
        assert sys.version_info.major >= 3
    except ImportError as e:
        pytest.fail(f"Basic import failed: {e}")


def test_project_structure():
    """Test that project has required structure"""
    from pathlib import Path

    required_paths = ["src", "tests", "scripts", "CLAUDE.md", "pyproject.toml"]

    for path in required_paths:
        assert Path(path).exists(), f"Required path {path} does not exist"


def test_python_version():
    """Test Python version compatibility"""
    import sys

    assert sys.version_info >= (3, 8), f"Python 3.8+ required, got {sys.version_info}"
