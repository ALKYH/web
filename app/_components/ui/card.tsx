import React from 'react';
import { Card as AntCard, CardProps as AntCardProps } from 'antd';
import { cn } from '@/lib/utils';

// 扩展的Card属性
interface CardProps extends Omit<AntCardProps, 'size'> {
  size?: 'default' | 'small';
}

// 主Card组件
export const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ className, children, size = 'default', ...props }, ref) => {
    return (
      <AntCard
        ref={ref}
        size={size}
        className={cn('shadow-sm', className)}
        {...props}
      >
        {children}
      </AntCard>
    );
  }
);

Card.displayName = 'Card';

// CardHeader组件 - 映射到Ant Design Card的title和extra
interface CardHeaderProps extends React.HTMLAttributes<HTMLDivElement> {
  children?: React.ReactNode;
}

export const CardHeader = React.forwardRef<HTMLDivElement, CardHeaderProps>(
  ({ className, children, ...props }, ref) => {
    // CardHeader通常包含CardTitle和CardAction，这些会被父Card组件处理
    // 这里返回一个容器用于兼容性
    return (
      <div
        ref={ref}
        className={cn('card-header-wrapper', className)}
        {...props}
      >
        {children}
      </div>
    );
  }
);

CardHeader.displayName = 'CardHeader';

// CardTitle组件
interface CardTitleProps extends React.HTMLAttributes<HTMLDivElement> {
  children?: React.ReactNode;
}

export const CardTitle = React.forwardRef<HTMLDivElement, CardTitleProps>(
  ({ className, children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn('font-semibold leading-none', className)}
        {...props}
      >
        {children}
      </div>
    );
  }
);

CardTitle.displayName = 'CardTitle';

// CardDescription组件
interface CardDescriptionProps extends React.HTMLAttributes<HTMLDivElement> {
  children?: React.ReactNode;
}

export const CardDescription = React.forwardRef<HTMLDivElement, CardDescriptionProps>(
  ({ className, children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn('text-muted-foreground text-sm', className)}
        {...props}
      >
        {children}
      </div>
    );
  }
);

CardDescription.displayName = 'CardDescription';

// CardAction组件
interface CardActionProps extends React.HTMLAttributes<HTMLDivElement> {
  children?: React.ReactNode;
}

export const CardAction = React.forwardRef<HTMLDivElement, CardActionProps>(
  ({ className, children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn('card-action', className)}
        {...props}
      >
        {children}
      </div>
    );
  }
);

CardAction.displayName = 'CardAction';

// CardContent组件
interface CardContentProps extends React.HTMLAttributes<HTMLDivElement> {
  children?: React.ReactNode;
}

export const CardContent = React.forwardRef<HTMLDivElement, CardContentProps>(
  ({ className, children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn('card-content', className)}
        {...props}
      >
        {children}
      </div>
    );
  }
);

CardContent.displayName = 'CardContent';

// CardFooter组件
interface CardFooterProps extends React.HTMLAttributes<HTMLDivElement> {
  children?: React.ReactNode;
}

export const CardFooter = React.forwardRef<HTMLDivElement, CardFooterProps>(
  ({ className, children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn('flex items-center card-footer', className)}
        {...props}
      >
        {children}
      </div>
    );
  }
);

CardFooter.displayName = 'CardFooter';
