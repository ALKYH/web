# Ant Design 组件映射参考

## 📋 Shadcn/ui → Ant Design 组件映射表

### 基础组件

| 原Shadcn/ui组件 | Ant Design组件 | 导入方式 | 主要差异 |
|----------------|----------------|----------|----------|
| `Button` | `Button` | `import { Button } from 'antd'` | props名称略有不同 |
| `Input` | `Input` | `import { Input } from 'antd'` | 基本一致 |
| `Textarea` | `Input.TextArea` | `import { Input } from 'antd'` | 使用Input.TextArea |
| `Card` | `Card` | `import { Card } from 'antd'` | 结构略有不同 |
| `Avatar` | `Avatar` | `import { Avatar } from 'antd'` | 基本一致 |
| `Badge` | `Badge` | `import { Badge } from 'antd'` | 基本一致 |
| `Alert` | `Alert` | `import { Alert } from 'antd'` | 基本一致 |

### 布局组件

| 原Shadcn/ui组件 | Ant Design组件 | 导入方式 | 主要差异 |
|----------------|----------------|----------|----------|
| `Dialog` | `Modal` | `import { Modal } from 'antd'` | API完全不同 |
| `Popover` | `Popover` | `import { Popover } from 'antd'` | trigger方式不同 |
| `DropdownMenu` | `Dropdown` | `import { Dropdown } from 'antd'` | 结构不同 |
| `NavigationMenu` | `Menu` | `import { Menu } from 'antd'` | 完全重构 |
| `Separator` | `Divider` | `import { Divider } from 'antd'` | 基本一致 |

### 表单组件

| 原Shadcn/ui组件 | Ant Design组件 | 导入方式 | 主要差异 |
|----------------|----------------|----------|----------|
| `Checkbox` | `Checkbox` | `import { Checkbox } from 'antd'` | 基本一致 |
| `RadioGroup` | `Radio.Group` | `import { Radio } from 'antd'` | 使用Radio.Group |
| `Select` | `Select` | `import { Select } from 'antd'` | 基本一致 |
| `Slider` | `Slider` | `import { Slider } from 'antd'` | 基本一致 |
| `Label` | `Form.Item` | `import { Form } from 'antd'` | 通常用Form.Item |

### 反馈组件

| 原Shadcn/ui组件 | Ant Design组件 | 导入方式 | 主要差异 |
|----------------|----------------|----------|----------|
| `Skeleton` | `Skeleton` | `import { Skeleton } from 'antd'` | 基本一致 |
| `Tooltip` | `Tooltip` | `import { Tooltip } from 'antd'` | 基本一致 |
| `Progress` | `Progress` | `import { Progress } from 'antd'` | 基本一致 |

### 特殊组件

| 原Shadcn/ui组件 | Ant Design组件 | 导入方式 | 说明 |
|----------------|----------------|----------|------|
| `Command` | `AutoComplete` | `import { AutoComplete } from 'antd'` | 用于搜索建议 |
| `ScrollArea` | 自定义 | - | Ant Design无对应组件 |
| `Timeline` | `Timeline` | `import { Timeline } from 'antd'` | 基本一致 |

## 🔄 主要API差异对比

### Button组件

```typescript
// Shadcn/ui Button
<Button variant="outline" size="sm" disabled>
  按钮
</Button>

// Ant Design Button  
<Button type="default" size="small" disabled>
  按钮
</Button>
```

**属性映射：**
- `variant="default"` → `type="primary"`
- `variant="outline"` → `type="default"`
- `variant="ghost"` → `type="text"`
- `variant="destructive"` → `type="primary" danger`
- `size="sm"` → `size="small"`
- `size="lg"` → `size="large"`

### Modal/Dialog组件

```typescript
// Shadcn/ui Dialog
<Dialog open={open} onOpenChange={setOpen}>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>标题</DialogTitle>
    </DialogHeader>
    内容
  </DialogContent>
</Dialog>

// Ant Design Modal
<Modal
  title="标题"
  open={open}
  onCancel={() => setOpen(false)}
  onOk={handleOk}
>
  内容
</Modal>
```

### Dropdown组件

```typescript
// Shadcn/ui DropdownMenu
<DropdownMenu>
  <DropdownMenuTrigger asChild>
    <Button>菜单</Button>
  </DropdownMenuTrigger>
  <DropdownMenuContent>
    <DropdownMenuItem>项目1</DropdownMenuItem>
    <DropdownMenuItem>项目2</DropdownMenuItem>
  </DropdownMenuContent>
</DropdownMenu>

// Ant Design Dropdown
<Dropdown
  menu={{
    items: [
      { key: '1', label: '项目1' },
      { key: '2', label: '项目2' },
    ]
  }}
  trigger={['click']}
>
  <Button>菜单</Button>
</Dropdown>
```

## 🎨 样式差异处理

### 1. 自定义样式
```css
/* 如果需要覆盖Ant Design默认样式 */
.ant-btn-custom {
  border-radius: 8px;
  font-weight: 500;
}
```

### 2. Tailwind与Ant Design结合
```typescript
// 可以在Ant Design组件上使用Tailwind类
<Button className="shadow-lg hover:shadow-xl transition-shadow">
  按钮
</Button>
```

### 3. 主题变量
```typescript
// 在antd-theme.ts中已配置的变量可以直接使用
// 组件会自动应用主题配置
```

## 📝 迁移注意事项

### 1. 导入方式变化
```typescript
// 旧的导入
import { Button } from '@/components/ui/button';

// 新的导入
import { Button } from 'antd';
```

### 2. 属性名称变化
- 仔细检查每个组件的属性名称
- 参考Ant Design官方文档确认正确的API

### 3. 事件处理变化
- 事件回调函数的参数可能不同
- 需要适配新的事件处理方式

### 4. 样式类名变化
- Ant Design使用`ant-`前缀的类名
- 可能需要调整自定义CSS选择器

## 🚀 下一步计划

1. **阶段二**：开始迁移核心组件（Button、Input、Card）
2. **阶段三**：迁移布局组件（Navbar、Footer）
3. **阶段四**：迁移复杂业务组件
4. **阶段五**：页面级迁移和测试

---

**备注**：这个映射表会随着迁移过程不断更新和完善。
