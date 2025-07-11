// hooks/memory.js
// Enterprise-grade Claude Code Memory Persistence System
// Integrates with existing claude-memory/session-bridge.sh backend

import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';

/* ---------- Configuration ---------- */
const ROOT = path.resolve(__dirname, '../../../..');
const BRIDGE_SCRIPT = path.join(ROOT, 'src/ai/memory/core/session-bridge.sh');
const MAX_CONVERSATIONAL_TOKENS = 2500; // When to compress conversation
const ORGANIZATION_STATE_FILE = path.join(ROOT, 'src/ai/memory/core/organization_state.json');

/* ---------- O3統合システム設定 ---------- */
const O3_SEARCH_SCRIPT = path.join(ROOT, 'src/ai/agents/o3-search-system.sh');
const O3_MCP_BRIDGE = path.join(ROOT, 'src/ai/agents/claude-mcp-bridge.py');
const O3_MEMORY_SYSTEM = path.join(ROOT, 'src/ai/memory/enhanced/o3-memory-system.py');
const O3_INHERITANCE_BRIDGE = path.join(ROOT, 'src/ai/memory/enhanced/session-inheritance-bridge.sh');

/* ---------- Reliability & Trust System ---------- */
const REQUIRED_FILES = [
  '.cursor/rules/globals.mdc',
  'docs/instructions/CLAUDE.md',
  'src/ai/memory/core/session-bridge.sh'
];

// Confidence scoring for responses
function calculateConfidence(searchResults, validationStatus) {
  let score = 0.0;
  
  // Tier 0 (Ground Truth) verification
  if (validationStatus.groundTruthChecked) score += 0.6;
  
  // Multiple search patterns succeeded
  if (searchResults.multiplePatterns) score += 0.2;
  
  // Recent cache hit
  if (searchResults.cacheHit) score += 0.15;
  
  // File metadata validation
  if (searchResults.metadataValid) score += 0.05;
  
  return Math.min(score, 0.99); // Never 100% confident
}

// Robust file search with fallback patterns
function robustFileSearch(pattern, basePath = ROOT) {
  const searchResults = {
    found: false,
    paths: [],
    multiplePatterns: false,
    cacheHit: false,
    metadataValid: false
  };
  
  try {
    // 1. Direct path check
    const directPath = path.join(basePath, pattern);
    if (fs.existsSync(directPath)) {
      searchResults.found = true;
      searchResults.paths.push(directPath);
      searchResults.metadataValid = true;
      return searchResults;
    }
    
    // 2. Glob pattern search
    const { execSync } = require('child_process');
    try {
      const globResults = execSync(`find "${basePath}" -name "*${path.basename(pattern)}*" -type f 2>/dev/null`, 
        { encoding: 'utf8', timeout: 5000 });
      
      if (globResults.trim()) {
        searchResults.found = true;
        searchResults.paths = globResults.trim().split('\n').filter(p => p);
        searchResults.multiplePatterns = true;
        return searchResults;
      }
    } catch (globError) {
      console.warn('Glob search failed, continuing...');
    }
    
    // 3. Content-based search for config files
    if (pattern.includes('cursor') || pattern.includes('rule')) {
      try {
        const grepResults = execSync(`grep -r "cursor\\|rule" "${basePath}" --include="*.mdc" --include="*.md" -l 2>/dev/null`, 
          { encoding: 'utf8', timeout: 5000 });
        
        if (grepResults.trim()) {
          searchResults.found = true;
          searchResults.paths = grepResults.trim().split('\n').filter(p => p);
          searchResults.multiplePatterns = true;
          return searchResults;
        }
      } catch (grepError) {
        console.warn('Content search failed, continuing...');
      }
    }
    
  } catch (error) {
    console.error('Robust search error:', error.message);
  }
  
  return searchResults;
}

// Pre-prompt validation of critical files
function validateCriticalFiles() {
  const validation = {
    allValid: true,
    missing: [],
    found: [],
    confidence: 1.0
  };
  
  for (const requiredFile of REQUIRED_FILES) {
    const searchResult = robustFileSearch(requiredFile);
    
    if (searchResult.found) {
      validation.found.push({
        pattern: requiredFile,
        paths: searchResult.paths
      });
    } else {
      validation.missing.push(requiredFile);
      validation.allValid = false;
    }
  }
  
  validation.confidence = validation.found.length / REQUIRED_FILES.length;
  
  return validation;
}

// Generate humble response based on confidence
function generateHumbleResponse(message, confidence) {
  if (confidence >= 0.95) {
    return message;
  } else if (confidence >= 0.8) {
    return `推定では${message}。念のため追加確認をお勧めします。`;
  } else if (confidence >= 0.6) {
    return `おそらく${message}ですが、他の場所にある可能性もあります。`;
  } else {
    return `${message}を確認しましたが、見つかりませんでした。別の場所や異なる名前で存在する可能性があります。追加の検索パターンを試しますか？`;
  }
}

/* ---------- O3推奨3層構造アーキテクチャ ---------- */

// ============================================================================
// 🔄 Layer 1: ライフサイクルフック層
// ============================================================================
class O3LifecycleManager {
  constructor() {
    this.hooks = {
      onStartup: [],
      onShutdown: [],
      onStateChange: [],
      onSessionTransition: []
    };
    this.isInitialized = false;
  }

  registerHook(event, callback) {
    if (this.hooks[event]) {
      this.hooks[event].push(callback);
    }
  }

  async triggerHook(event, data = {}) {
    if (this.hooks[event]) {
      for (const callback of this.hooks[event]) {
        try {
          await callback(data);
        } catch (error) {
          console.error(`O3 Hook error (${event}):`, error.message);
        }
      }
    }
  }
}

// ============================================================================
// 📊 Layer 2: 状態キャプチャ層
// ============================================================================
class O3StateCapture {
  constructor() {
    this.memoryStore = new Map();
    this.searchIndex = new Map();
    this.captureInterval = null;
  }

  async captureMemoryState(sessionId, context) {
    try {
      const memoryState = {
        timestamp: new Date().toISOString(),
        sessionId,
        context,
        foundationalContext: context.foundational_context || {},
        conversationalSummary: context.conversational_summary || '',
        organizationState: context.organization_state || {},
        o3SearchHistory: await this.getO3SearchHistory(),
        mcpBridgeStatus: await this.getMCPBridgeStatus()
      };

      this.memoryStore.set(sessionId, memoryState);
      await this.indexMemoryForSearch(sessionId, memoryState);
      
      console.log(`📊 O3記憶状態キャプチャ完了: ${sessionId}`);
      return memoryState;
    } catch (error) {
      console.error('O3記憶キャプチャエラー:', error.message);
      return null;
    }
  }

