/**
 * 验证 Vercel 代理配置是否生效
 * 在部署后运行此脚本来测试代理功能
 */

const BACKEND_URL = 'http://123.57.174.186:8000';
const FRONTEND_URL = process.env.VERCEL_URL
    ? `https://${process.env.VERCEL_URL}`
    : 'http://localhost:3000';

async function testProxy() {
    console.log('🔍 开始验证 Vercel 代理配置...\n');

    const testEndpoints = [
        '/api/v1/auth/health',
        '/api/v2/agents/health',
        '/api/v1/users/me'
    ];

    for (const endpoint of testEndpoints) {
        try {
            console.log(`测试端点: ${endpoint}`);

            // 测试代理请求
            const proxyResponse = await fetch(`${FRONTEND_URL}${endpoint}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            console.log(`  状态码: ${proxyResponse.status}`);
            console.log(`  CORS 头: ${proxyResponse.headers.get('access-control-allow-origin')}`);

            if (proxyResponse.ok) {
                console.log(`  ✅ 代理成功\n`);
            } else {
                console.log(`  ⚠️  代理响应异常\n`);
            }

        } catch (error) {
            console.log(`  ❌ 代理失败: ${error.message}\n`);
        }
    }

    // 测试直接后端连接
    console.log('🔍 测试直接后端连接...');
    try {
        const directResponse = await fetch(`${BACKEND_URL}/api/v1/auth/health`);
        console.log(`后端状态: ${directResponse.status}`);
        console.log(`后端可访问: ${directResponse.ok ? '✅' : '❌'}`);
    } catch (error) {
        console.log(`后端连接失败: ${error.message}`);
    }
}

// 运行测试
if (require.main === module) {
    testProxy().catch(console.error);
}

module.exports = { testProxy };
