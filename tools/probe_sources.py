# -*- coding: utf-8 -*-
"""소스 실측 — config/sources.yaml 의 모든 소스(비활성 포함)에 실제로 요청해 상태·형식·크기를 본다.

추측으로 적지 않기 위한 도구. 결과를 docs/SOURCES.md 에 날짜와 함께 옮긴다. 읽기 전용.
사용: py -X utf8 tools/probe_sources.py [모듈…]
"""
from __future__ import annotations

import concurrent.futures as cf
import json
import re
import sys
import urllib.request

from common import UA, load_yaml


def probe(label: str, url: str) -> str:
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=10) as r:
            body = r.read(400_000)
            ctype = (r.headers.get("Content-Type") or "").split(";")[0]
            code = r.status
    except Exception as e:
        return f"x {label:34s} {type(e).__name__}: {str(e)[:70]}"
    text = body.decode("utf-8", "ignore")
    if "json" in ctype or text[:1] in "[{":
        try:
            d = json.loads(text)
            sample = ("keys=" + ",".join(list(d)[:6])) if isinstance(d, dict) else f"list[{len(d)}]"
        except Exception:
            sample = "json parse fail"
    elif "xml" in ctype or "<rss" in text[:600] or "<feed" in text[:600]:
        sample = f"item {len(re.findall(r'<item[ >]', text))} · entry {len(re.findall(r'<entry[ >]', text))}"
    else:
        sample = "html/etc"
    return f"{'o' if code == 200 else '?'} {label:34s} {code} {ctype:20s} {len(body):>8,}B  {sample}"


def main(argv: list[str]) -> int:
    want = set(argv[1:])
    jobs = []
    for module, cfg in load_yaml("sources")["modules"].items():
        if want and module not in want:
            continue
        for s in cfg.get("sources", []):
            url = s.get("probe") or s.get("url")
            if url:
                jobs.append((f"{module}/{s['name']}", url))
    with cf.ThreadPoolExecutor(max_workers=12) as ex:
        for line in ex.map(lambda j: probe(*j), jobs):
            print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
