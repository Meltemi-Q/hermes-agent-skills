---
name: gpt-image-2
description: |
  用 gpt.meltemi.fun 调用 OpenAI gpt-image-2 模型生成图片。
  当用户说"画图"、"生成图片"、"AI 画图"且没有指定其他模型时触发。
  支持 1024x1024 / 1536x1024 / 1024x1536 三种尺寸。
---

# gpt-image-2 图片生成

调用 `https://gpt.meltemi.fun/v1/images/generations`，同步返回图片 URL。

## 使用

```bash
python3 scripts/generate.py "提示词"
python3 scripts/generate.py "提示词" --size square
python3 scripts/generate.py "提示词" --size portrait --batch 3
```

## 尺寸预设

| 简称 | 尺寸 | 用途 |
|------|------|------|
| square（默认） | 1024x1024 | 默认，通用 |
| landscape | 1536x1024 | 横版 |
| portrait | 1024x1536 | 竖版 |

## 参数

- `--size`: square / landscape / portrait（默认 square）
- `--batch`: 生成数量 1-4（默认 1）

## 输出

图片保存到 workspace，输出 markdown 图片语法，必须原样转发。
