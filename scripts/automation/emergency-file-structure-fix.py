#!/usr/bin/env python3
"""
緊急ファイル構造修正システム
全ての命名規則違反・配置違反を一括修正
"""

import os
import re
import shutil
from pathlib import Path
from datetime import datetime

def fix_filename(name: str) -> str:
    """ファイル名を正しい命名規則に修正"""
    # 大文字を小文字に
    name = name.lower()
    # アンダースコアをハイフンに
    name = name.replace('_', '-')
    # 連続ハイフンを単一に
    name = re.sub(r'-+', '-', name)
    # 先頭末尾のハイフンを削除
    name = name.strip('-')
    return name

def determine_target_directory(filename: str) -> str:
    """ファイルの適切な配置先を決定"""
    rules = {
        'test': 'scripts/testing/',
        'setup': 'scripts/setup/',
        'integration': 'scripts/integration/',
        'marketing': 'scripts/marketing/',
        'maintenance': 'scripts/maintenance/',
        'automation': 'scripts/automation/',
        'final': 'scripts/setup/',
        'verify': 'scripts/integration/',
        'check': 'scripts/testing/',
        'debug': 'scripts/testing/',
        'fix': 'scripts/maintenance/'
    }
    
    filename_lower = filename.lower()
    for keyword, target_dir in rules.items():
        if keyword in filename_lower:
            return target_dir
    
    # ファイル拡張子による判定
    if filename.endswith('.sh'):
        return 'scripts/misc/'
    elif filename.endswith('.py'):
        return 'scripts/misc/'
    
    return 'scripts/misc/'

def emergency_fix():
    """緊急修正実行"""
    print("🚨 緊急ファイル構造修正開始")
    print("=" * 50)
    
    project_root = Path.cwd()
    fixed_files = []
    created_dirs = set()
    
    # 1. ルートディレクトリの違反ファイル検出
    root_violations = []
    for item in project_root.iterdir():
        if item.is_file() and item.suffix in ['.sh', '.py']:
            # 除外ファイル
            if item.name in ['setup.py', 'manage.py']:
                continue
            root_violations.append(item)
    
    print(f"📋 ルート違反ファイル検出: {len(root_violations)}個")
    
    # 2. scripts/n8n_marketing/ ディレクトリの修正
    old_marketing_dir = project_root / "scripts" / "n8n_marketing"
    new_marketing_dir = project_root / "scripts" / "marketing"
    
    if old_marketing_dir.exists():
        print(f"📁 ディレクトリ名修正: {old_marketing_dir} → {new_marketing_dir}")
        
        # 新ディレクトリ作成
        new_marketing_dir.mkdir(exist_ok=True)
        created_dirs.add(str(new_marketing_dir))
        
        # ファイル移動・名前修正
        for file in old_marketing_dir.iterdir():
            if file.is_file():
                old_name = file.name
                new_name = fix_filename(old_name)
                new_path = new_marketing_dir / new_name
                
                shutil.move(str(file), str(new_path))
                fixed_files.append(f"{old_name} → {new_name}")
                print(f"   ✅ {old_name} → {new_name}")
        
        # 古いディレクトリ削除
        old_marketing_dir.rmdir()
        print(f"   🗑️ 古いディレクトリ削除: {old_marketing_dir}")
    
    # 3. ルート違反ファイルの移動・修正
    for violation_file in root_violations:
        old_name = violation_file.name
        new_name = fix_filename(old_name)
        target_dir = determine_target_directory(old_name)
        
        # ターゲットディレクトリ作成
        target_path = project_root / target_dir
        target_path.mkdir(parents=True, exist_ok=True)
        created_dirs.add(str(target_path))
        
        # ファイル移動
        new_file_path = target_path / new_name
        shutil.move(str(violation_file), str(new_file_path))
        
        # 実行権限復元（シェルスクリプトの場合）
        if new_name.endswith('.sh'):
            new_file_path.chmod(0o755)
        
        fixed_files.append(f"{old_name} → {target_dir}{new_name}")
        print(f"   ✅ {old_name} → {target_dir}{new_name}")
    
    # 4. 結果報告
    print(f"\n📊 修正完了サマリー")
    print(f"   作成ディレクトリ: {len(created_dirs)}個")
    print(f"   修正ファイル: {len(fixed_files)}個")
    
    print(f"\n📁 作成されたディレクトリ:")
    for dir_path in sorted(created_dirs):
        print(f"   ✅ {dir_path}")
    
    print(f"\n📝 修正されたファイル:")
    for file_fix in fixed_files:
        print(f"   ✅ {file_fix}")
    
    # 5. 修正レポート生成
    generate_fix_report(fixed_files, created_dirs)
    
    print(f"\n🎊 緊急修正完了!")
    print(f"📄 詳細レポート: docs/analysis/emergency-fix-report.md")

def generate_fix_report(fixed_files, created_dirs):
    """修正レポート生成"""
    report_content = f"""# 緊急ファイル構造修正レポート

**実行日時**: {datetime.now().isoformat()}  
**修正ファイル数**: {len(fixed_files)}個  
**作成ディレクトリ数**: {len(created_dirs)}個

## 修正内容

### 作成されたディレクトリ
```bash
{chr(10).join(f"mkdir -p {d}" for d in sorted(created_dirs))}
```

### 修正されたファイル
```bash
{chr(10).join(f"# {f}" for f in fixed_files)}
```

## 修正理由
- ルートディレクトリ汚染防止
- 命名規則統一（ハイフン使用）
- Function-Based Grouping準拠

## 次のステップ
1. Pre-commitフック有効化
2. 自動監視システム稼働
3. IDE統合設定
4. チーム周知・教育

---
**修正システム**: scripts/automation/emergency-file-structure-fix.py
"""
    
    report_path = Path("docs/analysis/emergency-fix-report.md")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report_content, encoding='utf-8')

if __name__ == "__main__":
    emergency_fix()