# -*- coding: utf-8 -*-
"""빌드 — 수집 결과(data/raw) → 검증 → 어제와 비교 → data/<모듈>.json + data/index.json + history.

계산에 현재 시각을 쓰지 않는다(기준일 = 오늘 날짜 문자열). 금지어가 걸리면 종료코드 2 → 배포 중단.

사용: py -X utf8 tools/build.py [--only weather,fx] [--no-net]
"""
from __future__ import annotations

import sys

from common import DATA_DIR, HISTORY_DIR, RAW_DIR, load_json, load_yaml, now_kst, save_json, today_str
from validate import validate_module


def _previous_ids(today: str) -> dict:
    """오늘보다 앞선 가장 최근 이력 — 어제가 비었어도 마지막 것을 쓴다."""
    files = sorted(p for p in HISTORY_DIR.glob("*.json") if p.stem < today)
    return (load_json(files[-1], {}) or {}).get("ids", {}) if files else {}


def _prune_history(keep_days: int) -> None:
    files = sorted(HISTORY_DIR.glob("*.json"))
    for p in files[:-keep_days] if keep_days > 0 else []:
        p.unlink()


def _must_know(index: dict, site: dict, th: dict) -> list[dict]:
    """편집층(규칙형) — 매체 수·관심 태그·새로움으로 점수를 매겨 사건(cluster)당 하나씩 고른다.
    LLM 편집은 Phase 3 — 그때도 이 목록이 폴백이다(핵심교안: LLM 없이도 돌아야 한다)."""
    cfg = th.get("must_know") or {}
    n = int(site.get("must_know_count", 5))
    picks: list[dict] = []
    news = load_json(DATA_DIR / "news.json")
    if news and index["modules"].get("news", {}).get("level") in ("ok", "warn"):
        interests = {k["tag"] for k in load_yaml("interests").get("keywords", [])}
        weights = cfg.get("tag_weights") or {}
        max_per_tag = int(cfg.get("max_per_tag", 99))
        scored = []
        for it in news.get("items", []):
            m = it.get("metrics", {})
            tags = m.get("cluster_tags") or it.get("tags", [])       # 사건 단위 태그(같은 사건의 다른 매체 것 포함)
            score = int(m.get("outlets", 1)) * int(cfg.get("outlets_weight", 3)) \
                + (int(cfg.get("interest_bonus", 2)) if set(tags) & interests else 0) \
                + (int(cfg.get("new_bonus", 1)) if it.get("is_new") else 0) \
                + sum(int(weights.get(t, 0)) for t in tags)
            scored.append((score, it))
        scored.sort(key=lambda x: -x[0])
        seen, tag_count = set(), {}
        for score, it in scored:
            c = it.get("metrics", {}).get("cluster")
            if c in seen:
                continue
            ctags = it.get("metrics", {}).get("cluster_tags") or it.get("tags") or []
            first_tag = (ctags or ["(없음)"])[0]
            if tag_count.get(first_tag, 0) >= max_per_tag:
                continue
            seen.add(c)
            tag_count[first_tag] = tag_count.get(first_tag, 0) + 1
            why = f"매체 {it['metrics'].get('outlets', 1)}곳" \
                + (" · " + "·".join(ctags[:3]) if ctags else "") \
                + ("" if it.get("is_new") else f" · {it.get('streak_days', 1)}일째 이어짐")
            picks.append({"module": "news", "item_ids": [it["id"]], "title": it["title"], "url": it["url"],
                          "why": why, "score": score})
            if len(picks) >= n:
                break
    crypto = load_json(DATA_DIR / "crypto.json")
    slots = int(cfg.get("crypto_big_move_slots", 1))
    if crypto and slots:
        big = [it for it in crypto.get("items", []) if "큰 변동" in it.get("tags", [])][:slots]
        if big:
            picks = picks[: max(0, n - len(big))] + [
                {"module": "crypto", "item_ids": [it["id"]], "title": it["title"], "url": it["url"],
                 "why": "큰 변동 · " + it["summary"], "score": 0} for it in big]
    return picks[:n]


