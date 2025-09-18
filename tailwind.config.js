/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['var(--font-geist-sans)', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        mono: ['var(--font-geist-mono)', 'ui-monospace', 'SFMono-Regular', 'monospace'],
      },
      colors: {
        // 保留一些自定义颜色，与Ant Design协调使用
        'brand-primary': '#bae0ff',
      },
    },
  },
  plugins: [],
  // 重要：避免Tailwind样式与Ant Design冲突
  corePlugins: {
    preflight: false, // 禁用Tailwind的CSS重置，让Ant Design的reset.css生效
  },
};
