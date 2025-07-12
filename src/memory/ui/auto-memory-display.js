#!/usr/bin/env node
/**
 * 🧠 自動記憶継承UI表示システム
 * ユーザーが「記憶を思い出して」と言わなくても、起動時に自動で過去情報を美しく表示
 */

const fs = require('fs').promises;
const path = require('path');
const { exec } = require('child_process');
const util = require('util');
const execAsync = util.promisify(exec);

class AutoMemoryDisplayUI {
    constructor() {
        this.memoryBasePath = path.join(__dirname, '../../memory/enhanced');
        this.displayConfig = {
            maxCriticalItems: 5,
            maxHighPriorityItems: 8,
            maxPendingTasks: 10,
            animationDelay: 200,
            displayWidth: 80
        };
    }

    /**
     * 🚀 起動時自動記憶表示
     */
    async displayStartupMemoryInheritance() {
        try {
            console.log('\n' + '='.repeat(this.displayConfig.displayWidth));
            this.printHeader('🧠 記憶継承システム起動');
            console.log('='.repeat(this.displayConfig.displayWidth));
            
            // 1. セッション情報取得
            const sessionInfo = await this.getCurrentSessionInfo();
            await this.displaySessionInfo(sessionInfo);
            
            // 2. 記憶継承情報表示
            const memoryContext = await this.loadMemoryContext();
            await this.displayMemoryInheritance(memoryContext);
            
            // 3. 必須記憶表示
            await this.displayCriticalMemories(memoryContext);
            
            // 4. 未完了タスク表示
            await this.displayPendingTasks(memoryContext);
            
            // 5. AI連携履歴表示
            await this.displayAICollaborationHistory(memoryContext);
            
            console.log('='.repeat(this.displayConfig.displayWidth));
            this.printSuccessMessage('記憶継承完了 - 作業を継続できます');
            console.log('='.repeat(this.displayConfig.displayWidth));
            
        } catch (error) {
            this.printErrorMessage(`記憶継承エラー: ${error.message}`);
        }
    }

    /**
     * 📊 現在のセッション情報取得
     */
    async getCurrentSessionInfo() {
        const timestamp = new Date().toISOString();
        const sessionId = `session-${new Date().getTime()}`;
        
        return {
            sessionId,
            timestamp,
            previousSession: await this.getPreviousSessionId(),
            totalSessions: await this.getTotalSessionCount()
        };
    }

    /**
     * 🔄 記憶コンテキスト読み込み
     */
    async loadMemoryContext() {
        try {
            // Python記憶システムからコンテキスト取得
            const { stdout } = await execAsync(
                `cd "${this.memoryBasePath}" && python3 -c "
import asyncio
from o3_memory_system import O3EnhancedMemorySystem
import json

async def get_context():
    system = O3EnhancedMemorySystem()
    context = await system.generate_startup_context('${Date.now()}')
    print(json.dumps(context, indent=2, ensure_ascii=False))

asyncio.run(get_context())
                "`
            );
            
            return JSON.parse(stdout);
        } catch (error) {
            // フォールバック: 基本情報のみ表示
            return {
                inheritance: { message: "記憶システム初期化中..." },
                critical_directives: [],
                pending_tasks: [],
                mistake_prevention_rules: [],
                ai_collaboration_history: {}
            };
        }
    }

    /**
     * 📋 セッション情報表示
     */
    async displaySessionInfo(sessionInfo) {
        this.printSubHeader('📋 セッション情報');
        
        console.log(`🆔 セッションID: ${sessionInfo.sessionId}`);
        console.log(`⏰ 開始時刻: ${new Date(sessionInfo.timestamp).toLocaleString('ja-JP')}`);
        
        if (sessionInfo.previousSession) {
            console.log(`🔗 前回セッション: ${sessionInfo.previousSession}`);
        }
        
        console.log(`📊 総セッション数: ${sessionInfo.totalSessions}\n`);
        
        await this.animationDelay();
    }

    /**
     * 🔄 記憶継承情報表示
     */
    async displayMemoryInheritance(memoryContext) {
        this.printSubHeader('🔄 記憶継承状況');
        
        const inheritance = memoryContext.inheritance;
        
        if (inheritance.inherited_memories_count > 0) {
            console.log(`✅ ${inheritance.inherited_memories_count}件の記憶を継承しました`);
            
            if (inheritance.memory_summary) {
                console.log('\n📝 前回セッション要約:');
                console.log(this.formatTextBlock(inheritance.memory_summary));
            }
            
            if (inheritance.continuation_points && inheritance.continuation_points.length > 0) {
                console.log('\n🎯 継続作業点:');
                inheritance.continuation_points.forEach((point, index) => {
                    console.log(`   ${index + 1}. ${point}`);
                });
            }
        } else {
            console.log('🆕 新規セッション - 継承記憶なし');
        }
        
        console.log('');
        await this.animationDelay();
    }

