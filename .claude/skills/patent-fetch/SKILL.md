---
name: patent-fetch
description: 从 Google Patents 页面提取 PDF 链接并下载到 inbox-patent 文件夹，与 patent-search 无缝联动
version: 1.1.0
author: Claude
tier: utility
destructive: false
---

# patent-fetch — Google Patents 专利 PDF 下载

从 Google Patents 页面提取 PDF 下载链接，并自动下载到 `data/inbox-patent/` 目录，供后续 `pipeline ingest` 入库。

常与 `patent-search` 配合使用：先用 `patent-search` 发现专利，再用 `patent-fetch` 或 `--fetch` 参数下载 PDF。

## 功能

- **专利 ID 直输**：只需输入专利公开号（如 `US20240176406A1`），自动构造 Google Patents URL
- **完整 URL 支持**：也支持直接传入完整的 Google Patents 页面链接
- **自动去重**：如果目标文件已存在，跳过下载
- **仅用于发现下载**：不入库，下载后需手动执行 `scholaraio pipeline ingest` 走专利入库流程

## 用法

### 通过专利 ID 下载

```bash
scholaraio patent-fetch US20240176406A1
```

### 通过完整 URL 下载

```bash
scholaraio patent-fetch "https://patents.google.com/patent/US20240176406A1"
```

### 与 patent-search 联动

```bash
# 方式一：搜索后根据提示手动下载
scholaraio patent-search "neural network" --count 5
# 输出中每条结果会显示：下载: scholaraio patent-fetch <公开号>

# 方式二：搜索时自动下载所有结果 PDF
scholaraio patent-search "neural network" --count 5 --fetch
```

## 输出示例

```
已下载: /path/to/data/inbox-patent/US20240176406A1.pdf (1679017 bytes)
已保存到: /path/to/data/inbox-patent/US20240176406A1.pdf
```

如果文件已存在：

```
文件已存在: /path/to/data/inbox-patent/US20240176406A1.pdf
已保存到: /path/to/data/inbox-patent/US20240176406A1.pdf
```

如果页面没有 PDF 链接：

```
未在该页面找到 PDF 下载链接
```

## 推荐工作流

### 手动下载流程
```bash
# 1. 搜索专利
scholaraio patent-search "quantum computing" --count 10

# 2. 根据公开号下载目标专利 PDF
scholaraio patent-fetch US20230123456A1

# 3. 走正常专利入库流程（自动按公开号去重、标记 patent 类型）
scholaraio pipeline ingest

# 4. 本地检索
scholaraio search "voltage overshoot"
```

### 自动下载流程
```bash
# 1. 搜索并自动下载前 5 条结果的 PDF
scholaraio patent-search "quantum computing" --count 5 --fetch

# 2. 直接入库
scholaraio pipeline ingest
```

## 故障排除

**页面请求超时**
- 检查网络连接和代理设置
- Google Patents 在某些网络环境下可能需要配置 HTTP 代理

**未在该页面找到 PDF 下载链接**
- 该专利可能尚未上传 PDF（如非常新的 WO 专利）
- 尝试在浏览器中打开页面确认是否有 "Download PDF" 按钮
- 部分专利确实不提供 Google Patents 直接下载，需要换源（如 USPTO、EPO）

**下载失败**
- 检查 `data/inbox-patent/` 目录是否有写入权限
- 确认磁盘空间充足

## 相关功能

- `scholaraio patent-search` — USPTO 专利搜索（发现专利公开号，支持 `--fetch` 自动下载）
- `scholaraio pipeline ingest` — 将 inbox-patent 中的 PDF 入库
- `scholaraio search` / `scholaraio vsearch` — 本地知识库检索
