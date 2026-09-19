# -*- coding: utf-8 -*-
"""공공데이터 모듈 — ①오늘 쓸 수 있는 공개 데이터 소스 상태판(키 없는 6소스 실측) ②다가오는 공휴일 ③이번 주 세계 지진 수.

한 행 = 소스 1개 / 공휴일 1건 / 지진 요약 1건. 매일 같은 id 가 정상(same_ids_ok).
"""
from __future__ import annotations

import time
from datetime import date

from common import http_get, http_json, item_id, load_yaml, module_payload, run_fetcher, today_str


def fetch() -> dict:
    cfg = load_yaml("sources")["modules"]["publicdata"]
    p = cfg.get("params", {})
    items, warns = [], []

    # ① 소스 상태판 — probe 가 있는 소스만
    for s in cfg["sources"]:
        url = s.get("probe")
        if not url:
            continue
        t0 = time.time()
        try:
            n = len(http_get(url, timeout=12, retries=1))
            ms = int((time.time() - t0) * 1000)
            ok, summary = True, f"정상 · {ms}ms · {n:,}B · 키 {s.get('key', 'none')}"
        except Exception as e:
            ok, summary = False, f"실패 · {type(e).__name__}"
            warns.append(f"{s['name']} 실패")
        items.append({
            "id": item_id(f"publicdata:src:{s['name']}"), "title": f"{'○' if ok else '✗'} {s['name']}",
            "url": s.get("page") or s["url"], "published_at": today_str(), "summary": summary,
            "tags": ["소스 상태", s.get("kind", "")], "metrics": {"ok": ok},
            "is_new": True, "streak_days": 1, "source_name": "실측",
        })

    # ② 공휴일 — 다가오는 n건
    hol = p.get("holidays")
    if hol:
        try:
            year = date.today().year
            data = http_json(hol["url"].format(year=year))
            up = [h for h in data if h["date"] >= today_str()][: int(hol.get("count", 3))]
            if not up:  # 연말이면 내년 것
                up = http_json(hol["url"].format(year=year + 1))[: int(hol.get("count", 3))]
            for h in up:
                d = date.fromisoformat(h["date"])
                left = (d - date.today()).days
                items.append({
                    "id": item_id(f"publicdata:holiday:{h['date']}"),
                    "title": f"{h['date'][5:].replace('-', '/')} {h.get('localName') or h.get('name')}",
                    "url": hol.get("page", hol["url"].format(year=year)), "published_at": h["date"],
                    "summary": ("오늘" if left == 0 else f"{left}일 뒤") + f" · {['월','화','수','목','금','토','일'][d.weekday()]}요일" + (" · 대체공휴일 가능" if h.get("global") is False else ""),
                    "tags": ["공휴일"], "metrics": {"days_left": left},
                    "is_new": True, "streak_days": 1, "source_name": "Nager.Date",
                })
        except Exception as e:
            warns.append(f"공휴일 실패: {type(e).__name__}")

    # ③ 지진 — USGS 주간 M4.5+
    q = p.get("quakes")
    if q:
        try:
            g = http_json(q["url"])
            feats = g.get("features", [])
            big = max(feats, key=lambda f: f["properties"].get("mag") or 0) if feats else None
            summary = f"이번 주 규모 4.5 이상 {len(feats)}건" + (f" · 최대 M{big['properties']['mag']} {big['properties'].get('place', '')}" if big else "")
            items.append({
                "id": item_id("publicdata:quakes:week"), "title": "세계 지진 (USGS, 7일)",
                "url": q.get("page", q["url"]), "published_at": today_str(), "summary": summary,
                "tags": ["지진"], "metrics": {"count": len(feats)},
                "is_new": True, "streak_days": 1, "source_name": "USGS",
            })
        except Exception as e:
            warns.append(f"지진 실패: {type(e).__name__}")

    return module_payload("publicdata", {"name": "공개 데이터 소스 실측", "url": "https://www.data.go.kr/", "kind": "json"},
                          items, warn=warns)


if __name__ == "__main__":
    run_fetcher("publicdata", fetch)
