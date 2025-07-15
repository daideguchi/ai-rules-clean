#!/usr/bin/env python3
"""
動的ミス数取得スクリプト
CLAUDE.mdテンプレート用
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from ai.mistake_counter_system import MistakeCounterSystem

def get_current_mistake_count():
    """現在のミス数を取得"""
    counter = MistakeCounterSystem()
    return counter.get_mistake_count()

def get_mistake_display():
    """表示用ミス数文字列を取得"""
    counter = MistakeCounterSystem()
    return counter.get_mistake_count_display()

if __name__ == "__main__":
    print(get_current_mistake_count())