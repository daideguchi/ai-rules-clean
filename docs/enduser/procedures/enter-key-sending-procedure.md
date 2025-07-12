# 🔥 Enterキー送信確実実行手順書

**作成日**: 2025-07-04  
**目的**: tmuxペインへのメッセージ送信時のEnterキー送信漏れ根絶  
**適用範囲**: 全4ワーカーシステム・Claude Code操作  

---

## 🚨 **問題の背景**
- メッセージ送信後のEnterキー（C-m）送信漏れが頻発
- 1回のEnterキーでは不十分なケースが存在
- Claude Code処理時間を考慮しない確認タイミング不備

---

## ✅ **確実実行手順**

### **Step 1: メッセージ送信**
```bash
tmux send-keys -t [session]:[pane] "[メッセージ内容]"
```

### **Step 2: 確実Enterキー送信（必須）**
```bash
# 1回目のEnterキー送信
tmux send-keys -t [session]:[pane] C-m

# 0.5秒待機
sleep 0.5

# 2回目のEnterキー送信（確実性向上）
tmux send-keys -t [session]:[pane] C-m
```

### **Step 3: 送信確認待機**
```bash
# Claude Code処理時間考慮（最低10秒）
sleep 10
```

### **Step 4: 応答確認**
```bash
# 最新状況確認
tmux capture-pane -t [session]:[pane] -p | tail -5

# 応答キーワード検索
tmux capture-pane -t [session]:[pane] -p | grep -E "(承知|了解|ありがとう|です)"
```

---

## 🔄 **標準化コマンド例**

### **単一ペインへの確実送信**
```bash
send_message_with_double_enter() {
    local session_pane=$1
    local message=$2
    
    echo "⚡ ${session_pane}にメッセージ送信中..."
    tmux send-keys -t "$session_pane" "$message"
    
    echo "⚡ 確実Enterキー送信（2回）..."
    tmux send-keys -t "$session_pane" C-m
    sleep 0.5
    tmux send-keys -t "$session_pane" C-m
    
    echo "⏳ 処理時間待機（10秒）..."
    sleep 10
    
    echo "🔍 応答確認中..."
    tmux capture-pane -t "$session_pane" -p | tail -3
    
    echo "✅ 送信プロセス完了"
}
```

### **全4ワーカー一括送信**
```bash
send_to_all_workers() {
    local messages=("$@")
    
    for i in {0..3}; do
        echo "=== WORKER$i 送信開始 ==="
        send_message_with_double_enter "multiagent:0.$i" "${messages[$i]}"
        echo ""
    done
}
```

---

## 🚨 **必須チェックリスト**

### **送信前確認**
- [ ] セッション・ペイン名が正確
- [ ] メッセージ内容に誤字脱字なし
- [ ] Claude Code起動済み確認（`>` プロンプト表示）

### **送信実行**
- [ ] メッセージ送信完了
- [ ] 1回目Enterキー送信完了
- [ ] 0.5秒待機完了
- [ ] 2回目Enterキー送信完了
- [ ] 10秒処理時間待機完了

### **送信後確認**
- [ ] 応答開始確認（キーワード検索）
- [ ] エラーメッセージなし確認
- [ ] 必要に応じて追加Enter送信

---

## 📊 **トラブルシューティング**

### **応答なしの場合**
1. 追加Enterキー送信（最大3回まで）
2. Claude Code再起動確認
3. セッション・ペイン正常性確認

### **エラーメッセージの場合**
1. メッセージ内容の見直し
2. ファイルパス・権限確認
3. 再送信実行

### **部分応答の場合**
1. 追加10秒待機
2. 必要に応じて補足メッセージ送信
3. 応答完了まで監視継続

---

## 🎯 **品質保証基準**

### **成功判定**
- ✅ AIからの応答開始（日本語での返答）
- ✅ エラーメッセージなし
- ✅ 期待される応答内容（役割認識等）

### **失敗判定**
- ❌ 15秒経過後も応答なし
- ❌ エラーメッセージ表示
- ❌ 不適切な応答内容

---

**この手順書に従うことで、Enterキー送信漏れを根絶し、確実なワーカー起動・メッセージ送信を保証します。**

**🔥 重要**: この手順は今後の全4ワーカーシステム操作で必須適用とします。