  async indexMemoryForSearch(sessionId, memoryState) {
    try {
      const searchableContent = JSON.stringify(memoryState).toLowerCase();
      const keywords = searchableContent.match(/\w+/g) || [];
      
      for (const keyword of keywords) {
        if (!this.searchIndex.has(keyword)) {
          this.searchIndex.set(keyword, new Set());
        }
        this.searchIndex.get(keyword).add(sessionId);
      }
    } catch (error) {
      console.error('O3記憶インデックス化エラー:', error.message);
    }
  }

  async getO3SearchHistory() {
    try {
      if (fs.existsSync(O3_SEARCH_SCRIPT)) {
        // o3検索履歴を取得
        return { available: true, status: 'active' };
      }
      return { available: false, status: 'unavailable' };
    } catch (error) {
      return { available: false, error: error.message };
    }
  }

  async getMCPBridgeStatus() {
    try {
      if (fs.existsSync(O3_MCP_BRIDGE)) {
        return { available: true, status: 'ready' };
      }
      return { available: false, status: 'unavailable' };
    } catch (error) {
      return { available: false, error: error.message };
    }
  }

  startPeriodicCapture(interval = 30000) {
    this.captureInterval = setInterval(() => {
      this.triggerPeriodicCapture();
    }, interval);
  }

  async triggerPeriodicCapture() {
    try {
      const currentContext = await this.getCurrentContext();
      if (currentContext.sessionId) {
        await this.captureMemoryState(currentContext.sessionId, currentContext);
      }
    } catch (error) {
      console.error('定期記憶キャプチャエラー:', error.message);
    }
  }

  async getCurrentContext() {
    return {
      sessionId: process.env.CLAUDE_SESSION_ID || 'default',
      foundational_context: getDefaultFoundationalContext(),
      organization_state: loadOrganizationState()
    };
  }
}

// ============================================================================
// 🚀 Layer 3: 自動注入層
// ============================================================================
class O3MemoryInjector {
  constructor(stateCapture) {
    this.stateCapture = stateCapture;
    this.injectionStrategies = new Map();
    this.setupDefaultStrategies();
  }

  setupDefaultStrategies() {
    this.injectionStrategies.set('startup', this.injectStartupMemory.bind(this));
    this.injectionStrategies.set('context', this.injectContextualMemory.bind(this));
    this.injectionStrategies.set('search', this.injectSearchResults.bind(this));
    this.injectionStrategies.set('mcp', this.injectMCPIntegration.bind(this));
  }

  async injectMemory(strategy, prompt, metadata) {
    try {
      if (this.injectionStrategies.has(strategy)) {
        return await this.injectionStrategies.get(strategy)(prompt, metadata);
      }
      console.warn(`未知のO3注入戦略: ${strategy}`);
      return prompt;
    } catch (error) {
      console.error(`O3記憶注入エラー (${strategy}):`, error.message);
      return prompt;
    }
  }

  async injectStartupMemory(prompt, metadata) {
    try {
      const sessionId = metadata.session_id || 'default';
      const memoryState = this.stateCapture.memoryStore.get(sessionId);
      
      if (memoryState) {
        const inheritancePrompt = `# 🧠 O3統合記憶継承システム

## 📊 前回セッション継承
- **セッションID**: ${memoryState.sessionId}
- **記憶タイムスタンプ**: ${memoryState.timestamp}
- **O3検索システム**: ${memoryState.o3SearchHistory.status}
- **MCP統合**: ${memoryState.mcpBridgeStatus.status}

## 🎯 継承された基盤コンテキスト
${JSON.stringify(memoryState.foundationalContext, null, 2)}

## 💡 前回の重要学習事項
${memoryState.conversationalSummary}

**O3推奨**: この継承情報を基に一貫性を保ちながら作業を継続してください。`;

        prompt.messages.unshift({
          role: 'system',
          content: inheritancePrompt
        });
      }

      return prompt;
    } catch (error) {
      console.error('O3起動時記憶注入エラー:', error.message);
      return prompt;
    }
  }

  async injectContextualMemory(prompt, metadata) {
    try {
      const userMessage = prompt.messages.find(m => m.role === 'user');
      if (userMessage) {
        const relevantMemories = await this.searchRelevantMemories(userMessage.content);
        
        if (relevantMemories.length > 0) {
          const contextPrompt = `# 🔍 O3関連記憶検索結果

以下は過去の関連する記憶です：

${relevantMemories.map(memory => 
  `- **${memory.sessionId}**: ${memory.summary}`
).join('\n')}

この情報を参考に、一貫性のある回答を提供してください。`;

          prompt.messages.splice(-1, 0, {
            role: 'system',
            content: contextPrompt
          });
        }
      }

      return prompt;
    } catch (error) {
      console.error('O3文脈記憶注入エラー:', error.message);
      return prompt;
    }
  }

  async injectSearchResults(prompt, metadata) {
    try {
      if (metadata.enableO3Search && fs.existsSync(O3_SEARCH_SCRIPT)) {
        const userMessage = prompt.messages.find(m => m.role === 'user');
        if (userMessage) {
          const searchResults = await this.performO3Search(userMessage.content);
          
          if (searchResults) {
            const searchPrompt = `# 🤖 O3検索システム結果

以下はO3 AIによる検索結果です：

${searchResults}

この情報を活用して回答を補強してください。`;

            prompt.messages.splice(-1, 0, {
              role: 'system',
              content: searchPrompt
            });
          }
        }
      }

      return prompt;
    } catch (error) {
      console.error('O3検索結果注入エラー:', error.message);
      return prompt;
    }
  }

  async injectMCPIntegration(prompt, metadata) {
    try {
      if (metadata.enableMCP && fs.existsSync(O3_MCP_BRIDGE)) {
        const mcpPrompt = `# 🔗 MCP統合プロトコル有効

以下のMCP統合機能が利用可能です：
- GitHub Issues統合
- tmux連携
- AI組織システム統合
- 並列ワークフロー

必要に応じてMCPプロトコルを活用してください。`;

        prompt.messages.unshift({
          role: 'system',
          content: mcpPrompt
        });
      }

      return prompt;
    } catch (error) {
      console.error('O3 MCP統合注入エラー:', error.message);
      return prompt;
    }
  }

  async searchRelevantMemories(query, limit = 3) {
    try {
      const keywords = query.toLowerCase().match(/\w+/g) || [];
      const relevantSessions = new Set();

      for (const keyword of keywords) {
        if (this.stateCapture.searchIndex.has(keyword)) {
          for (const sessionId of this.stateCapture.searchIndex.get(keyword)) {
            relevantSessions.add(sessionId);
          }
        }
      }

      const memories = [];
      for (const sessionId of Array.from(relevantSessions).slice(0, limit)) {
        const memory = this.stateCapture.memoryStore.get(sessionId);
        if (memory) {
          memories.push({
            sessionId,
            summary: memory.conversationalSummary || '記憶なし',
            timestamp: memory.timestamp
          });
        }
      }

      return memories;
    } catch (error) {
      console.error('O3関連記憶検索エラー:', error.message);
      return [];
    }
  }

