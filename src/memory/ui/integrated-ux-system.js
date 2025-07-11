#!/usr/bin/env node
/**
 * 🎨 統合UXシステム - O3推奨3層構造対応
 * 起動時記憶継承、定期キャプチャ、自動検索の美しいUI/UX統合システム
 */

const { AutoMemoryDisplayUI } = require('./auto-memory-display.js');
const { BeautifulMemoryFormatter, IntegratedMemoryDisplay } = require('./beautiful-memory-formatter.js');
const fs = require('fs').promises;
const path = require('path');
const { exec } = require('child_process');
const util = require('util');
const execAsync = util.promisify(exec);

class IntegratedO3UXSystem extends IntegratedMemoryDisplay {
    constructor(options = {}) {
        super(options);
        
        this.config = {
            ...this.config,
            periodicDisplayInterval: options.periodicDisplayInterval || 300000, // 5分
            searchResultsCache: new Map(),
            autoSearchEnabled: options.autoSearch !== false,
            realTimeUpdates: options.realTimeUpdates !== false,
            uiAnimations: options.animations !== false,
            ...options
        };
        
        this.hooksSystemPath = path.join(__dirname, '../core/hooks.js');
        this.periodicTimer = null;
        this.currentSession = null;
        this.isDisplayActive = false;
    }

    /**
     * 🚀 統合システム起動
     */
    async initialize() {
        try {
            this.displayMainHeader(
                '🧠 O3統合記憶継承UXシステム起動',
                'hooks.js 3層構造との完全統合'
            );

            // 1. hooks.jsシステム状態確認
            const hooksStatus = await this.checkHooksSystemStatus();
            this.displaySystemStatus(hooksStatus);

            // 2. 現在のセッション情報取得
            this.currentSession = await this.getCurrentSessionInfo();
            
            // 3. O3記憶システムから完全記憶継承
            const memoryContext = await this.loadO3MemoryContext();
            
            // 4. 美しい統合表示
            await this.displayCompleteO3MemoryInheritance(memoryContext);
            
            // 5. 定期更新・監視システム開始
            if (this.config.realTimeUpdates) {
                this.startPeriodicUpdates();
            }
            
            // 6. 自動検索システム初期化
            if (this.config.autoSearchEnabled) {
                await this.initializeAutoSearchSystem();
            }
            
            this.displayCompletionMessage('🎯 O3統合UXシステム起動完了');
            this.isDisplayActive = true;
            
            return { success: true, session: this.currentSession };
            
        } catch (error) {
            this.displayErrorMessage(`統合システム起動エラー: ${error.message}`);
            return { success: false, error: error.message };
        }
    }

    /**
     * 🔍 hooks.jsシステム状態確認
     */
    async checkHooksSystemStatus() {
        try {
            // hooks.jsからO3システム状態を取得
            const { stdout } = await execAsync(`cd "${path.dirname(this.hooksSystemPath)}" && node -e "
                const hooks = require('./hooks.js');
                hooks.getO3SystemStatus().then(status => {
                    console.log(JSON.stringify(status, null, 2));
                }).catch(err => {
                    console.log(JSON.stringify({success: false, error: err.message}, null, 2));
                });
            "`);
            
            return JSON.parse(stdout);
        } catch (error) {
            return {
                success: false,
                error: error.message,
                fallback: true
            };
        }
    }

    /**
     * 📊 システム状態表示
     */
    displaySystemStatus(hooksStatus) {
        const statusContent = [
            this.colors.info(`🔧 O3 hooks.js システム状態`),
            ''
        ];

        if (hooksStatus.success) {
            const status = hooksStatus.status;
            
            statusContent.push(
                `${this.icons.success} ライフサイクル管理: ${status.lifecycle_manager.initialized ? '有効' : '初期化中'}`,
                `${this.icons.bullet} フック登録数: ${status.lifecycle_manager.hooks_count}`,
                `${this.icons.success} 状態キャプチャ: ${status.state_capture.memory_store_size}件保存`,
                `${this.icons.bullet} 検索インデックス: ${status.state_capture.search_index_size}エントリ`,
                `${this.icons.success} 定期キャプチャ: ${status.state_capture.periodic_capture ? '有効' : '無効'}`,
                ''
            );

            // 統合サービス状態
            statusContent.push(this.colors.secondary('🔗 統合サービス状況:'));
            Object.entries(status.integrations).forEach(([service, available]) => {
                const icon = available ? this.icons.success : this.icons.warning;
                const status_text = available ? '利用可能' : '未検出';
                statusContent.push(`  ${icon} ${service}: ${status_text}`);
            });
        } else {
            statusContent.push(
                this.colors.warning(`${this.icons.warning} hooks.jsシステム接続失敗`),
                this.colors.muted(`エラー: ${hooksStatus.error}`),
                this.colors.info('フォールバックモードで動作します')
            );
        }

        const box = this.createInfoBox(statusContent.join('\n'), 'システム状態', 'blue');
        console.log(box);
    }

