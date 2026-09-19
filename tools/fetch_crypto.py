# -*- coding: utf-8 -*-
"""코인 모듈 — CoinGecko(시총 상위, KRW) + 업비트 일봉(시계열) + 빗썸·바이낸스 교차값.

한 행 = 코인 1개. |24h 변동| ≥ big_move_pct(thresholds/sources 설정)면 '큰 변동' 태그 + Naver 뉴스 2건(키 있을 때).
"""
from __future__ import annotations

from common import http_json, item_id, load_yaml, module_payload, run_fetcher, today_str
import naver


def fetch() -> dict:
    cfg = load_yaml("sources")["modules"]["crypto"]
    p = cfg["params"]
    src = {s["name"]: s for s in cfg["sources"]}
    warns = []

    top = http_json(src["CoinGecko markets"]["url"])[: int(p["top_n"])]

    bithumb_btc = None
    try:
        bithumb_btc = float(http_json(src["Bithumb ticker"]["url"])["data"]["closing_price"])
    except Exception as e:
        warns.append(f"빗썸 실패: {type(e).__name__}")
    binance_btc = None
    try:
        kl = http_json(src["Binance klines"]["url"])
        binance_btc = float(kl[-1][4])
    except Exception as e:
        warns.append(f"바이낸스 실패: {type(e).__name__}")

    items = []
    for c in top:
        sym = (c.get("symbol") or "").upper()
        chg24 = float(c.get("price_change_percentage_24h_in_currency") or c.get("price_change_percentage_24h") or 0.0)
        chg7 = c.get("price_change_percentage_7d_in_currency")
        big = abs(chg24) >= float(p["big_move_pct"])
        tags = ["코인"] + (["큰 변동"] if big else [])
        metrics = {"last": c.get("current_price"), "chg_1d": round(chg24, 2),
                   "chg_7d": round(float(chg7), 2) if chg7 is not None else None,
                   "market_cap_rank": c.get("market_cap_rank")}
        market = (p.get("upbit_series") or {}).get(sym)
        if market:
            try:
                cd = http_json(f'{src["Upbit candles"]["url"]}?market={market}&count={int(p["days"])}')
                metrics["series"] = sorted([[x["candle_date_time_kst"][:10], x["trade_price"]] for x in cd])
            except Exception as e:
                warns.append(f"업비트 {market} 실패: {type(e).__name__}")
        if sym == "BTC":
            if bithumb_btc:
                metrics["bithumb_krw"] = bithumb_btc
            if binance_btc:
                metrics["binance_usdt"] = binance_btc
        news = []
        if big and naver.has_key():
            try:
                news = [{"title": n["title"], "url": n["url"]} for n in naver.search(f"{c.get('name')} 코인", n=2)]
            except Exception as e:
                warns.append(f"{sym} 뉴스 검색 실패: {type(e).__name__}")
        metrics["news"] = news
        summary = f"24시간 {chg24:+.2f}%" + (f" · 7일 {float(chg7):+.2f}%" if chg7 is not None else "") \
            + f" · 시총 {c.get('market_cap_rank')}위"
        if sym == "BTC" and bithumb_btc:
            summary += f" · 빗썸 ₩{bithumb_btc:,.0f}"
        if news:
            summary += f" · 이슈: {news[0]['title'][:40]}"
        items.append({
            "id": item_id(f"crypto:{c.get('id')}"),
            "title": f"{c.get('name')} ({sym}) ₩{float(c.get('current_price') or 0):,.0f}",
            "url": f'{src["CoinGecko markets"]["page"]}{c.get("id")}',
            "published_at": today_str(), "summary": summary, "tags": tags,
            "metrics": metrics, "is_new": True, "streak_days": 1, "source_name": "CoinGecko",
        })
    items.sort(key=lambda it: (0 if "큰 변동" in it["tags"] else 1, it["metrics"]["market_cap_rank"] or 999))
    return module_payload("crypto", {"name": "CoinGecko + Upbit + Bithumb + Binance", "url": "https://www.coingecko.com/ko", "kind": "json"},
                          items, warn=warns)


if __name__ == "__main__":
    run_fetcher("crypto", fetch)