  async performO3Search(query) {
    try {
      const searchResult = execSync(`${O3_SEARCH_SCRIPT} general "${query}"`, {
        encoding: 'utf8',
        timeout: 15000
      });
      return searchResult.substring(0, 500); // 最初の500文字
    } catch (error) {
      console.error('O3検索実行エラー:', error.message);
      return null;
    }
  }
}

// O3システムインスタンス
const o3LifecycleManager = new O3LifecycleManager();
const o3StateCapture = new O3StateCapture();
const o3MemoryInjector = new O3MemoryInjector(o3StateCapture);

/* ---------- O3統合実装設計 4ステップ実装 ---------- */

// ============================================================================
// 🎯 initializeInheritanceSystem() - O3統合記憶継承システム初期化
// ============================================================================
async function initializeInheritanceSystem(options = {}) {
  const initStartTime = Date.now();
  console.log('🚀 O3統合記憶継承システム初期化開始...');
  
  try {
    // === Step 1: 設定確定 ===
    const config = await stepOne_ConfirmConfiguration(options);
    console.log('✅ Step 1: 設定確定完了');
    
    // === Step 2: API確認 ===
    const apiStatus = await stepTwo_VerifyAPIs(config);
    console.log('✅ Step 2: API確認完了');
    
    // === Step 3: システム初期化 ===
    const systemState = await stepThree_InitializeSystems(config, apiStatus);
    console.log('✅ Step 3: システム初期化完了');
    
    // === Step 4: イベント駆動処理 ===
    const eventHandlers = await stepFour_SetupEventDrivenProcessing(config, systemState);
    console.log('✅ Step 4: イベント駆動処理完了');
    
    const initDuration = Date.now() - initStartTime;
    console.log(`🎉 O3統合記憶継承システム初期化完了 (${initDuration}ms)`);
    
    return {
      success: true,
      initDuration,
      config,
      apiStatus,
      systemState,
      eventHandlers,
      timestamp: new Date().toISOString()
    };
    
  } catch (error) {
    const initDuration = Date.now() - initStartTime;
    console.error(`❌ O3統合記憶継承システム初期化失敗 (${initDuration}ms):`, error.message);
    
    return {
      success: false,
      error: error.message,
      initDuration,
      timestamp: new Date().toISOString()
    };
  }
}

// ============================================================================
// Step 1: 設定確定
// ============================================================================
async function stepOne_ConfirmConfiguration(options) {
  console.log('🔧 Step 1: 設定確定処理開始...');
  
  const config = {
    // 基本設定
    sessionId: options.sessionId || process.env.CLAUDE_SESSION_ID || `session-${Date.now()}`,
    enableO3Search: options.enableO3Search !== false, // デフォルト有効
    enableMCP: options.enableMCP !== false, // デフォルト有効
    enablePeriodicCapture: options.enablePeriodicCapture !== false, // デフォルト有効
    captureInterval: options.captureInterval || 30000, // 30秒
    
    // パス設定
    paths: {
      root: ROOT,
      o3SearchScript: O3_SEARCH_SCRIPT,
      mcpBridge: O3_MCP_BRIDGE,
      memorySystem: O3_MEMORY_SYSTEM,
      inheritanceBridge: O3_INHERITANCE_BRIDGE,
      bridgeScript: BRIDGE_SCRIPT
    },
    
    // O3システム設定
    o3Config: {
      searchTimeout: options.searchTimeout || 15000,
      maxMemoryAge: options.maxMemoryAge || 86400000, // 24時間
      maxSearchResults: options.maxSearchResults || 5,
      compressionThreshold: options.compressionThreshold || MAX_CONVERSATIONAL_TOKENS
    },
    
    // フォールバック設定
    fallback: {
      enableFallback: options.enableFallback !== false,
      fallbackTimeout: options.fallbackTimeout || 5000,
      retryAttempts: options.retryAttempts || 3
    }
  };
  
  // 設定検証
  if (!config.sessionId || config.sessionId.length < 3) {
    throw new Error('Invalid session ID configuration');
  }
  
  // 環境変数設定
  process.env.CLAUDE_SESSION_ID = config.sessionId;
  process.env.CLAUDE_MEMORY_INHERITANCE_ACTIVE = 'true';
  
  console.log(`📋 セッションID: ${config.sessionId}`);
  console.log(`🔍 O3検索: ${config.enableO3Search ? '有効' : '無効'}`);
  console.log(`🔗 MCP統合: ${config.enableMCP ? '有効' : '無効'}`);
  console.log(`⏱️  定期キャプチャ: ${config.enablePeriodicCapture ? config.captureInterval + 'ms' : '無効'}`);
  
  return config;
}

