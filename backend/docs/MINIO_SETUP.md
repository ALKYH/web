# MinIO对象存储服务设置指南

## 概述

本项目已集成MinIO对象存储服务，用于替换原有的本地文件存储系统。MinIO提供了高性能、分布式的对象存储解决方案，支持文件上传、下载和管理。

## 已完成的工作

### 1. MinIO服务安装和配置
- ✅ 下载并安装MinIO服务器 (`/usr/local/bin/minio`)
- ✅ 下载并安装MinIO客户端 (`/usr/local/bin/mc`)
- ✅ 启动MinIO服务 (端口: 9000, 控制台: 9001)
- ✅ 创建必要的存储桶:
  - `avatars` - 用户头像存储
  - `documents` - 文档文件存储
  - `general` - 通用文件存储

### 2. 代码集成
- ✅ 在 `libs/config/minio_config.py` 中添加MinIO配置
- ✅ 在 `libs/config/settings.py` 中集成MinIO配置
- ✅ 创建 `libs/storage/minio_client.py` MinIO客户端
- ✅ 创建 `libs/storage/minio_manager.py` MinIO存储管理器
- ✅ 重写 `apps/api/v1/endpoints/files.py` 文件上传接口
- ✅ 更新 `pyproject.toml` 添加MinIO依赖

### 3. 环境配置
- ✅ 在 `.env` 文件中添加MinIO配置项
- ✅ 创建MinIO服务管理脚本

## MinIO服务管理

### 使用管理脚本

项目提供了便捷的MinIO服务管理脚本:

```bash
# 启动MinIO服务
./scripts/minio/manage_minio.sh start

# 停止MinIO服务
./scripts/minio/manage_minio.sh stop

# 重启MinIO服务
./scripts/minio/manage_minio.sh restart

# 查看MinIO状态
./scripts/minio/manage_minio.sh status

# 初始化存储桶
./scripts/minio/manage_minio.sh init
```

### 手动管理

```bash
# 启动MinIO服务
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY no_proxy
nohup /usr/local/bin/minio server /data/minio --console-address ":9001" > /var/log/minio.log 2>&1 &

# 配置客户端别名
/usr/local/bin/mc alias set local http://localhost:9000 minioadmin minioadmin

# 创建存储桶
/usr/local/bin/mc mb local/avatars local/documents local/general

# 查看存储桶
/usr/local/bin/mc ls local/
```

## MinIO访问信息

- **服务器地址**: http://localhost:9000
- **控制台地址**: http://localhost:9001
- **访问密钥**: minioadmin
- **秘密密钥**: minioadmin
- **存储桶**:
  - `avatars` - 头像文件 (最大5MB)
  - `documents` - 文档文件 (最大10MB)
  - `general` - 通用文件 (最大50MB)

## API接口更新

文件上传接口已更新为使用MinIO存储:

### 头像上传
```
POST /api/v1/upload/avatar
```

### 文档上传
```
POST /api/v1/upload/document
```

### 批量上传
```
POST /api/v1/upload/multiple
```

### 文件删除
```
DELETE /api/v1/files/{bucket_name}/{object_name}
```

### 获取文件信息
```
GET /api/v1/files/{bucket_name}/{object_name}
```

### 刷新文件URL
```
POST /api/v1/files/{bucket_name}/{object_name}/refresh-url
```

## 配置说明

### 环境变量 (.env)

```bash
# MinIO服务器配置
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_SECURE=false
MINIO_REGION=us-east-1

# MinIO存储桶配置
MINIO_BUCKET_AVATARS=avatars
MINIO_BUCKET_DOCUMENTS=documents
MINIO_BUCKET_GENERAL=general

# 文件大小限制 (字节)
MAX_AVATAR_SIZE=5242880        # 5MB
MAX_DOCUMENT_SIZE=10485760     # 10MB
MAX_GENERAL_SIZE=52428800      # 50MB

# URL过期时间配置 (分钟)
AVATAR_URL_EXPIRE_MINUTES=60     # 头像URL 1小时
DOCUMENT_URL_EXPIRE_MINUTES=1440 # 文档URL 24小时
GENERAL_URL_EXPIRE_MINUTES=1440  # 通用文件URL 24小时
```

## 文件URL说明

MinIO生成的是预签名URL，有过期时间。不同的文件类型有不同的过期时间:
- 头像: 1小时
- 文档: 24小时
- 通用文件: 24小时

如果需要刷新URL，可以使用 `/api/v1/files/{bucket_name}/{object_name}/refresh-url` 接口。

## 优势

相比本地文件存储，MinIO提供了以下优势:

1. **高性能**: 分布式存储，支持高并发访问
2. **可扩展性**: 支持水平扩展，存储容量无上限
3. **可靠性**: 数据冗余和备份机制
4. **安全性**: 完整的访问控制和加密支持
5. **兼容性**: S3 API兼容，易于迁移
6. **管理便利**: Web控制台和丰富的管理工具

## 注意事项

1. MinIO服务需要在应用启动前先启动
2. 确保 `/data/minio` 目录有足够的存储空间
3. 生产环境建议使用更强的访问密钥和秘密密钥
4. 定期备份MinIO数据目录
5. 监控MinIO服务状态和资源使用情况

## 故障排除

### MinIO启动失败
```bash
# 检查端口是否被占用
netstat -tlnp | grep :9000

# 检查日志
tail -f /var/log/minio.log

# 清理数据目录重新启动
rm -rf /data/minio/*
./scripts/minio/manage_minio.sh start
```

### 连接失败
```bash
# 检查MinIO服务状态
./scripts/minio/manage_minio.sh status

# 测试连接
curl http://localhost:9000/minio/health/ready

# 重新配置客户端
/usr/local/bin/mc alias remove local
/usr/local/bin/mc alias set local http://localhost:9000 minioadmin minioadmin
```

### 存储桶不存在
```bash
# 重新创建存储桶
./scripts/minio/manage_minio.sh init
```

---

## 下一步

MinIO服务已成功集成到项目中。您可以:

1. 启动MinIO服务: `./scripts/minio/manage_minio.sh start`
2. 启动后端应用: `poetry run uvicorn apps.main:app --host 0.0.0.0 --port 8000 --reload`
3. 访问API文档: http://localhost:8000/docs
4. 测试文件上传功能

如有问题，请参考本文档或查看MinIO官方文档: https://docs.min.io/
