# -*- coding: utf-8 -*-
"""뉴스 모듈 — 매체 RSS 여러 곳을 받아 태그를 붙이고, 같은 사건은 묶어 '다룬 매체 수'를 센다.

한 행 = 기사 1건. metrics.outlets = 그 사건을 다룬 매체 수(편집층 점수의 재료).
"""
from __future__ import annotations

from common import item_id, load_yaml, module_payload, run_fetcher, today_str
from rss import cluster, fetch_feed, tag_by_rules


def fetch() -> dict:
    cfg = load_yaml("sources")["modules"]["news"]
    p = cfg.get("params", {})
    interests = load_yaml("interests").get("keywords", [])
    rules = list(p.get("tag_rules", [])) + [{"tag": k["tag"], "match": k["match"]} for k in interests]
    items, warns, seen, outlets = [], [], set(), 0
    for s in cfg["sources"]:
        if s.get("kind") not in ("rss", "atom") or s.get("enabled", True) is False:
            continue
        try:
            feed = fetch_feed(s["url"], limit=int(p.get("per_outlet", 15)))
        except Exception as e:
            warns.append(f"{s['name']} 실패: {type(e).__name__}")
            continue
        outlets += 1
        for f in feed:
            iid = item_id(f["url"])
            if iid in seen:
                continue
            seen.add(iid)
            items.append({
                "id": iid, "title": f["title"], "url": f["url"],
                "published_at": f["published_at"] or today_str(), "summary": f["summary"],
                "tags": tag_by_rules(f["title"] + " " + f["summary"], rules),
                "metrics": {}, "is_new": True, "streak_days": 1, "source_name": s["name"],
            })
    groups = cluster(items)
    by_group: dict[int, set[str]] = {}
    group_tags: dict[int, set[str]] = {}
    for it in items:
        g = groups[it["id"]]
        by_group.setdefault(g, set()).add(it["source_name"])
        group_tags.setdefault(g, set()).update(it["tags"])
    for it in items:
        g = groups[it["id"]]
        it["metrics"]["cluster"] = g
        it["metrics"]["outlets"] = len(by_group[g])
        # 같은 사건의 다른 매체 기사에 붙은 태그도 물려받는다 — 편집층 점수는 사건 단위로 매긴다
        it["metrics"]["cluster_tags"] = sorted(group_tags[g])
    items.sort(key=lambda it: (-it["metrics"]["outlets"], it["published_at"] or ""))
    return module_payload("news", {"name": f"매체 RSS {outlets}곳", "url": "https://news.google.com/?hl=ko&gl=KR", "kind": "rss"},
                          items, warn=warns)


if __name__ == "__main__":
    run_fetcher("news", fetch)
