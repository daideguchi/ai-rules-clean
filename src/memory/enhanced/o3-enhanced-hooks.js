// o3-enhanced-hooks.js
// o3統合セッション記憶継承システム - ベストプラクティス実装版
// Based on existing hooks.js with o3 enhancements

import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';

/* ---------- Enhanced Configuration ---------- */
const ROOT = path.resolve(__dirname, '../../../..');
const BRIDGE_SCRIPT = path.join(ROOT, 'src/ai/memory/core/session-bridge.sh');
const ENHANCED_BRIDGE = path.join(ROOT, 'src/ai/memory/enhanced/enhanced-session-bridge.sh');
const O3_API_URL = 'https://api.openai.com/v1/chat/completions';

/* ---------- Memory Importance Classification ---------- */
const IMPORTANCE_KEYWORDS = {
  CRITICAL: [
    '78回のミス', 'PRESIDENT', '職務放棄', '絶対禁止', '重大違反',
    '必須確認事項', '79回目を防ぐ', '記憶継承システム'
  ],
  HIGH: [
    'AI Compliance Engine', 'プロジェクト', '実装', 'o3', 'Phase 1',
    '外部ストレージ', 'pgvector', 'PostgreSQL', '$33,000'
  ],
  MEDIUM: [
    '作業', 'タスク', '進捗', '確認', '状況', '開発', '設計'
  ],
  LOW: [
    '参考', '補足', '一般', '詳細', '説明'
  ]
};

function classifyMemoryImportance(content) {
  if (!content || typeof content !== 'string') return 'MEDIUM';
  
  const contentLower = content.toLowerCase();
  
  for (const [level, keywords] of Object.entries(IMPORTANCE_KEYWORDS)) {
    if (keywords.some(keyword => 
      contentLower.includes(keyword.toLowerCase())
    )) {
      return level;
    }
  }
  return 'MEDIUM';
}

/* ---------- o3 API Integration ---------- */
async function analyzeMemoryWithO3(memory) {
  // Skip if no API key available
  if (!process.env.OPENAI_API_KEY) {
    console.warn('⚠️ OPENAI_API_KEY not found, skipping o3 analysis');
    return memory;
  }

  try {
    const analysisPrompt = `Analyze this AI session memory and provide:
1. importance_scores: Rate each memory item (CRITICAL/HIGH/MEDIUM/LOW)
2. key_insights: Extract 3-5 most important insights
3. continuation_points: Suggest next actions
4. memory_health: Rate memory completeness (1-10)

Memory to analyze:
${JSON.stringify(memory, null, 2)}

Respond with valid JSON only:`;

    const response = await fetch(O3_API_URL, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: 'gpt-4',  // Using GPT-4 as o3 placeholder
        messages: [{
          role: 'system',
          content: 'You are an AI memory analysis system. Respond with structured JSON only.'
        }, {
          role: 'user',
          content: analysisPrompt
        }],
        max_tokens: 1000,
        temperature: 0.1
      })
    });

    if (!response.ok) {
      throw new Error(`o3 API error: ${response.status}`);
    }

    const result = await response.json();
    const analysis = JSON.parse(result.choices[0].message.content);
    
    // Enhance memory with o3 analysis
    memory.o3_analysis = {
      ...analysis,
      analyzed_at: new Date().toISOString(),
      api_model: 'gpt-4'  // Will be o3 when available
    };

    console.log('🧠 o3 memory analysis completed');
    return memory;
    
  } catch (error) {
    console.warn('⚠️ o3 analysis failed:', error.message);
    // Fallback: Add basic analysis
    memory.o3_analysis = {
      importance_scores: { fallback: 'HIGH' },
      key_insights: ['o3 analysis unavailable - using fallback'],
      continuation_points: ['Continue with manual memory management'],
      memory_health: 7,
      analyzed_at: new Date().toISOString(),
      error: error.message
    };
    return memory;
  }
}

/* ---------- Enhanced Memory Processing ---------- */
function structureMemoryByImportance(memory) {
  const structured = {
    CRITICAL: [],
    HIGH: [],
    MEDIUM: [],
    LOW: []
  };

  // Process conversational log
  if (memory.conversational_log) {
    memory.conversational_log.forEach(item => {
      const importance = classifyMemoryImportance(item.content);
      structured[importance].push(item);
    });
  }

  // Process foundational context (always CRITICAL)
  if (memory.foundational_context) {
    structured.CRITICAL.push({
      type: 'foundational_context',
      content: memory.foundational_context,
      timestamp: new Date().toISOString()
    });
  }

  return structured;
}

