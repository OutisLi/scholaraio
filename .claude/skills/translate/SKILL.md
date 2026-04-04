---
name: translate
description: Translate paper markdown to a target language (default Chinese). Preserves LaTeX formulas, code blocks, and images. Supports single paper or batch translation. Use when the user wants to read papers in their native language or translate non-Chinese documents.
version: 1.0.0
author: ZimoLiao/scholaraio
license: MIT
tags: ["academic", "papers", "translation", "multilingual"]
---
# 论文翻译

将论文 Markdown 翻译为目标语言（默认中文），保留 LaTeX 公式、代码块、图片引用和 Markdown 格式。翻译结果保存为 `paper_{lang}.md`，原文保持不变。

当前实现支持：
- 单篇翻译时在终端显示块级进度
- 每成功翻译一块就立即刷新 `paper_{lang}.md`
- 中途中断后可从本地 checkpoint 继续续翻
- `--force` 会清理旧 checkpoint 并从头重新翻译

## 配置

`config.yaml` 中可设置默认行为：

```yaml
translate:
  auto_translate: false   # 入库时是否自动翻译（默认关闭）
  target_lang: zh          # 目标语言（zh/en/ja/ko/de/fr/es）
  chunk_size: 4000         # 分块大小（字符数）
  concurrency: 5           # 并发翻译数
```

每次调用时可通过 CLI 参数覆盖默认值。

## 执行逻辑

### 单篇翻译

```bash
scholaraio translate "<paper-id>" [--lang zh] [--force]
```

### 批量翻译

```bash
scholaraio translate --all [--lang zh] [--force]
```

### 查看翻译

```bash
scholaraio show "<paper-id>" --layer 4 --lang zh
```

### 作为 pipeline 步骤

```bash
scholaraio pipeline --steps toc,l3,translate
```

> **注意**：`translate` 默认不在预设（`full`/`ingest`/`enrich`/`reindex`）中；可通过 `--steps` 显式指定。若 `config.translate.auto_translate=true` 且 pipeline 包含 inbox 步骤，`translate` 会在 papers 阶段自动注入。

## 工作流程

1. 检测论文原文语言（基于字符集启发式检测）
2. 如果已是目标语言，跳过
3. 将 Markdown 按段落边界分块（保留代码块和公式完整性）
4. 通过 LLM 逐块翻译，保留所有格式标记
5. 每成功一块就增量写出 `paper_{lang}.md`
6. 同步写入本地 checkpoint：`.paper_{lang}.progress.json`
7. 若中途中断，下次再次运行同一命令时自动从已完成块继续
8. 全部完成后删除 checkpoint，并在 `meta.json` 中记录翻译元数据

## 进度与续翻

单篇翻译会输出：
- 总块数
- 当前块进度（如 `翻译进度: 3/12`）
- 中断位置
- 是否可续翻

如果中途中断：

```bash
scholaraio translate "<paper-id>" --lang zh
```

会自动检测 `.paper_zh.progress.json`，并从上次成功完成的块继续。

如果想忽略已有部分结果并重新开始：

```bash
scholaraio translate "<paper-id>" --lang zh --force
```

会删除旧的 checkpoint 和旧的 `paper_zh.md`，从头重新翻译。

## 示例

用户说："把这篇英文论文翻译成中文"
-> 执行 `scholaraio translate "<paper-id>" --lang zh`

用户说："把所有论文翻译成中文"
-> 执行 `scholaraio translate --all --lang zh`

用户说："看这篇论文的中文版"
-> 执行 `scholaraio show "<paper-id>" --layer 4 --lang zh`

用户说："重新翻译这篇论文"
-> 执行 `scholaraio translate "<paper-id>" --force`

用户说："上次翻译到一半断了，继续翻"
-> 直接执行 `scholaraio translate "<paper-id>" --lang zh`
