# -*- coding: utf-8 -*-
"""지수 모듈 — 야후 파이낸스 chart API(비공식, 키 없음). 종목·링크는 config/sources.yaml.

한 행 = 지수 1개(카드 1장). 1개월 종가 시계열 + 전일·기간 변동률.
"""
from __future__ import annotations

from datetime import datetime

from common import KST, http_json, item_id, load_yaml, module_payload, run_fetcher


def fetch() -> dict:
    cfg = load_yaml("sources")["modules"]["markets"]
    items, warns = [], []
    for s in cfg["sources"]:
        if s.get("kind") != "json" or not s.get("symbol") or s.get("enabled", True) is False:
            continue
        try:
            res = http_json(s["url"])["chart"]["result"][0]
            closes = res["indicators"]["quote"][0]["close"]
            series = [[datetime.fromtimestamp(t, KST).strftime("%Y-%m-%d"), round(c, 2)]
                      for t, c in zip(res["timestamp"], closes) if c is not None]
            if len(series) < 2:
                warns.append(f"{s['name']} 점 부족")
                continue
            last, prev, first = series[-1][1], series[-2][1], series[0][1]
            chg1, chgp = (last / prev - 1) * 100, (last / first - 1) * 100
            items.append({
                "id": item_id(f"markets:{s['symbol']}"),
                "title": f"{s['name']} {last:,.2f}",
                "url": s.get("page") or f"https://finance.yahoo.com/quote/{s['symbol']}/",
                "published_at": series[-1][0],
                "summary": f"전일 대비 {chg1:+.2f}% · 1개월 {chgp:+.2f}% ({series[0][0]}~{series[-1][0]}, {len(series)}영업일)",
                "tags": ["지수", s.get("region", "")] if s.get("region") else ["지수"],
                "metrics": {"last": last, "chg_1d": round(chg1, 3), "chg_period": round(chgp, 3), "series": series},
                "is_new": True, "streak_days": 1, "source_name": "Yahoo Finance",
            })
        except Exception as e:
            warns.append(f"{s['name']} 실패: {type(e).__name__}")
    return module_payload("markets", {"name": "Yahoo Finance chart (비공식)", "url": "https://finance.yahoo.com/", "kind": "json"},
                          items, warn=warns)


if __name__ == "__main__":
    run_fetcher("markets", fetch)
