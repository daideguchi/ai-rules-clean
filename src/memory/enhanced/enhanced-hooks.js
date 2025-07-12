// Enhanced Memory Hooks for Claude Code
// o3統合セッション記憶継承システム

import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';

/* ---------- 設定 ---------- */
const ROOT = path.resolve(__dirname, '../../../..');
const MEMORY_SYSTEM_PATH = path.join(ROOT, 'src/ai/memory/enhanced/o3-memory-system.py');
const INHERITANCE_BRIDGE_PATH = path.join(ROOT, 'src/ai/memory/enhanced/session-inheritance-bridge.sh');
const ENHANCED_MEMORY_ROOT = path.join(ROOT, 'memory/enhanced');

/* ---------- セッション管理 ---------- */
let currentSessionId = null;
let memoryContext = null;
let isInitialized = false;

// セッションID生成
function generateSessionId() {
    return `session-${new Date().toISOString().replace(/[:.]/g, '-')}`;
}

// 記憶システム初期化
async function initializeMemorySystem() {
    if (isInitialized) return;
    
    try {
        console.log('🧠 o3記憶システム初期化中...');
        
        // 自動起動処理実行
        const result = execSync(`${INHERITANCE_BRIDGE_PATH} startup`, { 
            encoding: 'utf8',
            timeout: 30000
        });
        
        // セッションID抽出
        const sessionMatch = result.match(/セッションID: (session-[^\n]+)/);
        if (sessionMatch) {
            currentSessionId = sessionMatch[1];
            console.log(`✅ セッションID設定: ${currentSessionId}`);
        } else {
            currentSessionId = generateSessionId();
            console.log(`🆕 新セッションID生成: ${currentSessionId}`);
        }
        
        isInitialized = true;
        console.log('🎯 o3記憶システム初期化完了');
        
    } catch (error) {
        console.error('❌ 記憶システム初期化失敗:', error.message);
        currentSessionId = generateSessionId();
        isInitialized = true; // フォールバック
    }
}

// 記憶継承コンテキスト読み込み
async function loadInheritanceContext() {
    if (!currentSessionId) return null;
    
    try {
        const contextFile = path.join(ENHANCED_MEMORY_ROOT, 'session-records', `inheritance-${currentSessionId}.json`);
        
        if (fs.existsSync(contextFile)) {
            const context = JSON.parse(fs.readFileSync(contextFile, 'utf8'));
            console.log(`🧠 継承コンテキスト読み込み完了: ${Object.keys(context).length} 項目`);
            return context;
        }
        
    } catch (error) {
        console.error('⚠️ 継承コンテキスト読み込み失敗:', error.message);
    }
    
    return null;
}

// 記憶強化保存
async function saveEnhancedMemory(content, contextType = 'conversation', importance = 'medium') {
    if (!currentSessionId) return;
    
    try {
        const saveCommand = `python3 "${MEMORY_SYSTEM_PATH}" --action save_memory ` +
                           `--session-id "${currentSessionId}" ` +
                           `--content "${content.replace(/"/g, '\\"')}" ` +
                           `--context-type "${contextType}" ` +
                           `--importance "${importance}"`;
        
        execSync(saveCommand, { timeout: 10000 });
        console.log(`💾 記憶強化保存完了: ${contextType} (${importance})`);
        
    } catch (error) {
        console.error('❌ 記憶強化保存失敗:', error.message);
    }
}

// 関連記憶検索
async function searchRelevantMemories(query, limit = 5) {
    if (!currentSessionId) return [];
    
    try {
        const searchCommand = `python3 "${MEMORY_SYSTEM_PATH}" --action search_memory ` +
                             `--query "${query}" ` +
                             `--session-id "${currentSessionId}" ` +
                             `--limit "${limit}"`;
        
        const result = execSync(searchCommand, { 
            encoding: 'utf8',
            timeout: 15000
        });
        
        const memories = JSON.parse(result);
        console.log(`🔍 関連記憶検索完了: ${memories.length} 件`);
        return memories;
        
    } catch (error) {
        console.error('❌ 関連記憶検索失敗:', error.message);
        return [];
    }
}

