# 🏗️ PeerPortal 前端架构 Mermaid 图表

## 1. 整体分层架构

```mermaid
graph TB
    subgraph "表现层 (Presentation Layer)"
        P1[页面路由 Pages]
        P2[用户界面 UI]
        P3[用户交互 Interactions]
    end
    
    subgraph "组件层 (Component Layer)"
        C1[UI组件库 ui/]
        C2[基础组件 base/]
        C3[业务组件 auth/, profile/]
        C4[功能组件 first-visit/, modal/]
    end
    
    subgraph "状态层 (State Layer)"
        S1[Zustand Store]
        S2[URL状态 nuqs]
        S3[本地存储 localStorage]
    end
    
    subgraph "服务层 (Service Layer)"
        SV1[API客户端 api.ts]
        SV2[认证服务 auth.ts]
        SV3[文件上传 file-upload-api.ts]
        SV4[AI服务 ai-agent-api.ts]
    end
    
    subgraph "工具层 (Utility Layer)"
        U1[通用工具 utils.ts]
        U2[配置管理 api-config.ts]
        U3[自定义Hooks]
    end
    
    P1 --> C1
    P2 --> C2
    P3 --> C3
    C1 --> S1
    C2 --> S2
    C3 --> SV1
    C4 --> SV2
    SV1 --> U1
    SV2 --> U2
    S1 --> S3
```

## 2. Next.js App Router 目录结构

```mermaid
graph TD
    subgraph "app/ (根目录)"
        A1[layout.tsx - 根布局]
        A2[page.tsx - 首页]
        A3[globals.css - 全局样式]
    end
    
    subgraph "路由分组"
        B1["(homepage)/ - 主页分组"]
        B2["(auth)/ - 认证分组"]
        B3[tutor/ - 导师功能]
        B4[ai-advisor/ - AI助手]
        B5[chat/ - 聊天功能]
        B6[profile/ - 用户资料]
    end
    
    subgraph "组件目录"
        C1[_components/ui/ - UI组件]
        C2[_components/base/ - 基础组件]
        C3[_components/auth/ - 认证组件]
        C4[_components/profile/ - 资料组件]
    end
    
    subgraph "功能目录"
        D1[_store/ - 状态管理]
        D2[_lib/ - 工具库]
        D3[_hooks/ - 自定义Hook]
        D4[_data/ - 静态数据]
    end
    
    A1 --> B1
    B1 --> B2
    B1 --> B3
    A1 --> B4
    A1 --> B5
    A1 --> B6
    
    B2 --> C3
    B6 --> C4
    C3 --> C1
    C4 --> C2
    
    C1 --> D1
    C2 --> D2
    D2 --> D3
    D3 --> D4
```

## 3. 技术栈组成架构

```mermaid
mindmap
  root((前端技术栈))
    核心框架
      Next.js 15.5.3
        App Router
        Turbopack
        SSR/SSG
      React 19.1.0
        Server Components
        Client Components
        Concurrent Mode
      TypeScript 5
        严格类型检查
        路径别名
        增量编译
    
    UI系统
      Tailwind CSS 4
        原子化CSS
        响应式设计
        深色模式
      Radix UI
        无障碍组件
        键盘导航
        屏幕阅读器
      Shadcn/ui
        设计系统
        组件变体
        New York风格
    
    状态管理
      Zustand 5.0.6
        轻量级Store
        持久化存储
        类型安全
      nuqs 2.4.3
        URL状态同步
        Next.js集成
        类型推断
    
    AI集成
      Vercel AI SDK
        流式响应
        多模型支持
        React集成
      OpenAI集成
        GPT模型
        嵌入向量
        函数调用
    
    开发工具
      ESLint 9
        代码检查
        Next.js规则
        TypeScript支持
      Prettier
        代码格式化
        统一风格
        自动修复
```

## 4. 数据流架构

```mermaid
sequenceDiagram
    participant U as 用户界面
    participant C as React组件
    participant S as Zustand Store
    participant A as API客户端
    participant B as 后端API
    participant L as localStorage
    
    Note over U,L: 用户操作流程
    
    U->>C: 用户交互 (点击/输入)
    C->>S: 触发状态更新
    S->>A: 调用API服务
    A->>B: 发送HTTP请求
    B-->>A: 返回响应数据
    A-->>S: 更新应用状态
    S-->>C: 通知组件更新
    C-->>U: 重新渲染界面
    
    Note over S,L: 状态持久化
    S->>L: 持久化关键状态
    L-->>S: 应用启动时恢复状态
    
    Note over C,S: 状态订阅
    C->>S: 订阅状态变化
    S-->>C: 状态变化通知
```

## 5. 组件架构层级

```mermaid
graph TB
    subgraph "原子级组件 (Atoms)"
        A1[Button 按钮]
        A2[Input 输入框]
        A3[Avatar 头像]
        A4[Badge 徽章]
    end
    
    subgraph "分子级组件 (Molecules)"
        M1[SearchField 搜索框]
        M2[FilterButton 筛选按钮]
        M3[ClickableAvatar 可点击头像]
    end
    
    subgraph "有机体组件 (Organisms)"
        O1[Navbar 导航栏]
        O2[Footer 页脚]
        O3[TutorFilterSidebar 筛选侧边栏]
        O4[EditProfileDialog 编辑资料对话框]
    end
    
    subgraph "模板组件 (Templates)"
        T1[AuthLayout 认证布局]
        T2[HomePage 主页模板]
        T3[ProfilePage 资料页模板]
    end
    
    subgraph "页面组件 (Pages)"
        P1[LoginPage 登录页]
        P2[TutorPage 导师页]
        P3[AIAdvisorPage AI助手页]
        P4[ChatPage 聊天页]
    end
    
    A1 --> M1
    A2 --> M1
    A3 --> M3
    A4 --> M3
    
    M1 --> O3
    M2 --> O3
    M3 --> O1
    
    O1 --> T1
    O2 --> T1
    O3 --> T2
    O4 --> T3
    
    T1 --> P1
    T2 --> P2
    T3 --> P3
    T1 --> P4
```

