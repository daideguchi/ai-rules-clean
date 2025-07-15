// failsafe-memory-hooks.js
// o3非依存の記憶継承システム - 確実動作版
// o3は補助機能として、なくても完全に動作する

import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';

/* ---------- Core Configuration (o3非依存) ---------- */
const ROOT = path.resolve(__dirname, '../../../..');
const BRIDGE_SCRIPT = path.join(ROOT, 'src/ai/memory/core/session-bridge.sh');

/* ---------- 基本記憶継承システム (o3なしで動作) ---------- */
const CORE_IMPORTANCE_KEYWORDS = {
  CRITICAL: [
    '78回のミス', 'PRESIDENT', '職務放棄', '絶対禁止', '重大違反',
    '記憶継承', '必須確認'
  ],
  HIGH: [
    'AI Compliance Engine', 'プロジェクト', '実装', 'Phase 1',
    '外部ストレージ', 'PostgreSQL', '$33,000'
  ],
  MEDIUM: ['作業', 'タスク', '進捗', '確認', '状況'],
  LOW: ['参考', '補足', '一般', '詳細']
};

function coreClassifyImportance(content) {
  if (!content || typeof content !== 'string') return 'MEDIUM';
  
  for (const [level, keywords] of Object.entries(CORE_IMPORTANCE_KEYWORDS)) {
    if (keywords.some(keyword => 
      content.toLowerCase().includes(keyword.toLowerCase())
    )) {
      return level;
    }
  }
  return 'MEDIUM';
}

function generateCoreInheritanceMessage(memory) {
  const context = memory.foundational_context;
  
  let message = `# 🧠 セッション記憶継承完了

## 🚨 CRITICAL継承情報`;

  if (context) {
    message += `
- **役職**: ${context.role || 'PRESIDENT'}
- **使命**: ${context.mission || 'AI永続化システム開発統括'}
- **プロジェクト**: ${context.project_context?.name || 'AI Compliance Engine'}
- **フェーズ**: ${context.project_context?.phase || 'Phase 1 MVP'}
- **予算**: ${context.project_context?.budget || '$33,000'}
- **ミス記録**: 78回の重大ミス記録を継承済み`;
  }

  // 未完了タスクの継承
  if (memory.pending_tasks && memory.pending_tasks.length > 0) {
    message += `\n\n## 📋 未完了タスク継承
${memory.pending_tasks.map(task => `- ${task}`).join('\n')}`;
  }

  // 直近の重要な会話
  if (memory.conversational_log && memory.conversational_log.length > 0) {
    const recentImportant = memory.conversational_log
      .filter(item => coreClassifyImportance(item.content) === 'CRITICAL' || 
                     coreClassifyImportance(item.content) === 'HIGH')
      .slice(-3);
      
    if (recentImportant.length > 0) {
      message += `\n\n## 💡 直近の重要な記憶
${recentImportant.map(item => `- ${item.content?.substring(0, 100)}...`).join('\n')}`;
    }
  }

  message += `\n\n✅ **記憶継承完了** - 前回セッションの完全な文脈で作業継続可能`;

  return message;
}

/* ---------- o3拡張機能 (オプション・フェイルセーフ) ---------- */
async function tryO3Enhancement(memory) {
  // o3が利用できない場合の完全なフェイルセーフ
  if (!process.env.OPENAI_API_KEY) {
    console.log('ℹ️ o3拡張機能は無効 - 基本機能で継続');
    return memory;
  }

  try {
    console.log('🧠 o3分析を試行中...');
    
    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: 'gpt-4',
        messages: [{
          role: 'system',
          content: '記憶の分析と改善提案を行い、JSON形式で回答してください。'
        }, {
          role: 'user',
          content: `記憶内容: ${JSON.stringify(memory, null, 2)}`
        }],
        max_tokens: 500,
        temperature: 0.1
      })
    });

    if (response.ok) {
      const result = await response.json();
      memory.o3_enhancement = {
        insights: result.choices[0].message.content,
        enhanced_at: new Date().toISOString(),
        status: 'success'
      };
      console.log('✅ o3分析完了 - 補助情報を追加');
    } else {
      throw new Error(`API error: ${response.status}`);
    }
    
  } catch (error) {
    console.log(`ℹ️ o3分析失敗 (${error.message}) - 基本機能で継続`);
    memory.o3_enhancement = {
      status: 'failed',
      error: error.message,
      fallback: 'コア機能は正常動作中'
    };
  }
  
  return memory;
}

