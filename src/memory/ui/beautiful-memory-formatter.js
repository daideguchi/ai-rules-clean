#!/usr/bin/env node
/**
 * 🎨 美しい記憶表示フォーマッター
 * 記憶継承情報を視覚的に美しく、使いやすい形式で表示
 */

const chalk = require('chalk');
const boxen = require('boxen');
const figures = require('figures');
const ora = require('ora');

class BeautifulMemoryFormatter {
    constructor(options = {}) {
        this.config = {
            width: options.width || 80,
            padding: options.padding || 2,
            borderStyle: options.borderStyle || 'round',
            colorScheme: options.colorScheme || 'vibrant',
            animationsEnabled: options.animations !== false,
            ...options
        };
        
        this.colors = this.initColorScheme();
        this.icons = this.initIcons();
    }

    /**
     * 🎨 カラースキーム初期化
     */
    initColorScheme() {
        const schemes = {
            vibrant: {
                primary: chalk.cyan.bold,
                secondary: chalk.magenta,
                success: chalk.green.bold,
                warning: chalk.yellow.bold,
                error: chalk.red.bold,
                info: chalk.blue,
                muted: chalk.gray,
                highlight: chalk.bgCyan.black
            },
            elegant: {
                primary: chalk.blue.bold,
                secondary: chalk.purple,
                success: chalk.green,
                warning: chalk.amber,
                error: chalk.red,
                info: chalk.cyan,
                muted: chalk.dim,
                highlight: chalk.inverse
            },
            minimal: {
                primary: chalk.white.bold,
                secondary: chalk.white,
                success: chalk.green,
                warning: chalk.yellow,
                error: chalk.red,
                info: chalk.blue,
                muted: chalk.gray,
                highlight: chalk.inverse
            }
        };
        
        return schemes[this.config.colorScheme] || schemes.vibrant;
    }

    /**
     * 🔤 アイコン初期化
     */
    initIcons() {
        return {
            brain: '🧠',
            memory: '💭',
            inheritance: '🔄',
            session: '📋',
            task: '📝',
            critical: '🚨',
            warning: '⚠️',
            success: '✅',
            info: 'ℹ️',
            ai: {
                claude: '🤖',
                gemini: '💎',
                o3: '🧠',
                default: '🔮'
            },
            arrow: '→',
            bullet: '•',
            check: '☑',
            cross: '☒',
            star: '⭐',
            clock: '⏰',
            link: '🔗'
        };
    }

    /**
     * 🖼️ メインヘッダー表示
     */
    displayMainHeader(title, subtitle = '') {
        const headerContent = [
            this.colors.primary(`${this.icons.brain} ${title}`),
            subtitle ? this.colors.secondary(subtitle) : '',
            this.colors.muted(`${'─'.repeat(60)}`)
        ].filter(Boolean).join('\n');

        const box = boxen(headerContent, {
            padding: 1,
            margin: 1,
            borderStyle: this.config.borderStyle,
            borderColor: 'cyan',
            backgroundColor: 'black'
        });

        console.log(box);
    }

    /**
     * 📊 セッション情報カード
     */
    displaySessionCard(sessionInfo) {
        const sessionContent = [
            this.colors.info(`${this.icons.session} セッション情報`),
            '',
            `${this.icons.bullet} ID: ${this.colors.highlight(sessionInfo.sessionId)}`,
            `${this.icons.clock} 開始: ${new Date(sessionInfo.timestamp).toLocaleString('ja-JP')}`,
            sessionInfo.previousSession ? 
                `${this.icons.link} 前回: ${this.colors.muted(sessionInfo.previousSession)}` : '',
            `${this.icons.star} 総回数: ${this.colors.success(sessionInfo.totalSessions || 0)}`
        ].filter(Boolean).join('\n');

        const box = boxen(sessionContent, {
            padding: 1,
            margin: { top: 0, bottom: 1, left: 2, right: 2 },
            borderStyle: 'single',
            borderColor: 'blue'
        });

        console.log(box);
    }