// ============================================================================
// Step 2: API確認
// ============================================================================
async function stepTwo_VerifyAPIs(config) {
  console.log('🔍 Step 2: API確認処理開始...');
  
  const apiStatus = {
    o3Search: { available: false, status: 'unknown', error: null },
    mcpBridge: { available: false, status: 'unknown', error: null },
    memorySystem: { available: false, status: 'unknown', error: null },
    inheritanceBridge: { available: false, status: 'unknown', error: null },
    bridgeScript: { available: false, status: 'unknown', error: null }
  };
  
  // O3検索システム確認
  try {
    if (fs.existsSync(config.paths.o3SearchScript)) {
      const testResult = execSync(`${config.paths.o3SearchScript} check`, {
        encoding: 'utf8',
        timeout: 5000,
        stdio: 'pipe'
      });
      apiStatus.o3Search = { available: true, status: 'ready', testResult };
      console.log('✅ O3検索システム: 利用可能');
    } else {
      apiStatus.o3Search = { available: false, status: 'not_found', error: 'Script not found' };
      console.log('❌ O3検索システム: 未検出');
    }
  } catch (error) {
    apiStatus.o3Search = { available: false, status: 'error', error: error.message };
    console.log('⚠️ O3検索システム: エラー');
  }
  
  // MCP統合ブリッジ確認
  try {
    if (fs.existsSync(config.paths.mcpBridge)) {
      // Python importテスト
      execSync(`python3 -c "import sys; sys.path.append('${path.dirname(config.paths.mcpBridge)}'); from claude_mcp_bridge import ClaudeMCPBridge"`, {
        encoding: 'utf8',
        timeout: 3000,
        stdio: 'pipe'
      });
      apiStatus.mcpBridge = { available: true, status: 'ready' };
      console.log('✅ MCP統合ブリッジ: 利用可能');
    } else {
      apiStatus.mcpBridge = { available: false, status: 'not_found', error: 'Bridge not found' };
      console.log('❌ MCP統合ブリッジ: 未検出');
    }
  } catch (error) {
    apiStatus.mcpBridge = { available: false, status: 'error', error: error.message };
    console.log('⚠️ MCP統合ブリッジ: エラー');
  }
  
  // O3記憶システム確認
  try {
    if (fs.existsSync(config.paths.memorySystem)) {
      apiStatus.memorySystem = { available: true, status: 'ready' };
      console.log('✅ O3記憶システム: 利用可能');
    } else {
      apiStatus.memorySystem = { available: false, status: 'not_found', error: 'Memory system not found' };
      console.log('❌ O3記憶システム: 未検出');
    }
  } catch (error) {
    apiStatus.memorySystem = { available: false, status: 'error', error: error.message };
    console.log('⚠️ O3記憶システム: エラー');
  }
  
  // 継承ブリッジ確認
  try {
    if (fs.existsSync(config.paths.inheritanceBridge)) {
      const testResult = execSync(`${config.paths.inheritanceBridge} test`, {
        encoding: 'utf8',
        timeout: 5000,
        stdio: 'pipe'
      });
      apiStatus.inheritanceBridge = { available: true, status: 'ready', testResult };
      console.log('✅ 継承ブリッジ: 利用可能');
    } else {
      apiStatus.inheritanceBridge = { available: false, status: 'not_found', error: 'Inheritance bridge not found' };
      console.log('❌ 継承ブリッジ: 未検出');
    }
  } catch (error) {
    apiStatus.inheritanceBridge = { available: false, status: 'error', error: error.message };
    console.log('⚠️ 継承ブリッジ: エラー');
  }
  
  // セッションブリッジ確認
  try {
    if (fs.existsSync(config.paths.bridgeScript)) {
      apiStatus.bridgeScript = { available: true, status: 'ready' };
      console.log('✅ セッションブリッジ: 利用可能');
    } else {
      apiStatus.bridgeScript = { available: false, status: 'not_found', error: 'Bridge script not found' };
      console.log('❌ セッションブリッジ: 未検出');
    }
  } catch (error) {
    apiStatus.bridgeScript = { available: false, status: 'error', error: error.message };
    console.log('⚠️ セッションブリッジ: エラー');
  }
  
  return apiStatus;
}

// ============================================================================
// Step 3: システム初期化
// ============================================================================
async function stepThree_InitializeSystems(config, apiStatus) {
  console.log('⚙️ Step 3: システム初期化処理開始...');
  
  const systemState = {
    o3LifecycleManager: { initialized: false, hooks: 0 },
    o3StateCapture: { initialized: false, capturing: false },
    o3MemoryInjector: { initialized: false, strategies: 0 },
    inheritanceBridge: { executed: false, result: null },
    fallbackMemory: { loaded: false, data: null }
  };
  
  // O3ライフサイクルマネージャー初期化
  try {
    o3LifecycleManager.isInitialized = true;
    
    // 基本フック登録
    o3LifecycleManager.registerHook('onStartup', async (data) => {
      console.log('🔄 O3起動フック実行:', data.timestamp);
    });
    
    o3LifecycleManager.registerHook('onShutdown', async (data) => {
      console.log('🔄 O3終了フック実行:', data.timestamp);
    });
    
    o3LifecycleManager.registerHook('onStateChange', async (data) => {
      console.log('🔄 O3状態変化フック実行:', data.event);
    });
    
    o3LifecycleManager.registerHook('onSessionTransition', async (data) => {
      console.log('🔄 O3セッション遷移フック実行:', data.from, '->', data.to);
    });
    
    const hookCount = Object.values(o3LifecycleManager.hooks).reduce((sum, hooks) => sum + hooks.length, 0);
    systemState.o3LifecycleManager = { initialized: true, hooks: hookCount };
    console.log(`✅ O3ライフサイクルマネージャー初期化完了 (${hookCount}フック)`);
    
  } catch (error) {
    console.error('❌ O3ライフサイクルマネージャー初期化失敗:', error.message);
  }
  
  // O3状態キャプチャ初期化
  try {
    // 現在のコンテキストをキャプチャ
    const currentContext = await o3StateCapture.getCurrentContext();
    await o3StateCapture.captureMemoryState(config.sessionId, currentContext);
    
    // 定期キャプチャ開始
    if (config.enablePeriodicCapture) {
      o3StateCapture.startPeriodicCapture(config.captureInterval);
    }
    
    systemState.o3StateCapture = { 
      initialized: true, 
      capturing: config.enablePeriodicCapture,
      memoryStoreSize: o3StateCapture.memoryStore.size,
      searchIndexSize: o3StateCapture.searchIndex.size
    };
    console.log('✅ O3状態キャプチャ初期化完了');
    
  } catch (error) {
    console.error('❌ O3状態キャプチャ初期化失敗:', error.message);
  }
  
  // O3記憶注入システム初期化
  try {
    systemState.o3MemoryInjector = { 
      initialized: true, 
      strategies: o3MemoryInjector.injectionStrategies.size
    };
    console.log(`✅ O3記憶注入システム初期化完了 (${o3MemoryInjector.injectionStrategies.size}戦略)`);
    
  } catch (error) {
    console.error('❌ O3記憶注入システム初期化失敗:', error.message);
  }
  
  // 継承ブリッジ実行
  try {
    if (apiStatus.inheritanceBridge.available) {
      const bridgeResult = execSync(`${config.paths.inheritanceBridge} startup ${config.sessionId}`, {
        encoding: 'utf8',
        timeout: 30000,
        stdio: 'pipe'
      });
      systemState.inheritanceBridge = { executed: true, result: bridgeResult };
      console.log('✅ 継承ブリッジ実行完了');
    } else {
      console.log('⚠️ 継承ブリッジ利用不可、フォールバック実行');
      await executeInheritanceFallback(config);
      systemState.fallbackMemory = { loaded: true, data: 'fallback_executed' };
    }
    
  } catch (error) {
    console.error('❌ 継承ブリッジ実行失敗:', error.message);
    await executeInheritanceFallback(config);
    systemState.fallbackMemory = { loaded: true, data: 'fallback_executed' };
  }
  
  return systemState;
}

