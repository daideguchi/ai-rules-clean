#!/usr/bin/env python3
"""
ファイル構造違反防止システム自動セットアップ
"""

import os
import stat
from pathlib import Path

def setup_pre_commit_hook():
    """Pre-commitフック設置"""
    print("🔧 Pre-commitフック設置中...")
    
    hook_content = '''#!/bin/bash
# ファイル構造・命名規則チェック

echo "🔍 ファイル構造チェック実行中..."

# 1. ルートディレクトリ汚染チェック
if ls *.sh *.py 2>/dev/null | grep -E "^(test|setup|fix|verify|check|debug)" >/dev/null; then
    echo "❌ ルートディレクトリにスクリプトファイルが検出されました"
    echo "   以下のファイルを適切なディレクトリに移動してください:"
    ls *.sh *.py 2>/dev/null | grep -E "^(test|setup|fix|verify|check|debug)" | sed 's/^/   - /'
    echo ""
    echo "   自動修正: python3 scripts/automation/emergency-file-structure-fix.py"
    exit 1
fi

# 2. 命名規則チェック
for file in $(git diff --cached --name-only); do
    basename_file=$(basename "$file")
    
    # アンダースコア使用チェック
    if [[ "$basename_file" =~ _ && "$file" != *requirements.txt && "$file" != *__* ]]; then
        echo "❌ 命名規則違反 (アンダースコア): $file"
        echo "   正しい形式: $(echo $basename_file | tr '_' '-')"
        echo "   自動修正: python3 scripts/automation/emergency-file-structure-fix.py"
        exit 1
    fi
    
    # 大文字使用チェック  
    if [[ "$basename_file" =~ [A-Z] && "$file" != *README* && "$file" != *LICENSE* && "$file" != *CHANGELOG* ]]; then
        echo "❌ 命名規則違反 (大文字): $file"
        echo "   正しい形式: $(echo $basename_file | tr 'A-Z' 'a-z')"
        exit 1
    fi
done

# 3. 配置ルールチェック
for file in $(git diff --cached --name-only); do
    if [[ "$file" =~ \\.sh$ || "$file" =~ \\.py$ ]]; then
        # ルートディレクトリの実行ファイルチェック
        if [[ "$file" != */* ]] && [[ "$file" != "setup.py" ]] && [[ "$file" != "manage.py" ]]; then
            echo "❌ 配置ルール違反: $file"
            echo "   スクリプトファイルはscripts/ディレクトリに配置してください"
            exit 1
        fi
    fi
done

echo "✅ ファイル構造チェック完了"
'''
    
    hook_path = Path(".git/hooks/pre-commit")
    hook_path.write_text(hook_content)
    hook_path.chmod(stat.S_IRWXU | stat.S_IRGRP | stat.S_IROTH)
    print("   ✅ Pre-commitフック設置完了")

def setup_file_watcher():
    """ファイル監視システム設置"""
    print("🔍 ファイル監視システム設置中...")
    
    watcher_content = '''#!/usr/bin/env python3
"""
リアルタイムファイル構造監視システム
"""

import time
import os
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class FileStructureWatcher(FileSystemEventHandler):
    def __init__(self):
        self.violations = []
    
    def on_created(self, event):
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        
        # ルートディレクトリチェック
        if file_path.parent.name == file_path.parent.parent.name:  # ルートディレクトリ
            if file_path.suffix in ['.sh', '.py']:
                if file_path.name not in ['setup.py', 'manage.py']:
                    print(f"⚠️  ルート違反検出: {file_path.name}")
                    print(f"   推奨配置: scripts/{self.suggest_directory(file_path.name)}")
        
        # 命名規則チェック
        if '_' in file_path.name and '__' not in file_path.name:
            print(f"⚠️  命名違反検出: {file_path.name}")
            print(f"   推奨名前: {file_path.name.replace('_', '-')}")
    
    def suggest_directory(self, filename):
        """適切なディレクトリ提案"""
        if 'test' in filename.lower():
            return 'testing/'
        elif 'setup' in filename.lower():
            return 'setup/'
        elif 'fix' in filename.lower():
            return 'maintenance/'
        else:
            return 'misc/'

def main():
    print("🔍 ファイル構造リアルタイム監視開始")
    print("   Ctrl+C で停止")
    
    event_handler = FileStructureWatcher()
    observer = Observer()
    observer.schedule(event_handler, '.', recursive=True)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()
'''
    
    watcher_path = Path("scripts/automation/file-structure-watcher.py")
    watcher_path.parent.mkdir(parents=True, exist_ok=True)
    watcher_path.write_text(watcher_content)
    print("   ✅ ファイル監視システム設置完了")

