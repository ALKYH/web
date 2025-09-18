import React from 'react';
import { Divider, DividerProps } from 'antd';
import { cn } from '@/lib/utils';

// 扩展的Separator属性
interface SeparatorProps extends Omit<DividerProps, 'type' | 'orientation'> {
  orientation?: 'horizontal' | 'vertical';
  decorative?: boolean;
  className?: string;
}

export const Separator = React.forwardRef<HTMLDivElement, SeparatorProps>(
  ({ orientation = 'horizontal', className, ...props }, ref) => {
    return (
      <div ref={ref}>
        <Divider
          type={orientation === 'horizontal' ? 'horizontal' : 'vertical'}
          className={cn(
            'shrink-0',
            orientation === 'horizontal' ? 'w-full' : 'h-full',
            className
          )}
          {...props}
        />
      </div>
    );
  }
);

Separator.displayName = 'Separator';