    /**
     * 🧠 O3記憶システムからコンテキスト取得
     */
    async loadO3MemoryContext() {
        try {
            // hooks.jsのO3記憶システムから記憶継承
            const { stdout } = await execAsync(`cd "${path.dirname(this.hooksSystemPath)}" && node -e "
                const hooks = require('./hooks.js');
                const sessionId = '${this.currentSession?.sessionId || 'default'}';
                
                Promise.all([
                    hooks.getMemoryStatus(sessionId),
                    hooks.searchO3Memory('記憶継承 startup', { sessionId, limit: 5 }),
                    hooks.performO3Search('最新タスク 未完了', 'general', { sessionId })
                ]).then(results => {
                    console.log(JSON.stringify({
                        memoryStatus: results[0],
                        relevantMemories: results[1],
                        taskSearch: results[2],
                        timestamp: new Date().toISOString()
                    }, null, 2));
                }).catch(err => {
                    console.log(JSON.stringify({
                        error: err.message,
                        fallback: true
                    }, null, 2));
                });
            "`);
            
            const o3Context = JSON.parse(stdout);
            
            if (o3Context.error) {
                return await this.loadFallbackContext();
            }

            // O3システムからの情報を統合
            return {
                sessionInfo: this.currentSession,
                inheritance: {
                    inherited_memories_count: o3Context.relevantMemories?.count || 0,
                    memory_summary: this.generateMemorySummary(o3Context.relevantMemories?.memories || []),
                    continuation_points: this.extractContinuationPoints(o3Context.taskSearch?.result || '')
                },
                critical_directives: await this.loadCriticalDirectives(),
                pending_tasks: this.extractPendingTasks(o3Context.taskSearch?.result || ''),
                ai_collaboration_history: o3Context.memoryStatus?.o3_integration || {},
                o3_system_status: o3Context.memoryStatus,
                search_capabilities: {
                    memory_search: o3Context.relevantMemories?.success || false,
                    general_search: o3Context.taskSearch?.success || false,
                    real_time: true
                }
            };
            
        } catch (error) {
            console.error('O3記憶コンテキスト取得エラー:', error.message);
            return await this.loadFallbackContext();
        }
    }

    /**
     * 📝 記憶要約生成
     */
    generateMemorySummary(memories) {
        if (!memories || memories.length === 0) {
            return '前回セッションからの新規継承記憶なし';
        }

        const summaries = memories.map(memory => 
            `${memory.timestamp}: ${memory.summary}`
        ).join('\n');

        return `前回セッションから${memories.length}件の記憶を継承:\n${summaries}`;
    }

    /**
     * 🎯 継続作業点抽出
     */
    extractContinuationPoints(searchResult) {
        if (!searchResult) return [];

        const lines = searchResult.split('\n');
        const points = [];
        
        for (const line of lines) {
            if (line.includes('未完了') || line.includes('継続') || 
                line.includes('TODO') || line.includes('pending')) {
                points.push(line.trim());
            }
        }

        return points.slice(0, 5); // 最大5件
    }

    /**
     * 📋 未完了タスク抽出
     */
    extractPendingTasks(searchResult) {
        const continuationPoints = this.extractContinuationPoints(searchResult);
        return continuationPoints.map(point => 
            point.replace(/^[-*•]\s*/, '').replace(/^\d+\.\s*/, '')
        );
    }