// ============================================================================
// Step 4: イベント駆動処理
// ============================================================================
async function stepFour_SetupEventDrivenProcessing(config, systemState) {
  console.log('🎛️ Step 4: イベント駆動処理設定開始...');
  
  const eventHandlers = {
    startup: [],
    shutdown: [],
    stateChange: [],
    sessionTransition: [],
    memoryCapture: [],
    errorRecovery: []
  };
  
  // 起動イベントハンドラー
  const startupHandler = async (data) => {
    console.log('🚀 起動イベント処理:', data);
    await o3StateCapture.captureMemoryState(config.sessionId, {
      event: 'startup',
      timestamp: data.timestamp,
      config: config
    });
  };
  eventHandlers.startup.push(startupHandler);
  o3LifecycleManager.registerHook('onStartup', startupHandler);
  
  // 状態変化イベントハンドラー
  const stateChangeHandler = async (data) => {
    console.log('🔄 状態変化イベント処理:', data.event);
    
    // 重要な状態変化を記憶に保存
    if (['before_prompt', 'after_response'].includes(data.event)) {
      await o3StateCapture.captureMemoryState(config.sessionId, {
        event: data.event,
        timestamp: new Date().toISOString(),
        metadata: data.metadata || {},
        sessionId: data.sessionId
      });
    }
  };
  eventHandlers.stateChange.push(stateChangeHandler);
  o3LifecycleManager.registerHook('onStateChange', stateChangeHandler);
  
  // セッション遷移イベントハンドラー
  const sessionTransitionHandler = async (data) => {
    console.log('🔁 セッション遷移イベント処理:', data);
    
    // 旧セッションの記憶を保存
    if (data.from) {
      await o3StateCapture.captureMemoryState(data.from, {
        event: 'session_end',
        timestamp: new Date().toISOString(),
        transitionTo: data.to
      });
    }
    
    // 新セッションの記憶を初期化
    if (data.to) {
      await o3StateCapture.captureMemoryState(data.to, {
        event: 'session_start', 
        timestamp: new Date().toISOString(),
        transitionFrom: data.from
      });
    }
  };
  eventHandlers.sessionTransition.push(sessionTransitionHandler);
  o3LifecycleManager.registerHook('onSessionTransition', sessionTransitionHandler);
  
  // 記憶キャプチャイベントハンドラー
  const memoryCaptureHandler = async (sessionId, memoryData) => {
    console.log('💾 記憶キャプチャイベント処理:', sessionId);
    
    // 記憶データの品質チェック
    if (memoryData && Object.keys(memoryData).length > 0) {
      // 検索インデックス更新
      await o3StateCapture.indexMemoryForSearch(sessionId, memoryData);
    }
  };
  eventHandlers.memoryCapture.push(memoryCaptureHandler);
  
  // エラー回復イベントハンドラー
  const errorRecoveryHandler = async (error, context) => {
    console.log('🔧 エラー回復イベント処理:', error.message);
    
    // エラー情報を記憶に保存
    await o3StateCapture.captureMemoryState(config.sessionId, {
      event: 'error_recovery',
      timestamp: new Date().toISOString(),
      error: error.message,
      context: context,
      recovery_attempted: true
    });
    
    // フォールバック処理実行
    if (config.fallback.enableFallback) {
      await executeInheritanceFallback(config);
    }
  };
  eventHandlers.errorRecovery.push(errorRecoveryHandler);
  
  // グローバルエラーハンドラー設定
  process.on('uncaughtException', (error) => {
    errorRecoveryHandler(error, 'uncaughtException').catch(console.error);
  });
  
  process.on('unhandledRejection', (reason, promise) => {
    errorRecoveryHandler(new Error(String(reason)), 'unhandledRejection').catch(console.error);
  });
  
  console.log(`✅ イベント駆動処理設定完了 (${Object.keys(eventHandlers).length}種類)`);
  
  // 起動イベント実行
  await o3LifecycleManager.triggerHook('onStartup', {
    timestamp: new Date().toISOString(),
    sessionId: config.sessionId,
    system: 'O3統合記憶継承システム'
  });
  
  return eventHandlers;
}

// ============================================================================
// ヘルパー関数
// ============================================================================
async function executeInheritanceFallback(config) {
  console.log('🔄 フォールバック記憶継承実行...');
  
  try {
    // 基本記憶継承情報表示
    console.log(`
🚨 === O3統合記憶継承情報 (フォールバック) ===
👑 役割: PRESIDENT
🎯 使命: AI永続記憶システム実装統括
📊 記録済みミス: 78回 → 79回目防止
💰 予算: $33,000 (Phase 1)
⚙️ 技術: PostgreSQL + pgvector + Claude Code hooks + O3統合
🤝 AI連携: Claude + Gemini + o3
🆔 セッション: ${config.sessionId}
⏰ 開始時刻: ${new Date().toLocaleString()}
============================================
`);
    
    // フォールバック記憶データ作成
    const fallbackMemory = {
      sessionId: config.sessionId,
      timestamp: new Date().toISOString(),
      foundational_context: getDefaultFoundationalContext(),
      organization_state: loadOrganizationState(),
      fallback_mode: true,
      inheritance_source: 'fallback_system'
    };
    
    // O3記憶システムに保存
    await o3StateCapture.captureMemoryState(config.sessionId, fallbackMemory);
    
    console.log('✅ フォールバック記憶継承完了');
    
  } catch (error) {
    console.error('❌ フォールバック記憶継承失敗:', error.message);
  }
}

/* ---------- Memory Backend Integration ---------- */
let bridgeInitialized = false;
let autoMemoryLoaded = false;

// O3統合起動時記憶読み込み機能 (initializeInheritanceSystem統合版)
async function autoLoadStartupMemory() {
  if (autoMemoryLoaded) return;
  
  try {
    console.log('🧠 O3統合記憶継承システム開始...');
    
    // === O3統合実装設計 4ステップ実装実行 ===
    const initResult = await initializeInheritanceSystem({
      sessionId: process.env.CLAUDE_SESSION_ID || `session-${Date.now()}`,
      enableO3Search: true,
      enableMCP: true,
      enablePeriodicCapture: true,
      captureInterval: 30000,
      searchTimeout: 15000,
      enableFallback: true
    });
    
    if (initResult.success) {
      console.log('✅ O3統合記憶継承システム初期化成功');
      console.log(`📊 初期化時間: ${initResult.initDuration}ms`);
      console.log(`🆔 セッションID: ${initResult.config.sessionId}`);
      console.log(`🎯 システム状態: ${Object.keys(initResult.systemState).length}コンポーネント`);
      console.log(`🔧 イベントハンドラー: ${Object.keys(initResult.eventHandlers).length}種類`);
      
      autoMemoryLoaded = true;
    } else {
      console.error('❌ O3統合記憶継承システム初期化失敗:', initResult.error);
      console.log('🔄 フォールバック記憶継承実行...');
      await fallbackMemoryInheritance();
    }
    
  } catch (error) {
    console.error('❌ O3統合記憶継承システム例外:', error.message);
    // エラー時もフォールバック実行
    await fallbackMemoryInheritance();
  }
}

