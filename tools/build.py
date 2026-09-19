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
