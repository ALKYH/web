// AI智能体 v2.0 API客户端
import { API_CONFIG, getFullUrl } from './api-config';

// Helper function to get auth token
const getAuthToken = (): string => {
  if (typeof window === 'undefined') return '';

  try {
    const authStorage = localStorage.getItem('auth-storage');
    if (authStorage) {
      const parsedAuth = JSON.parse(authStorage);
      if (parsedAuth?.state?.token) {
        return parsedAuth.state.token;
      }
    }
  } catch (error) {
    console.warn('Failed to parse auth storage:', error);
  }

  // Fallback to old localStorage key
  return localStorage.getItem('auth_token') || '';
};

// API request wrapper with automatic token handling
const apiRequest = async (
  url: string,
  options: RequestInit = {}
): Promise<Response> => {
  const token = getAuthToken();

  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
    ...(token && { Authorization: `Bearer ${token}` })
  };

  const response = await fetch(url, {
    ...options,
    headers
  });

  return response;
};

// AI智能体相关接口类型定义
export interface ChatRequest {
  message: string;
  session_id?: string | null;
}

export interface AutoChatRequest {
  request: ChatRequest;
  agent_type?: 'study_planner' | 'study_consultant';
}

export interface ChatResponse {
  response: string;
  agent_type: string;
  version: string;
  user_id: string;
  session_id: string | null;
}

export interface SystemStatusResponse {
  is_initialized: boolean;
  version: string;
  available_agents: string[];
  external_services: Record<string, boolean>;
}

export interface SystemInfoResponse {
  name: string;
  version: string;
  author: string;
  agent_types: string[];
  modules: string[];
  features: string[];
  tools: string[];
}

export interface HealthCheckResponse {
  // 健康检查返回null表示健康
}

export interface ApiError {
  detail: string;
  code?: string;
  timestamp?: string;
}

// AI智能体API客户端类
class AIAgentAPI {
  /**
   * 与留学规划师对话
   * @param request 对话请求参数
   * @param stream 是否启用流式响应，默认false
   * @returns 对话响应
   */
  async chatWithPlanner(request: ChatRequest, stream: boolean = false): Promise<ChatResponse> {
    const url = new URL(getFullUrl(API_CONFIG.ENDPOINTS.AGENTS.PLANNER_CHAT));
    if (stream) {
      url.searchParams.set('stream', 'true');
    }

    const response = await apiRequest(url.toString(), {
      method: 'POST',
      body: JSON.stringify(request)
    });

    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.detail || '与留学规划师对话失败');
    }

    return response.json();
  }

  /**
   * 与留学咨询师对话
   * @param request 对话请求参数
   * @param stream 是否启用流式响应，默认false
   * @returns 对话响应
   */
  async chatWithConsultant(request: ChatRequest, stream: boolean = false): Promise<ChatResponse> {
    const url = new URL(getFullUrl(API_CONFIG.ENDPOINTS.AGENTS.CONSULTANT_CHAT));
    if (stream) {
      url.searchParams.set('stream', 'true');
    }

    const response = await apiRequest(url.toString(), {
      method: 'POST',
      body: JSON.stringify(request)
    });

    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.detail || '与留学咨询师对话失败');
    }

    return response.json();
  }

  /**
   * 智能选择合适的智能体进行对话（推荐使用）
   * @param request 自动对话请求参数
   * @param stream 是否启用流式响应，默认false
   * @returns 对话响应
   */
  async chatWithAutoAgent(request: AutoChatRequest, stream: boolean = false): Promise<ChatResponse> {
    const url = new URL(getFullUrl(API_CONFIG.ENDPOINTS.AGENTS.AUTO_CHAT));
    if (stream) {
      url.searchParams.set('stream', 'true');
    }

    const response = await apiRequest(url.toString(), {
      method: 'POST',
      body: JSON.stringify(request)
    });

    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.detail || 'AI智能体对话失败');
    }

    return response.json();
  }

  /**
   * 流式对话方法 - 支持实时响应
   * @param request 自动对话请求参数
   * @param onChunk 接收每个数据块的回调函数
   * @param onComplete 对话完成的回调函数
   * @param onError 错误的回调函数
   * @returns AbortController 用于取消请求
   */
  async chatWithAutoAgentStream(
    request: AutoChatRequest,
    onChunk: (chunk: string) => void,
    onComplete: (response: ChatResponse) => void,
    onError: (error: Error) => void
  ): Promise<AbortController> {
    const controller = new AbortController();
    const url = new URL(getFullUrl(API_CONFIG.ENDPOINTS.AGENTS.AUTO_CHAT));
    url.searchParams.set('stream', 'true');

    try {
      const response = await apiRequest(url.toString(), {
        method: 'POST',
        body: JSON.stringify(request),
        signal: controller.signal
      });

      if (!response.ok) {
        const error: ApiError = await response.json();
        throw new Error(error.detail || 'AI智能体对话失败');
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('无法获取响应流');
      }

      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');

        // 处理完整的行
        for (let i = 0; i < lines.length - 1; i++) {
          const line = lines[i].trim();
          if (line.startsWith('data: ')) {
            const data = line.substring(6);
            if (data === '[DONE]') {
              // 流结束
              break;
            }
            try {
              const chunk = JSON.parse(data);
              if (chunk.response) {
                onChunk(chunk.response);
              }
            } catch (e) {
              console.warn('解析流数据失败:', e);
            }
          }
        }

        buffer = lines[lines.length - 1];
      }

      // 处理剩余缓冲区
      if (buffer.trim()) {
        try {
          const finalResponse: ChatResponse = JSON.parse(buffer);
          onComplete(finalResponse);
        } catch (e) {
          console.warn('解析最终响应失败:', e);
        }
      }

    } catch (error) {
      if (error instanceof Error && error.name !== 'AbortError') {
        onError(error);
      }
    }

    return controller;
  }

  /**
   * 兼容旧版规划师调用接口（已弃用，请使用 chatWithPlanner）
   * @deprecated 使用 chatWithPlanner 替代
   */
  async invokePlanner(request: ChatRequest): Promise<ChatResponse> {
    console.warn('invokePlanner 方法已弃用，请使用 chatWithPlanner 替代');
    return this.chatWithPlanner(request);
  }

  /**
   * 获取AI智能体系统状态
   */
  async getSystemStatus(): Promise<SystemStatusResponse> {
    const response = await apiRequest(
      getFullUrl(API_CONFIG.ENDPOINTS.AGENTS.STATUS)
    );

    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.detail || '获取系统状态失败');
    }

    return response.json();
  }

  /**
   * 获取AI智能体架构信息
   */
  async getSystemInfo(): Promise<SystemInfoResponse> {
    const response = await apiRequest(
      getFullUrl(API_CONFIG.ENDPOINTS.AGENTS.INFO)
    );

    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.detail || '获取架构信息失败');
    }

    return response.json();
  }

  /**
   * AI智能体系统健康检查
   */
  async healthCheck(): Promise<void> {
    const response = await apiRequest(
      getFullUrl(API_CONFIG.ENDPOINTS.AGENTS.HEALTH)
    );

    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.detail || '健康检查失败');
    }

    // 健康检查成功返回null，无需解析响应体
  }
}

// 导出AI智能体API实例
export const aiAgentAPI = new AIAgentAPI();