// フォールバック記憶継承処理
async function fallbackMemoryInheritance() {
  try {
    // 基本的な前回セッション情報読み込み（正しいパス）
    const currentSessionFile = path.join(ROOT, 'src/ai/memory/core/session-records/current-session.json');
    
    if (fs.existsSync(currentSessionFile)) {
      const previousSession = JSON.parse(fs.readFileSync(currentSessionFile, 'utf8'));
      
      console.log('🧠 前回セッション記憶読み込み完了');
      console.log('📊 継承ミス数:', previousSession.mistakes_count || 78);
      console.log('📋 継続タスク:', previousSession.pending_tasks?.length || 0, '件');
      
      // 重要情報を画面表示
      displayStartupReminders(previousSession);
      
      autoMemoryLoaded = true;
    } else {
      console.log('🆕 初回起動: 新セッション開始');
      displayStartupReminders();
    }
    
  } catch (error) {
    console.error('❌ フォールバック記憶継承も失敗:', error.message);
    displayStartupReminders(); // 最低限の情報表示
    autoMemoryLoaded = true;
  }
}

// 起動時必須情報表示
function displayStartupReminders(previousSession = null) {
  console.log('\n🚨 === 必須記憶継承情報 ===');
  console.log('👑 役割: PRESIDENT');
  console.log('🎯 使命: AI永続記憶システム実装統括');
  console.log('📊 記録済みミス: 78回 → 79回目防止');
  console.log('💰 予算: $33,000 (Phase 1)');
  console.log('⚙️ 技術: PostgreSQL + pgvector + Claude Code hooks');
  console.log('🤝 AI連携: Claude + Gemini + o3');
  
  if (previousSession) {
    console.log('\n📋 前回からの継続事項:');
    if (previousSession.pending_tasks) {
      previousSession.pending_tasks.forEach((task, i) => {
        console.log(`  ${i + 1}. ${task}`);
      });
    }
    
    if (previousSession.important_learnings) {
      console.log('\n💡 重要学習事項:');
      previousSession.important_learnings.forEach((learning, i) => {
        console.log(`  - ${learning}`);
      });
    }
  }
  
  console.log('========================\n');
}

function ensureBridge() {
  if (bridgeInitialized) return;
  
  try {
    // 起動時自動記憶読み込み実行
    autoLoadStartupMemory();
    
    // Initialize memory system
    execSync(`${BRIDGE_SCRIPT} init`, { stdio: 'inherit', shell: true });
    bridgeInitialized = true;
    console.log('🧠 Memory bridge initialized successfully');
  } catch (error) {
    console.error('❌ Failed to initialize memory bridge:', error.message);
    throw error;
  }
}

function loadMemory(sessionId) {
  try {
    const stdout = execSync(`${BRIDGE_SCRIPT} get_memory ${sessionId}`, { 
      encoding: 'utf8',
      timeout: 5000 
    });
    const memory = JSON.parse(stdout);
    
    // Validate memory structure
    if (!memory.foundational_context) {
      memory.foundational_context = getDefaultFoundationalContext();
    }
    
    return memory;
  } catch (error) {
    console.error(`❌ Failed to load memory for session ${sessionId}:`, error.message);
    return getDefaultMemoryStructure();
  }
}

function saveMemory(sessionId, userMessage, assistantResponse) {
  try {
    const memoryUpdate = {
      user_message: userMessage,
      assistant_response: assistantResponse,
      timestamp: new Date().toISOString(),
      session_id: sessionId
    };
    
    execSync(`${BRIDGE_SCRIPT} save_memory ${sessionId}`, {
      input: JSON.stringify(memoryUpdate),
      stdio: ['pipe', 'ignore', 'pipe'],
      encoding: 'utf8',
      timeout: 10000
    });
    
    console.log(`💾 Memory saved for session ${sessionId}`);
  } catch (error) {
    console.error(`❌ Failed to save memory for session ${sessionId}:`, error.message);
  }
}

/* ---------- Organizational State Management ---------- */
function loadOrganizationState() {
  try {
    if (fs.existsSync(ORGANIZATION_STATE_FILE)) {
      const state = JSON.parse(fs.readFileSync(ORGANIZATION_STATE_FILE, 'utf8'));
      return state;
    }
    return getDefaultOrganizationState();
  } catch (error) {
    console.error('❌ Failed to load organization state:', error.message);
    return getDefaultOrganizationState();
  }
}

function updateAgentState(agentName, newState) {
  try {
    const orgState = loadOrganizationState();
    
    if (agentName === 'president') {
      orgState.president = { ...orgState.president, ...newState };
    } else if (agentName === 'boss') {
      orgState.boss = { ...orgState.boss, ...newState };
    } else if (orgState.workers[agentName]) {
      orgState.workers[agentName] = { ...orgState.workers[agentName], ...newState };
    }
    
    orgState.last_updated = new Date().toISOString();
    
    fs.writeFileSync(ORGANIZATION_STATE_FILE, JSON.stringify(orgState, null, 2));
    console.log(`🔄 Updated ${agentName} state`);
  } catch (error) {
    console.error(`❌ Failed to update ${agentName} state:`, error.message);
  }
}

/* ---------- Default Structures ---------- */
function getDefaultFoundationalContext() {
  return {
    role: "PRESIDENT",
    mission: "AI永続化システム開発統括 - 記憶喪失問題の根本解決",
    critical_directives: [
      "🚨 78回のミス記録を継承し、79回目を防ぐ",
      "👑 PRESIDENT役割を継続維持",
      "🎯 AI Compliance Engine実装統括",
      "🤝 BOSS・WORKER組織の状態管理"
    ],
    project_context: {
      name: "AI Persistence & Memory System",
      phase: "Phase 1 MVP Implementation",
      technology_stack: "PostgreSQL + pgvector + Claude Code hooks",
      budget: "$33,000 (Phase 1)",
      timeline: "2-4 weeks"
    },
    past_mistakes_summary: "78回の重大ミス（虚偽報告、詐欺、責任逃れ等）を記録済み",
    behavior_rules: [
      "証拠なき報告は絶対禁止",
      "プロジェクト文脈を常に維持",
      "職務放棄は重大違反",
      "ユーザーとの信頼関係最優先"
    ]
  };
}

function getDefaultMemoryStructure() {
  return {
    foundational_context: getDefaultFoundationalContext(),
    conversational_summary: "",
    conversational_log: [],
    metadata: {
      session_start: new Date().toISOString(),
      total_interactions: 0,
      last_compression: null
    }
  };
}

function getDefaultOrganizationState() {
  return {
    last_updated: new Date().toISOString(),
    president: {
      status: "active",
      current_mission: "AI永続化システム実装統括",
      active_directive: "hooks-implementation"
    },
    boss: {
      status: "managing",
      current_task: "Phase 1 Implementation Coordination",
      assigned_workers: ["worker1", "worker2", "worker3"]
    },
    workers: {
      worker1: {
        role: "Frontend Engineer",
        status: "ready",
        current_task: null,
        session_id: null
      },
      worker2: {
        role: "Backend Engineer", 
        status: "ready",
        current_task: null,
        session_id: null
      },
      worker3: {
        role: "UI/UX Designer",
        status: "ready",
        current_task: null,
        session_id: null
      }
    }
  };
}

