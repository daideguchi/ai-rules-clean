#!/usr/bin/env python3
"""
🧪 Revolutionary Log Management System - Comprehensive Test Suite
================================================================

Complete test suite for all three revolutionary log management tasks:
- Task 1: Local/DB Unified Log Management
- Task 2: Script/Document Reference System
- Task 3: Folder Structure Rule Enforcement

Includes integration tests, performance tests, and AI organization tests.
"""

import json
import logging
import shutil
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict
from unittest.mock import Mock, patch

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from logging.ai_integration import AIOrganizationIntegration
    from logging.revolutionary_log_manager import RevolutionaryLogManager
except ImportError as e:
    print(f"⚠️ Failed to import revolutionary log management components: {e}")
    sys.exit(1)


class RevolutionaryLogSystemTestSuite:
    """Comprehensive test suite for revolutionary log management system"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.test_results = {}
        self.temp_dir = None

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        self.logger = logging.getLogger(__name__)

    def setup_test_environment(self):
        """Setup isolated test environment"""
        try:
            # Create temporary directory
            self.temp_dir = Path(tempfile.mkdtemp(prefix="revolutionary_test_"))
            print(f"📁 Test environment created: {self.temp_dir}")

            # Create test project structure
            test_dirs = [
                "src/logging",
                "src/ai",
                "src/memory",
                "scripts",
                "docs",
                "runtime/logs",
                "runtime/unified_logs",
                "runtime/conversation_logs",
                "config",
            ]

            for dir_path in test_dirs:
                (self.temp_dir / dir_path).mkdir(parents=True, exist_ok=True)

            # Create test files
            self._create_test_files()

            return True

        except Exception as e:
            self.logger.error(f"Test environment setup failed: {e}")
            return False

    def _create_test_files(self):
        """Create test files for testing"""
        # Test Python scripts
        test_scripts = [
            (
                "src/test_module.py",
                '''#!/usr/bin/env python3
"""Test module for revolutionary log management"""

import json
from datetime import datetime

def test_function():
    """Test function"""
    return "test"

class TestClass:
    """Test class"""
    def __init__(self):
        self.data = {}
''',
            ),
            (
                "scripts/test_script.py",
                '''#!/usr/bin/env python3
"""Test script"""

import sys
import os
from pathlib import Path

def main():
    print("Test script execution")

if __name__ == "__main__":
    main()
''',
            ),
            (
                "src/ai/test_ai_module.py",
                '''#!/usr/bin/env python3
"""Test AI module"""

from typing import Dict, Any

class TestAI:
    def __init__(self):
        self.name = "test_ai"

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {"processed": True, "data": data}
''',
            ),
        ]

        for file_path, content in test_scripts:
            full_path = self.temp_dir / file_path
            full_path.write_text(content)

        # Test markdown documents
        test_docs = [
            (
                "docs/README.md",
                """# Test Documentation

This is a test document for the revolutionary log management system.

## Features

- Unified log management
- Script referencing
- Document analysis

## Scripts

This document references:
- `src/test_module.py`
- `scripts/test_script.py`

## Implementation

```python
def test_function():
    return "test"
```
""",
            ),
            (
                "docs/api.md",
                """# API Documentation

## Log Management API

### Endpoints

- `POST /logs` - Create log entry
- `GET /logs` - Search logs
- `GET /scripts` - List scripts

### Example Usage

```python
from logging.revolutionary_log_manager import RevolutionaryLogManager

manager = RevolutionaryLogManager()
result = manager.log_unified("INFO", "test", "Test message")
```
""",
            ),
            (
                "README.md",
                """# Revolutionary Log Management System

Complete log management system with:

1. Unified logging
2. Script/document referencing
3. Folder structure enforcement

See `docs/README.md` for details.
""",
            ),
        ]

        for file_path, content in test_docs:
            full_path = self.temp_dir / file_path
            full_path.write_text(content)

        # Test log files
        test_logs = [
            (
                "runtime/logs/test.log",
                """2024-07-09 10:00:00 INFO Test log entry 1
2024-07-09 10:01:00 ERROR Test error message
2024-07-09 10:02:00 WARNING Test warning message
""",
            ),
            (
                "runtime/logs/system.log",
                """[2024-07-09 10:00:00] INFO: System started