    /**
     * ⚠️ 必須記憶表示
     */
    async displayCriticalMemories(memoryContext) {
        const criticalDirectives = memoryContext.critical_directives || [];
        
        if (criticalDirectives.length === 0) return;
        
        this.printSubHeader('⚠️ 必須記憶事項');
        
        criticalDirectives.slice(0, this.displayConfig.maxCriticalItems).forEach((directive, index) => {
            console.log(`🚨 ${index + 1}. ${directive}`);
        });
        
        if (criticalDirectives.length > this.displayConfig.maxCriticalItems) {
            console.log(`   ... 他${criticalDirectives.length - this.displayConfig.maxCriticalItems}件`);
        }
        
        console.log('');
        await this.animationDelay();
    }

    /**
     * 📝 未完了タスク表示
     */
    async displayPendingTasks(memoryContext) {
        const pendingTasks = memoryContext.pending_tasks || [];
        
        if (pendingTasks.length === 0) return;
        
        this.printSubHeader('📝 未完了タスク');
        
        pendingTasks.slice(0, this.displayConfig.maxPendingTasks).forEach((task, index) => {
            console.log(`☐ ${index + 1}. ${task}`);
        });
        
        if (pendingTasks.length > this.displayConfig.maxPendingTasks) {
            console.log(`   ... 他${pendingTasks.length - this.displayConfig.maxPendingTasks}件`);
        }
        
        console.log('');
        await this.animationDelay();
    }

    /**
     * 🤝 AI連携履歴表示
     */
    async displayAICollaborationHistory(memoryContext) {
        const collaborationHistory = memoryContext.ai_collaboration_history || {};
        
        if (Object.keys(collaborationHistory).length === 0) return;
        
        this.printSubHeader('🤝 AI連携履歴');
        
        Object.entries(collaborationHistory).forEach(([aiSource, stats]) => {
            const icon = this.getAIIcon(aiSource);
            console.log(`${icon} ${aiSource}: ${stats.interaction_count}回 (有用性: ${(stats.average_usefulness * 100).toFixed(1)}%)`);
        });
        
        console.log('');
        await this.animationDelay();
    }

    /**
     * 🎨 ヘルパーメソッド
     */
    printHeader(text) {
        const padding = Math.max(0, (this.displayConfig.displayWidth - text.length - 2) / 2);
        console.log(' '.repeat(Math.floor(padding)) + text);
    }

    printSubHeader(text) {
        console.log(`\n${text}`);
        console.log('-'.repeat(text.length));
    }

    printSuccessMessage(text) {
        console.log(`✅ ${text}`);
    }

    printErrorMessage(text) {
        console.log(`❌ ${text}`);
    }

    formatTextBlock(text, maxWidth = 70) {
        return text.split('\n').map(line => 
            line.length > maxWidth ? 
                line.substring(0, maxWidth - 3) + '...' : 
                line
        ).map(line => `   ${line}`).join('\n');
    }

    getAIIcon(aiSource) {
        const icons = {
            'claude': '🤖',
            'gemini': '💎',
            'o3': '🧠',
            'default': '🔮'
        };
        return icons[aiSource] || icons.default;
    }

    async animationDelay() {
        await new Promise(resolve => setTimeout(resolve, this.displayConfig.animationDelay));
    }

    async getPreviousSessionId() {
        try {
            const sessionRecordsPath = path.join(this.memoryBasePath, 'session-records');
            const files = await fs.readdir(sessionRecordsPath);
            const sessionFiles = files.filter(f => f.endsWith('.json')).sort().reverse();
            return sessionFiles.length > 0 ? sessionFiles[0].replace('.json', '') : null;
        } catch {
            return null;
        }
    }

    async getTotalSessionCount() {
        try {
            const sessionRecordsPath = path.join(this.memoryBasePath, 'session-records');
            const files = await fs.readdir(sessionRecordsPath);
            return files.filter(f => f.endsWith('.json')).length;
        } catch {
            return 0;
        }
    }
}

/**
 * 🎯 インタラクティブモード
 */
class InteractiveMemoryDisplay extends AutoMemoryDisplayUI {
    async showInteractiveMenu() {
        console.log('\n🎮 インタラクティブ記憶ナビゲーション');
        console.log('1. 詳細記憶検索');
        console.log('2. 特定セッション履歴表示');
        console.log('3. AI連携詳細分析');
        console.log('4. ミス防止ルール確認');
        console.log('5. メイン画面に戻る');
        
        // 実装は必要に応じて追加
    }
}

/**
 * 🚀 メイン実行
 */
async function main() {
    const args = process.argv.slice(2);
    const interactive = args.includes('--interactive') || args.includes('-i');
    
    if (interactive) {
        const display = new InteractiveMemoryDisplay();
        await display.displayStartupMemoryInheritance();
        await display.showInteractiveMenu();
    } else {
        const display = new AutoMemoryDisplayUI();
        await display.displayStartupMemoryInheritance();
    }
}

// CLI実行時
if (require.main === module) {
    main().catch(console.error);
}

module.exports = { AutoMemoryDisplayUI, InteractiveMemoryDisplay };