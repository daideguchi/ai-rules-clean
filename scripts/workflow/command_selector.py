#!/usr/bin/env python3
"""
🎯 Interactive Command Selector
===============================
Interactive system to help users navigate and execute the 121+ Makefile commands
"""

import json
import re
import subprocess
from pathlib import Path
from typing import Dict, List


class CommandSelector:
    """Interactive command selector for the Makefile"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.makefile_path = self.project_root / "Makefile"
        self.commands = self._parse_makefile()
        self.categories = self._categorize_commands()
        self.favorites = self._load_favorites()
        self.command_history = self._load_history()

    def _parse_makefile(self) -> Dict[str, str]:
        """Parse Makefile to extract commands and descriptions"""
        commands = {}

        try:
            with open(self.makefile_path, encoding='utf-8') as f:
                content = f.read()

            # Find all command definitions with descriptions
            pattern = r'^([a-zA-Z][a-zA-Z0-9_-]*)\s*:\s*##\s*(.+)$'
            matches = re.findall(pattern, content, re.MULTILINE)

            for command, description in matches:
                commands[command] = description.strip()

            # Find commands without descriptions
            pattern = r'^([a-zA-Z][a-zA-Z0-9_-]*)\s*:'
            all_matches = re.findall(pattern, content, re.MULTILINE)

            for command in all_matches:
                if command not in commands:
                    commands[command] = "No description available"

        except Exception as e:
            print(f"❌ Error parsing Makefile: {e}")

        return commands

    def _categorize_commands(self) -> Dict[str, List[str]]:
        """Categorize commands by functionality"""
        categories = {
            "🎯 Core System": ["help", "install", "test", "status", "cleanup", "validate", "startup", "quick-start"],
            "🤖 AI Organization": [cmd for cmd in self.commands if any(prefix in cmd for prefix in ["ai-", "declare-president", "run-president", "memory-"])],
            "🌐 Web UI": [cmd for cmd in self.commands if any(prefix in cmd for prefix in ["ui-", "claude-code-web-ui", "web-"])],
            "🔧 MCP & API": [cmd for cmd in self.commands if any(prefix in cmd for prefix in ["mcp-", "api-"])],
            "💬 Communication": [cmd for cmd in self.commands if any(prefix in cmd for prefix in ["slack-", "notification-"])],
            "📊 Monitoring": [cmd for cmd in self.commands if any(prefix in cmd for prefix in ["metrics-", "health-", "performance-", "logs-"])],
            "🛠️ Development": [cmd for cmd in self.commands if any(prefix in cmd for prefix in ["dev-", "debug-", "test-"])],
            "🗄️ Database": [cmd for cmd in self.commands if any(prefix in cmd for prefix in ["db-", "backup-", "migrate-"])],
            "🚀 Deployment": [cmd for cmd in self.commands if any(prefix in cmd for prefix in ["deploy-", "docker-", "compose-"])],
            "📁 Project Setup": [cmd for cmd in self.commands if any(prefix in cmd for prefix in ["init-", "template-", "project-"])],
        }

        # Remove empty categories and add uncategorized commands
        categorized_commands = set()
        for category, commands in list(categories.items()):
            if not commands:
                del categories[category]
            else:
                categorized_commands.update(commands)

        # Add uncategorized commands
        uncategorized = [cmd for cmd in self.commands if cmd not in categorized_commands]
        if uncategorized:
            categories["🔧 Other"] = uncategorized

        return categories

    def _load_favorites(self) -> List[str]:
        """Load user's favorite commands"""
        favorites_file = self.project_root / ".command_favorites.json"
        try:
            if favorites_file.exists():
                with open(favorites_file) as f:
                    return json.load(f)
        except:
            pass
        return []

    def _save_favorites(self):
        """Save user's favorite commands"""
        favorites_file = self.project_root / ".command_favorites.json"
        try:
            with open(favorites_file, 'w') as f:
                json.dump(self.favorites, f, indent=2)
        except Exception as e:
            print(f"⚠️ Could not save favorites: {e}")

    def _load_history(self) -> List[str]:
        """Load command execution history"""
        history_file = self.project_root / ".command_history.json"
        try:
            if history_file.exists():
                with open(history_file) as f:
                    return json.load(f)
        except:
            pass
        return []

    def _save_history(self):
        """Save command execution history"""
        history_file = self.project_root / ".command_history.json"
        try:
            with open(history_file, 'w') as f:
                json.dump(self.command_history[-50:], f, indent=2)  # Keep last 50 commands
        except Exception as e:
            print(f"⚠️ Could not save history: {e}")

    def display_main_menu(self):
        """Display the main menu"""
        print("\n" + "="*60)
        print("🎯 COMMAND SELECTOR - Choose Your Action")
        print("="*60)
        print("1. 📚 Browse by Category")
        print("2. 🔍 Search Commands")
        print("3. ⭐ Favorite Commands")
        print("4. 📜 Recent Commands")
        print("5. 🚀 Quick Start Workflows")
        print("6. 📊 Command Statistics")
        print("7. ❓ Help")
        print("0. 🚪 Exit")
        print("-"*60)

    def display_categories(self):
        """Display command categories"""
        print("\n📚 Command Categories:")
        print("-"*40)

        for i, (category, commands) in enumerate(self.categories.items(), 1):
            print(f"{i:2d}. {category} ({len(commands)} commands)")

        print(f"{len(self.categories) + 1:2d}. 🔙 Back to Main Menu")

    def display_category_commands(self, category: str):
        """Display commands in a category"""
        commands = self.categories[category]

        print(f"\n{category} Commands:")
        print("-"*50)

        for i, cmd in enumerate(commands, 1):
            description = self.commands.get(cmd, "No description")
            favorite_mark = "⭐" if cmd in self.favorites else "  "
            print(f"{i:2d}. {favorite_mark} {cmd}")
            print(f"     {description}")

        print(f"{len(commands) + 1:2d}. 🔙 Back to Categories")

    def search_commands(self, query: str) -> List[str]:
        """Search commands by name or description"""
        query = query.lower()
        results = []

        for cmd, desc in self.commands.items():
            if (query in cmd.lower() or
                query in desc.lower()):
                results.append(cmd)

        return results

    def execute_command(self, command: str) -> bool:
        """Execute a make command"""
        try:
            print(f"\n🚀 Executing: make {command}")
            print("-"*50)

            # Add to history
            if command in self.command_history:
                self.command_history.remove(command)
            self.command_history.append(command)
            self._save_history()

            # Execute the command
            result = subprocess.run(
                ["make", command],
                cwd=self.project_root,
                capture_output=False,
                text=True
            )

            print("-"*50)
            if result.returncode == 0:
                print("✅ Command executed successfully!")
            else:
                print(f"❌ Command failed with exit code {result.returncode}")

            return result.returncode == 0

        except KeyboardInterrupt:
            print("\n⚠️ Command interrupted by user")
            return False
        except Exception as e:
            print(f"❌ Error executing command: {e}")
            return False

    def toggle_favorite(self, command: str):
        """Toggle command favorite status"""
        if command in self.favorites:
            self.favorites.remove(command)
            print(f"💔 Removed {command} from favorites")
        else:
            self.favorites.append(command)
            print(f"⭐ Added {command} to favorites")

        self._save_favorites()

    def display_quick_workflows(self):
        """Display predefined quick workflows"""
        workflows = {
            "🚀 New User Setup": [
                "startup-check",
                "declare-president",
                "mcp-setup",
                "slack-setup"
            ],
            "💻 Development Start": [
                "declare-president",
                "ai-org-start",
                "mcp-start-all",
                "claude-code-web-ui"
            ],
            "🔧 System Maintenance": [
                "cleanup",
                "validate",
                "health-check-all",
                "backup-create"
            ],
            "🧪 Testing Workflow": [
                "test",
                "validate",
                "lint",
                "safety-enforce"
            ]
        }

        print("\n🚀 Quick Start Workflows:")
        print("-"*40)

        for i, (name, commands) in enumerate(workflows.items(), 1):
            print(f"{i}. {name}")
            for cmd in commands:
                status = "✅" if cmd in self.commands else "❌"
                print(f"   {status} make {cmd}")
            print()

    def display_statistics(self):
        """Display command statistics"""
        print("\n📊 Command Statistics:")
        print("-"*30)
        print(f"Total Commands: {len(self.commands)}")
        print(f"Categories: {len(self.categories)}")
        print(f"Favorites: {len(self.favorites)}")
        print(f"Recent Commands: {len(self.command_history)}")

        if self.command_history:
            print(f"Most Recent: {self.command_history[-1]}")

        print("\nCategory Distribution:")
        for category, commands in self.categories.items():
            print(f"  {category}: {len(commands)} commands")

    def run(self):
        """Main interactive loop"""
        print("🎯 Welcome to the Command Selector!")
        print(f"📁 Project: {self.project_root.name}")
        print(f"📊 Found {len(self.commands)} commands")

        while True:
            try:
                self.display_main_menu()
                choice = input("\nEnter your choice (0-7): ").strip()

                if choice == '0':
                    print("👋 Goodbye!")
                    break
                elif choice == '1':
                    self._handle_category_browsing()
                elif choice == '2':
                    self._handle_search()
                elif choice == '3':
                    self._handle_favorites()
                elif choice == '4':
                    self._handle_history()
                elif choice == '5':
                    self.display_quick_workflows()
                elif choice == '6':
                    self.display_statistics()
                elif choice == '7':
                    self._display_help()
                else:
                    print("❌ Invalid choice. Please try again.")

                input("\nPress Enter to continue...")

            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

    def _handle_category_browsing(self):
        """Handle category browsing"""
        while True:
            self.display_categories()
            try:
                choice = int(input("\nSelect category: "))
                if choice == len(self.categories) + 1:
                    break
                elif 1 <= choice <= len(self.categories):
                    category_name = list(self.categories.keys())[choice - 1]
                    self._handle_category_commands(category_name)
                else:
                    print("❌ Invalid choice.")
            except ValueError:
                print("❌ Please enter a number.")

    def _handle_category_commands(self, category: str):
        """Handle commands within a category"""
        while True:
            self.display_category_commands(category)
            try:
                choice = int(input("\nSelect command: "))
                commands = self.categories[category]

                if choice == len(commands) + 1:
                    break
                elif 1 <= choice <= len(commands):
                    command = commands[choice - 1]
                    self._handle_command_action(command)
                else:
                    print("❌ Invalid choice.")
            except ValueError:
                print("❌ Please enter a number.")

    def _handle_command_action(self, command: str):
        """Handle actions for a specific command"""
        while True:
            description = self.commands.get(command, "No description")
            favorite_mark = "⭐" if command in self.favorites else ""

            print(f"\n🎯 Command: {command} {favorite_mark}")
            print(f"📝 Description: {description}")
            print("-"*50)
            print("1. 🚀 Execute")
            print("2. ⭐ Toggle Favorite")
            print("3. 📋 Copy to Clipboard")
            print("4. 🔙 Back")

            choice = input("\nChoose action (1-4): ").strip()

            if choice == '1':
                self.execute_command(command)
            elif choice == '2':
                self.toggle_favorite(command)
            elif choice == '3':
                try:
                    import pyperclip
                    pyperclip.copy(f"make {command}")
                    print(f"📋 Copied 'make {command}' to clipboard!")
                except ImportError:
                    print("⚠️ pyperclip not installed. Install with: pip install pyperclip")
            elif choice == '4':
                break
            else:
                print("❌ Invalid choice.")

    def _handle_search(self):
        """Handle command search"""
        query = input("\n🔍 Enter search query: ").strip()
        if query:
            results = self.search_commands(query)
            if results:
                print(f"\n🔍 Found {len(results)} commands:")
                for i, cmd in enumerate(results, 1):
                    desc = self.commands[cmd]
                    favorite_mark = "⭐" if cmd in self.favorites else "  "
                    print(f"{i:2d}. {favorite_mark} {cmd}")
                    print(f"     {desc}")
            else:
                print("❌ No commands found.")

    def _handle_favorites(self):
        """Handle favorite commands"""
        if not self.favorites:
            print("\n💔 No favorite commands yet.")
            return

        print(f"\n⭐ Your {len(self.favorites)} Favorite Commands:")
        for i, cmd in enumerate(self.favorites, 1):
            desc = self.commands.get(cmd, "No description")
            print(f"{i:2d}. {cmd}")
            print(f"     {desc}")

    def _handle_history(self):
        """Handle command history"""
        if not self.command_history:
            print("\n📜 No command history yet.")
            return

        recent = self.command_history[-10:]  # Last 10 commands
        print(f"\n📜 Recent Commands ({len(recent)}):")
        for i, cmd in enumerate(reversed(recent), 1):
            desc = self.commands.get(cmd, "No description")
            print(f"{i:2d}. {cmd}")
            print(f"     {desc}")

    def _display_help(self):
        """Display help information"""
        print("\n❓ Help - Command Selector")
        print("="*40)
        print("This tool helps you navigate and execute the 121+ Makefile commands.")
        print("\nFeatures:")
        print("• 📚 Browse commands by category")
        print("• 🔍 Search commands by name or description")
        print("• ⭐ Save favorite commands")
        print("• 📜 View command history")
        print("• 🚀 Quick workflow templates")
        print("• 📊 Command statistics")
        print("\nTips:")
        print("• Use Ctrl+C to interrupt command execution")
        print("• Favorites and history are saved automatically")
        print("• Search is case-insensitive")


def main():
    """Main function"""
    selector = CommandSelector()
    selector.run()


if __name__ == "__main__":
    main()
