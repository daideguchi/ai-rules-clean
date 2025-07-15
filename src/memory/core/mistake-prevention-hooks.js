// mistake-prevention-hooks.js
// MISTAKE #79 「勝手に暴走」再発防止システム

import fs from 'fs';
import path from 'path';

const MISTAKE_LOG_FILE = path.join(__dirname, '../../../MISTAKE_79_PREVENTION_REPORT.md');
const DANGEROUS_PHRASES = [
  'による.*設計',
  '連携.*システム',
  '統合.*アーキテクチャ',
  '拡張.*機能'
];

/* ---------- 自動チェック機能 ---------- */
function checkForDangerousPhrases(content) {
  const violations = [];
  
  DANGEROUS_PHRASES.forEach(pattern => {
    const regex = new RegExp(pattern, 'gi');
    if (regex.test(content)) {
      violations.push({
        pattern: pattern,
        matches: content.match(regex)
      });
    }
  });
  
  return violations;
}

function validateUserInstructionInterpretation(userInstruction, myInterpretation) {
  // ユーザー指示と私の解釈の比較
  const userKeywords = userInstruction.toLowerCase().split(' ');
  const myKeywords = myInterpretation.toLowerCase().split(' ');
  
  // 勝手な追加単語の検出
  const addedWords = myKeywords.filter(word => !userKeywords.includes(word));
  const suspiciousAdditions = addedWords.filter(word => 
    ['連携', '統合', '設計', 'システム', 'アーキテクチャ'].includes(word)
  );
  
  return {
    hasViolations: suspiciousAdditions.length > 0,
    addedWords: addedWords,
    suspiciousAdditions: suspiciousAdditions
  };
}

/* ---------- 強制確認システム ---------- */
export function enforceMistakePrevention(prompt, metadata) {
  console.log('🚨 MISTAKE #79 防止チェック開始');
  
  // 1. 過去ミス記録の読み込み
  if (fs.existsSync(MISTAKE_LOG_FILE)) {
    console.log('✅ MISTAKE #79 記録確認済み');
  } else {
    console.warn('⚠️ MISTAKE #79 記録が見つかりません');
  }
  
  // 2. 危険フレーズチェック
  const userMessage = metadata.user_message || '';
  const violations = checkForDangerousPhrases(userMessage);
  
  if (violations.length > 0) {
    console.warn('🚨 危険フレーズ検出:', violations);
    return {
      shouldBlock: true,
      reason: '勝手な解釈の可能性'
    };
  }
  
  // 3. 強制確認プロンプト注入
  const preventionPrompt = `
# 🚨 MISTAKE #79 再発防止チェック

作業開始前に以下を確認してください：
□ ユーザー指示を正確に理解したか？
□ 勝手な解釈・追加をしていないか？
□ 曖昧な表現を使っていないか？
□ 必要なら質問で確認したか？

ユーザー指示: "${userMessage}"
私の理解: [ここに復唱]

確認完了後に作業を開始してください。
`;

  return {
    shouldBlock: false,
    injectedPrompt: preventionPrompt
  };
}

/* ---------- 78回ミス記録統合 ---------- */
export function getMistakeContext() {
  return `
🚨 重要な背景情報:
- 私は78回の重大ミスを犯した記録があります
- 最新のMISTAKE #79: 「勝手に暴走」- ユーザー指示の曲解
- 再発防止のため、指示の正確な理解と確認を最優先とします

この文脈を常に意識して慎重に作業を進めます。
`;
}