def build(only: set[str] | None = None, net: bool = True) -> dict:
    site, sources, th = load_yaml("site"), load_yaml("sources"), load_yaml("thresholds")
    today = today_str()
    prev_ids = _previous_ids(today)
    index = {
        "built_at": now_kst().isoformat(timespec="seconds"),
        "date": today,
        "site": {"title": site["title"], "locations": [l["name"] for l in site["locations"]],
                 "tabs": [t for t in site.get("tabs", []) if t.get("enabled", True)]},
        "modules": {},
        "must_know": [],          # Phase 3 편집층이 채운다
        "banned_hits": 0,
    }
    today_ids: dict[str, dict] = {}

    for module, cfg in sources["modules"].items():
        if not cfg.get("enabled"):
            index["modules"][module] = {"level": "off", "count": 0, "warn": [], "block": []}
            continue
        if only and module not in only:
            prev_pub = load_json(DATA_DIR / f"{module}.json")
            if prev_pub:                                   # 이번 빌드 대상이 아니면 지난 결과를 그대로 둔다
                st = prev_pub.get("status", {})
                index["modules"][module] = {"level": st.get("level", "ok"), "count": st.get("count", 0),
                                            "warn": st.get("warn", []), "block": st.get("block", []),
                                            "fetched_at": prev_pub.get("fetched_at"), "kept": True}
            continue

        payload = load_json(RAW_DIR / f"{module}.json")
        if payload is None:
            index["modules"][module] = {"level": "block", "count": 0, "warn": [], "block": ["수집 파일 없음"]}
            continue

        v = validate_module(payload, th, module, net=net)

        # 어제와 비교 — 같은 id 면 이어짐(streak+1), 없으면 새로움
        pm = prev_ids.get(module, {})
        items = payload.get("items") or []
        for it in items:
            if it["id"] in pm:
                it["is_new"], it["streak_days"] = False, int(pm[it["id"]]) + 1
            else:
                it["is_new"], it["streak_days"] = True, 1
        today_ids[module] = {it["id"]: it["streak_days"] for it in items}
        repeat = (sum(1 for it in items if not it["is_new"]) / len(items)) if items else 0.0
        # 시계열 모듈(날씨·환율)은 매일 같은 id 가 정상 → sources.yaml 의 same_ids_ok
        if not cfg.get("same_ids_ok") and repeat > float(th.get("repeat_ratio_warn", 0.2)):
            v["warn"].append(f"어제와 동일 {repeat:.0%}")
            v["level"] = "warn" if v["level"] == "ok" else v["level"]

        payload["status"].update({"level": v["level"], "warn": v["warn"], "block": v["block"]})
        save_json(DATA_DIR / f"{module}.json", payload)
        index["modules"][module] = {"level": v["level"], "count": v["count"], "warn": v["warn"],
                                    "block": v["block"], "fetched_at": payload["fetched_at"],
                                    "repeat_ratio": round(repeat, 3)}
        if any("금지어" in b for b in v["block"]):
            index["banned_hits"] += 1

    index["must_know"] = _must_know(index, site, th)
    save_json(HISTORY_DIR / f"{today}.json", {"date": today, "ids": today_ids})
    _prune_history(int(site.get("history_days", 90)))
    save_json(DATA_DIR / "index.json", index)

    for m, s in index["modules"].items():
        print(f"[build] {m:12s} {s['level']:5s} count={s.get('count', 0)}"
              + (f" warn={s['warn']}" if s.get("warn") else "") + (f" block={s['block']}" if s.get("block") else ""))
    if index["banned_hits"]:
        print(f"[build] 금지어 검출 {index['banned_hits']}모듈 — 배포하지 않는다")
    return index


def main(argv: list[str]) -> int:
    only = None
    for a in argv[1:]:
        if a.startswith("--only"):
            val = a.split("=", 1)[1] if "=" in a else argv[argv.index(a) + 1]
            only = {x.strip() for x in val.split(",") if x.strip()}
    index = build(only=only, net="--no-net" not in argv)
    return 2 if index["banned_hits"] else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
