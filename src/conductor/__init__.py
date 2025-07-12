"""
🎼 Conductor System - 指揮者システム
===================================
自動軌道修正機能を持つ多AI統合指揮システム

主要コンポーネント:
- ConductorCore: メイン指揮者システム
- CorrectionHandler: 自動エラー修正システム
- Task/TaskResult: タスク定義・結果管理
"""

from .core import ConductorCore, Task, TaskResult
from .corrector import CorrectionHandler

__version__ = "1.0.0"
__all__ = ["ConductorCore", "Task", "TaskResult", "CorrectionHandler"]