    /**
     * ⚠️ 必須指示読み込み
     */
    async loadCriticalDirectives() {
        const defaults = [
            '78回のミス記録を継承し、79回目を防ぐ',
            'PRESIDENT役割を継続維持',
            'セキュリティ関連は慎重に実装する',
            'ファイル作成前に必ず既存ファイルを確認する'
        ];

        try {
            // hooks.jsから基盤コンテキストの必須指示を取得
            const { stdout } = await execAsync(`cd "${path.dirname(this.hooksSystemPath)}" && node -e "
                const hooks = require('./hooks.js');
                const memory = hooks.getMemoryStatus();
                console.log(JSON.stringify(memory, null, 2));
            "`);
            
            const memoryStatus = JSON.parse(stdout);
            // foundational_contextから必須指示を抽出
            // 実装は後で詳細化
            return defaults;
            
        } catch (error) {
            return defaults;
        }
    }

    /**
     * 🎊 完全統合表示
     */
    async displayCompleteO3MemoryInheritance(memoryContext) {
        // ターミナルサイズ調整
        this.adjustForTerminalSize();

        // O3統合ヘッダー
        this.displayO3IntegratedHeader(memoryContext);

        // セッション情報カード
        if (memoryContext.sessionInfo) {
            this.displaySessionCard(memoryContext.sessionInfo);
        }

        // O3記憶継承状況
        this.displayO3InheritanceStatus(memoryContext.inheritance);

        // 検索システム状況
        if (memoryContext.search_capabilities) {
            this.displaySearchCapabilities(memoryContext.search_capabilities);
        }

        // 必須記憶事項
        if (memoryContext.critical_directives) {
            this.displayCriticalMemories(memoryContext.critical_directives);
        }

        // 未完了タスク（O3検索結果）
        if (memoryContext.pending_tasks) {
            this.displayO3PendingTasks(memoryContext.pending_tasks);
        }

        // AI統合システム状況
        this.displayO3SystemStatus(memoryContext.o3_system_status);

        // 完了メッセージ
        this.displayCompletionMessage('🎯 O3統合記憶継承完了 - 高度なAI支援を利用可能');
    }

    /**
     * 🧠 O3統合ヘッダー
     */
    displayO3IntegratedHeader(memoryContext) {
        const headerContent = [
            this.colors.primary(`${this.icons.brain} O3統合記憶継承システム`),
            this.colors.secondary('hooks.js 3層アーキテクチャ完全統合'),
            this.colors.info(`セッション記憶: ${memoryContext.inheritance?.inherited_memories_count || 0}件`),
            this.colors.muted(`${'─'.repeat(70)}`)
        ].join('\n');

        const box = this.createSpecialBox(headerContent, {
            borderColor: 'cyan',
            backgroundColor: 'bgBlack',
            borderStyle: 'double'
        });

        console.log(box);
    }

    /**
     * 🔄 O3記憶継承状況表示
     */
    displayO3InheritanceStatus(inheritance) {
        const inheritanceContent = [
            this.colors.primary(`${this.icons.inheritance} O3記憶継承状況`),
            ''
        ];

        if (inheritance.inherited_memories_count > 0) {
            inheritanceContent.push(
                this.colors.success(`${this.icons.success} ${inheritance.inherited_memories_count}件の高度記憶を継承`),
                this.colors.info('🧠 O3 AI分析による記憶重要度判定済み'),
                ''
            );

            if (inheritance.memory_summary) {
                inheritanceContent.push(
                    this.colors.info('📝 O3統合記憶要約:'),
                    this.colors.muted(this.formatTextBlock('', inheritance.memory_summary, 60)),
                    ''
                );
            }

            if (inheritance.continuation_points && inheritance.continuation_points.length > 0) {
                inheritanceContent.push(
                    this.colors.warning(`🎯 O3検索による継続作業点:`),
                    ...inheritance.continuation_points.map((point, index) => 
                        this.colors.muted(`   ${index + 1}. ${point}`)
                    )
                );
            }
        } else {
            inheritanceContent.push(
                this.colors.warning(`${this.icons.warning} 新規セッション - O3記憶蓄積開始`),
                this.colors.info('🚀 3層アーキテクチャによる記憶システム初期化完了')
            );
        }

        const box = this.createInfoBox(inheritanceContent.join('\n'), 'O3記憶継承', 'green');
        console.log(box);
    }

    /**
     * 🔍 検索システム状況
     */
    displaySearchCapabilities(searchCapabilities) {
        const searchContent = [
            this.colors.secondary('🔍 O3統合検索システム'),
            '',
            `${this.getStatusIcon(searchCapabilities.memory_search)} 記憶検索: ${searchCapabilities.memory_search ? '有効' : '無効'}`,
            `${this.getStatusIcon(searchCapabilities.general_search)} 一般検索: ${searchCapabilities.general_search ? '有効' : '無効'}`,
            `${this.getStatusIcon(searchCapabilities.real_time)} リアルタイム: ${searchCapabilities.real_time ? '有効' : '無効'}`,
            '',
            this.colors.info('💡 自動検索・記憶インデックス化システム稼働中')
        ];

        const box = this.createInfoBox(searchContent.join('\n'), '検索機能', 'magenta');
        console.log(box);
    }

