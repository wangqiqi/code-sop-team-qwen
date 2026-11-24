#!/usr/bin/env python3
"""把 code-sop-team/ 打成可上传安装的 ZIP，输出可复现（同一份源码永远同一个 SHA-256）。

用法：
    python tools/build_kit.py                       # 输出到 build/dist/
    python tools/build_kit.py --out some/dir        # 指定输出目录
    python tools/build_kit.py --skip-validate       # 跳过结构校验（不推荐）

在 GitHub Actions 里会额外写 GITHUB_OUTPUT（name/size/sha256/zip），并把同一组值打到 stdout。
"""

import argparse
import hashlib
import os
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import validate_kit  # noqa: E402

KIT = "code-sop-team"
FIXED_DATE = (1980, 1, 1, 0, 0, 0)
SKIP_DIRS = {"__pycache__", ".git"}
SKIP_FILES = {".qwenwork-format.json", "Thumbs.db", ".DS_Store"}
# 按文本归一为 LF，保证 Windows（autocrlf）与 Linux 检出打出的包哈希一致
TEXT_EXTS = {".md", ".json", ".py", ".ps1", ".sh", ".txt", ".yml", ".yaml", ".gitignore"}

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def iter_files(kit):
    for root, dirs, files in os.walk(kit):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        for fn in sorted(files):
            if fn in SKIP_FILES or fn.endswith(".pyc"):
                continue
            full = os.path.join(root, fn)
            rel = os.path.relpath(full, kit).replace("\\", "/")
            yield full, rel


def build(kit, out_dir):
    manifest_path = os.path.join(kit, ".qwenwork-plugin", "plugin.json")
    if not os.path.isfile(manifest_path):
        raise SystemExit("缺少 %s" % manifest_path)

    import json

    with open(manifest_path, encoding="utf-8") as fh:
        manifest = json.load(fh)
    name = manifest["name"]
    version = manifest["version"]

    os.makedirs(out_dir, exist_ok=True)
    zip_name = "%s-%s.zip" % (name, version)
    zip_path = os.path.join(out_dir, zip_name)

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for full, rel in iter_files(kit):
            info = zipfile.ZipInfo(rel, date_time=FIXED_DATE)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3  # 固定为 Unix，否则 Windows 打包头字节不同，哈希就不同
            info.external_attr = (0o644 & 0xFFFF) << 16
            with open(full, "rb") as src:
                payload = src.read()
            if os.path.splitext(full)[1].lower() in TEXT_EXTS:
                payload = payload.replace(b"\r\n", b"\n")
            zf.writestr(info, payload)

    with open(zip_path, "rb") as fh:
        blob = fh.read()

    return {
        "name": zip_name,
        "version": version,
        "zip": zip_path,
        "size": len(blob),
        "sha256": hashlib.sha256(blob).hexdigest(),
        "entries": len(zipfile.ZipFile(zip_path).namelist()),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--kit", default=KIT)
    parser.add_argument("--out", default=os.path.join("build", "dist"))
    parser.add_argument("--skip-validate", action="store_true")
    args = parser.parse_args()

    if not args.skip_validate:
        problems_before = 0
        validate_kit.problems.clear()
        validate_kit.validate(args.kit)
        problems_before = len(validate_kit.problems)
        if problems_before:
            print("\n结构校验未通过，终止打包")
            return 1

    result = build(args.kit, args.out)
    print("\n打包完成")
    print("name=%s" % result["name"])
    print("version=%s" % result["version"])
    print("zip=%s" % result["zip"])
    print("size=%d" % result["size"])
    print("entries=%d" % result["entries"])
    print("sha256=%s" % result["sha256"])

    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a", encoding="utf-8") as fh:
            for key in ("name", "version", "zip", "size", "sha256"):
                fh.write("%s=%s\n" % (key, result[key]))
    return 0


if __name__ == "__main__":
    sys.exit(main())