#!/usr/bin/env python3
"""
New Project Initialization Script
新プロジェクト初期化スクリプト

Customizes coding-rule2 template for new projects.
"""

from pathlib import Path
from typing import Dict


class NewProjectInitializer:
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()

    def initialize_for_project_type(self, project_type: str, project_name: str):
        """Initialize project based on type"""
        print(f"🚀 Initializing {project_type} project: {project_name}")

        # Define project-specific configurations
        configurations = {
            'web': {
                'allowed_files': [
                    'README.md', 'package.json', 'package-lock.json',
                    'index.html', 'vite.config.js', '.gitignore',
                    'LICENSE', 'tsconfig.json', '.env'
                ],
                'allowed_dirs': [
                    'src', 'public', 'docs', 'tests', 'scripts', 'node_modules', 'dist'
                ],
                'file_limit': 15
            },
            'python': {
                'allowed_files': [
                    'README.md', 'setup.py', 'pyproject.toml', 'requirements.txt',
                    'LICENSE', '.gitignore', 'MANIFEST.in', 'tox.ini',
                    'CHANGELOG.md', '.env'
                ],
                'allowed_dirs': [
                    'src', 'docs', 'tests', 'examples', 'scripts', '.tox', 'dist'
                ],
                'file_limit': 12
            },
            'ai-project': {  # Keep coding-rule2 structure for AI projects
                'allowed_files': [
                    'README.md', 'Makefile', 'pyproject.toml', 'requirements.txt',
                    'LICENSE', 'CLAUDE.md', 'Index.md', '.gitignore',
                    '.env', '.mcp.json', '.mypy.ini', 'docker-compose.yml'
                ],
                'allowed_dirs': [
                    'config', 'docs', 'scripts', 'src', 'tests', 'runtime', 'data', '.cursor'
                ],
                'file_limit': 12
            },
            'custom': {  # Let user customize
                'allowed_files': ['README.md', '.gitignore', 'LICENSE'],
                'allowed_dirs': ['src', 'docs', 'tests', 'scripts'],
                'file_limit': 20
            }
        }

        if project_type not in configurations:
            print(f"❌ Unknown project type: {project_type}")
            print(f"Available types: {', '.join(configurations.keys())}")
            return False

        config = configurations[project_type]

        # Update file organization rules
        self._update_file_organizer(config)

        # Update documentation
        self._update_documentation(project_name, project_type, config)

        # Create project-specific README
        self._create_project_readme(project_name, project_type)

        print(f"✅ Project '{project_name}' initialized as {project_type} project")
        print(f"📋 File limit: {config['file_limit']}")
        print(f"📁 Allowed directories: {', '.join(config['allowed_dirs'])}")

        return True

    def _update_file_organizer(self, config: Dict):
        """Update strict-file-organizer.py with project-specific rules"""
        organizer_path = self.project_root / 'scripts/automation/strict-file-organizer.py'

        if not organizer_path.exists():
            print(f"❌ File organizer not found: {organizer_path}")
            return

        with open(organizer_path, encoding='utf-8') as f:
            content = f.read()

        # Update ROOT_FILE_LIMIT
        content = content.replace(
            'self.ROOT_FILE_LIMIT = 12',
            f'self.ROOT_FILE_LIMIT = {config["file_limit"]}'
        )

        # Update ALLOWED_ROOT_FILES
        files_str = "{\n            " + ",\n            ".join([f"'{f}'" for f in config['allowed_files']]) + "\n        }"
        content = content.replace(
            "self.ALLOWED_ROOT_FILES = {\n            'README.md', 'Makefile', 'pyproject.toml', 'requirements.txt',\n            'LICENSE', 'CLAUDE.md', 'Index.md', '.gitignore',\n            '.env', '.mcp.json', '.mypy.ini', 'docker-compose.yml'\n        }",
            f"self.ALLOWED_ROOT_FILES = {files_str}"
        )

        # Update ALLOWED_ROOT_DIRS
        dirs_str = "{\n            " + ",\n            ".join([f"'{d}'" for d in config['allowed_dirs']]) + "\n        }"
        content = content.replace(
            "self.ALLOWED_ROOT_DIRS = {\n            'config', 'docs', 'scripts', 'src', 'tests', 'runtime', 'data', '.cursor'\n        }",
            f"self.ALLOWED_ROOT_DIRS = {dirs_str}"
        )

        # Update project detection
        content = content.replace(
            'coding-rule2',
            'this-project'  # Generic identifier
        )

        with open(organizer_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print("✅ Updated file organizer rules")

    def _update_documentation(self, project_name: str, project_type: str, config: Dict):
        """Update documentation with project-specific information"""
        rules_path = self.project_root / 'docs/04_reference/STRICT_FILE_ORGANIZATION_RULES.md'

        if not rules_path.exists():
            print(f"❌ Rules documentation not found: {rules_path}")
            return

        with open(rules_path, encoding='utf-8') as f:
            content = f.read()

        # Update title and header
        content = content.replace(
            'Strict File Organization Rules - 絶対遵守システム (coding-rule2専用)',
            f'Strict File Organization Rules - {project_name} Project'
        )

        content = content.replace(
            '⚠️ **重要**: これらのルールは`coding-rule2`プロジェクト専用に設計されています。',
            f'📋 **Project**: {project_name} ({project_type} project)'
        )

        # Update file limit
        content = content.replace(
            '**絶対最大ファイル数**: 12個まで',
            f'**絶対最大ファイル数**: {config["file_limit"]}個まで'
        )

        with open(rules_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print("✅ Updated documentation")

    def _create_project_readme(self, project_name: str, project_type: str):
        """Create project-specific README"""
        readme_path = self.project_root / 'README.md'

        readme_content = f"""# {project_name}

A {project_type} project based on the coding-rule2 template.

## Project Organization

This project follows strict file organization rules to maintain clarity and scalability.

### File Structure
- **Maximum files in root**: See project configuration
- **Organized folders**: All files categorized into appropriate directories
- **Automatic enforcement**: Pre-commit hooks prevent violations

### Quick Start

1. **Install dependencies**:
   ```bash
   make install
   ```

2. **Check project organization**:
   ```bash
   make check-file-organization
   ```

3. **Run tests**:
   ```bash
   make test
   ```

## Development

### File Organization
This project enforces strict file organization rules. See `docs/04_reference/STRICT_FILE_ORGANIZATION_RULES.md` for details.

### Commands
- `make enforce-file-organization` - Force file organization compliance
- `make check-file-organization` - Check organization status
- `make root-audit` - Quick file count check

## Template Information

This project was initialized from the [coding-rule2](https://github.com/your-repo/coding-rule2) template.
The file organization rules have been customized for {project_type} projects.

## License

See LICENSE file for details.
"""

        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)

        print("✅ Created project README")


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Initialize new project from coding-rule2 template')
    parser.add_argument('project_name', help='Name of the new project')
    parser.add_argument('--type', choices=['web', 'python', 'ai-project', 'custom'],
                       default='custom', help='Project type')
    parser.add_argument('--project-root', help='Project root directory')

    args = parser.parse_args()

    initializer = NewProjectInitializer(args.project_root)
    success = initializer.initialize_for_project_type(args.type, args.project_name)

    if success:
        print(f"\n🎉 Project '{args.project_name}' successfully initialized!")
        print("📋 Next steps:")
        print("  1. Review and customize file organization rules")
        print("  2. Update project-specific configurations")
        print("  3. Run 'make check-file-organization' to verify setup")
    else:
        print(f"\n❌ Failed to initialize project '{args.project_name}'")


if __name__ == "__main__":
    main()
