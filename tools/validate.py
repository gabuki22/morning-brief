# -*- coding: utf-8 -*-
"""계약(docs/CONTRACT.md) 검증 — 통과 / 경고 / 차단. 코드가 아는 건 필드 이름과 config/thresholds.yaml 뿐.

차단 = 이 문제를 안고는 계산이 틀린다(필드 없음 · id 중복 · 수집 실패 · 0건 · 금지어)
경고 = 계산은 되지만 해석에 영향(하한 미달 · 링크 확인 실패)

사용: py -X utf8 tools/validate.py <모듈> [--no-net]      (차단이면 종료코드 1)
"""
from __future__ import annotations

import json
import sys

from common import RAW_DIR, get_secret, http_get, load_json, load_yaml

REQ_TOP = ("module", "fetched_at", "source", "items", "status")
REQ_ITEM = ("id", "title", "url", "published_at", "summary", "tags", "metrics", "is_new", "streak_days")


def load_banned() -> list[str]:
    """금지어는 저장소에 두지 않는다 — 비밀 경로(BANNED_WORDS, 쉼표 구분)에서만 읽는다."""
    raw = get_secret("BANNED_WORDS") or ""
    return [w.strip() for w in raw.split(",") if w.strip()]


def validate_module(payload: dict, thresholds: dict, module: str | None = None, net: bool = True) -> dict:
    module = module or payload.get("module")
    warns, blocks = [], []
    for k in REQ_TOP:
        if k not in payload:
            blocks.append(f"상위 필드 없음: {k}")
    items = payload.get("items") or []
    seen = set()
    for i, it in enumerate(items):
        for k in REQ_ITEM:
            if k not in it:
                blocks.append(f"items[{i}] 필드 없음: {k}")
        url = str(it.get("url") or "")
        if not url.startswith(("http://", "https://")):
            blocks.append(f"items[{i}] url 형식")
        if it.get("id") in seen:
            blocks.append(f"items[{i}] id 중복")
        seen.add(it.get("id"))

    st = payload.get("status") or {}
    if st.get("error"):
        blocks.append(f"수집 실패: {st['error']}")

    minimum = (thresholds.get("min_items") or {}).get(module)
    if minimum is not None:
        if len(items) == 0:
            blocks.append("항목 0건")
        elif len(items) < minimum:
            warns.append(f"항목 {len(items)}건 (하한 {minimum})")

    banned = load_banned()
    if banned:
        text = json.dumps(payload, ensure_ascii=False)
        hits = sum(1 for w in banned if w in text)
        if hits:
            blocks.append(f"금지어 {hits}건")          # 금지어 자체는 출력하지 않는다

    if net and items:
        n = int(thresholds.get("link_check_sample", 3))
        bad = 0
        for it in items[:n]:
            try:
                http_get(it["url"], timeout=int(thresholds.get("link_check_timeout_sec", 6)), retries=1)
            except Exception:
                bad += 1
        if bad:
            warns.append(f"링크 확인 실패 {bad}/{min(n, len(items))}")

    level = "block" if blocks else ("warn" if warns else "ok")
    return {"module": module, "level": level, "warn": warns, "block": blocks, "count": len(items)}


def main(argv: list[str]) -> int:
    args = [a for a in argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__)
        return 2
    th = load_yaml("thresholds")
    net = "--no-net" not in argv
    rc = 0
    for module in args:
        payload = load_json(RAW_DIR / f"{module}.json")
        if payload is None:
            print(f"[{module}] block: 수집 파일 없음 (data/raw/{module}.json)")
            rc = 1
            continue
        v = validate_module(payload, th, module, net=net)
        print(f"[{module}] {v['level']} count={v['count']}"
              + (f" warn={v['warn']}" if v["warn"] else "")
              + (f" block={v['block']}" if v["block"] else ""))
        if v["level"] == "block":
            rc = 1
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
