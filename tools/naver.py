# -*- coding: utf-8 -*-
"""Naver 뉴스 검색 — 키는 경로로만(NAVER_CLIENT_ID / NAVER_CLIENT_SECRET). 키가 없으면 빈 목록."""
from __future__ import annotations

import json
import urllib.parse
import urllib.request

from common import UA, get_secret
from rss import parse_date, strip_html

API = "https://openapi.naver.com/v1/search/news.json"


def has_key() -> bool:
    return bool(get_secret("NAVER_CLIENT_ID") and get_secret("NAVER_CLIENT_SECRET"))


def search(query: str, n: int = 5, sort: str = "date") -> list[dict]:
    cid, csec = get_secret("NAVER_CLIENT_ID"), get_secret("NAVER_CLIENT_SECRET")
    if not (cid and csec):
        return []
    url = f"{API}?query={urllib.parse.quote(query)}&display={min(n, 100)}&sort={sort}"
    req = urllib.request.Request(url, headers={**UA, "X-Naver-Client-Id": cid, "X-Naver-Client-Secret": csec})
    with urllib.request.urlopen(req, timeout=15) as r:
        d = json.loads(r.read().decode("utf-8"))
    out = []
    for it in d.get("items", []):
        link = it.get("originallink") or it.get("link") or ""
        if link.startswith("http"):
            out.append({"title": strip_html(it.get("title")), "url": link,
                        "published_at": parse_date(it.get("pubDate")), "summary": strip_html(it.get("description"))[:160]})
    return out
