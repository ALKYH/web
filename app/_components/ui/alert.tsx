import React from 'react';
import { Alert as AntAlert, AlertProps as AntAlertProps } from 'antd';
import { cn } from '@/lib/utils';

// Shadcn/ui Alert变体类型
type ShadcnVariant = 'default' | 'destructive';

// 扩展的Alert属性
interface AlertProps extends Omit<AntAlertProps, 'type'> {
  variant?: ShadcnVariant;
  className?: string;
  children?: React.ReactNode;
}

// 变体映射函数
const getAntAlertType = (variant: ShadcnVariant): AntAlertProps['type'] => {
  const variantMap: Record<ShadcnVariant, AntAlertProps['type']> = {
    'default': 'info',
    'destructive': 'error'
  };
  return variantMap[variant];
};

// 主Alert组件
export const Alert = React.forwardRef<HTMLDivElement, AlertProps>(
  ({ variant = 'default', className, children, ...props }, ref) => {
    const type = getAntAlertType(variant);
    
    return (
      <div ref={ref}>
        <AntAlert
          type={type}
          message={children}
          className={cn(
            'w-full',
            variant === 'default' && 'border-border',
            variant === 'destructive' && 'border-destructive/50',
            className
          )}
          {...props}
        />
      </div>
    );
  }
);

Alert.displayName = 'Alert';

// AlertTitle组件 - 兼容性组件
interface AlertTitleProps {
  children?: React.ReactNode;
  className?: string;
}

export const AlertTitle: React.FC<AlertTitleProps> = ({ 
  children,
  className 
}) => {
  return (
    <h5 className={cn('mb-1 font-medium leading-none tracking-tight', className)}>
      {children}
    </h5>
  );
};

AlertTitle.displayName = 'AlertTitle';

// AlertDescription组件 - 兼容性组件
interface AlertDescriptionProps {
  children?: React.ReactNode;
  className?: string;
}

export const AlertDescription: React.FC<AlertDescriptionProps> = ({ 
  children,
  className 
}) => {
  return (
    <div className={cn('text-sm [&_p]:leading-relaxed', className)}>
      {children}
    </div>
  );
};

AlertDescription.displayName = 'AlertDescription';
