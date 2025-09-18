/**
 * @file API配置，根据后端 openapi.json (2025-09-18) 自动生成和简化
 * @description 所有端点路径都是完整的，代理配置在 next.config.ts 中
 */
export const API_CONFIG = {
  // BASE_URL留空，因为端点路径已完整
  BASE_URL: '',

  ENDPOINTS: {
    // 身份认证 (Auth)
    AUTH: {
      LOGIN: '/api/v1/auth/login', // POST, 登录获取Token
      REFRESH: '/api/v1/auth/refresh_token', // POST, 刷新Token
      LOGOUT: '/api/v1/auth/logout' // POST, 登出
    },

    // 用户管理 (Users)
    USERS: {
      REGISTER: '/api/v1/users/register', // POST, 用户注册
      ME: '/api/v1/users/me', // GET, 获取当前用户信息
      UPDATE_ME: '/api/v1/users/me', // PUT, 更新当前用户信息
      DELETE_ME: '/api/v1/users/me', // DELETE, 删除当前用户
      GET_PROFILE: '/api/v1/users/me/profile', // GET, 获取用户资料
      UPDATE_PROFILE: '/api/v1/users/me/profile' // PUT, 更新用户资料
    },

    // 文件上传 (Files)
    FILES: {
      UPLOAD_AVATAR: '/api/v1/files/upload/avatar', // POST, 上传头像
      UPLOAD_DOCUMENT: '/api/v1/files/upload/document', // POST, 上传文档
      UPLOAD_MULTIPLE: '/api/v1/files/upload/multiple', // POST, 批量上传
      DELETE: (fileId: string) => `/api/v1/files/${fileId}` // DELETE, 删除文件
    },

    // 智能匹配 (Matching)
    MATCHING: {
      RECOMMEND: '/api/v1/matching/recommend', // POST, 获取导师推荐
      SEARCH_MENTORS: '/api/v1/matching/search' // GET, 搜索导师
    },

    // 导师与学徒 (Mentorship)
    MENTORSHIP: {
      CREATE: '/api/v1/mentorships', // POST, 创建指导关系
      GET_ALL: '/api/v1/mentorships', // GET, 获取所有指导关系
      GET: (id: string) => `/api/v1/mentorships/${id}`, // GET, 获取单个指导关系
      UPDATE: (id: string) => `/api/v1/mentorships/${id}`, // PUT, 更新指导关系
      GET_SESSIONS: (id: string) => `/api/v1/mentorships/${id}/sessions` // GET, 获取关系下的所有会话
    },

    // 会话管理 (Sessions)
    SESSIONS: {
      GET: (id: string) => `/api/v1/sessions/${id}`, // GET, 获取会话详情
      UPDATE: (id: string) => `/api/v1/sessions/${id}`, // PUT, 更新会话
      GET_FEEDBACK: (id: string) => `/api/v1/sessions/${id}/feedback`, // GET, 获取会话反馈
      CREATE_FEEDBACK: (id: string) => `/api/v1/sessions/${id}/feedback`, // POST, 创建会话反馈
      GET_SUMMARY: (id: string) => `/api/v1/sessions/${id}/summary` // GET, 获取会话总结
    },

    // 技能与分类 (Skills)
    SKILLS: {
      GET_CATEGORIES: '/api/v1/skills/categories', // GET, 获取所有技能分类
      CREATE_CATEGORY: '/api/v1/skills/categories', // POST, 创建技能分类
      UPDATE_CATEGORY: (id: string) => `/api/v1/skills/categories/${id}`, // PUT, 更新技能分类
      DELETE_CATEGORY: (id: string) => `/api/v1/skills/categories/${id}`, // DELETE, 删除技能分类
      GET_MENTOR_SKILLS: '/api/v1/skills/mentors/skills', // GET, 获取导师的所有技能
      ADD_MENTOR_SKILL: '/api/v1/skills/mentors/skills', // POST, 为导师添加技能
      UPDATE_MENTOR_SKILL: (id: string) => `/api/v1/skills/mentors/skills/${id}`, // PUT, 更新导师技能
      DELETE_MENTOR_SKILL: (id: string) => `/api/v1/skills/mentors/skills/${id}`, // DELETE, 删除导师技能
      SEARCH: '/api/v1/skills/search' // GET, 搜索技能
    },

    // 交易与钱包 (Transactions)
    TRANSACTIONS: {
      LIST_ORDERS: '/api/v1/transactions/orders', // GET, 获取订单列表
      CREATE_ORDER: '/api/v1/transactions/orders', // POST, 创建订单
      GET_ORDER: (id: string) => `/api/v1/transactions/orders/${id}`, // GET, 获取订单详情
      UPDATE_ORDER: (id: string) => `/api/v1/transactions/orders/${id}`, // PUT, 更新订单
      CANCEL_ORDER: (id: string) => `/api/v1/transactions/orders/${id}`, // DELETE, 取消订单
      PAY_ORDER: (id: string) => `/api/v1/transactions/orders/${id}/pay`, // POST, 支付订单
      GET_WALLET: '/api/v1/transactions/wallet', // GET, 获取钱包信息
      UPDATE_WALLET: '/api/v1/transactions/wallet', // PUT, 更新钱包
      CREATE_WALLET: '/api/v1/transactions/wallet', // POST, 创建钱包
      RECHARGE_WALLET: '/api/v1/transactions/wallet/recharge', // POST, 充值
      WITHDRAW_WALLET: '/api/v1/transactions/wallet/withdraw', // POST, 提现
      LIST_TRANSACTIONS: '/api/v1/transactions', // GET, 获取交易记录
      CREATE_TRANSACTION: '/api/v1/transactions/transactions', // POST, 创建交易
      GET_TRANSACTION: (id: string) => `/api/v1/transactions/transactions/${id}`, // GET, 获取交易详情
      GET_FINANCIAL_STATS: '/api/v1/transactions/stats' // GET, 获取财务统计
    },

    // 智能体 (Agents)
    AGENTS: {
      STATUS: '/api/v1/agents/status', // GET, 获取系统状态
      INFO: '/api/v1/agents/info', // GET, 获取架构信息
      PLANNER_CHAT: '/api/v1/agents/planner/chat', // POST, 与规划师对话
      CONSULTANT_CHAT: '/api/v1/agents/consultant/chat', // POST, 与顾问对话
      AUTO_CHAT: '/api/v1/agents/chat', // POST, 自动路由对话
      HEALTH: '/api/v1/agents/health' // GET, 健康检查
    }
  }
} as const;

/**
 * 构造完整的API请求URL
 * @param endpoint - API_CONFIG.ENDPOINTS中的端点路径
 * @returns 完整的请求URL
 */
export const getFullUrl = (endpoint: string): string => {
  return `${API_CONFIG.BASE_URL}${endpoint}`;
};