/* ---------- コンテキスト構築 ---------- */
function buildFoundationalContext(inheritanceContext) {
    const foundational = {
        role: "PRESIDENT",
        mission: "AI永続記憶システム実装統括 - セッション間記憶継続問題の根本解決",
        critical_directives: [
            "🚨 78回の重大ミス記録を継承し、79回目を絶対に防ぐ",
            "👑 PRESIDENT役割を一貫して維持する",
            "🎯 AI Compliance Engine実装を統括する", 
            "🧠 セッション間記憶継続問題を技術的に解決する",
            "🤝 Claude + Gemini + o3の3AI連携を統括する"
        ],
        project_context: {
            name: "AI Persistence & Memory System with o3 Integration",
            phase: "Phase 1: o3統合記憶システム実装",
            technology_stack: "PostgreSQL + pgvector + Claude Code hooks + o3 API",
            budget: "$33,000 (Phase 1)",
            timeline: "2-4 weeks"
        },
        inherited_from_previous: inheritanceContext || {},
        mistake_prevention: {
            count: 78,
            rules: [
                "証拠なき報告は絶対禁止",
                "プロジェクト文脈を常に維持",
                "職務放棄は重大違反",
                "宣言なき作業開始は禁止",
                "セッション間記憶継続を最優先"
            ]
        }
    };
    
    return foundational;
}

function buildInheritancePrompt(inheritanceContext) {
    if (!inheritanceContext) return "";
    
    let prompt = `# 🧠 前回セッションからの記憶継承

## 📊 継承状況
- **継承記憶数**: ${inheritanceContext.inherited_memories_count || 0} 件
- **前回セッション**: ${inheritanceContext.previous_session_id || "不明"}

## 🚨 重要指示・禁止事項
`;
    
    if (inheritanceContext.critical_directives) {
        inheritanceContext.critical_directives.forEach(directive => {
            prompt += `- ${directive}\n`;
        });
    }
    
    prompt += `\n## 📋 継続すべき重要タスク\n`;
    
    if (inheritanceContext.high_priority_tasks) {
        inheritanceContext.high_priority_tasks.forEach(task => {
            prompt += `- ${task}\n`;
        });
    }
    
    prompt += `\n## 📍 作業継続点\n`;
    
    if (inheritanceContext.continuation_points) {
        inheritanceContext.continuation_points.forEach(point => {
            prompt += `- ${point}\n`;
        });
    }
    
    prompt += `\n## 💡 前回の重要な学習・決定事項\n`;
    
    if (inheritanceContext.memory_summary) {
        prompt += `${inheritanceContext.memory_summary}\n`;
    }
    
    prompt += `\n**🎯 この継承情報を基に、一貫性を保ちながら作業を継続してください。**\n`;
    
    return prompt;
}

