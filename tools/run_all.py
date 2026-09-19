# -*- coding: utf-8 -*-
"""활성 모듈 전부 수집 → 빌드. 한 모듈이 죽어도 나머지는 간다. GitHub Actions 와 로컬이 같은 진입점.

사용: py -X utf8 tools/run_all.py [--no-net]     (금지어 검출 시 종료코드 2)
"""
from __future__ import annotations

import importlib
import sys

from build import build
from common import load_yaml, run_fetcher


def main(argv: list[str]) -> int:
    sources = load_yaml("sources")["modules"]
    for module, cfg in sources.items():
        if not cfg.get("enabled"):
            continue
        mod = importlib.import_module(cfg["fetcher"])
        run_fetcher(module, mod.fetch)
    index = build(net="--no-net" not in argv)
    return 2 if index["banned_hits"] else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
