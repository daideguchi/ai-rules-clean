#!/usr/bin/env node

/**
 * n8n API接続テスト
 * 提供されたAPIキーでn8nインスタンスに接続できるかテスト
 */

const https = require('https');

class N8nApiTester {
    constructor() {
        this.apiUrl = 'https://app.n8n.io';
        this.apiKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxZDhkZjBkNS1jNTc2LTRkMTctOTZmZC1lYzYwNjUyZDQ2OTQiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzUyMzE5Mzk5fQ.m3nqC6d3HimtXRhlVAHu-jDG70Xex9KA8PgKZ0Z1-B8';
    }

    async makeApiRequest(endpoint, method = 'GET', data = null) {
        return new Promise((resolve, reject) => {
            const url = new URL(endpoint, this.apiUrl);
            
            const options = {
                hostname: url.hostname,
                port: url.port || 443,
                path: url.pathname + url.search,
                method: method,
                headers: {
                    'Authorization': `Bearer ${this.apiKey}`,
                    'Content-Type': 'application/json',
                    'User-Agent': 'n8n-mcp-tester/1.0'
                }
            };

            if (data && method !== 'GET') {
                const postData = JSON.stringify(data);
                options.headers['Content-Length'] = Buffer.byteLength(postData);
            }

            const req = https.request(options, (res) => {
                let responseData = '';
                
                res.on('data', (chunk) => {
                    responseData += chunk;
                });

                res.on('end', () => {
                    try {
                        const response = {
                            status: res.statusCode,
                            headers: res.headers,
                            data: responseData ? JSON.parse(responseData) : null
                        };
                        resolve(response);
                    } catch (e) {
                        resolve({
                            status: res.statusCode,
                            headers: res.headers,
                            data: responseData,
                            parseError: e.message
                        });
                    }
                });
            });

            req.on('error', (err) => {
                reject(err);
            });

            if (data && method !== 'GET') {
                req.write(JSON.stringify(data));
            }

            req.end();

            // タイムアウト設定
            setTimeout(() => {
                req.destroy();
                reject(new Error('Request timeout'));
            }, 10000);
        });
    }

    async testBasicConnection() {
        console.log('🔗 基本接続テスト');
        try {
            const response = await this.makeApiRequest('/api/v1/workflows');
            
            if (response.status === 200) {
                console.log('✅ API接続成功');
                console.log(`📊 ワークフロー数: ${response.data?.data?.length || 0}`);
                return true;
            } else if (response.status === 401) {
                console.log('❌ 認証エラー: APIキーが無効または期限切れ');
                return false;
            } else {
                console.log(`⚠️ 予期しないレスポンス: ${response.status}`);
                console.log('📋 レスポンス:', response.data);
                return false;
            }
        } catch (error) {
            console.log(`❌ 接続エラー: ${error.message}`);
            return false;
        }
    }

    async testWorkflowOperations() {
        console.log('\n⚙️ ワークフロー操作テスト');

        try {
            // ワークフロー一覧取得
            const listResponse = await this.makeApiRequest('/api/v1/workflows');
            
            if (listResponse.status === 200) {
                const workflows = listResponse.data?.data || [];
                console.log(`✅ ワークフロー一覧取得成功: ${workflows.length}件`);
                
                if (workflows.length > 0) {
                    const firstWorkflow = workflows[0];
                    console.log(`📋 最初のワークフロー: "${firstWorkflow.name}" (ID: ${firstWorkflow.id})`);
                    
                    // 特定ワークフローの詳細取得テスト
                    const detailResponse = await this.makeApiRequest(`/api/v1/workflows/${firstWorkflow.id}`);
                    if (detailResponse.status === 200) {
                        console.log('✅ ワークフロー詳細取得成功');
                        console.log(`📊 ノード数: ${detailResponse.data?.nodes?.length || 0}`);
                    }
                }
                
                return true;
            } else {
                console.log(`❌ ワークフロー一覧取得失敗: ${listResponse.status}`);
                return false;
            }
        } catch (error) {
            console.log(`❌ ワークフロー操作エラー: ${error.message}`);
            return false;
        }
    }

    async testExecutionHistory() {
        console.log('\n📈 実行履歴テスト');

        try {
            const response = await this.makeApiRequest('/api/v1/executions?limit=5');
            
            if (response.status === 200) {
                const executions = response.data?.data || [];
                console.log(`✅ 実行履歴取得成功: ${executions.length}件`);
                
                if (executions.length > 0) {
                    console.log('📋 最近の実行:');
                    executions.slice(0, 3).forEach((exec, i) => {
                        console.log(`  ${i + 1}. ${exec.workflowData?.name || 'Unknown'} - ${exec.status} (${new Date(exec.startedAt).toLocaleDateString()})`);
                    });
                }
                
                return true;
            } else {
                console.log(`❌ 実行履歴取得失敗: ${response.status}`);
                return false;
            }
        } catch (error) {
            console.log(`❌ 実行履歴エラー: ${error.message}`);
            return false;
        }
    }

    async testApiCapabilities() {
        console.log('\n🔍 API機能確認テスト');

        const endpoints = [
            { path: '/api/v1/workflows', name: 'ワークフロー管理' },
            { path: '/api/v1/executions', name: '実行管理' },
            { path: '/api/v1/credentials', name: '認証情報管理' },
            { path: '/api/v1/nodes', name: 'ノード情報' }
        ];

        for (const endpoint of endpoints) {
            try {
                const response = await this.makeApiRequest(endpoint.path);
                if (response.status === 200) {
                    console.log(`✅ ${endpoint.name}: 利用可能`);
                } else if (response.status === 401) {
                    console.log(`❌ ${endpoint.name}: 認証エラー`);
                } else if (response.status === 403) {
                    console.log(`⚠️ ${endpoint.name}: 権限不足`);
                } else {
                    console.log(`❓ ${endpoint.name}: ${response.status}`);
                }
            } catch (error) {
                console.log(`❌ ${endpoint.name}: ${error.message}`);
            }
        }
    }

    async runAllTests() {
        console.log('🧪 n8n API テスト開始');
        console.log('=' * 50);

        const results = {
            connection: await this.testBasicConnection(),
            workflows: false,
            executions: false
        };

        if (results.connection) {
            results.workflows = await this.testWorkflowOperations();
            results.executions = await this.testExecutionHistory();
            await this.testApiCapabilities();
        }

        console.log('\n' + '='.repeat(50));
        console.log('📊 テスト結果サマリー');
        console.log('='.repeat(50));

        const totalTests = Object.keys(results).length;
        const passedTests = Object.values(results).filter(Boolean).length;

        console.log(`✅ 成功: ${passedTests}/${totalTests} (${Math.round(passedTests/totalTests*100)}%)`);

        if (results.connection) {
            console.log('\n🎉 n8n API接続確認完了!');
            console.log('📋 Claude Desktopでn8n-mcpツールが完全に利用可能です');
            console.log('\n🚀 試してみてください:');
            console.log('  "n8n-mcpツールで私のワークフロー一覧を表示して"');
            console.log('  "n8nでSlackに通知するワークフローを作成して"');
        } else {
            console.log('\n⚠️ API接続に問題があります');
            console.log('📋 ドキュメント用ツールは利用可能ですが、管理機能は制限されます');
        }

        return results;
    }
}

async function main() {
    const tester = new N8nApiTester();
    await tester.runAllTests();
}

if (require.main === module) {
    main().catch(console.error);
}

module.exports = N8nApiTester;