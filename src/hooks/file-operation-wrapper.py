#!/usr/bin/env python3
"""
File Operation Wrapper - ファイル操作の自動フック統合
既存のファイル操作を透明にフック化
"""

import shutil
from contextlib import contextmanager
from pathlib import Path
from typing import Union

# Audio Hooks System統合
try:
    from .audio_hooks_system import (
        EventType,
        emit_file_created,
        emit_file_deleted,
        emit_file_modified,
        emit_validation_result,
        get_hooks_system,
    )
except ImportError:
    # スタンドアロン実行時のフォールバック
    def emit_file_created(path: str, details: dict = None):
        pass

    def emit_file_modified(path: str, details: dict = None):
        pass

    def emit_file_deleted(path: str, details: dict = None):
        pass

    def emit_validation_result(path: str, passed: bool, details: dict = None):
        pass


class HookedFileOperations:
    """フック統合ファイル操作クラス"""

    def __init__(self, enable_hooks: bool = True):
        self.enable_hooks = enable_hooks

    def create_file(
        self, path: Union[str, Path], content: str = "", encoding: str = "utf-8"
    ) -> bool:
        """ファイル作成（フック付き）"""
        path = Path(path)

        try:
            # ディレクトリ作成
            path.parent.mkdir(parents=True, exist_ok=True)

            # ファイル作成
            with open(path, "w", encoding=encoding) as f:
                f.write(content)

            # フック発行
            if self.enable_hooks:
                details = {
                    "size": len(content.encode(encoding)),
                    "encoding": encoding,
                    "created_dirs": not path.parent.exists(),
                }
                emit_file_created(str(path), details)

            return True

        except Exception as e:
            if self.enable_hooks:
                emit_validation_result(str(path), False, {"error": str(e)})
            raise

    def modify_file(
        self,
        path: Union[str, Path],
        content: str,
        mode: str = "w",
        encoding: str = "utf-8",
    ) -> bool:
        """ファイル変更（フック付き）"""
        path = Path(path)

        try:
            # 既存サイズ取得
            old_size = path.stat().st_size if path.exists() else 0

            # ファイル変更
            with open(path, mode, encoding=encoding) as f:
                f.write(content)

            # 新サイズ取得
            new_size = path.stat().st_size

            # フック発行
            if self.enable_hooks:
                details = {
                    "old_size": old_size,
                    "new_size": new_size,
                    "size_change": new_size - old_size,
                    "mode": mode,
                    "encoding": encoding,
                }
                emit_file_modified(str(path), details)

            return True

        except Exception as e:
            if self.enable_hooks:
                emit_validation_result(str(path), False, {"error": str(e)})
            raise

    def delete_file(self, path: Union[str, Path], missing_ok: bool = True) -> bool:
        """ファイル削除（フック付き）"""
        path = Path(path)

        try:
            # 削除前情報取得
            file_info = {}
            if path.exists():
                stat = path.stat()
                file_info = {
                    "size": stat.st_size,
                    "modified_time": stat.st_mtime,
                    "is_directory": path.is_dir(),
                }

            # ファイル削除
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink(missing_ok=missing_ok)

            # フック発行
            if self.enable_hooks:
                emit_file_deleted(str(path), file_info)

            return True

        except Exception as e:
            if self.enable_hooks:
                emit_validation_result(str(path), False, {"error": str(e)})
            if not missing_ok:
                raise
            return False

    def copy_file(
        self, src: Union[str, Path], dst: Union[str, Path], follow_symlinks: bool = True
    ) -> bool:
        """ファイルコピー（フック付き）"""
        src, dst = Path(src), Path(dst)

        try:
            # コピー実行
            if src.is_dir():
                shutil.copytree(src, dst, symlinks=not follow_symlinks)
            else:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)

            # フック発行
            if self.enable_hooks:
                details = {
                    "source": str(src),
                    "destination": str(dst),
                    "size": dst.stat().st_size if dst.exists() else 0,
                    "operation": "copy",
                }
                emit_file_created(str(dst), details)

            return True

        except Exception as e:
            if self.enable_hooks:
                emit_validation_result(
                    str(dst), False, {"error": str(e), "operation": "copy"}
                )
            raise

    def move_file(self, src: Union[str, Path], dst: Union[str, Path]) -> bool:
        """ファイル移動（フック付き）"""
        src, dst = Path(src), Path(dst)

        try:
            # 移動前情報取得
            src_info = {}
            if src.exists():
                stat = src.stat()
                src_info = {"size": stat.st_size, "source": str(src)}

            # 移動実行
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))

            # フック発行（削除 + 作成）
            if self.enable_hooks:
                emit_file_deleted(str(src), src_info)
                emit_file_created(str(dst), {**src_info, "operation": "move"})

            return True

        except Exception as e:
            if self.enable_hooks:
                emit_validation_result(
                    str(dst), False, {"error": str(e), "operation": "move"}
                )
            raise


