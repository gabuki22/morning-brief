# -*- coding: utf-8 -*-
"""환율 모듈 — Frankfurter(ECB 고시, 키 없음). 통화·기간은 config/sources.yaml.

한 행 = 통화쌍 1개(카드 1장). 시계열은 영업일 기준이라 30일 요청에 20~22점이 정상.
"""
from __future__ import annotations

from datetime import timedelta

from common import http_json, item_id, load_yaml, module_payload, now_kst, run_fetcher, today_str


def fetch() -> dict:
    cfg = load_yaml("sources")["modules"]["fx"]
    p = cfg["params"]
    base_url = cfg["sources"][0]["url"]
    end = today_str()
    start = (now_kst() - timedelta(days=p["days"])).strftime("%Y-%m-%d")
    d = http_json(f"{base_url}/{start}..{end}?base={p['base']}&symbols={','.join(p['symbols'])}")
    rates = d["rates"]
    days = sorted(rates)
    items = []
    for sym in p["symbols"]:
        series = [[day, rates[day][sym]] for day in days if sym in rates[day]]
        if not series:
            continue
        last, first = series[-1][1], series[0][1]
        prev = series[-2][1] if len(series) > 1 else last
        chg1 = (last / prev - 1) * 100 if prev else 0.0
        chgp = (last / first - 1) * 100 if first else 0.0
        items.append({
            "id": item_id(f"fx:{p['base']}{sym}"),
            "title": f"{p['base']}/{sym} {last:,.2f}",
            "url": f"https://www.google.com/finance/quote/{p['base']}-{sym}",
            "published_at": series[-1][0],
            "summary": f"전 영업일 대비 {chg1:+.2f}% · {p['days']}일 전 대비 {chgp:+.2f}% (ECB {series[-1][0]} 고시)",
            "tags": ["환율", sym],
            "metrics": {"last": last, "chg_1d": round(chg1, 3), "chg_period": round(chgp, 3), "series": series},
            "is_new": True,
            "streak_days": 1,
        })
    return module_payload("fx", {"name": "Frankfurter (ECB 고시)", "url": base_url, "kind": "json"}, items)


if __name__ == "__main__":
    run_fetcher("fx", fetch)