def setup_auto_placement():
    """自動配置システム設置"""
    print("🤖 自動配置システム設置中...")
    
    placement_content = '''#!/usr/bin/env python3
"""
スマートファイル自動配置システム
"""

import shutil
from pathlib import Path

class SmartFilePlacer:
    def __init__(self):
        self.rules = {
            'test': 'scripts/testing/',
            'setup': 'scripts/setup/',
            'fix': 'scripts/maintenance/',
            'debug': 'scripts/testing/',
            'verify': 'scripts/integration/',
            'check': 'scripts/testing/',
            'integration': 'scripts/integration/',
            'automation': 'scripts/automation/',
            'marketing': 'scripts/marketing/',
            'monitor': 'scripts/monitoring/'
        }
    
    def suggest_placement(self, filename: str) -> str:
        """最適な配置先提案"""
        filename_lower = filename.lower()
        
        for keyword, directory in self.rules.items():
            if keyword in filename_lower:
                return directory
        
        # ファイル種別による判定
        if filename.endswith('.sh'):
            return 'scripts/misc/'
        elif filename.endswith('.py'):
            if 'src/' in str(Path.cwd()):
                return 'src/'
            else:
                return 'scripts/misc/'
        
        return 'misc/'
    
    def auto_place_file(self, source_path: str, target_dir: str = None):
        """ファイル自動配置実行"""
        source = Path(source_path)
        if not source.exists():
            print(f"❌ ファイルが存在しません: {source}")
            return False
        
        if target_dir is None:
            target_dir = self.suggest_placement(source.name)
        
        target_path = Path(target_dir)
        target_path.mkdir(parents=True, exist_ok=True)
        
        destination = target_path / source.name
        shutil.move(str(source), str(destination))
        
        # 実行権限復元
        if source.suffix == '.sh':
            destination.chmod(0o755)
        
        print(f"✅ 自動配置完了: {source.name} → {target_dir}")
        return True

def main():
    import sys
    if len(sys.argv) < 2:
        print("使用法: python3 auto-file-placement.py <ファイルパス>")
        sys.exit(1)
    
    placer = SmartFilePlacer()
    placer.auto_place_file(sys.argv[1])

if __name__ == "__main__":
    main()
'''
    
    placement_path = Path("scripts/automation/auto-file-placement.py")
    placement_path.write_text(placement_content)
    print("   ✅ 自動配置システム設置完了")

def setup_ide_integration():
    """IDE統合設定"""
    print("💻 IDE統合設定中...")
    
    # VSCode設定
    vscode_settings = '''{
  "files.autoSave": "onFocusChange",
  "editor.formatOnSave": true,
  "python.defaultInterpreterPath": "./venv/bin/python",
  
  "files.associations": {
    "*.mdc": "markdown"
  },
  
  "emmet.includeLanguages": {
    "markdown": "html"
  },
  
  "files.watcherExclude": {
    "**/venv/**": true,
    "**/__pycache__/**": true,
    "**/node_modules/**": true
  },
  
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  
  "git.hooks.pre-commit": "scripts/automation/pre-commit-check.sh"
}'''
    
    vscode_path = Path(".vscode")
    vscode_path.mkdir(exist_ok=True)
    (vscode_path / "settings.json").write_text(vscode_settings)
    
    print("   ✅ VSCode統合設定完了")

def main():
    """防止システム全体セットアップ"""
    print("🛡️ ファイル構造違反防止システムセットアップ")
    print("=" * 60)
    
    try:
        setup_pre_commit_hook()
        setup_file_watcher()
        setup_auto_placement()
        setup_ide_integration()
        
        print(f"\n🎊 防止システムセットアップ完了!")
        print(f"\n📋 次のステップ:")
        print(f"   1. 緊急修正実行: python3 scripts/automation/emergency-file-structure-fix.py")
        print(f"   2. 監視開始: python3 scripts/automation/file-structure-watcher.py")
        print(f"   3. Git設定確認: git config core.hooksPath .git/hooks")
        
    except Exception as e:
        print(f"❌ セットアップエラー: {e}")

if __name__ == "__main__":
    main()