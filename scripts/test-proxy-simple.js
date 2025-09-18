/**
 * 简单代理测试脚本
 */

async function testProxy() {
    console.log('🔍 测试代理配置...\n');

    try {
        // 测试根路径
        console.log('测试根路径代理...');
        const rootResponse = await fetch('/api/', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        console.log(`状态码: ${rootResponse.status}`);
        const rootData = await rootResponse.text();
        console.log(`响应: ${rootData.substring(0, 100)}...`);
        console.log('✅ 代理工作正常\n');

    } catch (error) {
        console.log(`❌ 代理测试失败: ${error.message}\n`);
    }

    // 测试直接后端连接
    console.log('🔍 测试直接后端连接...');
    try {
        const directResponse = await fetch('http://123.57.174.186:8000/', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        console.log(`后端状态: ${directResponse.status}`);
        const directData = await directResponse.json();
        console.log(`后端响应: ${JSON.stringify(directData).substring(0, 100)}...`);
        console.log('✅ 后端可访问');

    } catch (error) {
        console.log(`❌ 后端连接失败: ${error.message}`);
    }
}

// 在浏览器环境中运行
if (typeof window !== 'undefined') {
    window.testProxy = testProxy;
    console.log('运行 window.testProxy() 来测试代理');
} else {
    // Node.js环境
    testProxy().catch(console.error);
}
