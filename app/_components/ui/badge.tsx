import React from 'react';
import { Badge as AntBadge, BadgeProps as AntBadgeProps } from 'antd';
import { cn } from '@/lib/utils';

// Shadcn/ui Badge变体类型
type ShadcnVariant = 'default' | 'secondary' | 'destructive' | 'outline';

// 扩展的Badge属性
interface BadgeProps extends Omit<AntBadgeProps, 'status' | 'color'> {
  variant?: ShadcnVariant;
  asChild?: boolean;
  className?: string;
}

// 变体映射函数
const getAntBadgeColor = (variant: ShadcnVariant): string => {
  const variantMap: Record<ShadcnVariant, string> = {
    'default': 'blue',
    'secondary': 'default',
    'destructive': 'red',
    'outline': 'default'
  };
  return variantMap[variant];
};

// 获取自定义样式
const getCustomStyles = (variant: ShadcnVariant, className?: string) => {
  let customClass = '';
  
  // 处理outline变体的特殊样式
  if (variant === 'outline') {
    customClass += ' !border-current !bg-transparent !text-foreground';
  }
  
  // 处理secondary变体
  if (variant === 'secondary') {
    customClass += ' !bg-secondary !text-secondary-foreground !border-transparent';
  }
  
  // 保留过渡效果
  customClass += ' transition-all duration-200';
  
  return cn(customClass, className);
};

export const Badge = React.forwardRef<HTMLSpanElement, BadgeProps>(
  ({ 
    variant = 'default', 
    className,
    children,
    asChild = false,
    ...props 
  }, ref) => {
    // asChild暂时不支持，因为Ant Design Badge结构不同
    if (asChild) {
      console.warn('Badge: asChild prop is not supported with Ant Design Badge.');
    }
    
    const color = getAntBadgeColor(variant);
    const customClassName = getCustomStyles(variant, className);
    
    // 如果有children，使用Badge.Ribbon或直接显示文本
    if (children) {
      return (
        <span
          ref={ref}
          className={cn(
            'inline-flex items-center justify-center rounded-full px-1.5 text-xs font-medium whitespace-nowrap shrink-0',
            variant === 'default' && 'bg-primary text-primary-foreground',
            variant === 'secondary' && 'bg-secondary text-secondary-foreground',
            variant === 'destructive' && 'bg-destructive text-white',
            variant === 'outline' && 'border border-current bg-transparent text-foreground',
            customClassName
          )}
          {...props}
        >
          {children}
        </span>
      );
    }
    
    // 没有children时使用Ant Design的Badge组件
    return (
      <AntBadge
        ref={ref}
        color={color}
        className={customClassName}
        {...props}
      />
    );
  }
);

Badge.displayName = 'Badge';

// 为了兼容性，导出badgeVariants（虽然不再使用）
export const badgeVariants = () => '';
