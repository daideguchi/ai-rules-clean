#!/usr/bin/env python3
"""
Strict File Organization Enforcer
厳格ファイル組織強制システム

Enforces absolute file organization rules with zero tolerance.
"""

import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class StrictFileOrganizer:
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.violations = []
        self.moved_files = []

        # 🔴 CRITICAL: These rules ONLY apply to the coding-rule2 project
        # When used as template in other projects, they should be customized
        if not self._is_coding_rule2_project():
            print("⚠️  WARNING: These file organization rules are designed for coding-rule2 project")
            print("⚠️  For other projects, customize the rules in strict-file-organizer.py")
            print("⚠️  Current project appears to be different - proceeding with caution")
            # Don't exit, but warn user

        # ABSOLUTE RULES - NO EXCEPTIONS (FOR CODING-RULE2 PROJECT)
        self.ROOT_FILE_LIMIT = 12
        self.ALLOWED_ROOT_FILES = {
            'README.md', 'Makefile', 'pyproject.toml', 'requirements.txt',
            'LICENSE', 'CLAUDE.md', 'Index.md', '.gitignore',
            '.env', '.mcp.json', '.mypy.ini', 'docker-compose.yml'
        }

        # ALLOWED ROOT DIRECTORIES (specific to coding-rule2)
        self.ALLOWED_ROOT_DIRS = {
            'config', 'docs', 'scripts', 'src', 'tests', 'runtime', 'data', '.cursor'
        }

        # File classification rules (FOR CODING-RULE2 ONLY)
        self.FILE_RULES = {
            # Editor configurations (EXCEPT .cursor directory which stays in root)
            '.cursorrules': 'config/editor/',
            '.claude-project': 'config/editor/',
            '.cursorignore': 'config/editor/',
            '.cursorindexignore': 'config/editor/',
            '.forbidden-move': 'config/editor/',

            # Git configurations
            '.gitattributes': 'config/git/',
            '.pre-commit-config.yaml': 'config/git/',

            # Development tools
            '.pylintrc': 'config/dev/',
            '.flake8': 'config/dev/',
            '.black': 'config/dev/',

            # Environment files
            '.env.example': 'scripts/setup/',
            '.env.local': 'scripts/setup/',
            '.env.test': 'scripts/setup/',
        }

        # Pattern-based rules
        self.PATTERN_RULES = {
            r'.*\.md$': 'docs/',  # Markdown files except allowed ones
            r'setup_.*\.py$': 'scripts/setup/',
            r'.*_test\.py$': 'tests/',
            r'.*\.config\..*$': 'config/',
            r'.*\.ini$': 'config/dev/',
            r'.*\.toml$': 'config/dev/',  # Except pyproject.toml
        }

    def _is_coding_rule2_project(self) -> bool:
        """Check if this is the coding-rule2 project"""
        # Check for specific files that indicate this is coding-rule2
        indicators = [
            'CLAUDE.md',  # Our specific AI config
            'scripts/automation/strict-file-organizer.py',  # This script itself
            'docs/04_reference/STRICT_FILE_ORGANIZATION_RULES.md'  # Our rules doc
        ]

        for indicator in indicators:
            if not (self.project_root / indicator).exists():
                return False

        # Check if README.md contains coding-rule2 specific content
        readme = self.project_root / 'README.md'
        if readme.exists():
            try:
                with open(readme, encoding='utf-8') as f:
                    content = f.read()
                    # Look for coding-rule2 specific markers
                    if 'coding-rule2' in content.lower() or 'AI Safety Governance' in content:
                        return True
            except:
                pass

        return False

    def audit_root_directory(self) -> Dict:
        """Audit root directory compliance"""
        root_files = [f for f in os.listdir(self.project_root)
                     if os.path.isfile(os.path.join(self.project_root, f))]

        violations = []
        misplaced = []

        for file in root_files:
            if file not in self.ALLOWED_ROOT_FILES:
                violations.append(file)

                # Determine where it should go
                target = self._get_target_location(file)
                if target:
                    misplaced.append((file, target))

        return {
            'total_files': len(root_files),
            'limit': self.ROOT_FILE_LIMIT,
            'over_limit': len(root_files) > self.ROOT_FILE_LIMIT,
            'violations': violations,
            'misplaced': misplaced,
            'compliant': len(violations) == 0 and len(root_files) <= self.ROOT_FILE_LIMIT
        }

    def _get_target_location(self, filename: str) -> str:
        """Determine target location for a file"""
        # Check exact filename matches
        if filename in self.FILE_RULES:
            return self.FILE_RULES[filename]

        # Check pattern matches
        import re
        for pattern, target in self.PATTERN_RULES.items():
            if re.match(pattern, filename):
                # Special handling for markdown files
                if pattern.endswith(r'\.md$'):
                    if filename in ['README.md', 'CLAUDE.md', 'Index.md']:
                        return None  # Keep in root
                return target

        # Default fallback based on file type
        if filename.startswith('.'):
            return 'config/'
        elif filename.endswith('.md'):
            return 'docs/'
        elif filename.endswith('.py') and 'setup' in filename:
            return 'scripts/setup/'
        elif filename.endswith('.sh'):
            return 'scripts/'

        return None

    def enforce_organization(self, dry_run: bool = False) -> Dict:
        """Enforce file organization rules"""
        audit = self.audit_root_directory()

        if audit['compliant']:
            return {
                'status': 'compliant',
                'message': f"✅ Root directory compliant: {audit['total_files']}/{self.ROOT_FILE_LIMIT} files",
                'actions': []
            }

        actions = []

        # Move misplaced files
        for file, target_dir in audit['misplaced']:
            source = self.project_root / file
            target_path = self.project_root / target_dir

            # Create target directory if it doesn't exist
            target_path.mkdir(parents=True, exist_ok=True)

            target_file = target_path / file

            action = {
                'type': 'move',
                'source': str(source),
                'target': str(target_file),
                'reason': 'File not allowed in root directory'
            }

            if not dry_run:
                try:
                    shutil.move(str(source), str(target_file))
                    action['status'] = 'success'
                    self.moved_files.append((str(source), str(target_file)))
                except Exception as e:
                    action['status'] = 'failed'
                    action['error'] = str(e)
            else:
                action['status'] = 'dry_run'

            actions.append(action)

        # Final audit after moves
        if not dry_run:
            final_audit = self.audit_root_directory()
            compliance_status = 'compliant' if final_audit['compliant'] else 'non_compliant'
        else:
            compliance_status = 'dry_run'

        return {
            'status': compliance_status,
            'initial_audit': audit,
            'actions': actions,
            'files_moved': len([a for a in actions if a['status'] == 'success'])
        }

    def generate_compliance_report(self) -> Dict:
        """Generate detailed compliance report"""
        audit = self.audit_root_directory()

        # Check directory structure
        required_dirs = ['config', 'docs', 'scripts', 'src', 'tests', 'runtime', 'data']
        missing_dirs = []
        for dir_name in required_dirs:
            if not (self.project_root / dir_name).exists():
                missing_dirs.append(dir_name)

        # Get severity level
        severity = self._get_severity_level(audit['total_files'])

        report = {
            'timestamp': datetime.now().isoformat(),
            'project_root': str(self.project_root),
            'compliance': audit,
            'severity': severity,
            'missing_directories': missing_dirs,
            'recommendations': self._generate_recommendations(audit, missing_dirs)
        }

        return report

    def _get_severity_level(self, file_count: int) -> Dict:
        """Determine violation severity level"""
        if file_count <= self.ROOT_FILE_LIMIT:
            return {'level': 'GREEN', 'action': 'none', 'message': '✅ Compliant'}
        elif file_count <= 15:
            return {'level': 'YELLOW', 'action': 'auto_move', 'message': '🟡 Auto-enforcement triggered'}
        else:
            return {'level': 'RED', 'action': 'block_commits', 'message': '🔴 CRITICAL: Manual cleanup required'}

    def _generate_recommendations(self, audit: Dict, missing_dirs: List[str]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        if audit['over_limit']:
            recommendations.append(f"Reduce root files from {audit['total_files']} to {self.ROOT_FILE_LIMIT} maximum")

        if audit['violations']:
            recommendations.append(f"Move {len(audit['violations'])} misplaced files to appropriate directories")

        if missing_dirs:
            recommendations.append(f"Create missing directories: {', '.join(missing_dirs)}")

        if not recommendations:
            recommendations.append("Maintain current organization structure")

        return recommendations

    def save_report(self, report: Dict, filename: str = None):
        """Save compliance report to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"file_organization_report_{timestamp}.json"

        report_path = self.project_root / "runtime" / "compliance_reports"
        report_path.mkdir(parents=True, exist_ok=True)

        with open(report_path / filename, 'w') as f:
            json.dump(report, f, indent=2)

        return str(report_path / filename)


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Strict File Organization Enforcer')
    parser.add_argument('--check-only', action='store_true', help='Check compliance without making changes')
    parser.add_argument('--force', action='store_true', help='Force file reorganization')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be moved without doing it')
    parser.add_argument('--report', action='store_true', help='Generate detailed compliance report')
    parser.add_argument('--project-root', type=str, help='Project root directory')

    args = parser.parse_args()

    organizer = StrictFileOrganizer(args.project_root)

    if args.check_only:
        audit = organizer.audit_root_directory()
        print("📊 ROOT DIRECTORY AUDIT")
        print(f"Files: {audit['total_files']}/{organizer.ROOT_FILE_LIMIT}")
        print(f"Status: {'✅ COMPLIANT' if audit['compliant'] else '❌ NON-COMPLIANT'}")

        if audit['violations']:
            print(f"\n🔴 VIOLATIONS ({len(audit['violations'])}):")
            for file in audit['violations']:
                target = organizer._get_target_location(file)
                print(f"  • {file} → {target if target else 'UNKNOWN'}")

        severity = organizer._get_severity_level(audit['total_files'])
        print(f"\n🚨 SEVERITY: {severity['level']} - {severity['message']}")

        sys.exit(0 if audit['compliant'] else 1)

    elif args.report:
        report = organizer.generate_compliance_report()
        report_file = organizer.save_report(report)

        print("📋 COMPLIANCE REPORT GENERATED")
        print(f"File: {report_file}")
        print(f"Status: {report['severity']['message']}")
        print(f"Recommendations: {len(report['recommendations'])}")

        for rec in report['recommendations']:
            print(f"  • {rec}")

    elif args.force or args.dry_run:
        result = organizer.enforce_organization(dry_run=args.dry_run)

        print(f"🔧 FILE ORGANIZATION {'DRY RUN' if args.dry_run else 'ENFORCEMENT'}")
        print(f"Status: {result['status'].upper()}")

        if result['actions']:
            print(f"\n📋 ACTIONS ({len(result['actions'])}):")
            for action in result['actions']:
                status_icon = {'success': '✅', 'failed': '❌', 'dry_run': '🔍'}[action['status']]
                print(f"  {status_icon} {action['type'].upper()}: {Path(action['source']).name} → {action['target']}")

        if not args.dry_run and result['files_moved'] > 0:
            print(f"\n🎉 Successfully moved {result['files_moved']} files")

        final_audit = organizer.audit_root_directory()
        print(f"\n📊 FINAL STATUS: {final_audit['total_files']}/{organizer.ROOT_FILE_LIMIT} files in root")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
