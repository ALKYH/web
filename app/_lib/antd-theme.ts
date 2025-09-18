import type { ThemeConfig } from 'antd';

// Ant Design主题配置
export const antdTheme: ThemeConfig = {
  token: {
    // 品牌色配置 - 调整为更深的蓝色以提高可读性
    colorPrimary: '#40a9ff', // 基于#bae0ff调整的更深版本，确保文字对比度
    colorPrimaryBg: '#bae0ff', // 保留您的原始品牌色用于背景
    colorPrimaryBorder: '#91d5ff', // 边框色
    
    // 功能色使用Ant Design默认值
    colorSuccess: '#52c41a',
    colorWarning: '#faad14', 
    colorError: '#ff4d4f',
    colorInfo: '#1677ff',
    
    // 中性色使用Ant Design默认值
    colorText: '#000000d9',
    colorTextSecondary: '#00000073',
    colorTextTertiary: '#00000040',
    colorTextQuaternary: '#00000026',
    
    // 字体配置
    fontFamily: 'var(--font-geist-sans), -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    fontFamilyCode: 'var(--font-geist-mono), "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace',
    
    // 尺寸配置 - 中等尺寸
    controlHeight: 32,
    controlHeightSM: 24,
    controlHeightLG: 40,
    
    // 圆角配置 - 8px
    borderRadius: 8,
    borderRadiusLG: 12,
    borderRadiusSM: 6,
    borderRadiusXS: 4,
    
    // 间距配置
    padding: 16,
    paddingLG: 24,
    paddingSM: 12,
    paddingXS: 8,
    paddingXXS: 4,
    
    margin: 16,
    marginLG: 24,
    marginSM: 12,
    marginXS: 8,
    marginXXS: 4,
    
    // 线条配置
    lineWidth: 1,
    lineType: 'solid',
    
    // 阴影配置
    boxShadow: '0 1px 2px 0 rgba(0, 0, 0, 0.03), 0 1px 6px -1px rgba(0, 0, 0, 0.02), 0 2px 4px 0 rgba(0, 0, 0, 0.02)',
    boxShadowSecondary: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
  },
  
  // 组件特定配置
  components: {
    Button: {
      borderRadius: 8,
      controlHeight: 32,
      controlHeightLG: 40,
      controlHeightSM: 24,
      fontWeight: 500,
    },
    
    Card: {
      borderRadius: 12,
      paddingLG: 24,
      headerBg: 'transparent',
    },
    
    Input: {
      borderRadius: 8,
      controlHeight: 32,
      controlHeightLG: 40,
      controlHeightSM: 24,
    },
    
    Select: {
      borderRadius: 8,
      controlHeight: 32,
      controlHeightLG: 40,
      controlHeightSM: 24,
    },
    
    Modal: {
      borderRadius: 12,
      paddingLG: 24,
    },
    
    Dropdown: {
      borderRadius: 8,
    },
    
    Menu: {
      borderRadius: 8,
      itemBorderRadius: 6,
    },
    
    Badge: {
      borderRadius: 10,
    },
    
    Avatar: {
      borderRadius: 8,
    },
    
    Alert: {
      borderRadius: 8,
    },
    
    Divider: {
      margin: 16,
      marginLG: 24,
    },
    
    Skeleton: {
      borderRadius: 8,
    },
    
    Popover: {
      borderRadius: 8,
    },
    
    Tooltip: {
      borderRadius: 6,
    },
  },
  
  // 算法配置 - 暂时只使用默认算法（浅色模式）
  algorithm: undefined,
};

// 导出主题配置
export default antdTheme;