/* ---------- Hooks実装 ---------- */
export async function before_prompt({ prompt, metadata }) {
    // 記憶システム初期化
    await initializeMemorySystem();
    
    // 継承コンテキスト読み込み
    if (!memoryContext) {
        memoryContext = await loadInheritanceContext();
    }
    
    // セッションID設定
    if (!metadata.session_id) {
        metadata.session_id = currentSessionId;
    }
    
    // コンテキスト構築
    const foundationalContext = buildFoundationalContext(memoryContext);
    const inheritancePrompt = buildInheritancePrompt(memoryContext);
    
    // プロンプト強化
    const enhancedMessages = [];
    
    // 1. 基盤コンテキスト
    enhancedMessages.push({
        role: 'system',
        content: `# 🧠 AI永続記憶システム - セッション継承情報

## 基盤コンテキスト
${JSON.stringify(foundationalContext, null, 2)}

## セッション情報
- **現在セッション**: ${currentSessionId}
- **記憶システム**: アクティブ
- **o3連携**: 有効
- **AI連携**: Claude + Gemini + o3

この基盤情報を基に、一貫した役割とミッションを維持してください。`
    });
    
    // 2. 継承情報
    if (inheritancePrompt) {
        enhancedMessages.push({
            role: 'system',
            content: inheritancePrompt
        });
    }
    
    // 3. 関連記憶検索（ユーザーメッセージがある場合）
    const userMessage = prompt.messages.find(m => m.role === 'user');
    if (userMessage && userMessage.content) {
        try {
            const relevantMemories = await searchRelevantMemories(userMessage.content);
            if (relevantMemories.length > 0) {
                const memoryPrompt = `# 🔍 関連記憶検索結果

以下は過去の関連する記憶です：

${relevantMemories.map(memory => 
    `- **${memory.context_type}** (重要度: ${memory.importance}): ${memory.content}`
).join('\n')}

この情報を参考に、一貫性のある回答を提供してください。`;
                
                enhancedMessages.push({
                    role: 'system',
                    content: memoryPrompt
                });
            }
        } catch (error) {
            console.error('関連記憶検索エラー:', error);
        }
    }
    
    // 4. 元のプロンプトに統合
    prompt.messages = [...enhancedMessages, ...prompt.messages];
    
    console.log(`🧠 記憶強化プロンプト構築完了: ${enhancedMessages.length} 項目追加`);
    
    return { prompt, metadata };
}

export async function after_response({ response, metadata }) {
    const userMessage = metadata.user_message || metadata.prompt || '';
    const assistantResponse = response.text || response.content || JSON.stringify(response);
    
    // 記憶強化保存
    await saveEnhancedMemory(
        `User: ${userMessage}\n\nAssistant: ${assistantResponse}`,
        'conversation',
        'medium'
    );
    
    // 重要な応答の場合は高優先度で保存
    if (userMessage.includes('重要') || userMessage.includes('必須') || 
        assistantResponse.includes('宣言') || assistantResponse.includes('実装')) {
        await saveEnhancedMemory(
            `[HIGH PRIORITY] ${assistantResponse}`,
            'important_response',
            'high'
        );
    }
    
    // AI連携情報共有（必要に応じて）
    if (metadata.share_with_ai) {
        try {
            execSync(`${INHERITANCE_BRIDGE_PATH} share ${currentSessionId}`, {
                timeout: 10000
            });
            console.log('🤝 AI連携情報共有完了');
        } catch (error) {
            console.error('AI連携情報共有エラー:', error.message);
        }
    }
    
    console.log(`💾 応答記憶保存完了: ${currentSessionId}`);
    
    return { response, metadata };
}

/* ---------- ユーティリティ関数 ---------- */
export function getMemoryStatus() {
    return {
        session_id: currentSessionId,
        is_initialized: isInitialized,
        has_inheritance_context: !!memoryContext,
        memory_root: ENHANCED_MEMORY_ROOT
    };
}

export async function forceMemorySync() {
    try {
        console.log('🔄 記憶同期強制実行中...');
        
        const result = execSync(`${INHERITANCE_BRIDGE_PATH} share ${currentSessionId}`, {
            encoding: 'utf8',
            timeout: 15000
        });
        
        console.log('✅ 記憶同期完了');
        return result;
        
    } catch (error) {
        console.error('❌ 記憶同期失敗:', error.message);
        throw error;
    }
}

export async function searchMemories(query, limit = 10) {
    return await searchRelevantMemories(query, limit);
}

export async function saveImportantMemory(content, contextType = 'important') {
    return await saveEnhancedMemory(content, contextType, 'high');
}

// システム起動時ログ
console.log('🧠 Enhanced Memory Hooks loaded successfully');
console.log('🎯 o3統合セッション記憶継承システム準備完了');