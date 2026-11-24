#!/usr/bin/env python3
"""连续打包两次，断言 SHA-256 一致（保证发布产物可复现）。

用法：python tools/check_reproducible.py
"""

import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import build_kit  # noqa: E402


def main():
    hashes = []
    with tempfile.TemporaryDirectory() as tmp:
        for i in (1, 2):
            out = os.path.join(tmp, "run%d" % i)
            result = build_kit.build(build_kit.KIT, out)
            hashes.append(result["sha256"])
            print("run%d %s %d bytes" % (i, result["sha256"], result["size"]))

    if len(set(hashes)) != 1:
        print("FAIL 两次打包哈希不一致，产物不可复现")
        return 1
    print("OK   两次打包完全一致")
    return 0


if __name__ == "__main__":
    sys.exit(main())