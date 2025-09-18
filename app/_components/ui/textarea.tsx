import React from 'react';
import { Input } from 'antd';
import type { TextAreaProps as AntTextAreaProps, TextAreaRef } from 'antd/es/input/TextArea';
import { cn } from '@/lib/utils';

const { TextArea: AntTextArea } = Input;

// 扩展的Textarea属性
interface TextareaProps extends AntTextAreaProps {
  className?: string;
}

// 获取自定义样式
const getCustomStyles = (className?: string) => {
  let customClass = '';
  
  // 保留原有的最小高度
  customClass += ' !min-h-[4.875rem]'; // min-h-19.5 = 78px = 4.875rem
  
  // 保留过渡效果
  customClass += ' transition-all duration-200';
  
  return cn(customClass, className);
};

export const Textarea = React.forwardRef<TextAreaRef, TextareaProps>(
  ({ className, ...props }, ref) => {
    const customClassName = getCustomStyles(className);
    
    return (
      <AntTextArea
        ref={ref}
        className={customClassName}
        {...props}
      />
    );
  }
);

Textarea.displayName = 'Textarea';
