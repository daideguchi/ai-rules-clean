#!/usr/bin/env python3
"""
設定ファイル統合システム
======================

分散している設定ファイルを統合し、一元管理する
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class ConfigIntegration:
    """設定ファイル統合システム"""
    
    def __init__(self):
        self.project_root = project_root
        self.config_dir = self.project_root / "config"
        self.unified_config_file = self.config_dir / "unified_config.json"
        self.backup_dir = self.project_root / "runtime" / "config_backups"
        
        # 統合対象ファイル
        self.config_files = {
            'mcp': self.config_dir / ".mcp.json",
            'api_keys': self.config_dir / "security" / "api_keys.json",
            'rbac': self.config_dir / "security" / "rbac_config.json",
            'integration': self.config_dir / "integrations" / "integration_config.json",
            'claude_settings': self.config_dir / "claude-settings-envvar.json",
            'log_management': self.project_root / "runtime" / "log_management_config.json",
            'mistake_config': self.project_root / "runtime" / "mistakes" / "mistake_config.json",
            'interceptor': self.project_root / "runtime" / "unified_interceptor_config.json"
        }
        
        # 統合設定の構造
        self.unified_structure = {
            'metadata': {
                'version': '1.0',
                'created_at': datetime.now().isoformat(),
                'description': 'Unified configuration for coding-rule2 project'
            },
            'system': {
                'name': 'coding-rule2',
                'environment': 'development',
                'debug': False
            },
            'database': {
                'postgresql': {
                    'host': 'localhost',
                    'port': 5432,
                    'database': 'coding_rule2_ai',
                    'user': 'dd',
                    'password': ''
                },
                'supabase': {
                    'url': 'http://127.0.0.1:54321',
                    'anon_key': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0'
                }
            },
            'api_keys': {},
            'mcp': {},
            'logging': {
                'level': 'INFO',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'handlers': ['console', 'database'],
                'database_logging': True
            },
            'security': {
                'rbac': {},
                'encryption_key_path': 'config/security/.encryption_key'
            },
            'integrations': {},
            'claude': {
                'memory_code': '7749',
                'enforcement_level': 'strict',
                'thinking_required': True,
                'template_required': True
            },
            'file_management': {
                'max_python_files': 500,
                'max_markdown_files': 350,
                'max_total_files': 1000,
                'auto_cleanup': True
            },
            'monitoring': {
                'enabled': True,
                'metrics_collection': True,
                'performance_tracking': True
            }
        }
        
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def backup_existing_configs(self) -> Dict[str, bool]:
        """既存設定ファイルのバックアップ"""
        backup_results = {}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for name, file_path in self.config_files.items():
            if file_path.exists():
                backup_path = self.backup_dir / f"{name}_{timestamp}.json"
                try:
                    with open(file_path, 'r') as src, open(backup_path, 'w') as dst:
                        dst.write(src.read())
                    backup_results[name] = True
                    print(f"✅ バックアップ完了: {name} -> {backup_path}")
                except Exception as e:
                    backup_results[name] = False
                    print(f"❌ バックアップ失敗: {name} - {e}")
            else:
                backup_results[name] = False
                print(f"⚠️ ファイルなし: {name}")
        
        return backup_results
    
    def load_existing_configs(self) -> Dict[str, Any]:
        """既存設定ファイルの読み込み"""
        configs = {}
        
        for name, file_path in self.config_files.items():
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        configs[name] = json.load(f)
                    print(f"✅ 設定読み込み: {name}")
                except Exception as e:
                    configs[name] = {}
                    print(f"❌ 設定読み込み失敗: {name} - {e}")
            else:
                configs[name] = {}
                print(f"⚠️ 設定ファイルなし: {name}")
        
        return configs
    
    def merge_configs(self, existing_configs: Dict[str, Any]) -> Dict[str, Any]:
        """設定をマージ"""
        unified_config = self.unified_structure.copy()
        
        # MCP設定のマージ
        if 'mcp' in existing_configs and existing_configs['mcp']:
            unified_config['mcp'] = existing_configs['mcp']
        
        # API Keys設定のマージ
        if 'api_keys' in existing_configs and existing_configs['api_keys']:
            unified_config['api_keys'] = existing_configs['api_keys']
        
        # RBAC設定のマージ
        if 'rbac' in existing_configs and existing_configs['rbac']:
            unified_config['security']['rbac'] = existing_configs['rbac']
        
        # Integration設定のマージ
        if 'integration' in existing_configs and existing_configs['integration']:
            unified_config['integrations'] = existing_configs['integration']
        
        # Claude設定のマージ
        if 'claude_settings' in existing_configs and existing_configs['claude_settings']:
            claude_settings = existing_configs['claude_settings']
            if 'enforcement_level' in claude_settings:
                unified_config['claude']['enforcement_level'] = claude_settings['enforcement_level']
            if 'thinking_required' in claude_settings:
                unified_config['claude']['thinking_required'] = claude_settings['thinking_required']
        
        # ログ管理設定のマージ
        if 'log_management' in existing_configs and existing_configs['log_management']:
            log_config = existing_configs['log_management']
            if 'level' in log_config:
                unified_config['logging']['level'] = log_config['level']
            if 'database_logging' in log_config:
                unified_config['logging']['database_logging'] = log_config['database_logging']
        
        # ミス設定のマージ
        if 'mistake_config' in existing_configs and existing_configs['mistake_config']:
            mistake_config = existing_configs['mistake_config']
            if 'prevention_enabled' in mistake_config:
                unified_config['monitoring']['mistake_prevention'] = mistake_config['prevention_enabled']
        
        # インターセプター設定のマージ
        if 'interceptor' in existing_configs and existing_configs['interceptor']:
            interceptor_config = existing_configs['interceptor']
            if 'enabled' in interceptor_config:
                unified_config['monitoring']['interceptor_enabled'] = interceptor_config['enabled']
        
        return unified_config
    
    def save_unified_config(self, unified_config: Dict[str, Any]) -> bool:
        """統合設定ファイルの保存"""
        try:
            with open(self.unified_config_file, 'w', encoding='utf-8') as f:
                json.dump(unified_config, f, indent=2, ensure_ascii=False)
            print(f"✅ 統合設定保存完了: {self.unified_config_file}")
            return True
        except Exception as e:
            print(f"❌ 統合設定保存失敗: {e}")
            return False
    
    def create_config_loader(self) -> bool:
        """設定読み込みユーティリティ作成"""
        loader_code = '''#!/usr/bin/env python3
"""
統合設定読み込みユーティリティ
============================

