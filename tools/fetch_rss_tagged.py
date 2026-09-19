# -*- coding: utf-8 -*-
"""RSS 태깅 수집기 — IT·자동차·부동산(뉴스 부분)이 같이 쓴다. 모듈별 차이는 전부 config/sources.yaml params.

params:
  per_source    소스당 최대 건수
  max_items     모듈 최대 건수
  tag_rules     [{tag, match:[…]}]  제목+요약에 걸리면 태그
  require_tags  [태그…]  이 중 하나라도 없으면 버린다(예: 경제 피드에서 부동산만)
"""
from __future__ import annotations

from common import item_id, load_yaml, module_payload, today_str
from rss import fetch_feed, tag_by_rules


def fetch(module: str) -> dict:
    cfg = load_yaml("sources")["modules"][module]
    p = cfg.get("params", {})
    interests = load_yaml("interests").get("keywords", [])
    rules = list(p.get("tag_rules", [])) + [{"tag": k["tag"], "match": k["match"]} for k in interests]
    items, warns, seen, ok = [], [], set(), 0
    for s in cfg["sources"]:
        if s.get("kind") not in ("rss", "atom") or s.get("enabled", True) is False:
            continue
        # 소스별 require_tags 가 있으면 그것을, 없으면 모듈 것을 쓴다(종합 피드는 걸러내고 전문 피드는 그대로)
        require = set(s.get("require_tags", p.get("require_tags", [])) or [])
        try:
            feed = fetch_feed(s["url"], limit=int(p.get("per_source", 20)))
        except Exception as e:
            warns.append(f"{s['name']} 실패: {type(e).__name__}")
            continue
        ok += 1
        for f in feed:
            iid = item_id(f["url"])
            if iid in seen:
                continue
            tags = tag_by_rules(f["title"] + " " + f["summary"], rules)
            if require and not (set(tags) & require):
                continue
            seen.add(iid)
            items.append({
                "id": iid, "title": f["title"], "url": f["url"],
                "published_at": f["published_at"] or today_str(), "summary": f["summary"],
                "tags": tags, "metrics": {}, "is_new": True, "streak_days": 1, "source_name": s["name"],
            })
    items.sort(key=lambda it: it["published_at"] or "", reverse=True)
    items = items[: int(p.get("max_items", 60))]
    return module_payload(module, {"name": f"RSS {ok}곳", "url": cfg["sources"][0]["url"] if cfg["sources"] else "", "kind": "rss"},
                          items, warn=warns)


if __name__ == "__main__":
    import sys
    from common import run_fetcher
    m = sys.argv[1] if len(sys.argv) > 1 else "it"
    run_fetcher(m, lambda: fetch(m))