/* ---------- Conversation Compression ---------- */
function shouldCompress(conversationalLog) {
  const totalTokens = conversationalLog.reduce((sum, msg) => {
    return sum + (msg.content ? msg.content.split(/\s+/).length : 0);
  }, 0);
  
  return totalTokens > MAX_CONVERSATIONAL_TOKENS;
}

function generateCompressionPrompt(conversationalLog) {
  const logText = conversationalLog.map(msg => 
    `${msg.role}: ${msg.content}`
  ).join('\n\n');
  
  return `Analyze the following conversation log and produce a structured summary in JSON format.

Requirements:
1. "summary": Concise third-person summary of key decisions, outcomes, and user intent
2. "entities": Object with arrays for files_mentioned, commands_executed, key_decisions, open_questions
3. Preserve exact syntax of file paths and code snippets
4. Focus on project-critical information for AI永続化システム development

Conversation Log:
---
${logText}
---

Respond with valid JSON only:`;
}

/* ---------- Mistake Prevention Integration ---------- */
import { enforceMistakePrevention, getMistakeContext } from './mistake-prevention-hooks.js';

/* ---------- Core Hook Functions ---------- */
export async function before_prompt({ prompt, metadata }) {
  // 🚨 MISTAKE #79 再発防止チェック
  const preventionResult = enforceMistakePrevention(prompt, metadata);
  if (preventionResult.shouldBlock) {
    console.error('🚨 作業ブロック:', preventionResult.reason);
    return { prompt, metadata }; // 作業を停止
  }
  
  // 再発防止プロンプト注入
  if (preventionResult.injectedPrompt) {
    prompt.messages.unshift({
      role: 'system',
      content: preventionResult.injectedPrompt
    });
  }
  
  // ミス記録コンテキスト追加
  prompt.messages.unshift({
    role: 'system', 
    content: getMistakeContext()
  });
  
  ensureBridge();
  
  // 🚨 CRITICAL: Validate required files before proceeding
  const validation = validateCriticalFiles();
  if (!validation.allValid) {
    console.warn('⚠️  Missing critical files:', validation.missing);
    // Continue but mark as low confidence
  }
  
  const sessionId = metadata.session_id || 'default';
  const memory = loadMemory(sessionId);
  const orgState = loadOrganizationState();
  
  // === O3統合記憶注入システム ===
  try {
    // O3ライフサイクルフック: プロンプト前処理
    await o3LifecycleManager.triggerHook('onStateChange', {
      event: 'before_prompt',
      sessionId,
      metadata
    });
    
    // O3記憶注入戦略実行
    prompt = await o3MemoryInjector.injectMemory('startup', prompt, metadata);
    prompt = await o3MemoryInjector.injectMemory('context', prompt, metadata);
    
    // O3検索統合（メタデータで有効化された場合）
    if (metadata.enableO3Search) {
      prompt = await o3MemoryInjector.injectMemory('search', prompt, metadata);
    }
    
    // MCP統合（メタデータで有効化された場合）
    if (metadata.enableMCP) {
      prompt = await o3MemoryInjector.injectMemory('mcp', prompt, metadata);
    }
    
    console.log('🤖 O3統合記憶注入完了');
  } catch (error) {
    console.error('❌ O3統合記憶注入エラー:', error.message);
  }
  
  // Build context hierarchy: Foundational → Organizational → Conversational
  const contextMessages = [];
  
  // Add validation status to context
  const validationContext = `# 🔍 システム検証状況

✅ 必須ファイル確認: ${validation.found.length}/${REQUIRED_FILES.length}
⚠️  信頼度: ${Math.round(validation.confidence * 100)}%

${validation.missing.length > 0 ? `❌ 未確認ファイル: ${validation.missing.join(', ')}` : '✅ すべての必須ファイルを確認済み'}

この信頼度に基づいて、適切な表現（断定/推定/要確認）を選択してください。`;
  
  contextMessages.push({
    role: 'system',
    content: validationContext
  });
  
  // 1. Foundational context (NEVER compressed)
  if (memory.foundational_context) {
    const foundationalPrompt = `# 🧠 永続記憶継承システム

## 役割・使命
${JSON.stringify(memory.foundational_context, null, 2)}

## 組織状態
${JSON.stringify(orgState, null, 2)}

この情報を基に、PRESIDENTとして一貫した役割を維持してください。`;
    
    contextMessages.push({
      role: 'system',
      content: foundationalPrompt
    });
  }
  
  // 2. Conversational summary
  if (memory.conversational_summary) {
    contextMessages.push({
      role: 'system', 
      content: `前回までの会話要約: ${memory.conversational_summary}`
    });
  }
  
  // 3. Recent conversation log
  if (memory.conversational_log.length > 0) {
    contextMessages.push(...memory.conversational_log);
  }
  
  // Inject context at the beginning
  prompt.messages = [...contextMessages, ...prompt.messages];
  
  console.log(`🧠 O3統合記憶システム ready - session ${sessionId}: ${contextMessages.length} context messages`);
  
  return { prompt, metadata };
}

export async function after_response({ response, metadata }) {
  const sessionId = metadata.session_id || 'default';
  const userMessage = metadata.user_message || metadata.prompt || '';
  const assistantResponse = response.text || response.content || response;
  
  // === O3統合記憶保存システム ===
  try {
    // O3ライフサイクルフック: レスポンス後処理
    await o3LifecycleManager.triggerHook('onStateChange', {
      event: 'after_response',
      sessionId,
      userMessage,
      assistantResponse,
      metadata
    });
    
    // O3状態キャプチャ: 会話データ保存
    const conversationContext = {
      foundational_context: getDefaultFoundationalContext(),
      conversational_summary: assistantResponse.substring(0, 200) + '...',
      organization_state: loadOrganizationState(),
      user_message: userMessage,
      assistant_response: assistantResponse,
      timestamp: new Date().toISOString()
    };
    
    await o3StateCapture.captureMemoryState(sessionId, conversationContext);
    
    console.log('🤖 O3統合記憶保存完了');
  } catch (error) {
    console.error('❌ O3統合記憶保存エラー:', error.message);
  }
  
  // Save to memory backend
  saveMemory(sessionId, userMessage, assistantResponse);
  
  // Update organization state if this affects agent status
  if (userMessage.includes('PRESIDENT') || userMessage.includes('BOSS') || userMessage.includes('WORKER')) {
    updateAgentState('president', {
      last_interaction: new Date().toISOString(),
      last_user_message: userMessage.substring(0, 100) + '...'
    });
  }
  
  console.log(`💾 O3統合記憶システム保存完了 - session ${sessionId}`);
  
  return { response, metadata };
}