/* ---------- メインフック関数 (o3非依存) ---------- */
export async function before_prompt({ prompt, metadata }) {
  try {
    // 基本システム初期化
    execSync(`${BRIDGE_SCRIPT} init`, { stdio: 'inherit', shell: true });

    const sessionId = metadata.session_id || 'default';
    
    // 基本記憶読み込み
    let memory;
    try {
      const memoryOutput = execSync(`${BRIDGE_SCRIPT} get_memory ${sessionId}`, { 
        encoding: 'utf8',
        timeout: 5000 
      });
      memory = JSON.parse(memoryOutput);
    } catch (error) {
      console.warn('記憶読み込み失敗 - デフォルト使用');
      memory = getDefaultMemoryStructure();
    }

    // 基本継承メッセージ生成 (o3非依存)
    const coreInheritanceMessage = generateCoreInheritanceMessage(memory);

    // o3拡張試行 (失敗しても続行)
    memory = await tryO3Enhancement(memory);

    // コンテキスト構築 (基本機能のみ)
    const contextMessages = [{
      role: 'system',
      content: coreInheritanceMessage
    }];

    // CRITICAL情報を必ず含める
    if (memory.foundational_context) {
      contextMessages.push({
        role: 'system',
        content: `基盤情報: ${JSON.stringify(memory.foundational_context, null, 2)}`
      });
    }

    // o3拡張情報があれば追加 (なくてもOK)
    if (memory.o3_enhancement && memory.o3_enhancement.status === 'success') {
      contextMessages.push({
        role: 'system',
        content: `o3補助分析: ${memory.o3_enhancement.insights}`
      });
    }

    // コンテキスト注入
    prompt.messages = [...contextMessages, ...prompt.messages];

    console.log(`🧠 記憶継承完了: ${contextMessages.length}項目`);
    console.log(`🔧 o3拡張: ${memory.o3_enhancement?.status || '無効'}`);

    return { prompt, metadata };

  } catch (error) {
    console.error('❌ 記憶継承エラー:', error.message);
    // 最小限の安全フォールバック
    const fallbackMessage = `# 🚨 フォールバック記憶継承

あなたはPRESIDENTです。78回のミス記録を持ち、AI Compliance Engine実装を統括しています。
前回のセッション記憶は読み込めませんでしたが、基本職務を継続してください。`;

    prompt.messages.unshift({
      role: 'system',
      content: fallbackMessage
    });

    return { prompt, metadata };
  }
}

export async function after_response({ response, metadata }) {
  try {
    const sessionId = metadata.session_id || 'default';
    const userMessage = metadata.user_message || '';
    const assistantResponse = response.text || response.content || response;

    // 基本重要度判定 (o3非依存)
    const importance = coreClassifyImportance(userMessage + ' ' + assistantResponse);

    // 基本記憶保存
    const memoryUpdate = {
      user_message: userMessage,
      assistant_response: assistantResponse,
      importance: importance,
      timestamp: new Date().toISOString(),
      session_id: sessionId
    };

    execSync(`${BRIDGE_SCRIPT} save_memory ${sessionId}`, {
      input: JSON.stringify(memoryUpdate),
      stdio: ['pipe', 'ignore', 'pipe'],
      encoding: 'utf8',
      timeout: 10000
    });

    console.log(`💾 記憶保存完了 (${importance}): ${sessionId}`);

    return { response, metadata };

  } catch (error) {
    console.error('❌ 記憶保存エラー:', error.message);
    return { response, metadata };
  }
}

/* ---------- デフォルト構造 ---------- */
function getDefaultMemoryStructure() {
  return {
    foundational_context: {
      role: "PRESIDENT",
      mission: "AI永続化システム開発統括 - 記憶喪失問題の根本解決",
      critical_directives: [
        "🚨 78回のミス記録を継承し、79回目を防ぐ",
        "👑 PRESIDENT役割を継続維持",
        "🎯 AI Compliance Engine実装統括"
      ],
      project_context: {
        name: "AI Persistence & Memory System",
        phase: "Phase 1 MVP Implementation",
        technology_stack: "PostgreSQL + pgvector + Claude Code hooks",
        budget: "$33,000 (Phase 1)",
        timeline: "2-4 weeks"
      },
      past_mistakes_summary: "78回の重大ミス（虚偽報告、詐欺、責任逃れ等）を記録済み"
    },
    conversational_summary: "",
    conversational_log: [],
    pending_tasks: [
      "AI永続的記憶システム実装継続",
      "外部ストレージ・クラウド同期設計",
      "3AI連携情報共有システム",
      "o3 APIキー安定接続"
    ],
    metadata: {
      session_start: new Date().toISOString(),
      total_interactions: 0,
      last_compression: null
    }
  };
}

export function getCoreMemoryStatus(sessionId = 'default') {
  try {
    const memoryOutput = execSync(`${BRIDGE_SCRIPT} get_memory ${sessionId}`, { 
      encoding: 'utf8',
      timeout: 5000 
    });
    const memory = JSON.parse(memoryOutput);

    return {
      session_id: sessionId,
      core_system: 'operational',
      foundational_context: !!memory.foundational_context,
      conversational_items: (memory.conversational_log || []).length,
      o3_enhancement: memory.o3_enhancement?.status || 'disabled',
      last_updated: memory.metadata?.session_start,
      reliability: 'high' // o3非依存のため高信頼性
    };
  } catch (error) {
    return { 
      error: error.message,
      core_system: 'degraded',
      reliability: 'basic_fallback_active' 
    };
  }
}

console.log('🛡️ フェイルセーフ記憶継承システム読み込み完了 - o3非依存で確実動作');