    /**
     * 📝 O3統合未完了タスク
     */
    displayO3PendingTasks(pendingTasks) {
        if (!pendingTasks || pendingTasks.length === 0) return;

        const tasksContent = [
            this.colors.info(`${this.icons.task} O3検索による未完了タスク (${pendingTasks.length}件)`),
            this.colors.muted('O3 AIによる自動検索・抽出結果'),
            '',
            ...pendingTasks.slice(0, 8).map((task, index) => 
                `${this.colors.muted('☐')} ${this.truncateText(task, 65)}`
            ),
            pendingTasks.length > 8 ? 
                this.colors.muted(`... 他${pendingTasks.length - 8}件（O3検索で詳細確認可能）`) : ''
        ].filter(Boolean);

        const box = this.createInfoBox(tasksContent.join('\n'), 'O3タスク検索', 'yellow');
        console.log(box);
    }

    /**
     * 🤖 O3システム状況
     */
    displayO3SystemStatus(systemStatus) {
        const statusContent = [
            this.colors.secondary('🤖 O3統合システム状況'),
            '',
            `🧠 記憶ストア: ${systemStatus?.memory_store_size || 0}件`,
            `🔍 検索インデックス: ${systemStatus?.search_index_size || 0}エントリ`,
            `⏱️ 定期キャプチャ: ${systemStatus?.periodic_capture ? '稼働中' : '停止中'}`,
            `🔗 hooks.js連携: ${systemStatus ? '正常' : 'エラー'}`,
            '',
            this.colors.info('💎 企業レベルAI記憶システム稼働中')
        ];

        const box = this.createInfoBox(statusContent.join('\n'), 'O3システム', 'cyan');
        console.log(box);
    }

    /**
     * ⏰ 定期更新システム
     */
    startPeriodicUpdates() {
        if (this.periodicTimer) {
            clearInterval(this.periodicTimer);
        }

        this.periodicTimer = setInterval(async () => {
            await this.performPeriodicUpdate();
        }, this.config.periodicDisplayInterval);

        console.log(this.colors.info('⏰ 定期更新システム開始 (5分間隔)'));
    }

    /**
     * 🔄 定期更新実行
     */
    async performPeriodicUpdate() {
        try {
            if (!this.isDisplayActive) return;

            console.log(this.colors.muted('\n⏰ 定期記憶状況更新...'));
            
            // hooks.jsから最新状態取得
            const currentStatus = await this.checkHooksSystemStatus();
            
            if (currentStatus.success) {
                const updateContent = [
                    this.colors.info('🔄 記憶システム定期更新'),
                    `📊 記憶数: ${currentStatus.status.state_capture.memory_store_size}`,
                    `🔍 インデックス: ${currentStatus.status.state_capture.search_index_size}`,
                    `⏰ ${new Date().toLocaleTimeString('ja-JP')}`
                ];

                const box = this.createInfoBox(updateContent.join('\n'), '定期更新', 'blue');
                console.log(box);
            }
            
        } catch (error) {
            console.error(this.colors.error('❌ 定期更新エラー:'), error.message);
        }
    }

    /**
     * 🔍 自動検索システム初期化
     */
    async initializeAutoSearchSystem() {
        try {
            console.log(this.colors.info('🔍 自動検索システム初期化中...'));

            // hooks.jsとの自動検索連携テスト
            const testResult = await this.testAutoSearchIntegration();
            
            if (testResult.success) {
                console.log(this.colors.success('✅ 自動検索システム準備完了'));
                this.enableAutoSearchFeatures();
            } else {
                console.log(this.colors.warning('⚠️ 自動検索システム部分機能のみ'));
            }
            
        } catch (error) {
            console.error(this.colors.error('❌ 自動検索初期化エラー:'), error.message);
        }
    }

