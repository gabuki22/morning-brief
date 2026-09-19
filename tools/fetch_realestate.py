# -*- coding: utf-8 -*-
"""부동산 모듈 — ①부동산 뉴스(RSS 태깅, 수도권·청약·경매 키워드) ②바로가기 카드(LH·온비드·법원경매)
③LH·온비드 공공데이터 API(키 DATA_GO_KR_KEY 가 있을 때만 — 아직 미구현, 키 없으면 경고만).
"""
from __future__ import annotations

from common import get_secret, item_id, load_yaml, module_payload, run_fetcher, today_str
from fetch_rss_tagged import fetch as fetch_tagged


def fetch() -> dict:
    news = fetch_tagged("realestate")
    items, warns = list(news["items"]), list(news["status"]["warn"])
    cfg = load_yaml("sources")["modules"]["realestate"]
    for link in cfg.get("params", {}).get("links", []):
        items.append({
            "id": item_id(f"realestate:link:{link['name']}"),
            "title": link["name"], "url": link["url"], "published_at": today_str(),
            "summary": link.get("summary", ""), "tags": ["바로가기"] + list(link.get("tags", [])),
            "metrics": {}, "is_new": True, "streak_days": 1, "source_name": "바로가기",
        })
    if not get_secret("DATA_GO_KR_KEY"):
        warns.append("LH·온비드 공공데이터 API: 키 없음(DATA_GO_KR_KEY) — 뉴스·바로가기만")
    else:
        warns.append("LH·온비드 API 수집기 미구현 — 보드 참조")
    return module_payload("realestate", news["source"], items, warn=warns)


if __name__ == "__main__":
    run_fetcher("realestate", fetch)
