#!/usr/bin/env python3
"""
AI自動学習システム有効化スクリプト
Claude Code → 自動パフォーマンス送信 → n8n → Supabase学習
"""

import os
import sys
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root / "src"))

def update_autonomous_growth_engine():
    """自律成長エンジンのWebhook URL更新"""
    growth_engine_path = project_root / "src/ai/autonomous_growth_engine.py"
    
    if not growth_engine_path.exists():
        print("❌ autonomous_growth_engine.py not found")
        return False
    
    # Read current content
    with open(growth_engine_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update webhook URL
    old_url = 'self.n8n_webhook_url = "https://n8n.cloud/webhook/claude-performance"'
    new_url = 'self.n8n_webhook_url = "https://dd1107.app.n8n.cloud/webhook/claude-performance"'
    
    if old_url in content:
        content = content.replace(old_url, new_url)
        with open(growth_engine_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ Webhook URL updated in autonomous_growth_engine.py")
        return True
    else:
        print("⚠️ Webhook URL already up to date")
        return True

def create_hook_integration():
    """Claude Code Hook統合システム作成"""
    hook_path = project_root / "scripts/hooks/performance_auto_sender.py"
    
    hook_content = '''#!/usr/bin/env python3
"""
Claude Code Performance Auto Sender
Claude Codeの実行終了時に自動的にパフォーマンスデータをn8nに送信
"""

import os
import sys
import json
import time
import requests
from datetime import datetime
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root / "src"))

def send_performance_data(
    success: bool = True,
    execution_time: float = 0.0,
    tools_used: list = None,
    thinking_tag_used: bool = True,
    todo_tracking: bool = True,
    task_complexity: str = "medium",
    error_count: int = 0,
    user_feedback: str = None
):
    """Claude Codeパフォーマンスデータを自動送信"""
    
    webhook_url = os.getenv('N8N_WEBHOOK_URL', 'https://dd1107.app.n8n.cloud/webhook/claude-performance')
    
    # Performance data preparation
    performance_data = {
        "session_id": f"auto_{int(time.time())}",
        "timestamp": datetime.now().isoformat(),
        "success": success,
        "execution_time": execution_time,
        "tools_used": tools_used or [],
        "thinking_tag_used": thinking_tag_used,
        "todo_tracking": todo_tracking,
        "task_complexity": task_complexity,
        "error_count": error_count,
        "user_feedback": user_feedback,
        "auto_generated": True
    }
    
    try:
        response = requests.post(
            webhook_url,
            json=performance_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"🤖 AI Learning: Data sent successfully")
            return True
        else:
            print(f"⚠️ AI Learning: Failed to send data ({response.status_code})")
            return False
            
    except Exception as e:
        print(f"❌ AI Learning: Error sending data: {e}")
        return False

def hook_post_tool_use(tool_name: str, success: bool, execution_time: float, error: str = None):
    """ツール使用後フック"""
    send_performance_data(
        success=success,
        execution_time=execution_time,
        tools_used=[tool_name],
        error_count=1 if error else 0,
        user_feedback=f"Tool: {tool_name}, Error: {error}" if error else None
    )

def hook_session_end(total_tools: int, total_time: float, overall_success: bool):
    """セッション終了フック"""
    send_performance_data(
        success=overall_success,
        execution_time=total_time,
        tools_used=[f"session_total_{total_tools}_tools"],
        task_complexity="complex" if total_tools > 5 else "medium" if total_tools > 2 else "simple"
    )

if __name__ == "__main__":
    # Manual test
    print("🧪 Testing auto learning system...")
    result = send_performance_data(
        success=True,
        execution_time=1.5,
        tools_used=["Test"],
        user_feedback="Manual test execution"
    )
    print(f"Test result: {'✅ Success' if result else '❌ Failed'}")
'''
    
    hook_path.parent.mkdir(parents=True, exist_ok=True)
    with open(hook_path, 'w', encoding='utf-8') as f:
        f.write(hook_content)
    
    # Make executable
    os.chmod(hook_path, 0o755)
    print(f"✅ Auto sender hook created: {hook_path}")
    return hook_path

def create_runtime_integration():
    """Runtime Dispatcher統合"""
    integration_path = project_root / "src/orchestrator/performance_auto_reporter.py"
    
    integration_content = '''#!/usr/bin/env python3
"""
Performance Auto Reporter
Runtime Dispatcherと統合してClaude Codeの実行をリアルタイム監視
"""

import time
import threading
from typing import Dict, List, Any
from datetime import datetime

class PerformanceAutoReporter:
    """パフォーマンス自動レポーター"""
    
    def __init__(self):
        self.session_start = time.time()
        self.tools_used = []
        self.error_count = 0
        self.thinking_used = False
        self.todo_used = False
        
    def track_tool_use(self, tool_name: str, success: bool = True, error: str = None):
        """ツール使用追跡"""
        self.tools_used.append(tool_name)
        if error:
            self.error_count += 1
        
        # Check for thinking and todo usage
        if 'thinking' in tool_name.lower():
            self.thinking_used = True
        if 'todo' in tool_name.lower():
            self.todo_used = True
            
    def generate_report(self) -> Dict[str, Any]:
        """レポート生成"""
        execution_time = time.time() - self.session_start
        
        return {
            "session_id": f"runtime_{int(self.session_start)}",
            "success": self.error_count == 0,
            "execution_time": execution_time,
            "tools_used": list(set(self.tools_used)),  # Remove duplicates
            "thinking_tag_used": self.thinking_used,
            "todo_tracking": self.todo_used,
            "task_complexity": self._calculate_complexity(),
            "error_count": self.error_count,
            "timestamp": datetime.now().isoformat()
        }
    
    def _calculate_complexity(self) -> str:
        """タスク複雑さ計算"""
        tool_count = len(set(self.tools_used))
        if tool_count > 5:
            return "complex"
        elif tool_count > 2:
            return "medium"
        else:
            return "simple"
    
    def send_report(self):
        """レポート送信"""
        try:
            from scripts.hooks.performance_auto_sender import send_performance_data
            report = self.generate_report()
            return send_performance_data(**report)
        except ImportError:
            print("⚠️ Performance auto sender not available")
            return False

# Global instance for runtime integration
_global_reporter = PerformanceAutoReporter()

def get_performance_reporter() -> PerformanceAutoReporter:
    """グローバルレポーター取得"""
    return _global_reporter
'''
    
    with open(integration_path, 'w', encoding='utf-8') as f:
        f.write(integration_content)
    
    print(f"✅ Runtime integration created: {integration_path}")
    return integration_path

def activate_auto_learning():
    """自動学習システム有効化"""
    print("🚀 AI自動学習システム有効化開始")
    print("=" * 50)
    
    # Step 1: Update autonomous growth engine
    print("1. 自律成長エンジン更新...")
    update_autonomous_growth_engine()
    
    # Step 2: Create hook integration
    print("2. Hook統合システム作成...")
    hook_path = create_hook_integration()
    
    # Step 3: Create runtime integration  
    print("3. Runtime統合システム作成...")
    integration_path = create_runtime_integration()
    
    # Step 4: Test hook system
    print("4. システムテスト...")
    test_result = test_auto_learning()
    
    print(f"\\n🎉 自動学習システム有効化完了！")
    print("=" * 50)
    print("✅ Webhook URL更新完了")
    print(f"✅ Auto sender hook: {hook_path}")
    print(f"✅ Runtime integration: {integration_path}")
    print(f"✅ System test: {'SUCCESS' if test_result else 'NEEDS CHECK'}")
    
    print("\\n🤖 これで Claude Code を使うたびに自動的に AI が学習します！")
    
    return test_result

def test_auto_learning():
    """自動学習システムテスト"""
    try:
        # Import and test the hook
        hook_path = project_root / "scripts/hooks/performance_auto_sender.py"
        if hook_path.exists():
            import subprocess
            result = subprocess.run([sys.executable, str(hook_path)], 
                                  capture_output=True, text=True, timeout=30)
            return result.returncode == 0
        return False
    except Exception as e:
        print(f"Test error: {e}")
        return False

if __name__ == "__main__":
    activate_auto_learning()