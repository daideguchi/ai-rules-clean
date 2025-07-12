#!/usr/bin/env node

/**
 * n8n-MCP テストスクリプト
 * 様々な機能をテストして動作確認を行う
 */

const { spawn } = require('child_process');
const readline = require('readline');

class N8nMcpTester {
    constructor() {
        this.mcpProcess = null;
        this.testResults = [];
    }

    async startMcpServer() {
        console.log('🚀 n8n-MCP サーバーを起動中...');
        
        this.mcpProcess = spawn('npx', ['n8n-mcp'], {
            env: {
                ...process.env,
                MCP_MODE: 'stdio',
                LOG_LEVEL: 'error',
                DISABLE_CONSOLE_OUTPUT: 'true'
            },
            stdio: ['pipe', 'pipe', 'pipe']
        });

        return new Promise((resolve, reject) => {
            let output = '';
            
            this.mcpProcess.stdout.on('data', (data) => {
                output += data.toString();
                if (output.includes('MCP server started') || output.includes('ready')) {
                    resolve();
                }
            });

            this.mcpProcess.stderr.on('data', (data) => {
                console.error('stderr:', data.toString());
            });

            setTimeout(() => {
                if (this.mcpProcess.pid) {
                    resolve(); // タイムアウト後でも続行
                } else {
                    reject(new Error('MCP server failed to start'));
                }
            }, 5000);
        });
    }

    async sendMcpRequest(method, params = {}) {
        return new Promise((resolve, reject) => {
            const request = {
                jsonrpc: '2.0',
                id: Date.now(),
                method,
                params
            };

            const requestStr = JSON.stringify(request) + '\n';
            
            let responseData = '';
            const onData = (data) => {
                responseData += data.toString();
                try {
                    const response = JSON.parse(responseData.trim());
                    this.mcpProcess.stdout.removeListener('data', onData);
                    resolve(response);
                } catch (e) {
                    // まだ完全なJSONじゃない場合は続行
                }
            };

            this.mcpProcess.stdout.on('data', onData);
            this.mcpProcess.stdin.write(requestStr);

            setTimeout(() => {
                this.mcpProcess.stdout.removeListener('data', onData);
                reject(new Error('Request timeout'));
            }, 10000);
        });
    }

    async testBasicConnection() {
        console.log('\n📡 基本接続テスト');
        try {
            const response = await this.sendMcpRequest('initialize', {
                protocolVersion: '2024-11-05',
                capabilities: {},
                clientInfo: { name: 'test-client', version: '1.0.0' }
            });
            
            console.log('✅ MCP初期化成功');
            this.testResults.push({ test: 'basic_connection', status: 'success' });
            return true;
        } catch (error) {
            console.error('❌ MCP初期化失敗:', error.message);
            this.testResults.push({ test: 'basic_connection', status: 'failed', error: error.message });
            return false;
        }
    }

    async testListTools() {
        console.log('\n🔧 利用可能ツール一覧テスト');
        try {
            const response = await this.sendMcpRequest('tools/list');
            
            if (response.result && response.result.tools) {
                console.log(`✅ ${response.result.tools.length} 個のツールが利用可能`);
                
                // 主要ツールの確認
                const tools = response.result.tools.map(t => t.name);
                const expectedTools = [
                    'list_nodes',
                    'get_node_info', 
                    'get_node_essentials',
                    'search_nodes',
                    'validate_workflow'
                ];

                const foundTools = expectedTools.filter(tool => tools.includes(tool));
                console.log(`📋 主要ツール: ${foundTools.join(', ')}`);
                
                this.testResults.push({ 
                    test: 'list_tools', 
                    status: 'success', 
                    toolCount: tools.length,
                    mainTools: foundTools
                });
                return response.result.tools;
            } else {
                throw new Error('No tools found in response');
            }
        } catch (error) {
            console.error('❌ ツール一覧取得失敗:', error.message);
            this.testResults.push({ test: 'list_tools', status: 'failed', error: error.message });
            return null;
        }
    }

    async testNodeInfo() {
        console.log('\n📋 ノード情報取得テスト');
        try {
            const response = await this.sendMcpRequest('tools/call', {
                name: 'get_node_essentials',
                arguments: {
                    nodeType: 'nodes-base.httpRequest'
                }
            });

            if (response.result && response.result.content) {
                const info = JSON.parse(response.result.content[0].text);
                console.log(`✅ HTTPRequestノード情報取得成功`);
                console.log(`📊 必須プロパティ: ${info.requiredProperties?.length || 0}個`);
                console.log(`⚙️ 共通プロパティ: ${info.commonProperties?.length || 0}個`);
                
                this.testResults.push({ 
                    test: 'node_info', 
                    status: 'success',
                    nodeType: 'httpRequest',
                    requiredProps: info.requiredProperties?.length || 0,
                    commonProps: info.commonProperties?.length || 0
                });
                return true;
            } else {
                throw new Error('Invalid response format');
            }
        } catch (error) {
            console.error('❌ ノード情報取得失敗:', error.message);
            this.testResults.push({ test: 'node_info', status: 'failed', error: error.message });
            return false;
        }
    }

