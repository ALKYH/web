import React from 'react';
import { Avatar as AntAvatar, AvatarProps as AntAvatarProps } from 'antd';
import { cn } from '@/lib/utils';

// 扩展的Avatar属性
interface AvatarProps extends Omit<AntAvatarProps, 'size'> {
  size?: number | 'large' | 'small' | 'default';
  className?: string;
}

// 主Avatar组件
export const Avatar = React.forwardRef<HTMLSpanElement, AvatarProps>(
  ({ className, size = 32, ...props }, ref) => {
    return (
      <AntAvatar
        ref={ref}
        size={size}
        className={cn('shrink-0', className)}
        {...props}
      />
    );
  }
);

Avatar.displayName = 'Avatar';

// AvatarImage组件 - 兼容性组件，映射到Avatar的src属性
interface AvatarImageProps {
  src?: string;
  alt?: string;
  className?: string;
}

export const AvatarImage: React.FC<AvatarImageProps> = () => {
  // 这是一个兼容性组件，实际的src会被传递给父Avatar组件
  return null;
};

AvatarImage.displayName = 'AvatarImage';

// AvatarFallback组件 - 兼容性组件，映射到Avatar的children
interface AvatarFallbackProps {
  children?: React.ReactNode;
  className?: string;
}

export const AvatarFallback: React.FC<AvatarFallbackProps> = () => {
  // 这是一个兼容性组件，实际的fallback内容会被传递给父Avatar组件
  return null;
};

AvatarFallback.displayName = 'AvatarFallback';
