import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  images: {
    domains: ['example.com', 'web-4w0h.onrender.com', 'localhost'],
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**'
      },
      {
        protocol: 'http',
        hostname: 'localhost',
        port: '8000'
      }
    ]
  },

  // 开发环境代理配置
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://123.57.174.186:8000/api/:path*' // 代理到后端API
      }
    ];
  },

  // 生产环境代理配置（Vercel）
  async headers() {
    return [
      {
        source: '/api/:path*',
        headers: [
          {
            key: 'Access-Control-Allow-Origin',
            value: '*'
          },
          {
            key: 'Access-Control-Allow-Methods',
            value: 'GET, POST, PUT, DELETE, OPTIONS'
          },
          {
            key: 'Access-Control-Allow-Headers',
            value: 'Content-Type, Authorization'
          }
        ]
      }
    ];
  }
};

export default nextConfig;
