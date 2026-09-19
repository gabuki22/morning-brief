# 소스 레지스트리 — 실측 기록

정본은 `config/sources.yaml`(코드가 읽는 곳). 이 문서는 **실측 이력**만 쌓는다 — 추측으로 적지 않는다.
실측 도구: `py -X utf8 tools/probe_sources.py [모듈]` → 결과를 날짜와 함께 아래에 덧붙인다.

## 2026-09-19 (계획 수립일, 키 없이)

| 상태 | 소스 | 결과 |
|---|---|---|
| ○ | Open-Meteo Forecast / Air Quality | 200 json |
| ○ | Nager.Date 공휴일 KR 2026 | 200 json 18건 |
| ○ | Frankfurter USD→KRW·JPY·EUR | 200 json |
| ○ | Upbit ticker·candles · Bithumb · Binance klines · CoinGecko markets | 200 json |
| ○ | Yahoo chart ^KS11·^IXIC·^N225·^GSPC (1mo) | 200 json 22~24점 — **비공식** |
| ✗ | Stooq CSV | 200 이지만 HTML 반환 — 보류 |
| ○ | RSS: 연합 120 · 조선 100 · 매경 50 · 경향 50 · 동아 50 · 한경 50 · 한겨레 30 · SBS 29 · 구글뉴스KR 33 | 200 xml |
| ✗ | KBS RSS | 404 — 주소 재탐색 |
| ○ | 지디넷코리아 30 · 전자신문 28 | 200 xml |
| ✗ | IT조선 403 · 디지털데일리 HTML · 글로벌오토뉴스 403 | — |
| △ | The Verge | 200 Atom(`<entry>`) — 파서 필요 |
| ○ | 모터그래프 50 · 오토헤럴드 50 | 200 xml |
| △ | LH 청약플러스 · 온비드 · 법원경매정보 | 200 이지만 JS 렌더(87~847B) — API 키 필요 |
| △ | 공공데이터포털 · 기상청 API허브 | 페이지 200, API 는 키 |

## 잔여 탐색 (키 발급 뒤)

data.go.kr: LH 분양·임대공고 · 온비드 공매물건 · 고캠핑 / FRED 키 / 기상청 API허브 / 가전·사무기기 피드 / KBS·IT조선 대체 주소