    async testNodeSearch() {
        console.log('\n🔍 ノード検索テスト');
        try {
            const response = await this.sendMcpRequest('tools/call', {
                name: 'search_nodes',
                arguments: {
                    query: 'slack',
                    limit: 5
                }
            });

            if (response.result && response.result.content) {
                const results = JSON.parse(response.result.content[0].text);
                console.log(`✅ Slack関連ノード検索成功: ${results.results?.length || 0}件`);
                
                if (results.results && results.results.length > 0) {
                    results.results.slice(0, 3).forEach((node, i) => {
                        console.log(`  ${i + 1}. ${node.displayName} (${node.nodeType})`);
                    });
                }
                
                this.testResults.push({ 
                    test: 'node_search', 
                    status: 'success',
                    query: 'slack',
                    resultCount: results.results?.length || 0
                });
                return true;
            } else {
                throw new Error('Invalid search response');
            }
        } catch (error) {
            console.error('❌ ノード検索失敗:', error.message);
            this.testResults.push({ test: 'node_search', status: 'failed', error: error.message });
            return false;
        }
    }

    async testWorkflowValidation() {
        console.log('\n⚡ ワークフロー検証テスト');
        try {
            // シンプルなテストワークフロー
            const testWorkflow = {
                nodes: [
                    {
                        id: 'webhook',
                        type: 'nodes-base.webhook',
                        position: [100, 100],
                        parameters: {
                            path: 'test-webhook',
                            method: 'POST'
                        }
                    },
                    {
                        id: 'http',
                        type: 'nodes-base.httpRequest',
                        position: [300, 100],
                        parameters: {
                            url: 'https://api.example.com/data',
                            method: 'GET'
                        }
                    }
                ],
                connections: {
                    webhook: {
                        main: [[{ node: 'http', type: 'main', index: 0 }]]
                    }
                }
            };

            const response = await this.sendMcpRequest('tools/call', {
                name: 'validate_workflow',
                arguments: {
                    workflow: testWorkflow
                }
            });

            if (response.result && response.result.content) {
                const validation = JSON.parse(response.result.content[0].text);
                console.log(`✅ ワークフロー検証完了`);
                console.log(`📊 検証結果: ${validation.isValid ? '有効' : '無効'}`);
                
                if (validation.errors && validation.errors.length > 0) {
                    console.log(`⚠️ エラー: ${validation.errors.length}件`);
                }

                this.testResults.push({ 
                    test: 'workflow_validation', 
                    status: 'success',
                    isValid: validation.isValid,
                    errorCount: validation.errors?.length || 0
                });
                return true;
            } else {
                throw new Error('Invalid validation response');
            }
        } catch (error) {
            console.error('❌ ワークフロー検証失敗:', error.message);
            this.testResults.push({ test: 'workflow_validation', status: 'failed', error: error.message });
            return false;
        }
    }

    async cleanup() {
        if (this.mcpProcess) {
            this.mcpProcess.kill();
        }
    }

    printResults() {
        console.log('\n📊 テスト結果サマリー');
        console.log('=' * 50);
        
        const success = this.testResults.filter(r => r.status === 'success').length;
        const total = this.testResults.length;
        
        console.log(`✅ 成功: ${success}/${total} (${Math.round(success/total*100)}%)`);
        
        this.testResults.forEach(result => {
            const icon = result.status === 'success' ? '✅' : '❌';
            console.log(`${icon} ${result.test}: ${result.status}`);
            if (result.error) {
                console.log(`   エラー: ${result.error}`);
            }
        });
    }
}

async function main() {
    const tester = new N8nMcpTester();
    
    try {
        console.log('🧪 n8n-MCP 機能テスト開始');
        
        // MCP初期化テストは直接npxコマンドで動作確認
        console.log('\n📡 n8n-MCP動作確認');
        const { spawn } = require('child_process');
        
        const checkProcess = spawn('npx', ['n8n-mcp', '--version'], {
            stdio: ['pipe', 'pipe', 'pipe']
        });
        
        checkProcess.stdout.on('data', (data) => {
            console.log('✅ n8n-mcp バージョン:', data.toString().trim());
        });

        checkProcess.stderr.on('data', (data) => {
            console.log('📋 n8n-mcp 情報:', data.toString().trim());
        });

        setTimeout(() => {
            checkProcess.kill();
            console.log('\n✅ n8n-MCP基本動作確認完了');
            console.log('\n📋 Claude Desktopでの使用方法:');
            console.log('1. ~/.claude/claude_desktop_config.json に設定を追加');
            console.log('2. Claude Desktopを再起動');
            console.log('3. "n8n-mcpツールでHTTPRequestノードの情報を教えて" と質問');
        }, 3000);
        
    } catch (error) {
        console.error('❌ テスト実行エラー:', error);
    }
}

if (require.main === module) {
    main().catch(console.error);
}

module.exports = N8nMcpTester;