#!/usr/bin/env python3
"""校验专家套件目录是否符合上传/安装格式。

用法：
    python tools/validate_kit.py                # 校验 code-sop-team/
    python tools/validate_kit.py --kit <目录>

退出码：0 全部通过；1 存在 FAIL。
"""

import argparse
import json
import os
import re
import sys

REQUIRED_MANIFEST = [
    "name",
    "displayName",
    "displayNameEn",
    "displayNameCn",
    "version",
    "description",
    "descriptionEn",
    "descriptionZh",
]
REQUIRED_SKILL_FIELDS = [
    "name",
    "description",
    "name_en",
    "name_zh",
    "description_en",
    "description_zh",
]
JUNK_DIRS = {"__pycache__", ".git"}
JUNK_FILES = {".qwenwork-format.json", "Thumbs.db", ".DS_Store"}
MAX_ZIP_BYTES = 50 * 1024 * 1024
MAX_ICON_BYTES = 2 * 1024 * 1024
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
KEBAB = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

problems = []


def fail(msg):
    problems.append(msg)
    print("FAIL  " + msg)


def ok(msg):
    print("OK    " + msg)


def read_frontmatter(path):
    with open(path, encoding="utf-8", errors="replace") as fh:
        text = fh.read()
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    fields = {}
    for line in text[3:end].splitlines():
        m = re.match(r"^([A-Za-z0-9_-]+)\s*:\s*(.*)$", line)
        if m:
            fields[m.group(1)] = m.group(2).strip()
    return fields


def validate(kit):
    manifest_path = os.path.join(kit, ".qwenwork-plugin", "plugin.json")
    root_path = os.path.join(kit, "plugin.json")

    if not os.path.isfile(manifest_path):
        fail("缺少 .qwenwork-plugin/plugin.json")
        return None
    with open(manifest_path, encoding="utf-8") as fh:
        manifest = json.load(fh)
    ok(".qwenwork-plugin/plugin.json 可解析")

    if os.path.isfile(root_path):
        with open(root_path, encoding="utf-8") as fh:
            root = json.load(fh)
        if root != manifest:
            fail("根级 plugin.json 与 .qwenwork-plugin/plugin.json 内容不一致")
        else:
            ok("两份清单内容一致")
    else:
        fail("缺少根级 plugin.json（后台上传需要）")

    missing = [k for k in REQUIRED_MANIFEST if not manifest.get(k)]
    if missing:
        fail("清单缺少字段: " + ", ".join(missing))
    else:
        ok("清单字段齐全（含中英双语）")

    name = manifest.get("name", "")
    if not KEBAB.match(name):
        fail("name 需为 kebab-case: %r" % name)
    else:
        ok("name=%s" % name)

    version = manifest.get("version", "")
    if not SEMVER.match(version):
        fail("version 需为语义化版本: %r" % version)
    else:
        ok("version=%s" % version)

    skills_root = os.path.join(kit, "skills")
    declared = [s.replace("./", "").replace("skills/", "") for s in manifest.get("skills", [])]
    if not declared:
        fail("清单未声明任何 skills")
    on_disk = sorted(
        d for d in os.listdir(skills_root) if os.path.isdir(os.path.join(skills_root, d))
    )
    for s in declared:
        skill_md = os.path.join(skills_root, s, "SKILL.md")
        if not os.path.isfile(skill_md):
            fail("技能 %s 缺少 SKILL.md" % s)
            continue
        fields = read_frontmatter(skill_md)
        if fields is None:
            fail("技能 %s 的 SKILL.md 没有 frontmatter" % s)
            continue
        if fields.get("name") != s:
            fail("技能 %s 的 frontmatter name=%r 与目录名不一致" % (s, fields.get("name")))
        missing = [k for k in REQUIRED_SKILL_FIELDS if not fields.get(k)]
        if missing:
            fail("技能 %s frontmatter 缺少: %s" % (s, ", ".join(missing)))
    extra = [d for d in on_disk if d not in declared]
    if extra:
        fail("磁盘上存在未声明的技能: " + ", ".join(extra))
    if not extra and declared:
        ok("%d 个技能声明齐全、frontmatter 完整" % len(declared))

    icon = os.path.join(kit, "icon.png")
    if not os.path.isfile(icon):
        fail("缺少 icon.png")
    else:
        size = os.path.getsize(icon)
        if size > MAX_ICON_BYTES:
            fail("icon.png 超过 2MB: %d 字节" % size)
        else:
            ok("icon.png %.0f KB" % (size / 1024.0))

    junk = []
    total = 0
    for root, dirs, files in os.walk(kit):
        dirs[:] = [d for d in dirs if d not in JUNK_DIRS]
        for fn in files:
            total += os.path.getsize(os.path.join(root, fn))
            if fn in JUNK_FILES or fn.endswith(".pyc"):
                junk.append(os.path.relpath(os.path.join(root, fn), kit))
    if junk:
        fail("发现不应入库的文件: " + ", ".join(junk[:5]))
    else:
        ok("无构建残留文件")
    if os.path.isdir(os.path.join(kit, "__pycache__")):
        fail("kit 根目录存在 __pycache__")
    if total > MAX_ZIP_BYTES:
        fail("套件过大: %.1f MB（上限 50 MB）" % (total / 1024.0 / 1024.0))
    else:
        ok("套件体积 %.1f MB（上限 50 MB）" % (total / 1024.0 / 1024.0))

    return manifest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--kit", default="code-sop-team")
    args = parser.parse_args()

    if not os.path.isdir(args.kit):
        fail("套件目录不存在: %s" % args.kit)
    else:
        print("校验套件: %s" % args.kit)
        validate(args.kit)

    if problems:
        print("\n%d 项校验失败" % len(problems))
        return 1
    print("\n全部校验通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())