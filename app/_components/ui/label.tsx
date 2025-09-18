import React from 'react';
import { cn } from '@/lib/utils';

// Label属性接口
interface LabelProps extends React.LabelHTMLAttributes<HTMLLabelElement> {
  className?: string;
}

export const Label = React.forwardRef<HTMLLabelElement, LabelProps>(
  ({ className, ...props }, ref) => {
    return (
      <label
        ref={ref}
        className={cn(
          'text-foreground text-sm leading-4 font-medium select-none group-data-[disabled=true]:pointer-events-none group-data-[disabled=true]:opacity-50 peer-disabled:cursor-not-allowed peer-disabled:opacity-50',
          className
        )}
        {...props}
      />
    );
  }
);

Label.displayName = 'Label';
