# -*- coding: utf-8 -*-
"""레저·캠핑 모듈 — Naver 뉴스 검색(키 있을 때) + 고캠핑 바로가기. 고캠핑 API(DATA_GO_KR_KEY)는 키가 오면 붙인다.

한 행 = 기사 1건 또는 바로가기 1장.
"""
from __future__ import annotations

from common import get_secret, item_id, load_yaml, module_payload, run_fetcher, today_str
import naver


def fetch() -> dict:
    cfg = load_yaml("sources")["modules"]["leisure"]
    p = cfg.get("params", {})
    items, warns, seen = [], [], set()
    if naver.has_key():
        for q in p.get("queries", []):
            try:
                for n in naver.search(q, n=int(p.get("per_query", 8))):
                    iid = item_id(n["url"])
                    if iid in seen:
                        continue
                    seen.add(iid)
                    items.append({
                        "id": iid, "title": n["title"], "url": n["url"],
                        "published_at": n["published_at"] or today_str(), "summary": n["summary"],
                        "tags": ["캠핑", q], "metrics": {}, "is_new": True, "streak_days": 1, "source_name": "Naver 뉴스",
                    })
            except Exception as e:
                warns.append(f"검색 '{q}' 실패: {type(e).__name__}")
    else:
        warns.append("Naver 키 없음 — 검색 생략")
    for link in p.get("links", []):
        items.append({
            "id": item_id(f"leisure:link:{link['name']}"), "title": link["name"], "url": link["url"],
            "published_at": today_str(), "summary": link.get("summary", ""), "tags": ["바로가기"],
            "metrics": {}, "is_new": True, "streak_days": 1, "source_name": "바로가기",
        })
    if not get_secret("DATA_GO_KR_KEY"):
        warns.append("고캠핑 API: 키 없음(DATA_GO_KR_KEY)")
    items.sort(key=lambda it: it["published_at"] or "", reverse=True)
    return module_payload("leisure", {"name": "Naver 뉴스 검색 + 고캠핑", "url": "https://www.gocamping.or.kr/", "kind": "api"},
                          items[: int(p.get("max_items", 40))], warn=warns)


if __name__ == "__main__":
    run_fetcher("leisure", fetch)
