#!/usr/bin/env python3
"""
Thinking Enforcer Hook - 自動実行フック
"""

import sys

sys.path.append("src")
from memory.thinking_enforcer import ThinkingEnforcer

enforcer = ThinkingEnforcer()
print(enforcer.get_session_reminder())
