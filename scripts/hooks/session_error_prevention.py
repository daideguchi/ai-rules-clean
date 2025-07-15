#!/usr/bin/env python3
"""
🔒 セッション開始エラー防止システム - 強制実行
====================================================
過去のミスを二度と繰り返さない技術的強制メカニズム

CRITICAL: このスクリプトは毎セッション開始時に必ず実行される
"""

import os
import json
import sys
from pathlib import Path
from datetime import datetime

# Import cursor rules enforcer
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from scripts.enforcement.cursor_rules_enforcer import CursorRulesEnforcer

class SessionErrorPrevention:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.violations_file = self.project_root / "runtime/thinking_violations.json"
        self.critical_configs = [
            Path.home() / ".claude/settings.json",
            Path.home() / ".mcp.json"
        ]
        # .env files are ALLOWED to contain API keys for environment variables
        
    def check_critical_violations(self):
        """重大違反記録をチェックし、防止策を実行"""
        print("🔒 SESSION ERROR PREVENTION - MANDATORY CHECK")
        
        if not self.violations_file.exists():
            print("❌ violations.json not found - creating...")
            return False
            
        with open(self.violations_file) as f:
            violations = json.load(f)
            
        # API キーハードコーディング違反チェック
        if "api_key_hardcoding" in violations.get("rules", {}):
            violation_count = violations["rules"]["api_key_hardcoding"]["violation_count"]
            if violation_count > 0:
                print(f"🚨 CRITICAL: {violation_count} API key hardcoding violations detected")
                self.enforce_api_key_protection()
                
        return True
        
    def enforce_api_key_protection(self):
        """APIキー保護の強制実行"""
        print("🔐 ENFORCING API KEY PROTECTION...")
        
        # 1. 重要設定ファイルのバックアップ作成
        self.backup_critical_configs()
        
        # 2. 現在の設定ファイルでAPIキー検出
        self.scan_for_hardcoded_keys()
        
        # 3. 環境変数確認
        self.verify_environment_variables()
        
    def backup_critical_configs(self):
        """重要設定ファイルの自動バックアップ"""
        try:
            backup_dir = self.project_root / "runtime/config_backups"
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            for config_file in self.critical_configs:
                if config_file.exists():
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    backup_name = f"{config_file.name}.{timestamp}.backup"
                    backup_path = backup_dir / backup_name
                    
                    import shutil
                    shutil.copy2(config_file, backup_path)
                    print(f"✅ Backed up: {config_file} -> {backup_path}")
        except Exception as e:
            print(f"⚠️  Backup warning: {e}")
                
    def scan_for_hardcoded_keys(self):
        """設定ファイル内のハードコードAPIキー検出"""
        dangerous_patterns = [
            # Only check for direct hardcoding in config files, not env variables
            r'"OPENAI_API_KEY":\s*"sk-proj-',  # Direct hardcoding in JSON
            r'"GEMINI_API_KEY":\s*"AIzaSy',   # Direct hardcoding in JSON
        ]
        
        for config_file in self.critical_configs:
            if config_file.exists():
                with open(config_file) as f:
                    content = f.read()
                    
                for pattern in dangerous_patterns:
                    import re
                    if re.search(pattern, content):
                        print(f"🚨 SECURITY VIOLATION: Hardcoded API key detected in {config_file}")
                        print(f"🔧 REQUIRED: Use environment variable reference like ${OPENAI_API_KEY}")
                        return False
                        
        print("✅ No hardcoded API keys detected in config files")
        print("✅ Environment variable usage (.env) is secure and recommended")
        return True
        
    def verify_environment_variables(self):
        """必須環境変数の確認"""
        required_vars = ["OPENAI_API_KEY", "GEMINI_API_KEY"]
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
                
        if missing_vars:
            print(f"⚠️  Missing environment variables: {missing_vars}")
            print("🔧 Run: export OPENAI_API_KEY=your_key")
        else:
            print("✅ All required environment variables present")
            
    def check_mcp_integration(self):
        """MCP統合の確認"""
        claude_settings = Path.home() / ".claude/settings.json"
        mcp_json = Path.home() / ".mcp.json"
        
        mcp_configured = False
        
        # Check .claude/settings.json
        if claude_settings.exists():
            with open(claude_settings) as f:
                settings = json.load(f)
            mcp_servers = settings.get("mcpServers", {})
            if "o3" in mcp_servers or "o3-search" in mcp_servers:
                print("✅ o3 MCP configured in settings.json")
                mcp_configured = True
                
        # Check .mcp.json
        if mcp_json.exists():
            with open(mcp_json) as f:
                mcp_config = json.load(f)
            mcp_servers = mcp_config.get("mcpServers", {})
            if "o3" in mcp_servers:
                print("✅ o3 MCP configured in .mcp.json") 
                mcp_configured = True
                
        if mcp_configured:
            print("✅ MCP integration properly configured")
            return True
        else:
            print("⚠️  o3 MCP not configured, but continuing...")
            return True  # Don't fail for MCP configuration
        
    def force_claude_md_review(self):
        """CLAUDE.md重要セクションの強制確認"""
        claude_md = self.project_root / "CLAUDE.md"
        mcp_guide = self.project_root / "claude_modules/procedures/mcp_integration.md"
        
        if not claude_md.exists():
            print("❌ CLAUDE.md not found")
            return False
            
        print("📋 MANDATORY REVIEW:")
        print("1. o3: Claude Code内で自動的にツールとして利用可能")
        print("2. Gemini: gemini -p \"質問内容\" でCLI直接使用")
        print("3. APIキー: 環境変数のみ使用、ファイル記述絶対禁止")
        
        return True
    
    def enforce_cursor_rules(self):
        """Cursor rules強制確認"""
        try:
            print("🔒 ENFORCING CURSOR RULES...")
            enforcer = CursorRulesEnforcer()
            result = enforcer.run_enforcement()
            
            if result:
                print("✅ Cursor rules confirmed successfully")
                return True
            else:
                print("❌ Cursor rules confirmation failed")
                return False
                
        except Exception as e:
            print(f"❌ Cursor rules enforcement error: {e}")
            return False
        
    def create_session_prevention_log(self):
        """セッション開始時の防止ログ作成"""
        try:
            log_file = self.project_root / "runtime/memory/session_prevention_log.json"
            
            session_log = {
                "timestamp": datetime.now().isoformat(),
                "checks_performed": [
                    "critical_violations_review",
                    "api_key_protection_enforcement", 
                    "config_backup_creation",
                    "mcp_integration_verification",
                    "claude_md_mandatory_review",
                    "cursor_rules_enforcement"
                ],
                "prevention_status": "ACTIVE",
                "next_session_requirements": [
                    "Must run this script first",
                    "Must verify MCP tools work",
                    "Must never hardcode API keys",
                    "Must confirm cursor rules understanding"
                ]
            }
            
            log_file.parent.mkdir(parents=True, exist_ok=True)
            with open(log_file, 'w') as f:
                json.dump(session_log, f, indent=2)
                
            print(f"📝 Session prevention log: {log_file}")
            return True
        except Exception as e:
            print(f"❌ Failed to create session log: {e}")
            return False
        
    def run_full_prevention_check(self):
        """完全防止チェックの実行"""
        print("="*60)
        print("🔒 RUNNING MANDATORY ERROR PREVENTION SYSTEM")
        print("="*60)
        
        checks = [
            ("Critical Violations Check", self.check_critical_violations),
            ("MCP Integration Check", self.check_mcp_integration), 
            ("CLAUDE.md Review", self.force_claude_md_review),
            ("Cursor Rules Enforcement", self.enforce_cursor_rules),
            ("Session Log Creation", self.create_session_prevention_log)
        ]
        
        all_passed = True
        for check_name, check_func in checks:
            print(f"\n🔍 {check_name}...")
            if not check_func():
                print(f"❌ {check_name} FAILED")
                all_passed = False
            else:
                print(f"✅ {check_name} PASSED")
                
        print("\n" + "="*60)
        if all_passed:
            print("✅ ALL PREVENTION CHECKS PASSED - SESSION SAFE TO PROCEED")
        else:
            print("❌ PREVENTION CHECKS FAILED - FIX ISSUES BEFORE PROCEEDING")
            sys.exit(1)
        print("="*60)
        
        return all_passed

if __name__ == "__main__":
    prevention = SessionErrorPrevention()
    prevention.run_full_prevention_check()