function generateInheritanceMessage(memory, structuredMemory) {
  const critical = structuredMemory.CRITICAL;
  const high = structuredMemory.HIGH;
  const o3Analysis = memory.o3_analysis;

  let message = `# 🧠 セッション記憶継承完了

## 🚨 CRITICAL継承情報`;

  // Critical information
  critical.forEach(item => {
    if (item.type === 'foundational_context') {
      const context = item.content;
      message += `
- **役職**: ${context.role}
- **使命**: ${context.mission}
- **プロジェクト**: ${context.project_context?.name} (${context.project_context?.phase})
- **予算**: ${context.project_context?.budget}
- **ミス記録**: ${context.past_mistakes_summary}`;
    }
  });

  // High priority items
  if (high.length > 0) {
    message += `\n\n## 🎯 HIGH優先度継承
${high.slice(0, 3).map(item => `- ${item.content?.substring(0, 100)}...`).join('\n')}`;
  }

  // o3 Analysis insights
  if (o3Analysis && o3Analysis.key_insights) {
    message += `\n\n## 💡 o3分析による重要ポイント
${o3Analysis.key_insights.map(insight => `- ${insight}`).join('\n')}`;
  }

  // Continuation points
  if (o3Analysis && o3Analysis.continuation_points) {
    message += `\n\n## 📋 推奨される継続アクション
${o3Analysis.continuation_points.map(point => `- ${point}`).join('\n')}`;
  }

  message += `\n\n✅ **記憶継承完了** - 前回セッションの文脈で作業を継続してください。`;

  return message;
}

/* ---------- Enhanced Hook Functions ---------- */
export async function before_prompt({ prompt, metadata }) {
  try {
    // Initialize bridge
    if (fs.existsSync(ENHANCED_BRIDGE)) {
      execSync(`${ENHANCED_BRIDGE} init`, { stdio: 'inherit', shell: true });
    } else {
      execSync(`${BRIDGE_SCRIPT} init`, { stdio: 'inherit', shell: true });
    }

    const sessionId = metadata.session_id || 'default';
    
    // Load memory
    let memory;
    try {
      const memoryOutput = execSync(`${BRIDGE_SCRIPT} get_memory ${sessionId}`, { 
        encoding: 'utf8',
        timeout: 5000 
      });
      memory = JSON.parse(memoryOutput);
    } catch (error) {
      console.warn('Failed to load memory, using default');
      memory = getDefaultMemoryStructure();
    }

    // Enhance with o3 analysis
    memory = await analyzeMemoryWithO3(memory);

    // Structure by importance
    const structuredMemory = structureMemoryByImportance(memory);

    // Generate inheritance message
    const inheritanceMessage = generateInheritanceMessage(memory, structuredMemory);

    // Build enhanced context
    const contextMessages = [];

    // Add inheritance message
    contextMessages.push({
      role: 'system',
      content: inheritanceMessage
    });

    // Add CRITICAL items first
    structuredMemory.CRITICAL.forEach(item => {
      if (item.content && typeof item.content === 'object') {
        contextMessages.push({
          role: 'system',
          content: `CRITICAL情報: ${JSON.stringify(item.content, null, 2)}`
        });
      }
    });

    // Add HIGH priority items
    structuredMemory.HIGH.slice(0, 5).forEach(item => {
      contextMessages.push({
        role: item.role || 'system',
        content: item.content
      });
    });

    // Inject context at the beginning
    prompt.messages = [...contextMessages, ...prompt.messages];

    console.log(`🧠 Enhanced memory loaded: ${contextMessages.length} context messages`);
    console.log(`📊 Memory breakdown: CRITICAL:${structuredMemory.CRITICAL.length}, HIGH:${structuredMemory.HIGH.length}, MEDIUM:${structuredMemory.MEDIUM.length}, LOW:${structuredMemory.LOW.length}`);

    return { prompt, metadata };

  } catch (error) {
    console.error('❌ Enhanced hooks error:', error.message);
    // Fallback to basic functionality
    return { prompt, metadata };
  }
}

export async function after_response({ response, metadata }) {
  try {
    const sessionId = metadata.session_id || 'default';
    const userMessage = metadata.user_message || metadata.prompt || '';
    const assistantResponse = response.text || response.content || response;

    // Classify importance of this interaction
    const importance = classifyMemoryImportance(userMessage + ' ' + assistantResponse);

    // Enhanced memory save with importance
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

    console.log(`💾 Enhanced memory saved (${importance}) for session ${sessionId}`);

    return { response, metadata };

  } catch (error) {
    console.error('❌ Enhanced after_response error:', error.message);
    return { response, metadata };
  }
}

/* ---------- Utility Functions ---------- */
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
    metadata: {
      session_start: new Date().toISOString(),
      total_interactions: 0,
      last_compression: null
    }
  };
}

export function getEnhancedMemoryStatus(sessionId = 'default') {
  try {
    const memoryOutput = execSync(`${BRIDGE_SCRIPT} get_memory ${sessionId}`, { 
      encoding: 'utf8',
      timeout: 5000 
    });
    const memory = JSON.parse(memoryOutput);
    const structured = structureMemoryByImportance(memory);

    return {
      session_id: sessionId,
      total_memories: (memory.conversational_log || []).length,
      breakdown: {
        CRITICAL: structured.CRITICAL.length,
        HIGH: structured.HIGH.length,
        MEDIUM: structured.MEDIUM.length,
        LOW: structured.LOW.length
      },
      o3_analysis_available: !!memory.o3_analysis,
      memory_health: memory.o3_analysis?.memory_health || 'unknown',
      last_updated: memory.metadata?.session_start
    };
  } catch (error) {
    console.error('Error getting memory status:', error.message);
    return { error: error.message };
  }
}

console.log('🚀 o3-Enhanced Claude Code Memory Hooks loaded successfully');