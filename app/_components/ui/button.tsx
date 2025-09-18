import React from 'react';
import { Button as AntButton } from 'antd';
import type { ButtonProps as AntButtonProps } from 'antd';
import { cn } from '@/lib/utils';

// Shadcn/ui Button变体类型
type ShadcnVariant = 'default' | 'destructive' | 'outline' | 'secondary' | 'ghost' | 'link';
type ShadcnSize = 'default' | 'sm' | 'lg' | 'icon';

// 扩展的Button属性
interface ButtonProps extends Omit<AntButtonProps, 'type' | 'size' | 'danger' | 'variant'> {
  variant?: ShadcnVariant;
  size?: ShadcnSize;
  asChild?: boolean; // 兼容Shadcn/ui的asChild属性
  type?: 'button' | 'submit' | 'reset'; // HTML button type
}

// 变体映射函数
const getAntButtonType = (variant: ShadcnVariant): AntButtonProps['type'] => {
  const variantMap: Record<ShadcnVariant, AntButtonProps['type']> = {
    'default': 'primary',
    'destructive': 'primary',
    'outline': 'default',
    'secondary': 'default',
    'ghost': 'text',
    'link': 'link'
  };
  return variantMap[variant];
};

// 尺寸映射函数
const getAntButtonSize = (size: ShadcnSize): AntButtonProps['size'] => {
  const sizeMap: Record<ShadcnSize, AntButtonProps['size']> = {
    'sm': 'small',
    'default': 'middle',
    'lg': 'large',
    'icon': 'middle' // icon按钮使用默认尺寸
  };
  return sizeMap[size];
};

// 获取自定义样式
const getCustomStyles = (variant: ShadcnVariant, size: ShadcnSize, className?: string) => {
  let customClass = '';
  
  // 处理secondary变体的特殊样式
  if (variant === 'secondary') {
    customClass += ' !bg-secondary !text-secondary-foreground !border-transparent hover:!bg-secondary/90';
  }
  
  // 处理icon尺寸的特殊样式
  if (size === 'icon') {
    customClass += ' !w-9 !h-9 !min-w-0 !p-0';
  }
  
  // 保留过渡效果
  customClass += ' transition-all duration-200';
  
  return cn(customClass, className);
};

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ 
    variant = 'default', 
    size = 'default', 
    className,
    children,
    asChild = false,
    type: htmlType,
    ...props 
  }, ref) => {
    // 如果使用asChild，我们需要特殊处理（暂时忽略，因为Ant Design不支持）
    if (asChild) {
      console.warn('Button: asChild prop is not supported with Ant Design. Rendering as normal button.');
    }
    
    const antType = getAntButtonType(variant);
    const antSize = getAntButtonSize(size);
    const isDanger = variant === 'destructive';
    const customClassName = getCustomStyles(variant, size, className);
    
    return (
      <AntButton
        ref={ref}
        type={antType}
        size={antSize}
        danger={isDanger}
        className={customClassName}
        htmlType={htmlType}
        {...props}
      >
        {children}
      </AntButton>
    );
  }
);

Button.displayName = 'Button';

// 为了兼容性，导出buttonVariants（虽然不再使用）
export const buttonVariants = () => '';