## 6. 路由架构

```mermaid
graph LR
    subgraph "根路由 /"
        R1[layout.tsx - 全局布局]
        R2[page.tsx - 首页]
    end
    
    subgraph "分组路由 (homepage)"
        H1[page.tsx - 主页内容]
        
        subgraph "认证路由 (auth)"
            A1[layout.tsx - 认证布局]
            A2[login/page.tsx - 登录]
            A3[signup/page.tsx - 注册]
        end
    end
    
    subgraph "功能路由"
        F1[tutor/page.tsx - 导师列表]
        F2[tutor/[id]/page.tsx - 导师详情]
        F3[ai-advisor/page.tsx - AI助手]
        F4[chat/page.tsx - 聊天]
        F5[profile/page.tsx - 用户资料]
        F6[contact/page.tsx - 联系我们]
    end
    
    R1 --> H1
    R1 --> A1
    A1 --> A2
    A1 --> A3
    R1 --> F1
    F1 --> F2
    R1 --> F3
    R1 --> F4
    R1 --> F5
    R1 --> F6
```

## 7. 状态管理架构

```mermaid
graph TD
    subgraph "Zustand Store"
        Z1[AuthStore - 认证状态]
        Z2[UserStore - 用户信息]
        Z3[UIStore - 界面状态]
    end
    
    subgraph "持久化存储"
        P1[localStorage - 本地存储]
        P2[sessionStorage - 会话存储]
    end
    
    subgraph "URL状态"
        U1[nuqs - 查询参数]
        U2[Next.js Router - 路由状态]
    end
    
    subgraph "组件状态"
        C1[useState - 本地状态]
        C2[useEffect - 副作用]
        C3[自定义Hooks]
    end
    
    Z1 <--> P1
    Z2 <--> P1
    Z3 <--> P2
    
    U1 <--> Z3
    U2 <--> Z1
    
    C1 --> Z1
    C2 --> Z2
    C3 --> Z3
```

## 8. API服务架构

```mermaid
graph TB
    subgraph "API配置层"
        AC1[api-config.ts - 端点配置]
        AC2[环境变量配置]
    end
    
    subgraph "API客户端层"
        API1[api.ts - 通用API客户端]
        API2[auth.ts - 认证API]
        API3[ai-agent-api.ts - AI服务API]
        API4[matching-api.ts - 匹配API]
        API5[file-upload-api.ts - 文件上传API]
    end
    
    subgraph "后端服务"
        BE1[FastAPI - 认证服务]
        BE2[FastAPI - AI智能体]
        BE3[FastAPI - 用户管理]
        BE4[FastAPI - 匹配系统]
        BE5[FastAPI - 文件服务]
    end
    
    AC1 --> API1
    AC2 --> API1
    
    API1 --> BE1
    API2 --> BE1
    API3 --> BE2
    API4 --> BE4
    API5 --> BE5
    
    BE1 --> BE3
    BE2 --> BE3
    BE4 --> BE3
```

## 9. 性能优化架构

```mermaid
graph TB
    subgraph "构建优化"
        B1[Turbopack - 快速构建]
        B2[代码分割 - 按路由分割]
        B3[Tree Shaking - 死代码消除]
    end
    
    subgraph "渲染优化"
        R1[Server Components - 服务端渲染]
        R2[Client Components - 客户端渲染]
        R3[Streaming - 流式渲染]
    end
    
    subgraph "缓存策略"
        C1[Next.js缓存 - 页面缓存]
        C2[浏览器缓存 - 静态资源]
        C3[状态缓存 - Zustand持久化]
    end
    
    subgraph "加载优化"
        L1[懒加载 - 组件懒加载]
        L2[预加载 - 关键资源预加载]
        L3[图片优化 - Next.js Image]
    end
    
    B1 --> R1
    B2 --> R2
    B3 --> R3
    
    R1 --> C1
    R2 --> C2
    R3 --> C3
    
    C1 --> L1
    C2 --> L2
    C3 --> L3
```

## 📊 架构特点总结

### ✅ 优势
- **现代化**: 使用最新版本的React和Next.js
- **类型安全**: 100% TypeScript覆盖
- **模块化**: 清晰的目录结构和组件分层
- **可维护**: 职责分离，易于扩展
- **性能优化**: 多层次的性能优化策略

### 🎯 设计原则
- **分层架构**: 明确的层级划分
- **组件化**: 可复用的组件设计
- **状态集中**: 统一的状态管理
- **类型安全**: 严格的TypeScript约束
- **用户体验**: 响应式和无障碍设计

### 🚀 技术亮点
- **App Router**: Next.js 13+的新路由系统
- **Server Components**: 服务端组件优化
- **Zustand**: 轻量级状态管理
- **Tailwind CSS**: 原子化CSS框架
- **AI集成**: 完整的AI功能支持
