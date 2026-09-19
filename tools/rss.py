# -*- coding: utf-8 -*-
"""RSS/Atom 공용 파서 + 태그·묶음 도우미. 외부 의존성 없음(xml.etree).

fetch_feed(url)      → [{title, url, published_at, summary}]  (RSS 2.0 · RDF · Atom 전부)
tag_by_rules(text, rules) → 규칙 목록({tag, match:[…]})에 걸린 태그들
cluster(items)       → 제목 유사도(자카드)로 같은 사건 묶음 번호를 매긴다
"""
from __future__ import annotations

import email.utils
import html
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

from common import KST, http_get

_TAG = re.compile(r"<[^>]+>")
_WS = re.compile(r"\s+")
_TOKEN = re.compile(r"[가-힣A-Za-z0-9]{2,}")
STOP = {"이번", "오늘", "내일", "지난", "관련", "위해", "대한", "통해", "따라", "그리고", "하는", "있는", "에서", "으로", "the", "and", "for", "with"}


def strip_html(s: str | None) -> str:
    s = re.sub(r"<!\[CDATA\[(.*?)\]\]>", r"\1", s or "", flags=re.S)
    return _WS.sub(" ", html.unescape(_TAG.sub(" ", s))).strip()


def parse_date(s: str | None) -> str | None:
    """RFC822(RSS)·ISO8601(Atom) → KST ISO. 못 읽으면 None(수집기가 오늘 날짜로 채운다)."""
    if not s:
        return None
    s = s.strip()
    dt = None
    try:
        dt = email.utils.parsedate_to_datetime(s)
    except Exception:
        try:
            dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        except Exception:
            return None
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(KST).isoformat(timespec="seconds")


def _local(tag: str) -> str:
    return tag.split("}")[-1]


def _text(el, name: str) -> str:
    for c in el:
        if _local(c.tag) == name:
            return (c.text or "").strip()
    return ""


def _atom_link(el) -> str:
    fallback = ""
    for c in el:
        if _local(c.tag) == "link":
            rel = c.get("rel")
            href = (c.get("href") or c.text or "").strip()
            if rel in (None, "alternate"):
                return href
            fallback = fallback or href
    return fallback


def fetch_feed(url: str, limit: int = 30) -> list[dict]:
    root = ET.fromstring(http_get(url, timeout=15))
    is_atom = _local(root.tag) == "feed"
    entries = [el for el in root.iter() if _local(el.tag) == ("entry" if is_atom else "item")]
    out = []
    for e in entries[:limit]:
        if is_atom:
            title, link = strip_html(_text(e, "title")), _atom_link(e)
            date = parse_date(_text(e, "published") or _text(e, "updated"))
            summary = strip_html(_text(e, "summary") or _text(e, "content"))
        else:
            title, link = strip_html(_text(e, "title")), _text(e, "link")
            date = parse_date(_text(e, "pubDate") or _text(e, "date"))
            summary = strip_html(_text(e, "description") or _text(e, "encoded"))
        if title and link.startswith("http"):
            out.append({"title": title, "url": link, "published_at": date, "summary": summary[:160]})
    return out


_ASCII = re.compile(r"^[A-Za-z0-9&.+-]+$")


def _hit(term: str, low: str) -> bool:
    """영문·숫자 토큰(AI·PC·EV·TV)은 단어 경계로 — 'gmail' 안의 ai, 'PCB' 안의 PC 가 걸리지 않게. 한글은 부분 일치."""
    t = str(term)
    if _ASCII.match(t):
        return re.search(r"(?<![A-Za-z0-9])" + re.escape(t.lower()) + r"(?![A-Za-z0-9])", low) is not None
    return t.lower() in low


def tag_by_rules(text: str, rules: list[dict]) -> list[str]:
    low = text.lower()
    tags = []
    for r in rules or []:
        if any(_hit(m, low) for m in r.get("match", [])):
            if r["tag"] not in tags:
                tags.append(r["tag"])
    return tags


def _tokens(s: str) -> set[str]:
    return {t.lower() for t in _TOKEN.findall(s) if t.lower() not in STOP}


def cluster(items: list[dict], threshold: float = 0.45) -> dict[str, int]:
    """같은 사건을 다룬 기사끼리 묶는다 — 제목 토큰 자카드 ≥ threshold. 반환: {id: cluster_no}."""
    toks = [(it["id"], _tokens(it["title"])) for it in items]
    groups: list[list[int]] = []
    rep: list[set[str]] = []
    assign: dict[str, int] = {}
    for i, (iid, tk) in enumerate(toks):
        if not tk:
            assign[iid] = len(groups); groups.append([i]); rep.append(tk); continue
        best, best_j = 0.0, -1
        for j, r in enumerate(rep):
            if not r:
                continue
            jac = len(tk & r) / len(tk | r)
            if jac > best:
                best, best_j = jac, j
        if best >= threshold:
            groups[best_j].append(i); rep[best_j] = rep[best_j] | tk; assign[iid] = best_j
        else:
            assign[iid] = len(groups); groups.append([i]); rep.append(set(tk))
    return assign
