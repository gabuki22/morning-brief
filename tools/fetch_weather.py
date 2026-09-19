# -*- coding: utf-8 -*-
"""날씨·대기 모듈 — Open-Meteo(키 없음). 좌표는 config/site.yaml, 파라미터는 config/sources.yaml.

한 행 = 한 위치의 하루 예보(카드 1장). 오늘 카드에 7일 시계열(최고·최저)과 대기질을 싣는다.
"""
from __future__ import annotations

import urllib.parse

from common import http_json, item_id, load_yaml, module_payload, run_fetcher

# WMO 날씨 코드 → 한국어. 코드 표는 Open-Meteo 문서 기준(바뀌지 않는 표준이라 여기 둔다).
WMO = {0: "맑음", 1: "대체로 맑음", 2: "구름 조금", 3: "흐림", 45: "안개", 48: "안개",
       51: "이슬비", 53: "이슬비", 55: "이슬비", 56: "언 이슬비", 57: "언 이슬비",
       61: "비", 63: "비", 65: "강한 비", 66: "언 비", 67: "언 비",
       71: "눈", 73: "눈", 75: "강한 눈", 77: "싸락눈", 80: "소나기", 81: "소나기", 82: "강한 소나기",
       85: "소낙눈", 86: "강한 소낙눈", 95: "뇌우", 96: "뇌우·우박", 99: "뇌우·우박"}


def fetch() -> dict:
    site = load_yaml("site")
    cfg = load_yaml("sources")["modules"]["weather"]
    p = cfg["params"]
    src = {s["name"]: s for s in cfg["sources"]}
    items, warns = [], []

    for loc in site["locations"]:
        q = urllib.parse.urlencode({
            "latitude": loc["lat"], "longitude": loc["lon"], "daily": p["daily"],
            "timezone": site["timezone"], "forecast_days": p["forecast_days"]})
        d = http_json(f'{src["Open-Meteo Forecast"]["url"]}?{q}')["daily"]

        pm10, pm25 = [], []
        try:
            aqq = urllib.parse.urlencode({
                "latitude": loc["lat"], "longitude": loc["lon"], "hourly": p["aq_hourly"],
                "timezone": site["timezone"], "forecast_days": 1})
            aq = http_json(f'{src["Open-Meteo Air Quality"]["url"]}?{aqq}')["hourly"]
            pm10 = [v for v in aq.get("pm10", []) if v is not None]
            pm25 = [v for v in aq.get("pm2_5", []) if v is not None]
        except Exception as e:  # 대기질은 없어도 날씨 카드는 산다
            warns.append(f"대기질 실패: {type(e).__name__}")

        # 드릴다운 링크: Open-Meteo 문서 페이지가 같은 좌표의 차트를 그린다
        page = f'https://open-meteo.com/en/docs?{q}'
        smax = [[t, v] for t, v in zip(d["time"], d["temperature_2m_max"])]
        smin = [[t, v] for t, v in zip(d["time"], d["temperature_2m_min"])]

        for i, day in enumerate(d["time"]):
            code = d["weather_code"][i]
            tmax, tmin, pop = d["temperature_2m_max"][i], d["temperature_2m_min"][i], d["precipitation_probability_max"][i]
            metrics = {"tmax": tmax, "tmin": tmin, "pop": pop, "code": code, "label": WMO.get(code, f"코드 {code}")}
            summary = f"강수확률 {pop}%"
            if i == 0:
                metrics["series"] = smax
                metrics["series2"] = smin
                if pm25 and pm10:
                    metrics["pm25_max"], metrics["pm10_max"] = max(pm25), max(pm10)
                    summary += f" · PM2.5 최대 {max(pm25):.0f} · PM10 최대 {max(pm10):.0f} ㎍/㎥"
            items.append({
                "id": item_id(f"weather:{loc['name']}:{day}"),
                "title": f"{day[5:].replace('-', '/')} {metrics['label']} {tmin:.0f}~{tmax:.0f}°",
                "url": page,
                "published_at": day,
                "summary": summary,
                "tags": ["날씨", loc["name"]],
                "metrics": metrics,
                "is_new": True,
                "streak_days": 1,
            })

    return module_payload("weather", {"name": "Open-Meteo", "url": "https://open-meteo.com/", "kind": "json"},
                          items, warn=warns)


if __name__ == "__main__":
    run_fetcher("weather", fetch)
