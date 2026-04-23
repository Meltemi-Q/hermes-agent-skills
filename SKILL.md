---
name: minimax-image-gen
description: "Use Minimax (mmx) CLI for image generation. Key pre-configured at /root/.local/bin/mmx with sk-c...qkGM. API endpoint: api.minimaxi.com"
---

# Minimax Image Generation (mmx)

## Quick Reference

**Command:** `mmx image generate --prompt "描述" --aspect-ratio 16:9`

**Key:** `sk-c...qkGM` (已配置好)
**API:** `api.minimaxi.com`

## Usage

### Basic generation

```bash
mmx image generate --prompt "一只白猫在草地上" --aspect-ratio 1:1
```

### With output path

```bash
mmx image generate --prompt "描述" --aspect-ratio 16:9 --output /path/to/output.png
```

### Aspect ratios

- `1:1` — 正方形
- `16:9` — 宽屏
- `9:16` — 竖屏/手机
- `4:3` — 4:3

## Tips

- Prompt 用英文效果更好
- `--aspect-ratio` 参数决定图片比例
- 图片默认保存路径看输出日志