# グローバルインスタンス
file_ops = HookedFileOperations()


# 便利関数
def create_file(
    path: Union[str, Path], content: str = "", encoding: str = "utf-8"
) -> bool:
    """フック付きファイル作成"""
    return file_ops.create_file(path, content, encoding)


def modify_file(
    path: Union[str, Path], content: str, mode: str = "w", encoding: str = "utf-8"
) -> bool:
    """フック付きファイル変更"""
    return file_ops.modify_file(path, content, mode, encoding)


def delete_file(path: Union[str, Path], missing_ok: bool = True) -> bool:
    """フック付きファイル削除"""
    return file_ops.delete_file(path, missing_ok)


def copy_file(src: Union[str, Path], dst: Union[str, Path]) -> bool:
    """フック付きファイルコピー"""
    return file_ops.copy_file(src, dst)


def move_file(src: Union[str, Path], dst: Union[str, Path]) -> bool:
    """フック付きファイル移動"""
    return file_ops.move_file(src, dst)


@contextmanager
def file_operation_context(operation_name: str, target_path: str):
    """ファイル操作コンテキストマネージャー"""
    start_time = time.time()

    try:
        if file_ops.enable_hooks:
            get_hooks_system().emit_event(
                EventType.SYSTEM_ACTION,
                target_path,
                {"operation": operation_name, "status": "started"},
                f"🔧 {operation_name} 開始: {Path(target_path).name}",
            )

        yield

        if file_ops.enable_hooks:
            duration = time.time() - start_time
            get_hooks_system().emit_event(
                EventType.SYSTEM_ACTION,
                target_path,
                {
                    "operation": operation_name,
                    "status": "completed",
                    "duration": f"{duration:.2f}s",
                },
                f"✅ {operation_name} 完了: {Path(target_path).name}",
            )

    except Exception as e:
        if file_ops.enable_hooks:
            duration = time.time() - start_time
            get_hooks_system().emit_event(
                EventType.SYSTEM_ACTION,
                target_path,
                {
                    "operation": operation_name,
                    "status": "failed",
                    "error": str(e),
                    "duration": f"{duration:.2f}s",
                },
                f"❌ {operation_name} 失敗: {Path(target_path).name}",
            )
        raise


def main():
    """テスト実行"""
    import time

    print("🧪 File Operation Wrapper テスト開始")

    import tempfile

    with tempfile.NamedTemporaryFile(suffix="_test_hooks.txt", delete=False) as tmp:
        test_file = tmp.name

    # ファイル作成テスト
    print("1. ファイル作成テスト")
    create_file(test_file, "Hello, Hooks World!")
    time.sleep(1)

    # ファイル変更テスト
    print("2. ファイル変更テスト")
    modify_file(test_file, "\nHooks system is working!", mode="a")
    time.sleep(1)

    # ファイル削除テスト
    print("3. ファイル削除テスト")
    delete_file(test_file)

    print("✅ テスト完了")


if __name__ == "__main__":
    import time

    main()
