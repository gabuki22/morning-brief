# -*- coding: utf-8 -*-
"""활성 모듈 전부 수집 → 빌드. 한 모듈이 죽어도 나머지는 간다. GitHub Actions 와 로컬이 같은 진입점.

사용: py -X utf8 tools/run_all.py [--only news,crypto] [--no-net]     (금지어 검출 시 종료코드 2)
"""
from __future__ import annotations

import importlib
import inspect
import sys

from build import build
from common import load_yaml, run_fetcher


def main(argv: list[str]) -> int:
    only = None
    for a in argv[1:]:
        if a.startswith("--only"):
            val = a.split("=", 1)[1] if "=" in a else argv[argv.index(a) + 1]
            only = {x.strip() for x in val.split(",") if x.strip()}
    sources = load_yaml("sources")["modules"]
    for module, cfg in sources.items():
        if not cfg.get("enabled") or (only and module not in only):
            continue
        mod = importlib.import_module(cfg["fetcher"])
        fn = mod.fetch
        # 공용 수집기(fetch(module)) 와 전용 수집기(fetch()) 둘 다 받는다
        if inspect.signature(fn).parameters:
            run_fetcher(module, lambda m=module, f=fn: f(m))
        else:
            run_fetcher(module, fn)
    index = build(only=only, net="--no-net" not in argv)
    return 2 if index["banned_hits"] else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
