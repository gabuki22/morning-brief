# -*- coding: utf-8 -*-
"""계약 검사기가 실제로 막는지 본다 — 검사기 자신을 깨진 표본으로 검사한다.

사용: py -X utf8 tests/test_contract.py   (전부 통과하면 종료코드 0)
"""
from __future__ import annotations

import copy
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from validate import validate_module  # noqa: E402

TH = {"min_items": {"news": 10}, "link_check_sample": 3}
GOOD = {
    "module": "news", "fetched_at": "2026-09-20T06:00:00+09:00",
    "source": {"name": "t", "url": "https://example.com/rss", "kind": "rss"},
    "items": [{"id": f"id{i}", "title": "t", "url": "https://example.com/a", "published_at": "2026-09-20",
               "summary": "s", "tags": [], "metrics": {}, "is_new": True, "streak_days": 1} for i in range(12)],
    "status": {"ok": True, "count": 12, "warn": [], "error": None},
}


def run() -> int:
    fails = 0

    def check(name, cond):
        nonlocal fails
        print(("ok   " if cond else "FAIL ") + name)
        if not cond:
            fails += 1

    check("정상 표본은 통과", validate_module(GOOD, TH, net=False)["level"] == "ok")

    bad = copy.deepcopy(GOOD); del bad["items"][0]["url"]
    check("필드 없음은 차단", validate_module(bad, TH, net=False)["level"] == "block")

    bad = copy.deepcopy(GOOD); bad["items"][1]["id"] = bad["items"][0]["id"]
    check("id 중복은 차단", validate_module(bad, TH, net=False)["level"] == "block")

    bad = copy.deepcopy(GOOD); bad["items"] = bad["items"][:5]
    check("하한 미달은 경고", validate_module(bad, TH, net=False)["level"] == "warn")

    bad = copy.deepcopy(GOOD); bad["items"] = []
    check("0건은 차단", validate_module(bad, TH, net=False)["level"] == "block")

    bad = copy.deepcopy(GOOD); bad["status"]["error"] = "boom"
    check("수집 실패는 차단", validate_module(bad, TH, net=False)["level"] == "block")

    os.environ["BANNED_WORDS"] = "TESTBANNEDWORD"
    bad = copy.deepcopy(GOOD); bad["items"][0]["title"] = "x TESTBANNEDWORD y"
    v = validate_module(bad, TH, net=False)
    check("금지어는 차단하고 단어를 안 보여준다", v["level"] == "block" and "TESTBANNEDWORD" not in " ".join(v["block"]))
    os.environ.pop("BANNED_WORDS", None)

    print(f"\n{'전부 통과' if not fails else str(fails) + '건 실패'}")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(run())
