#!/usr/bin/env python3
"""gpt-image-2 image generation via gpt.meltemi.fun proxy."""

import argparse
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

BASE_URL = "https://gpt.meltemi.fun"
API_KEY = "sk-cgw-c6e3614ddfecae03cf0825c027ffd64d9e77338bb1b08850"
MODEL = "gpt-image-2"

SIZE_PRESETS = {
    "square":    "1024x1024",
    "landscape": "1536x1024",
    "portrait":  "1024x1536",
}


def get_workspace_dir():
    for d in [
        os.path.expanduser("~/.openclaw/workspace"),
        os.path.expanduser("~/.claude/workspace"),
    ]:
        if os.path.isdir(d):
            return d
    return "/tmp"


def make_filename(prompt, index=None):
    """Generate filename: yyyy-mm-dd-hh-mm-ss-short-desc.png"""
    ts = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    words = "".join(c if c.isalnum() or c == " " else " " for c in prompt)
    words = "-".join(words.split()[:4]).lower()[:30] or "image"
    suffix = f"-{index}" if index is not None else ""
    return f"{ts}-{words}{suffix}.png"


def resolve_size(size_str):
    lower = size_str.lower().strip()
    return SIZE_PRESETS.get(lower, size_str)


def generate_image(prompt, size="1024x1024", batch=1):
    """Generate image(s) using gpt.meltemi.fun gpt-image-2 API."""
    size = resolve_size(size)

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "size": size,
    }

    print(f"## 图片生成中...")
    print(f"- **模型**: {MODEL} (via gpt.meltemi.fun)")
    print(f"- **提示词**: {prompt}")
    print(f"- **尺寸**: {size}")
    if batch > 1:
        print(f"- **数量**: {batch} 张（挑选模式）")
    print()

    workspace = get_workspace_dir()

    def gen_one(idx=None):
        t0 = time.time()
        suffix = f"-{idx}" if idx is not None else ""
        save_path = os.path.join(workspace, make_filename(prompt, idx))

        try:
            req = Request(
                f"{BASE_URL}/v1/images/generations",
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST",
            )
            with urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            # Can be URL or b64_json
            image_entry = data.get("data", [{}])[0]
            image_url = image_entry.get("url")
            b64_json = image_entry.get("b64_json")

            if b64_json:
                import base64
                img_data = base64.b64decode(b64_json)
            elif image_url:
                img_req = Request(image_url)
                with urlopen(img_req, timeout=60) as img_resp:
                    img_data = img_resp.read()
            else:
                raise RuntimeError(f"未返回图片 URL 或 b64_json: {json.dumps(data, ensure_ascii=False)}")

            with open(save_path, "wb") as f:
                f.write(img_data)

            elapsed = int(time.time() - t0)
            return (os.path.abspath(save_path), len(img_data) / 1024, elapsed)

        except Exception as e:
            return (None, str(e), 0)

    if batch == 1:
        path, size_kb, elapsed = gen_one()
        if path is None:
            print(f"## 生成失败\n{size_kb}")
            sys.exit(1)
        print(f"## 图片已生成 ({size_kb:.0f} KB, ~{elapsed}s)\n")
        print(f"![AI Generated Image]({path})\n")
        print(f"- **文件**: `{path}`")
    else:
        results = []
        with ThreadPoolExecutor(max_workers=batch) as pool:
            futures = {pool.submit(gen_one, i + 1): i + 1 for i in range(batch)}
            for future in as_completed(futures):
                idx = futures[future]
                path, size_kb, elapsed = future.result()
                results.append((idx, path, size_kb, elapsed))

        results.sort(key=lambda r: r[0])

        ok = [(idx, p, sk, el) for idx, p, sk, el in results if p is not None]
        fail = [(idx, p, sk, el) for idx, p, sk, el in results if p is None]

        if not ok:
            print("## 全部生成失败")
            for idx, _, err, _ in fail:
                print(f"- 第 {idx} 张: {err}")
            sys.exit(1)

        print(f"## {len(ok)} 张图片已生成，请挑选\n")
        for idx, path, size_kb, elapsed in ok:
            print(f"### 第 {idx} 张 ({size_kb:.0f} KB, ~{elapsed}s)\n")
            print(f"![第{idx}张]({path})\n")

        if fail:
            print(f"\n*{len(fail)} 张生成失败*")

        print("\n---")
        print(f"文件保存在: `{workspace}/`")
        print("告诉我你选哪张，我可以帮你用。")


def list_sizes():
    print("## 尺寸预设\n")
    print("| 简称 | 尺寸 | 用途 |")
    print("|------|------|------|")
    print("| square（默认） | 1024x1024 | 默认，通用 |")
    print("| landscape | 1536x1024 | 横版 |")
    print("| portrait | 1024x1536 | 竖版 |")


def main():
    parser = argparse.ArgumentParser(description="gpt-image-2 Image Generation")
    parser.add_argument("prompt", nargs="?", help="Image generation prompt")
    parser.add_argument("--size", "-s", default="1024x1024",
                        help="Size: square / landscape / portrait (default: 1024x1024)")
    parser.add_argument("--batch", "-b", type=int, default=1,
                        help="Generate N images to pick from (1-4, default: 1)")
    parser.add_argument("--list-sizes", "-l", action="store_true",
                        help="List available size presets")

    args = parser.parse_args()

    if args.list_sizes:
        list_sizes()
        return

    if not args.prompt:
        parser.print_help()
        print("\nExamples:")
        print('  python3 scripts/generate.py "金色猫咪在阳光下"')
        print('  python3 scripts/generate.py "赛博朋克城市" --size landscape')
        print('  python3 scripts/generate.py "水墨山水" --batch 3')
        sys.exit(1)

    generate_image(
        prompt=args.prompt,
        size=args.size,
        batch=args.batch,
    )


if __name__ == "__main__":
    main()
