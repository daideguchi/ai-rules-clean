#!/usr/bin/env python3
"""
🧠 Memory Manager - Enhanced Memory System Interface
===================================================
Command-line interface for the enhanced memory inheritance system
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.memory.enhanced_memory_inheritance import get_memory_system


class MemoryManager:
    """Command-line interface for memory management"""

    def __init__(self):
        self.memory_system = get_memory_system()

    def status(self) -> str:
        """Show memory system status"""
        return self.memory_system.get_inheritance_report()

    def verify(self) -> str:
        """Verify memory inheritance"""
        verified, message = self.memory_system.verify_memory_inheritance()
        status = "✅ VERIFIED" if verified else "❌ FAILED"
        return f"🔍 Memory Verification: {status}\n📝 Details: {message}"

    def search(self, query: str, limit: int = 10) -> str:
        """Search memories"""
        results = self.memory_system.search_memories(query, limit)

        if not results:
            return f"❌ No memories found for query: {query}"

        output = [f"🔍 Found {len(results)} memories for '{query}':"]
        output.append("-" * 50)

        for i, memory in enumerate(results, 1):
            output.append(f"{i}. {memory.key} (importance: {memory.importance})")
            output.append(f"   {memory.content}")
            output.append(f"   Category: {memory.category} | Tags: {', '.join(memory.tags)}")
            output.append("")

        return "\n".join(output)

    def store(self, key: str, content: str, importance: int = 5,
              category: str = "general", tags: List[str] = None) -> str:
        """Store a new memory"""
        success = self.memory_system.store_memory(key, content, importance, category, tags)

        if success:
            return f"✅ Memory stored successfully: {key}"
        else:
            return f"❌ Failed to store memory: {key}"

    def retrieve(self, key: str) -> str:
        """Retrieve a specific memory"""
        memory = self.memory_system.retrieve_memory(key)

        if not memory:
            return f"❌ Memory not found: {key}"

        output = [f"📝 Memory: {memory.key}"]
        output.append(f"Content: {memory.content}")
        output.append(f"Importance: {memory.importance}")
        output.append(f"Category: {memory.category}")
        output.append(f"Tags: {', '.join(memory.tags)}")
        output.append(f"Created: {memory.timestamp}")
        output.append(f"Accessed: {memory.access_count} times")
        if memory.last_accessed:
            output.append(f"Last accessed: {memory.last_accessed}")
        if memory.violation_count > 0:
            output.append(f"⚠️ Violations: {memory.violation_count}")

        return "\n".join(output)

    def violations(self) -> str:
        """Show violation summary"""
        violations = self.memory_system.get_violation_summary()

        if not violations:
            return "✅ No violations recorded"

        output = [f"⚠️ Violation Summary ({len(violations)} types):"]
        output.append("-" * 40)

        for violation_type, data in violations.items():
            output.append(f"• {violation_type}: {data['count']} times")
            output.append(f"  Last occurrence: {data['last_occurrence']}")

        return "\n".join(output)

    def record_violation(self, violation_type: str, description: str) -> str:
        """Record a new violation"""
        success = self.memory_system.record_violation(violation_type, description)

        if success:
            return f"⚠️ Violation recorded: {violation_type}"
        else:
            return f"❌ Failed to record violation: {violation_type}"

    def critical_reminders(self) -> str:
        """Show critical reminders"""
        reminders = self.memory_system.get_critical_reminders()

        if not reminders:
            return "❌ No critical reminders found"

        output = [f"🔴 Critical Reminders ({len(reminders)}):"]
        output.append("=" * 40)

        for i, reminder in enumerate(reminders, 1):
            output.append(f"{i}. {reminder}")

        return "\n".join(output)

    def backup(self, filename: str = None) -> str:
        """Create memory backup"""
        if not filename:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"memory_backup_{timestamp}.json"

        try:
            backup_path = Path(filename)

            # Export all memories
            memories = self.memory_system.search_memories("", limit=10000)  # Get all

            backup_data = {
                "timestamp": datetime.now().isoformat(),
                "memory_count": len(memories),
                "memories": []
            }

            for memory in memories:
                backup_data["memories"].append({
                    "key": memory.key,
                    "content": memory.content,
                    "importance": memory.importance,
                    "category": memory.category,
                    "tags": memory.tags,
                    "violation_count": memory.violation_count,
                    "access_count": memory.access_count
                })

            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)

            return f"✅ Memory backup created: {backup_path}"

        except Exception as e:
            return f"❌ Backup failed: {e}"

    def restore(self, filename: str) -> str:
        """Restore memory from backup"""
        try:
            backup_path = Path(filename)

            if not backup_path.exists():
                return f"❌ Backup file not found: {filename}"

            with open(backup_path, encoding='utf-8') as f:
                backup_data = json.load(f)

            memories = backup_data.get("memories", [])
            restored_count = 0

            for memory_data in memories:
                success = self.memory_system.store_memory(
                    key=memory_data["key"],
                    content=memory_data["content"],
                    importance=memory_data["importance"],
                    category=memory_data["category"],
                    tags=memory_data["tags"]
                )

                if success:
                    restored_count += 1

            return f"✅ Restored {restored_count}/{len(memories)} memories from {filename}"

        except Exception as e:
            return f"❌ Restore failed: {e}"

    def cleanup(self, days: int = 30) -> str:
        """Clean up old data"""
        try:
            self.memory_system.cleanup_old_sessions(days)
            return f"✅ Cleaned up sessions older than {days} days"
        except Exception as e:
            return f"❌ Cleanup failed: {e}"

    def reset_critical(self) -> str:
        """Reset critical memories to default state"""
        try:
            self.memory_system._load_critical_memories()
            return "✅ Critical memories reset to default state"
        except Exception as e:
            return f"❌ Reset failed: {e}"


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description="Enhanced Memory System Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python memory_manager.py status           # Show system status
  python memory_manager.py verify           # Verify memory inheritance
  python memory_manager.py search "specstory"  # Search memories
  python memory_manager.py store "MY_KEY" "My content" --importance 8
  python memory_manager.py violations       # Show violation summary
  python memory_manager.py backup          # Create backup
        """
    )

    parser.add_argument('command', choices=[
        'status', 'verify', 'search', 'store', 'retrieve', 'violations',
        'record-violation', 'critical-reminders', 'backup', 'restore',
        'cleanup', 'reset-critical'
    ], help='Command to execute')

    parser.add_argument('args', nargs='*', help='Command arguments')
    parser.add_argument('--importance', type=int, default=5, help='Memory importance (1-10)')
    parser.add_argument('--category', default='general', help='Memory category')
    parser.add_argument('--tags', nargs='*', help='Memory tags')
    parser.add_argument('--limit', type=int, default=10, help='Search result limit')
    parser.add_argument('--days', type=int, default=30, help='Days for cleanup')

    args = parser.parse_args()

    manager = MemoryManager()

    try:
        if args.command == 'status':
            print(manager.status())

        elif args.command == 'verify':
            print(manager.verify())

        elif args.command == 'search':
            if not args.args:
                print("❌ Search query required")
                sys.exit(1)
            print(manager.search(args.args[0], args.limit))

        elif args.command == 'store':
            if len(args.args) < 2:
                print("❌ Key and content required")
                sys.exit(1)
            print(manager.store(args.args[0], args.args[1], args.importance,
                               args.category, args.tags))

        elif args.command == 'retrieve':
            if not args.args:
                print("❌ Memory key required")
                sys.exit(1)
            print(manager.retrieve(args.args[0]))

        elif args.command == 'violations':
            print(manager.violations())

        elif args.command == 'record-violation':
            if len(args.args) < 2:
                print("❌ Violation type and description required")
                sys.exit(1)
            print(manager.record_violation(args.args[0], args.args[1]))

        elif args.command == 'critical-reminders':
            print(manager.critical_reminders())

        elif args.command == 'backup':
            filename = args.args[0] if args.args else None
            print(manager.backup(filename))

        elif args.command == 'restore':
            if not args.args:
                print("❌ Backup filename required")
                sys.exit(1)
            print(manager.restore(args.args[0]))

        elif args.command == 'cleanup':
            print(manager.cleanup(args.days))

        elif args.command == 'reset-critical':
            print(manager.reset_critical())

    except KeyboardInterrupt:
        print("\n👋 Memory manager interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