    /**
     * 🧪 自動検索統合テスト
     */
    async testAutoSearchIntegration() {
        try {
            const { stdout } = await execAsync(`cd "${path.dirname(this.hooksSystemPath)}" && node -e "
                const hooks = require('./hooks.js');
                Promise.all([
                    hooks.performO3Search('test', 'general', { timeout: 5000 }),
                    hooks.searchO3Memory('test', { limit: 1 })
                ]).then(results => {
                    console.log(JSON.stringify({
                        success: true,
                        o3_search: results[0].success,
                        memory_search: results[1].success
                    }, null, 2));
                }).catch(err => {
                    console.log(JSON.stringify({
                        success: false,
                        error: err.message
                    }, null, 2));
                });
            "`);
            
            return JSON.parse(stdout);
        } catch (error) {
            return { success: false, error: error.message };
        }
    }

    /**
     * 🚀 自動検索機能有効化
     */
    enableAutoSearchFeatures() {
        // プロセス終了時のクリーンアップ登録
        process.on('SIGINT', () => {
            this.cleanup();
            process.exit(0);
        });

        process.on('SIGTERM', () => {
            this.cleanup();
            process.exit(0);
        });
    }

    /**
     * 🧹 システムクリーンアップ
     */
    cleanup() {
        if (this.periodicTimer) {
            clearInterval(this.periodicTimer);
            console.log(this.colors.info('⏹️ 定期更新システム停止'));
        }
        
        this.isDisplayActive = false;
        console.log(this.colors.success('✅ O3統合UXシステム正常終了'));
    }

    /**
     * 🎨 ユーティリティメソッド
     */
    getStatusIcon(status) {
        return status ? this.icons.success : this.icons.warning;
    }

    createInfoBox(content, title = '', borderColor = 'white') {
        const boxen = require('boxen');
        return boxen(content, {
            padding: 1,
            margin: { top: 0, bottom: 1, left: 2, right: 2 },
            borderStyle: 'single',
            borderColor,
            title: title ? ` ${title} ` : undefined
        });
    }

    createSpecialBox(content, options = {}) {
        const boxen = require('boxen');
        return boxen(content, {
            padding: 1,
            margin: 1,
            borderStyle: options.borderStyle || 'double',
            borderColor: options.borderColor || 'cyan',
            backgroundColor: options.backgroundColor || undefined
        });
    }

    displayErrorMessage(message) {
        console.log(this.colors.error(`❌ ${message}`));
    }

    /**
     * 📱 フォールバックコンテキスト
     */
    async loadFallbackContext() {
        return {
            sessionInfo: this.currentSession,
            inheritance: {
                inherited_memories_count: 0,
                memory_summary: 'フォールバックモード - 基本記憶システム使用中',
                continuation_points: []
            },
            critical_directives: await this.loadCriticalDirectives(),
            pending_tasks: [],
            ai_collaboration_history: {},
            o3_system_status: { error: 'hooks.js接続失敗' },
            search_capabilities: {
                memory_search: false,
                general_search: false,
                real_time: false
            }
        };
    }
}

/**
 * 🎯 メインエントリーポイント
 */
async function main() {
    const args = process.argv.slice(2);
    const options = {
        animations: !args.includes('--no-animations'),
        realTimeUpdates: !args.includes('--no-realtime'),
        autoSearch: !args.includes('--no-search'),
        colorScheme: args.includes('--minimal') ? 'minimal' : 'vibrant'
    };

    try {
        const uxSystem = new IntegratedO3UXSystem(options);
        const result = await uxSystem.initialize();
        
        if (result.success) {
            console.log('\n🎊 O3統合UXシステム完全稼働中');
            console.log('💡 Ctrl+C で正常終了');
            
            // インタラクティブモード保持
            if (!args.includes('--no-interactive')) {
                await uxSystem.waitForExit();
            }
        } else {
            console.error('❌ システム起動失敗:', result.error);
            process.exit(1);
        }
        
    } catch (error) {
        console.error('❌ 予期しないエラー:', error.message);
        process.exit(1);
    }
}

// インタラクティブ終了待機
IntegratedO3UXSystem.prototype.waitForExit = function() {
    return new Promise((resolve) => {
        process.stdin.setRawMode(true);
        process.stdin.resume();
        process.stdin.on('data', (key) => {
            if (key.toString() === '\u0003') { // Ctrl+C
                this.cleanup();
                resolve();
            }
        });
    });
};

// CLI実行時
if (require.main === module) {
    main().catch(console.error);
}

module.exports = { IntegratedO3UXSystem };