import React from 'react';
import { Skeleton as AntSkeleton, SkeletonProps as AntSkeletonProps } from 'antd';
import { cn } from '@/lib/utils';

// 扩展的Skeleton属性
interface SkeletonProps extends AntSkeletonProps {
  className?: string;
}

export const Skeleton = React.forwardRef<HTMLDivElement, SkeletonProps>(
  ({ className, children, ...props }, ref) => {
    // 如果有children，使用简单的div来保持兼容性
    if (children || className) {
      return (
        <div
          ref={ref}
          className={cn('animate-pulse rounded-md bg-muted', className)}
          {...(props as React.HTMLAttributes<HTMLDivElement>)}
        >
          {children}
        </div>
      );
    }
    
    // 否则使用Ant Design的Skeleton
    return (
      <AntSkeleton
        {...props}
      />
    );
  }
);

Skeleton.displayName = 'Skeleton';
