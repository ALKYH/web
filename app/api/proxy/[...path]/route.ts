import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://123.57.174.186:8000';

/**
 * API代理路由 - 将所有/api/*请求代理到后端服务器
 * 解决跨域问题，统一API入口
 */
type RouteContext = { params?: { path?: string[] } };

function getPathFromContext(context: unknown): string[] {
    const c = context as RouteContext | undefined;
    const p = c?.params?.path;
    return Array.isArray(p) ? p : [];
}
export async function GET(
    request: NextRequest,
    context: unknown
) {
    const path = getPathFromContext(context);
    return handleRequest(request, path, 'GET');
}

export async function POST(
    request: NextRequest,
    context: unknown
) {
    const path = getPathFromContext(context);
    return handleRequest(request, path, 'POST');
}

export async function PUT(
    request: NextRequest,
    context: unknown
) {
    const path = getPathFromContext(context);
    return handleRequest(request, path, 'PUT');
}

export async function DELETE(
    request: NextRequest,
    context: unknown
) {
    const path = getPathFromContext(context);
    return handleRequest(request, path, 'DELETE');
}

export async function OPTIONS(
    request: NextRequest,
    context: unknown
) {
    const path = getPathFromContext(context);
    return handleRequest(request, path, 'OPTIONS');
}

async function handleRequest(
    request: NextRequest,
    path: string[],
    method: string
) {
    try {
        // 构建目标URL
        const pathString = path.join('/');
        const targetUrl = `${BACKEND_URL}/api/${pathString}`;

        // 获取查询参数
        const searchParams = request.nextUrl.searchParams.toString();
        const fullUrl = searchParams ? `${targetUrl}?${searchParams}` : targetUrl;

        // 准备请求头
        const headers: HeadersInit = {
            'Content-Type': 'application/json',
        };

        // 复制认证头
        const authHeader = request.headers.get('authorization');
        if (authHeader) {
            headers['Authorization'] = authHeader;
        }

        // 复制其他重要头
        const contentType = request.headers.get('content-type');
        if (contentType) {
            headers['Content-Type'] = contentType;
        }

        // 准备请求体
        let body: string | undefined;
        if (method !== 'GET' && method !== 'DELETE') {
            try {
                body = await request.text();
            } catch (error) {
                console.error('读取请求体失败:', error);
            }
        }

        // 发送代理请求
        const response = await fetch(fullUrl, {
            method,
            headers,
            body,
        });

        // 获取响应数据
        const responseData = await response.text();

        // 创建响应
        const nextResponse = new NextResponse(responseData, {
            status: response.status,
            statusText: response.statusText,
        });

        // 复制响应头
        response.headers.forEach((value, key) => {
            // 跳过一些可能导致问题的头
            if (!['content-encoding', 'content-length', 'transfer-encoding'].includes(key.toLowerCase())) {
                nextResponse.headers.set(key, value);
            }
        });

        // 添加CORS头
        nextResponse.headers.set('Access-Control-Allow-Origin', '*');
        nextResponse.headers.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
        nextResponse.headers.set('Access-Control-Allow-Headers', 'Content-Type, Authorization');

        return nextResponse;

    } catch (error) {
        console.error('代理请求失败:', error);

        return NextResponse.json(
            {
                error: '代理请求失败',
                message: error instanceof Error ? error.message : '未知错误',
                details: process.env.NODE_ENV === 'development' ? error : undefined
            },
            { status: 500 }
        );
    }
}
