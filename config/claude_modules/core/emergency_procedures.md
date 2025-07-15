# Emergency & Crisis Response Procedures

## 🚨 緊急時対応プロトコル

### 緊急時対応
1. **フックブロック** → PRESIDENT宣言確認 (`make declare-president`)
2. **ミス検出** → Constitutional AI自動修正稼働
3. **システム異常** → 多層監視アラート・自動回復
4. **Gemini CLI** → 自動構文修正 (`gemini -p "message"`)
5. **統合テスト** → `python3 tests/integration_test.py`

### フックブロック対応
```bash
# PRESIDENT宣言確認
make declare-president

# システム状態確認
python3 src/memory/breakthrough_memory_system.py

# 違反履歴確認
if [ -f "runtime/memory/violations.json" ]; then
  cat runtime/memory/violations.json
fi
```

### システム復旧手順
```bash
# 1. 緊急診断
python3 tests/integration_test.py

# 2. Constitutional AI再起動
python3 src/ai/constitutional_ai.py

# 3. 指揮者システム再起動
python3 src/conductor/core.py

# 4. 記憶継承確認
python3 src/memory/unified_memory_manager.py
```

### Critical Task Failure Recovery
**ULTRATHINK Mode Protocol Violation Recovery**:
1. Stop current execution immediately
2. Acknowledge protocol violation
3. Re-analyze task classification
4. Execute proper CRITICAL task protocol
5. Resume with corrective measures

### Hook System Malfunction Response
1. **Manual Intervention**: User override required
2. **System Diagnosis**: Check hook configuration
3. **Fallback Protocol**: Manual validation procedures
4. **Recovery**: Re-initialize hook system