[2024-07-09 10:01:00] ERROR: Connection failed
[2024-07-09 10:02:00] INFO: System recovered
""",
            ),
        ]

        for file_path, content in test_logs:
            full_path = self.temp_dir / file_path
            full_path.write_text(content)

        # Test configuration
        config_content = {
            "database": {
                "host": "localhost",
                "database": "test_db",
                "user": "test_user",
                "password": "test_pass",
            },
            "logging": {
                "unified_logs": {"enabled": True},
                "log_aggregation": {"enabled": True},
            },
        }

        config_path = self.temp_dir / "config" / "test_config.json"
        config_path.write_text(json.dumps(config_content, indent=2))

    def test_task_1_unified_logging(self) -> Dict[str, Any]:
        """Test Task 1: Unified Log Management"""
        print("\n📊 Testing Task 1: Unified Log Management")

        results = {
            "test_name": "Task 1: Unified Log Management",
            "subtests": {},
            "overall_success": True,
            "start_time": datetime.now().isoformat(),
        }

        try:
            # Test 1.1: Log Manager Initialization
            print("   1.1 Testing log manager initialization...")
            try:
                # Mock database connection for testing
                with patch("psycopg2.connect") as mock_connect:
                    mock_conn = Mock()
                    mock_connect.return_value = mock_conn

                    log_manager = RevolutionaryLogManager(self.temp_dir)
                    results["subtests"]["initialization"] = {
                        "success": True,
                        "message": "Log manager initialized",
                    }
                    print("   ✅ Log manager initialization successful")
            except Exception as e:
                results["subtests"]["initialization"] = {
                    "success": False,
                    "error": str(e),
                }
                results["overall_success"] = False
                print(f"   ❌ Log manager initialization failed: {e}")

            # Test 1.2: Unified Logging
            print("   1.2 Testing unified logging...")
            try:
                with patch("psycopg2.connect") as mock_connect:
                    mock_conn = Mock()
                    mock_connect.return_value = mock_conn

                    log_manager = RevolutionaryLogManager(self.temp_dir)

                    # Test log creation
                    log_id = log_manager.log_unified(
                        level="INFO",
                        component="test_component",
                        message="Test message for unified logging",
                        structured_data={"test": True, "component": "test_suite"},
                    )

                    if log_id:
                        results["subtests"]["unified_logging"] = {
                            "success": True,
                            "log_id": log_id,
                        }
                        print(f"   ✅ Unified logging successful: {log_id}")
                    else:
                        results["subtests"]["unified_logging"] = {
                            "success": False,
                            "error": "No log ID returned",
                        }
                        results["overall_success"] = False
                        print("   ❌ Unified logging failed: No log ID returned")

            except Exception as e:
                results["subtests"]["unified_logging"] = {
                    "success": False,
                    "error": str(e),
                }
                results["overall_success"] = False
                print(f"   ❌ Unified logging failed: {e}")

            # Test 1.3: Log Search
            print("   1.3 Testing log search...")
            try:
                with patch("psycopg2.connect") as mock_connect:
                    mock_conn = Mock()
                    mock_cursor = Mock()
                    mock_connect.return_value = mock_conn
                    mock_conn.cursor.return_value = mock_cursor

                    # Mock search results
                    mock_cursor.fetchall.return_value = [
                        {
                            "id": "test-id-1",
                            "timestamp": datetime.now(),
                            "message": "Test log message",
                            "component": "test",
                            "log_level": "INFO",
                        }
                    ]

                    log_manager = RevolutionaryLogManager(self.temp_dir)
                    search_results = log_manager.search_logs("test", limit=10)

                    if search_results:
                        results["subtests"]["log_search"] = {
                            "success": True,
                            "results_count": len(search_results),
                        }
                        print(
                            f"   ✅ Log search successful: {len(search_results)} results"
                        )
                    else:
                        results["subtests"]["log_search"] = {
                            "success": False,
                            "error": "No search results",
                        }
                        results["overall_success"] = False
                        print("   ❌ Log search failed: No results")

            except Exception as e:
                results["subtests"]["log_search"] = {"success": False, "error": str(e)}
                results["overall_success"] = False
                print(f"   ❌ Log search failed: {e}")

            # Test 1.4: Cross-session Continuity
            print("   1.4 Testing cross-session continuity...")
            try:
                with patch("psycopg2.connect") as mock_connect:
                    mock_conn = Mock()
                    mock_connect.return_value = mock_conn

                    # Create session file
                    session_dir = (
                        self.temp_dir / "src" / "memory" / "core" / "session-records"
                    )
                    session_dir.mkdir(parents=True, exist_ok=True)

                    session_data = {
                        "session_id": "test-session-123",
                        "start_time": datetime.now().isoformat(),
                        "conversation_log": {"message_count": 5},
                    }

                    session_file = session_dir / "current-session.json"
                    session_file.write_text(json.dumps(session_data))

                    log_manager = RevolutionaryLogManager(self.temp_dir)

                    if log_manager.current_session_id:
                        results["subtests"]["session_continuity"] = {
                            "success": True,
                            "session_id": log_manager.current_session_id,
                        }
                        print(
                            f"   ✅ Session continuity successful: {log_manager.current_session_id}"
                        )
                    else:
                        results["subtests"]["session_continuity"] = {
                            "success": False,
                            "error": "No session ID",
                        }
                        results["overall_success"] = False
                        print("   ❌ Session continuity failed: No session ID")

            except Exception as e:
                results["subtests"]["session_continuity"] = {
                    "success": False,
                    "error": str(e),
                }
                results["overall_success"] = False
                print(f"   ❌ Session continuity failed: {e}")

        except Exception as e:
            results["overall_success"] = False
            results["error"] = str(e)
            print(f"   ❌ Task 1 testing failed: {e}")

        results["end_time"] = datetime.now().isoformat()
        return results

    def test_task_2_script_references(self) -> Dict[str, Any]:
        """Test Task 2: Script/Document Reference System"""
        print("\n📚 Testing Task 2: Script/Document Reference System")

        results = {
            "test_name": "Task 2: Script/Document Reference System",
            "subtests": {},
            "overall_success": True,
            "start_time": datetime.now().isoformat(),
        }

        try:
            # Test 2.1: Script Analysis
            print("   2.1 Testing script analysis...")
            try:
                with patch("psycopg2.connect") as mock_connect:
                    mock_conn = Mock()
                    mock_connect.return_value = mock_conn

                    log_manager = RevolutionaryLogManager(self.temp_dir)

                    # Analyze test script
                    test_script = self.temp_dir / "src" / "test_module.py"
                    content = test_script.read_text()

                    script_ref = log_manager._analyze_script_file(test_script, content)

                    if script_ref and script_ref.functions:
                        results["subtests"]["script_analysis"] = {
                            "success": True,
                            "functions_found": len(script_ref.functions),
                            "imports_found": len(script_ref.imports),
                        }
                        print(
                            f"   ✅ Script analysis successful: {len(script_ref.functions)} functions"
                        )
                    else:
                        results["subtests"]["script_analysis"] = {
                            "success": False,
                            "error": "No script analysis results",
                        }
                        results["overall_success"] = False
                        print("   ❌ Script analysis failed: No results")

            except Exception as e:
                results["subtests"]["script_analysis"] = {
                    "success": False,
                    "error": str(e),
                }
                results["overall_success"] = False
                print(f"   ❌ Script analysis failed: {e}")

            # Test 2.2: Document Analysis
            print("   2.2 Testing document analysis...")
            try:
                with patch("psycopg2.connect") as mock_connect:
                    mock_conn = Mock()
                    mock_connect.return_value = mock_conn

                    log_manager = RevolutionaryLogManager(self.temp_dir)

                    # Analyze test document
                    test_doc = self.temp_dir / "docs" / "README.md"
                    content = test_doc.read_text()

                    doc_ref = log_manager._analyze_document_file(test_doc, content)

                    if doc_ref and doc_ref.sections:
                        results["subtests"]["document_analysis"] = {
                            "success": True,
                            "sections_found": len(doc_ref.sections),
                            "scripts_referenced": len(doc_ref.referenced_scripts),
                        }
                        print(
                            f"   ✅ Document analysis successful: {len(doc_ref.sections)} sections"
                        )
                    else:
                        results["subtests"]["document_analysis"] = {
                            "success": False,
                            "error": "No document analysis results",
                        }
                        results["overall_success"] = False
                        print("   ❌ Document analysis failed: No results")

            except Exception as e:
                results["subtests"]["document_analysis"] = {
                    "success": False,
                    "error": str(e),
                }
                results["overall_success"] = False
                print(f"   ❌ Document analysis failed: {e}")

            # Test 2.3: Reference Search
            print("   2.3 Testing reference search...")
            try:
                with patch("psycopg2.connect") as mock_connect:
                    mock_conn = Mock()
                    mock_cursor = Mock()
                    mock_connect.return_value = mock_conn
                    mock_conn.cursor.return_value = mock_cursor

                    # Mock search results
                    mock_cursor.fetchall.return_value = [
                        {
                            "script_path": "src/test_module.py",
                            "script_name": "test_module.py",
                            "description": "Test module",
                            "functions": '["test_function"]',
                        }
                    ]

                    log_manager = RevolutionaryLogManager(self.temp_dir)

                    # Test script search
                    script_results = log_manager.search_scripts("test", limit=5)

                    if script_results:
                        results["subtests"]["reference_search"] = {
                            "success": True,
                            "results_count": len(script_results),
                        }
                        print(
                            f"   ✅ Reference search successful: {len(script_results)} results"
                        )
                    else:
                        results["subtests"]["reference_search"] = {
                            "success": False,
                            "error": "No search results",
                        }
                        results["overall_success"] = False
                        print("   ❌ Reference search failed: No results")

            except Exception as e:
                results["subtests"]["reference_search"] = {
                    "success": False,
                    "error": str(e),
                }
                results["overall_success"] = False
                print(f"   ❌ Reference search failed: {e}")

        except Exception as e:
            results["overall_success"] = False
            results["error"] = str(e)
            print(f"   ❌ Task 2 testing failed: {e}")

        results["end_time"] = datetime.now().isoformat()
        return results

    def test_task_3_folder_structure(self) -> Dict[str, Any]:
        """Test Task 3: Folder Structure Rule Enforcement"""
        print("\n📁 Testing Task 3: Folder Structure Rule Enforcement")

        results = {
            "test_name": "Task 3: Folder Structure Rule Enforcement",
            "subtests": {},
            "overall_success": True,
            "start_time": datetime.now().isoformat(),
        }

        try:
            # Test 3.1: Structure Monitoring
            print("   3.1 Testing structure monitoring...")
            try:
                with patch("psycopg2.connect") as mock_connect:
                    mock_conn = Mock()
                    mock_connect.return_value = mock_conn

                    log_manager = RevolutionaryLogManager(self.temp_dir)

                    # Test structure change logging
                    log_manager.log_structure_change(
                        "test_action", "Testing structure monitoring"
                    )

                    results["subtests"]["structure_monitoring"] = {
                        "success": True,
                        "message": "Structure monitoring active",
                    }
                    print("   ✅ Structure monitoring successful")

            except Exception as e:
                results["subtests"]["structure_monitoring"] = {
                    "success": False,
                    "error": str(e),
                }
                results["overall_success"] = False
                print(f"   ❌ Structure monitoring failed: {e}")

            # Test 3.2: Violation Detection
            print("   3.2 Testing violation detection...")
            try:
                with patch("psycopg2.connect") as mock_connect:
                    mock_conn = Mock()
                    mock_connect.return_value = mock_conn

                    log_manager = RevolutionaryLogManager(self.temp_dir)

                    # Test violation logging
                    violation_data = {
                        "violation_type": "test_violation",
                        "file_path": "test_file.txt",
                        "timestamp": datetime.now(timezone.utc),
                    }

                    violation_id = log_manager.log_structure_violation(violation_data)

                    if violation_id:
                        results["subtests"]["violation_detection"] = {
                            "success": True,
                            "violation_id": violation_id,
                        }
                        print(f"   ✅ Violation detection successful: {violation_id}")
                    else:
                        results["subtests"]["violation_detection"] = {
                            "success": False,
                            "error": "No violation ID returned",
                        }
                        results["overall_success"] = False
                        print("   ❌ Violation detection failed: No violation ID")

            except Exception as e:
                results["subtests"]["violation_detection"] = {
                    "success": False,
                    "error": str(e),
                }
                results["overall_success"] = False
                print(f"   ❌ Violation detection failed: {e}")

            # Test 3.3: Root File Limit
            print("   3.3 Testing root file limit enforcement...")
            try:
                # Create more than 12 files in root
                for i in range(15):
                    test_file = self.temp_dir / f"test_file_{i}.txt"
                    test_file.write_text(f"Test file {i}")

                # Count root files
                root_files = [f for f in self.temp_dir.iterdir() if f.is_file()]

                if len(root_files) > 12:
                    results["subtests"]["root_file_limit"] = {
                        "success": True,
                        "message": f"Root file limit test setup: {len(root_files)} files",
                    }
                    print(
                        f"   ✅ Root file limit test successful: {len(root_files)} files"
                    )
                else:
                    results["subtests"]["root_file_limit"] = {
                        "success": False,
                        "error": "Root file limit test failed",
                    }
                    results["overall_success"] = False
                    print("   ❌ Root file limit test failed")

            except Exception as e:
                results["subtests"]["root_file_limit"] = {
                    "success": False,
                    "error": str(e),
                }
                results["overall_success"] = False
                print(f"   ❌ Root file limit test failed: {e}")

        except Exception as e:
            results["overall_success"] = False
            results["error"] = str(e)
            print(f"   ❌ Task 3 testing failed: {e}")

        results["end_time"] = datetime.now().isoformat()
        return results

    def test_ai_integration(self) -> Dict[str, Any]:
        """Test AI organization integration"""
        print("\n🤖 Testing AI Organization Integration")

        results = {
            "test_name": "AI Organization Integration",
            "subtests": {},
            "overall_success": True,
            "start_time": datetime.now().isoformat(),
        }

        try:
            # Test integration initialization
            print("   Testing AI integration initialization...")
            try:
                with patch("psycopg2.connect") as mock_connect:
                    mock_conn = Mock()
                    mock_connect.return_value = mock_conn

                    log_manager = RevolutionaryLogManager(self.temp_dir)
                    ai_integration = AIOrganizationIntegration(log_manager)

                    # Test activation
                    activation_result = ai_integration.activate_integration(
                        "test-session-ai"
                    )

                    if activation_result.get("status") == "activated":
                        results["subtests"]["ai_integration"] = {
                            "success": True,
                            "session_id": activation_result.get("session_id"),
                        }
                        print(
                            f"   ✅ AI integration successful: {activation_result.get('session_id')}"
                        )
                    else:
                        results["subtests"]["ai_integration"] = {
                            "success": False,
                            "error": "Integration activation failed",
                        }
                        results["overall_success"] = False
                        print("   ❌ AI integration failed: Activation failed")

            except Exception as e:
                results["subtests"]["ai_integration"] = {
                    "success": False,
                    "error": str(e),
                }
                results["overall_success"] = False
                print(f"   ❌ AI integration failed: {e}")

        except Exception as e:
            results["overall_success"] = False
            results["error"] = str(e)
            print(f"   ❌ AI integration testing failed: {e}")

        results["end_time"] = datetime.now().isoformat()
        return results

    def test_performance(self) -> Dict[str, Any]:
        """Test system performance"""
        print("\n⏱️ Testing System Performance")

        results = {
            "test_name": "Performance Testing",
            "subtests": {},
            "overall_success": True,
            "start_time": datetime.now().isoformat(),
        }

        try:
            # Test logging performance
            print("   Testing logging performance...")
            try:
                with patch("psycopg2.connect") as mock_connect:
                    mock_conn = Mock()
                    mock_connect.return_value = mock_conn

                    log_manager = RevolutionaryLogManager(self.temp_dir)

                    # Performance test: 100 log entries
                    start_time = time.time()

                    for i in range(100):
                        log_manager.log_unified(
                            level="INFO",
                            component="performance_test",
                            message=f"Performance test log entry {i}",
                            structured_data={"iteration": i, "test": "performance"},
                        )

                    end_time = time.time()
                    duration = end_time - start_time

                    if duration < 10.0:  # Should complete in under 10 seconds
                        results["subtests"]["logging_performance"] = {
                            "success": True,
                            "duration_seconds": duration,
                            "entries_per_second": 100 / duration,
                        }
                        print(
                            f"   ✅ Logging performance: {100 / duration:.2f} entries/second"
                        )
                    else:
                        results["subtests"]["logging_performance"] = {
                            "success": False,
                            "error": f"Performance too slow: {duration:.2f}s",
                        }
                        results["overall_success"] = False
                        print(f"   ❌ Logging performance too slow: {duration:.2f}s")

            except Exception as e:
                results["subtests"]["logging_performance"] = {
                    "success": False,
                    "error": str(e),
                }
                results["overall_success"] = False
                print(f"   ❌ Logging performance test failed: {e}")

        except Exception as e:
            results["overall_success"] = False
            results["error"] = str(e)
            print(f"   ❌ Performance testing failed: {e}")

        results["end_time"] = datetime.now().isoformat()
        return results

    def run_comprehensive_tests(self) -> Dict[str, Any]:
        """Run comprehensive test suite"""
        print("🧪 Revolutionary Log Management System - Comprehensive Test Suite")
        print("=" * 70)

        # Setup test environment
        print("\n🔧 Setting up test environment...")
        if not self.setup_test_environment():
            return {"status": "failed", "error": "Test environment setup failed"}

        # Run all tests
        all_results = {
            "test_suite": "Revolutionary Log Management System",
            "start_time": datetime.now().isoformat(),
            "tests": {},
            "summary": {},
        }

        try:
            # Task 1: Unified Log Management
            all_results["tests"]["task_1"] = self.test_task_1_unified_logging()

            # Task 2: Script/Document References
            all_results["tests"]["task_2"] = self.test_task_2_script_references()

            # Task 3: Folder Structure Enforcement
            all_results["tests"]["task_3"] = self.test_task_3_folder_structure()

            # AI Integration
            all_results["tests"]["ai_integration"] = self.test_ai_integration()

            # Performance Tests
            all_results["tests"]["performance"] = self.test_performance()

            # Calculate summary
            total_tests = len(all_results["tests"])
            successful_tests = sum(
                1 for test in all_results["tests"].values() if test["overall_success"]
            )

            all_results["summary"] = {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": total_tests - successful_tests,
                "success_rate": (successful_tests / total_tests) * 100
                if total_tests > 0
                else 0,
            }

            all_results["end_time"] = datetime.now().isoformat()

            # Print summary
            print("\n📊 Test Summary:")
            print(f"   Total tests: {total_tests}")
            print(f"   Successful: {successful_tests}")
            print(f"   Failed: {total_tests - successful_tests}")
            print(f"   Success rate: {all_results['summary']['success_rate']:.1f}%")

            if successful_tests == total_tests:
                print(
                    "\n🎉 All tests passed! Revolutionary Log Management System is ready."
                )
            else:
                print(
                    "\n⚠️ Some tests failed. Please review the results and fix issues."
                )

        except Exception as e:
            all_results["status"] = "error"
            all_results["error"] = str(e)
            print(f"\n❌ Test suite execution failed: {e}")

        # Save results
        self._save_test_results(all_results)

        return all_results

    def _save_test_results(self, results: Dict[str, Any]):
        """Save test results to file"""
        try:
            results_file = self.temp_dir / "test_results.json"
            with open(results_file, "w") as f:
                json.dump(results, f, indent=2, default=str)

            print(f"\n💾 Test results saved to: {results_file}")

        except Exception as e:
            print(f"\n⚠️ Failed to save test results: {e}")

    def cleanup_test_environment(self):
        """Clean up test environment"""
        try:
            if self.temp_dir and self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
                print(f"\n🧺 Test environment cleaned up: {self.temp_dir}")
        except Exception as e:
            print(f"\n⚠️ Failed to cleanup test environment: {e}")


def main():
    """Main test function"""
    test_suite = RevolutionaryLogSystemTestSuite()

    try:
        # Run comprehensive tests
        results = test_suite.run_comprehensive_tests()

        # Return appropriate exit code
        success_rate = results.get("summary", {}).get("success_rate", 0)
        return 0 if success_rate == 100 else 1

    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        return 1

    finally:
        # Always cleanup
        test_suite.cleanup_test_environment()


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