    /**
     * 🔄 記憶継承ステータス
     */
    displayInheritanceStatus(inheritance) {
        const spinner = this.config.animationsEnabled ? ora() : null;
        
        if (spinner) {
            spinner.start(this.colors.info('記憶継承処理中...'));
            setTimeout(() => spinner.succeed(this.colors.success('記憶継承完了')), 1000);
        }

        const inheritanceContent = [
            this.colors.primary(`${this.icons.inheritance} 記憶継承状況`),
            '',
            inheritance.inherited_memories_count > 0 ?
                this.colors.success(`${this.icons.success} ${inheritance.inherited_memories_count}件の記憶を継承`) :
                this.colors.warning(`${this.icons.warning} 新規セッション`),
            '',
            inheritance.memory_summary ? 
                this.formatTextBlock('📝 前回要約:', inheritance.memory_summary) : ''
        ].filter(Boolean).join('\n');

        const box = boxen(inheritanceContent, {
            padding: 1,
            margin: { top: 1, bottom: 1, left: 2, right: 2 },
            borderStyle: 'double',
            borderColor: 'green'
        });

        console.log(box);

        // 継続作業点がある場合
        if (inheritance.continuation_points && inheritance.continuation_points.length > 0) {
            this.displayContinuationPoints(inheritance.continuation_points);
        }
    }

    /**
     * 🎯 継続作業点表示
     */
    displayContinuationPoints(points) {
        const pointsContent = [
            this.colors.warning(`${this.icons.arrow} 継続作業点`),
            '',
            ...points.slice(0, 5).map((point, index) => 
                `${this.colors.muted(`${index + 1}.`)} ${point}`
            ),
            points.length > 5 ? this.colors.muted(`... 他${points.length - 5}件`) : ''
        ].filter(Boolean).join('\n');

        const box = boxen(pointsContent, {
            padding: 1,
            margin: { left: 4, right: 2 },
            borderStyle: 'single',
            borderColor: 'yellow'
        });

        console.log(box);
    }

    /**
     * 🚨 必須記憶事項表示
     */
    displayCriticalMemories(criticalDirectives) {
        if (!criticalDirectives || criticalDirectives.length === 0) return;

        const criticalContent = [
            this.colors.error(`${this.icons.critical} 必須記憶事項`),
            this.colors.muted('以下の重要事項を必ず遵守してください'),
            '',
            ...criticalDirectives.slice(0, 5).map((directive, index) => 
                this.colors.warning(`${this.icons.warning} ${directive}`)
            ),
            criticalDirectives.length > 5 ? 
                this.colors.muted(`... 他${criticalDirectives.length - 5}件の重要事項`) : ''
        ].filter(Boolean).join('\n');

        const box = boxen(criticalContent, {
            padding: 1,
            margin: 1,
            borderStyle: 'double',
            borderColor: 'red',
            backgroundColor: 'bgRed'
        });

        console.log(box);
    }

    /**
     * 📝 未完了タスク表示
     */
    displayPendingTasks(pendingTasks) {
        if (!pendingTasks || pendingTasks.length === 0) return;

        const tasksContent = [
            this.colors.info(`${this.icons.task} 未完了タスク (${pendingTasks.length}件)`),
            '',
            ...pendingTasks.slice(0, 8).map((task, index) => 
                `${this.colors.muted('☐')} ${this.truncateText(task, 60)}`
            ),
            pendingTasks.length > 8 ? 
                this.colors.muted(`... 他${pendingTasks.length - 8}件`) : ''
        ].filter(Boolean).join('\n');

        const box = boxen(tasksContent, {
            padding: 1,
            margin: { top: 1, bottom: 1, left: 2, right: 2 },
            borderStyle: 'round',
            borderColor: 'magenta'
        });

        console.log(box);
    }

    /**
     * 🤝 AI連携履歴表示
     */
    displayAICollaboration(collaborationHistory) {
        if (!collaborationHistory || Object.keys(collaborationHistory).length === 0) return;

        const aiContent = [
            this.colors.secondary(`🤝 AI連携履歴`),
            '',
            ...Object.entries(collaborationHistory).map(([aiSource, stats]) => {
                const icon = this.icons.ai[aiSource] || this.icons.ai.default;
                const usefulnessBar = this.createProgressBar(stats.average_usefulness, 20);
                return `${icon} ${aiSource}: ${stats.interaction_count}回 ${usefulnessBar}`;
            })
        ];

        const box = boxen(aiContent.join('\n'), {
            padding: 1,
            margin: { top: 1, bottom: 1, left: 2, right: 2 },
            borderStyle: 'single',
            borderColor: 'cyan'
        });

        console.log(box);
    }

    /**
     * 🎊 完了メッセージ表示
     */
    displayCompletionMessage(message = '記憶継承完了 - 作業を継続できます') {
        const completionContent = this.colors.success(`${this.icons.success} ${message}`);
        
        const box = boxen(completionContent, {
            padding: 1,
            margin: 1,
            borderStyle: 'double',
            borderColor: 'green',
            align: 'center'
        });

        console.log(box);
    }

