#!/usr/bin/env python3
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