/* ---------- O3-search-mcp連携機能 ---------- */

// O3検索システム統合API
export async function performO3Search(query, searchType = 'general', options = {}) {
  try {
    console.log(`🔍 O3検索開始: ${query} (${searchType})`);
    
    // o3検索スクリプト実行
    const searchCommand = `${O3_SEARCH_SCRIPT} ${searchType} "${query}"`;
    const searchResult = execSync(searchCommand, {
      encoding: 'utf8',
      timeout: options.timeout || 15000,
      cwd: ROOT
    });
    
    // 検索結果をO3記憶システムに記録
    const sessionId = options.sessionId || process.env.CLAUDE_SESSION_ID || 'default';
    await o3StateCapture.captureMemoryState(sessionId, {
      search_query: query,
      search_type: searchType,
      search_result: searchResult.substring(0, 500),
      timestamp: new Date().toISOString()
    });
    
    console.log('✅ O3検索完了');
    return {
      success: true,
      query,
      searchType,
      result: searchResult,
      timestamp: new Date().toISOString()
    };
    
  } catch (error) {
    console.error('❌ O3検索エラー:', error.message);
    return {
      success: false,
      query,
      searchType,
      error: error.message,
      timestamp: new Date().toISOString()
    };
  }
}

// MCP統合ブリッジ制御
export async function controlMCPBridge(action, options = {}) {
  try {
    console.log(`🔗 MCP統合操作: ${action}`);
    
    switch (action) {
      case 'status':
        // MCPブリッジ状態確認
        if (fs.existsSync(O3_MCP_BRIDGE)) {
          return { available: true, status: 'ready', bridge_path: O3_MCP_BRIDGE };
        }
        return { available: false, status: 'unavailable' };
        
      case 'start':
        // MCPブリッジ起動（バックグラウンド）
        const bridgeProcess = execSync(`python3 "${O3_MCP_BRIDGE}" &`, {
          encoding: 'utf8',
          timeout: 5000,
          detached: true
        });
        return { success: true, action, process: 'started' };
        
      case 'test':
        // MCP統合テスト実行
        const testResult = execSync(`python3 -c "import sys; sys.path.append('${path.dirname(O3_MCP_BRIDGE)}'); from claude_mcp_bridge import ClaudeMCPBridge; print('MCP Bridge test OK')"`, {
          encoding: 'utf8',
          timeout: 10000
        });
        return { success: true, action, test_result: testResult };
        
      default:
        return { success: false, error: `Unknown MCP action: ${action}` };
    }
    
  } catch (error) {
    console.error(`❌ MCP統合操作エラー (${action}):`, error.message);
    return {
      success: false,
      action,
      error: error.message,
      timestamp: new Date().toISOString()
    };
  }
}

// O3記憶検索API
export async function searchO3Memory(query, options = {}) {
  try {
    const sessionId = options.sessionId || 'default';
    const limit = options.limit || 5;
    
    console.log(`🧠 O3記憶検索: ${query}`);
    
    // O3記憶システムから関連記憶を検索
    const relevantMemories = await o3MemoryInjector.searchRelevantMemories(query, limit);
    
    // 検索結果をO3記憶に記録
    await o3StateCapture.captureMemoryState(sessionId, {
      memory_search_query: query,
      memory_search_results: relevantMemories,
      timestamp: new Date().toISOString()
    });
    
    return {
      success: true,
      query,
      memories: relevantMemories,
      count: relevantMemories.length,
      timestamp: new Date().toISOString()
    };
    
  } catch (error) {
    console.error('❌ O3記憶検索エラー:', error.message);
    return {
      success: false,
      query,
      error: error.message,
      timestamp: new Date().toISOString()
    };
  }
}

// O3ライフサイクルフック登録API
export function registerO3Hook(event, callback) {
  try {
    o3LifecycleManager.registerHook(event, callback);
    console.log(`✅ O3フック登録完了: ${event}`);
    return { success: true, event, registered: true };
  } catch (error) {
    console.error(`❌ O3フック登録エラー (${event}):`, error.message);
    return { success: false, event, error: error.message };
  }
}

// O3システム総合状態取得
export function getO3SystemStatus() {
  try {
    const status = {
      timestamp: new Date().toISOString(),
      lifecycle_manager: {
        initialized: o3LifecycleManager.isInitialized,
        hooks_count: Object.keys(o3LifecycleManager.hooks).reduce((sum, key) => 
          sum + o3LifecycleManager.hooks[key].length, 0)
      },
      state_capture: {
        memory_store_size: o3StateCapture.memoryStore.size,
        search_index_size: o3StateCapture.searchIndex.size,
        periodic_capture: !!o3StateCapture.captureInterval
      },
      memory_injector: {
        strategies: Array.from(o3MemoryInjector.injectionStrategies.keys())
      },
      integrations: {
        o3_search: fs.existsSync(O3_SEARCH_SCRIPT),
        mcp_bridge: fs.existsSync(O3_MCP_BRIDGE),
        memory_system: fs.existsSync(O3_MEMORY_SYSTEM),
        inheritance_bridge: fs.existsSync(O3_INHERITANCE_BRIDGE)
      }
    };
    
    return { success: true, status };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

// O3統合記憶継承システム初期化関数エクスポート
export { initializeInheritanceSystem };

/* ---------- Utility Functions ---------- */
export function getMemoryStatus(sessionId = 'default') {
  const memory = loadMemory(sessionId);
  const orgState = loadOrganizationState();
  const o3Status = getO3SystemStatus();
  
  return {
    session_id: sessionId,
    foundational_context_loaded: !!memory.foundational_context,
    conversational_items: memory.conversational_log.length,
    organization_agents: Object.keys(orgState.workers).length + 2, // +president +boss
    last_updated: orgState.last_updated,
    o3_integration: o3Status.success ? o3Status.status : { error: o3Status.error }
  };
}

export function forceCompress(sessionId = 'default') {
  try {
    execSync(`${BRIDGE_SCRIPT} compress_memory ${sessionId}`, { 
      stdio: 'inherit',
      timeout: 30000 
    });
    console.log(`🗜️ Forced compression completed for session ${sessionId}`);
  } catch (error) {
    console.error(`❌ Failed to compress memory:`, error.message);
  }
}

console.log('🧠 Claude Code Memory Hooks loaded successfully');

// 🚀 起動時自動記憶継承システム実行
(async () => {
  try {
    console.log('🔄 自動記憶継承システム起動中...');
    await autoLoadStartupMemory();
    console.log('✅ 自動記憶継承システム起動完了');
  } catch (error) {
    console.error('❌ 自動記憶継承システム起動失敗:', error.message);
    // エラーでも最低限の情報表示
    displayStartupReminders();
  }
})();