    /**
     * 🔧 ユーティリティメソッド
     */
    formatTextBlock(title, text, maxWidth = 50) {
        const lines = text.split('\n').map(line => 
            this.truncateText(line.trim(), maxWidth)
        ).filter(Boolean);

        return [
            this.colors.info(title),
            ...lines.map(line => this.colors.muted(`  ${line}`))
        ].join('\n');
    }

    truncateText(text, maxLength) {
        return text.length > maxLength ? 
            text.substring(0, maxLength - 3) + '...' : text;
    }

    createProgressBar(value, width = 20) {
        const filled = Math.round(value * width);
        const empty = width - filled;
        const bar = '█'.repeat(filled) + '░'.repeat(empty);
        const percentage = (value * 100).toFixed(1);
        return this.colors.info(`${bar} ${percentage}%`);
    }

    /**
     * 📱 レスポンシブ表示調整
     */
    adjustForTerminalSize() {
        const { columns, rows } = process.stdout;
        
        if (columns < 80) {
            this.config.width = columns - 4;
            this.config.borderStyle = 'single';
        }
        
        return { width: this.config.width, height: rows };
    }

    /**
     * 🎬 アニメーション効果
     */
    async typewriterEffect(text, delay = 50) {
        if (!this.config.animationsEnabled) {
            console.log(text);
            return;
        }

        for (const char of text) {
            process.stdout.write(char);
            await new Promise(resolve => setTimeout(resolve, delay));
        }
        console.log('');
    }

    /**
     * 🌈 テーマ切り替え
     */
    setTheme(themeName) {
        this.config.colorScheme = themeName;
        this.colors = this.initColorScheme();
    }
}

/**
 * 🎯 統合表示システム
 */
class IntegratedMemoryDisplay extends BeautifulMemoryFormatter {
    async displayCompleteMemoryInheritance(memoryContext) {
        // ターミナルサイズ調整
        this.adjustForTerminalSize();

        // メインヘッダー
        this.displayMainHeader(
            'Claude Code 記憶継承システム',
            '前回セッションの記憶を自動継承中...'
        );

        // セッション情報
        if (memoryContext.sessionInfo) {
            this.displaySessionCard(memoryContext.sessionInfo);
        }

        // 記憶継承状況
        if (memoryContext.inheritance) {
            this.displayInheritanceStatus(memoryContext.inheritance);
        }

        // 必須記憶事項
        if (memoryContext.critical_directives) {
            this.displayCriticalMemories(memoryContext.critical_directives);
        }

        // 未完了タスク
        if (memoryContext.pending_tasks) {
            this.displayPendingTasks(memoryContext.pending_tasks);
        }

        // AI連携履歴
        if (memoryContext.ai_collaboration_history) {
            this.displayAICollaboration(memoryContext.ai_collaboration_history);
        }

        // 完了メッセージ
        this.displayCompletionMessage();
    }
}

module.exports = { 
    BeautifulMemoryFormatter, 
    IntegratedMemoryDisplay 
};

// CLI実行時
if (require.main === module) {
    const display = new IntegratedMemoryDisplay({ animations: true });
    
    // テストデータで表示
    const testContext = {
        sessionInfo: {
            sessionId: 'session-20250705-233000',
            timestamp: new Date().toISOString(),
            previousSession: 'session-20250705-120000',
            totalSessions: 15
        },
        inheritance: {
            inherited_memories_count: 8,
            memory_summary: 'AI記憶継承システムの実装を進行中。78回のミス防止ルール適用。o3 APIとの連携テスト完了。',
            continuation_points: [
                'UI表示システムの最終調整',
                'フック機能の統合テスト',
                'ドキュメント作成'
            ]
        },
        critical_directives: [
            '78回のミスを記録し、同じミスを絶対に繰り返さない',
            'ファイル作成前に必ず既存ファイルを確認する',
            'セキュリティ関連は慎重に実装する'
        ],
        pending_tasks: [
            'メモリ使用量の最適化',
            'エラーハンドリングの強化',
            '多言語対応の検討'
        ],
        ai_collaboration_history: {
            'claude': { interaction_count: 45, average_usefulness: 0.92 },
            'gemini': { interaction_count: 12, average_usefulness: 0.78 },
            'o3': { interaction_count: 8, average_usefulness: 0.95 }
        }
    };
    
    display.displayCompleteMemoryInheritance(testContext).catch(console.error);
}