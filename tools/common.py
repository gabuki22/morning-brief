# -*- coding: utf-8 -*-
"""공통 — 설정 읽기 · 비밀 경로 · HTTP · JSON 저장 · 항목 id.

규칙: 값을 코드에 박지 않는다(config/*.yaml). 비밀은 경로만 다루고 값은 절대 출력하지 않는다.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = ROOT / "config"
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
HISTORY_DIR = DATA_DIR / "history"
KST = timezone(timedelta(hours=9))
UA = {"User-Agent": "morning-brief/0.1 (personal, non-commercial)"}

if hasattr(sys.stdout, "reconfigure"):          # Windows 콘솔(cp949)에서 한글 출력
    sys.stdout.reconfigure(encoding="utf-8")


def now_kst() -> datetime:
    return datetime.now(KST)


def today_str() -> str:
    return now_kst().strftime("%Y-%m-%d")


def load_yaml(name: str) -> dict:
    with open(CONFIG_DIR / f"{name}.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def get_secret(name: str) -> str | None:
    """환경변수 → ~/jarvis/secrets/<name 소문자>.txt → None. 값은 절대 출력하지 않는다."""
    v = os.environ.get(name)
    if v and v.strip():
        return v.strip()
    p = Path.home() / "jarvis" / "secrets" / f"{name.lower()}.txt"
    if p.is_file():
        v = p.read_text(encoding="utf-8").strip()
        return v or None
    return None


def http_get(url: str, timeout: int = 15, retries: int = 3) -> bytes:
    """429·일시 오류는 5·10·20초 뒤 재시도. 그 외 HTTP 오류는 바로 올린다."""
    backoff = (5, 10, 20)
    last: Exception | None = None
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            last = e
            if e.code == 429 and i < retries - 1:
                time.sleep(backoff[min(i, len(backoff) - 1)])
                continue
            raise
        except Exception as e:  # 네트워크 일시 오류
            last = e
            if i < retries - 1:
                time.sleep(backoff[min(i, len(backoff) - 1)])
                continue
            raise
    raise last  # pragma: no cover


def http_json(url: str, **kw) -> dict | list:
    return json.loads(http_get(url, **kw).decode("utf-8"))


TRACKING = {"utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "fbclid", "gclid", "ref"}


def normalize_url(url: str) -> str:
    """추적 파라미터 제거 · 소문자 호스트 · 끝 슬래시 제거 — 같은 기사가 다른 id를 갖지 않게."""
    u = urllib.parse.urlsplit(url.strip())
    q = [(k, v) for k, v in urllib.parse.parse_qsl(u.query, keep_blank_values=True)
         if k.lower() not in TRACKING]
    path = u.path.rstrip("/") or "/"
    return urllib.parse.urlunsplit((u.scheme.lower(), u.netloc.lower(), path, urllib.parse.urlencode(q), ""))


def item_id(key: str) -> str:
    """항목 id = sha1(정규화 url) 앞 16자. url 이 아닌 키(날씨:집:날짜)도 그대로 받는다."""
    if key.startswith(("http://", "https://")):
        key = normalize_url(key)
    return hashlib.sha1(key.encode("utf-8")).hexdigest()[:16]


def save_json(path: Path, obj) -> None:
    """encode 먼저 → 임시 파일 → 교체. 인코딩 오류로 0바이트 파일이 남지 않게."""
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(obj, ensure_ascii=False, indent=1).encode("utf-8")
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_bytes(data)
    tmp.replace(path)


def load_json(path: Path, default=None):
    if not path.is_file():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def module_payload(module: str, source: dict, items: list, warn: list | None = None,
                   error: str | None = None) -> dict:
    """docs/CONTRACT.md 의 모듈 파일 형식. 모든 수집기는 이걸로 끝낸다."""
    return {
        "module": module,
        "fetched_at": now_kst().isoformat(timespec="seconds"),
        "source": source,
        "items": items,
        "status": {"ok": error is None, "count": len(items), "warn": warn or [], "error": error},
    }


def write_raw(module: str, payload: dict) -> dict:
    save_json(RAW_DIR / f"{module}.json", payload)
    return payload


def run_fetcher(module: str, fn) -> dict:
    """수집기 본체를 감싼다 — 실패해도 파일은 남긴다(status.error). 한 모듈이 죽어도 나머지는 간다."""
    try:
        payload = fn()
    except Exception as e:
        payload = module_payload(module, {}, [], error=f"{type(e).__name__}: {str(e)[:200]}")
    write_raw(module, payload)
    st = payload["status"]
    print(f"[{module}] {'ok' if st['ok'] else 'FAIL'} count={st['count']} {st['error'] or ''}".rstrip())
    return payload
