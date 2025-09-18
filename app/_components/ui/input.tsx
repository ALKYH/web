import React from 'react';
import { Input as AntInput, InputProps as AntInputProps, InputRef } from 'antd';
import { cn } from '@/lib/utils';

// 扩展的Input属性
interface InputProps extends Omit<AntInputProps, 'size'> {
  size?: 'small' | 'middle' | 'large'; // Ant Design的size选项
  type?: string; // HTML input type
}

// 获取自定义样式
const getCustomStyles = (className?: string, type?: string) => {
  let customClass = '';
  
  // 保留原有的高度和样式
  customClass += ' !h-9'; // 保持原有高度
  
  // 处理搜索框特殊样式
  if (type === 'search') {
    customClass += ' [&::-webkit-search-cancel-button]:appearance-none [&::-webkit-search-decoration]:appearance-none';
  }
  
  // 保留过渡效果
  customClass += ' transition-all duration-200';
  
  return cn(customClass, className);
};

export const Input = React.forwardRef<InputRef, InputProps>(
  ({ 
    className,
    type,
    size = 'middle',
    ...props 
  }, ref) => {
    const customClassName = getCustomStyles(className, type);
    
    // 处理文件上传类型 - 使用原生input，因为Ant Design的Upload组件API差异太大
    if (type === 'file') {
      return (
        <input
          ref={ref as React.Ref<HTMLInputElement>}
          type="file"
          className={cn(
            // 保留原有的file input样式
            'text-muted-foreground/70 file:border-input file:text-foreground flex h-9 w-full rounded-md border border-input bg-transparent p-0 pr-3 text-sm italic shadow-xs transition-[color,box-shadow] outline-none',
            'file:me-3 file:h-full file:border-0 file:border-r file:border-solid file:bg-transparent file:px-3 file:text-sm file:font-medium file:not-italic',
            'focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px]',
            'disabled:cursor-not-allowed disabled:opacity-50',
            className
          )}
          {...(props as React.InputHTMLAttributes<HTMLInputElement>)}
        />
      );
    }
    
    // 处理搜索类型
    if (type === 'search') {
      return (
        <AntInput.Search
          ref={ref}
          size={size}
          className={customClassName}
          {...props}
        />
      );
    }
    
    // 处理密码类型
    if (type === 'password') {
      return (
        <AntInput.Password
          ref={ref}
          size={size}
          className={customClassName}
          {...props}
        />
      );
    }
    
    // 默认输入框
    return (
      <AntInput
        ref={ref}
        type={type}
        size={size}
        className={customClassName}
        {...props}
      />
    );
  }
);

Input.displayName = 'Input';

export { Input as default };