統合設定ファイルを読み込むためのユーティリティ
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigLoader:
    """統合設定読み込みクラス"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.project_root = Path(__file__).parent.parent.parent
        self.config_file = config_file or self.project_root / "config" / "unified_config.json"
        self._config = None
    
    def load_config(self) -> Dict[str, Any]:
        """設定ファイル読み込み"""
        if self._config is None:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
        return self._config
    
    def get_database_config(self) -> Dict[str, Any]:
        """データベース設定取得"""
        config = self.load_config()
        return config.get('database', {})
    
    def get_api_keys(self) -> Dict[str, Any]:
        """API Key設定取得"""
        config = self.load_config()
        return config.get('api_keys', {})
    
    def get_mcp_config(self) -> Dict[str, Any]:
        """MCP設定取得"""
        config = self.load_config()
        return config.get('mcp', {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """ログ設定取得"""
        config = self.load_config()
        return config.get('logging', {})
    
    def get_security_config(self) -> Dict[str, Any]:
        """セキュリティ設定取得"""
        config = self.load_config()
        return config.get('security', {})
    
    def get_claude_config(self) -> Dict[str, Any]:
        """Claude設定取得"""
        config = self.load_config()
        return config.get('claude', {})
    
    def get_file_management_config(self) -> Dict[str, Any]:
        """ファイル管理設定取得"""
        config = self.load_config()
        return config.get('file_management', {})
    
    def get_monitoring_config(self) -> Dict[str, Any]:
        """監視設定取得"""
        config = self.load_config()
        return config.get('monitoring', {})
    
    def get_value(self, key_path: str, default: Any = None) -> Any:
        """ドット記法でのキー取得"""
        config = self.load_config()
        keys = key_path.split('.')
        value = config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value


# グローバルインスタンス
_config_loader = ConfigLoader()

# 便利関数
def get_config() -> Dict[str, Any]:
    """設定全体取得"""
    return _config_loader.load_config()

def get_database_config() -> Dict[str, Any]:
    """データベース設定取得"""
    return _config_loader.get_database_config()

def get_api_keys() -> Dict[str, Any]:
    """API Key設定取得"""
    return _config_loader.get_api_keys()

def get_mcp_config() -> Dict[str, Any]:
    """MCP設定取得"""
    return _config_loader.get_mcp_config()

def get_logging_config() -> Dict[str, Any]:
    """ログ設定取得"""
    return _config_loader.get_logging_config()

def get_security_config() -> Dict[str, Any]:
    """セキュリティ設定取得"""
    return _config_loader.get_security_config()

def get_claude_config() -> Dict[str, Any]:
    """Claude設定取得"""
    return _config_loader.get_claude_config()

def get_file_management_config() -> Dict[str, Any]:
    """ファイル管理設定取得"""
    return _config_loader.get_file_management_config()

def get_monitoring_config() -> Dict[str, Any]:
    """監視設定取得"""
    return _config_loader.get_monitoring_config()

def get_value(key_path: str, default: Any = None) -> Any:
    """ドット記法でのキー取得"""
    return _config_loader.get_value(key_path, default)
'''
        
        try:
            loader_file = self.project_root / "src" / "config" / "config_loader.py"
            loader_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(loader_file, 'w', encoding='utf-8') as f:
                f.write(loader_code)
            
            print(f"✅ 設定読み込みユーティリティ作成完了: {loader_file}")
            return True
        except Exception as e:
            print(f"❌ 設定読み込みユーティリティ作成失敗: {e}")
            return False
    
    def clean_old_configs(self) -> Dict[str, bool]:
        """古い設定ファイルのクリーンアップ"""
        cleanup_results = {}
        
        for name, file_path in self.config_files.items():
            if file_path.exists():
                try:
                    file_path.unlink()
                    cleanup_results[name] = True
                    print(f"🗑️ 削除完了: {name}")
                except Exception as e:
                    cleanup_results[name] = False
                    print(f"❌ 削除失敗: {name} - {e}")
            else:
                cleanup_results[name] = False
        
        return cleanup_results
    
    def integrate_configs(self) -> Dict[str, Any]:
        """設定ファイル統合メイン処理"""
        print("🔧 設定ファイル統合開始")
        print("=" * 50)
        
        # 1. 既存設定ファイルのバックアップ
        print("\n1. 既存設定ファイルのバックアップ")
        backup_results = self.backup_existing_configs()
        
        # 2. 既存設定ファイルの読み込み
        print("\n2. 既存設定ファイルの読み込み")
        existing_configs = self.load_existing_configs()
        
        # 3. 設定のマージ
        print("\n3. 設定のマージ")
        unified_config = self.merge_configs(existing_configs)
        
        # 4. 統合設定ファイルの保存
        print("\n4. 統合設定ファイルの保存")
        save_success = self.save_unified_config(unified_config)
        
        # 5. 設定読み込みユーティリティの作成
        print("\n5. 設定読み込みユーティリティの作成")
        loader_success = self.create_config_loader()
        
        # 6. 古い設定ファイルのクリーンアップ
        print("\n6. 古い設定ファイルのクリーンアップ")
        cleanup_results = self.clean_old_configs()
        
        # 結果レポート
        result = {
            'integration_completed': save_success and loader_success,
            'backup_results': backup_results,
            'cleanup_results': cleanup_results,
            'unified_config_file': str(self.unified_config_file),
            'config_loader_file': str(self.project_root / "src" / "config" / "config_loader.py"),
            'backup_count': sum(backup_results.values()),
            'cleanup_count': sum(cleanup_results.values())
        }
        
        print("\n" + "=" * 50)
        print("📊 設定統合結果:")
        print(f"✅ バックアップ完了: {result['backup_count']}件")
        print(f"🗑️ 削除完了: {result['cleanup_count']}件")
        print(f"📝 統合設定ファイル: {result['unified_config_file']}")
        print(f"🔧 設定読み込みユーティリティ: {result['config_loader_file']}")
        
        return result


def main():
    """メイン実行"""
    integrator = ConfigIntegration()
    
    try:
        result = integrator.integrate_configs()
        
        if result['integration_completed']:
            print("\n✅ 設定ファイル統合完了！")
            print("💡 今後は統合設定ファイルを使用してください")
        else:
            print("\n❌ 設定ファイル統合失敗")
            return 1
            
    except Exception as e:
        print(f"\n❌ 統合中にエラーが発生: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())