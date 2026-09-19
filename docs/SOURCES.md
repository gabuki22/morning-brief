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

## 2026-09-19 오후 (모듈 구현 중 추가 실측)

| 상태 | 소스 | 결과 |
|---|---|---|
| ○ | 한국경제 부동산 `/feed/realestate` 50 · 한국경제 IT `/feed/it` 50 | 200 — IT 는 진짜 IT 기사 |
| ○ | 연합 경제 `economy.xml` 120 · 조선 경제 100 · 동아 경제 50 · 경향 경제 50 · 한겨레 경제 30 | 200 |
| ✗ | 매경 섹션 피드(50300009 · 30100041) | 403 — 헤드라인 `30000001` 만 씀 |
| ✗ | 연합 `it.xml`·`science.xml`·`technology.xml` | 404. `industry.xml` 은 이름과 달리 산업·지역 종합 → 태그 필터로만 |
| △ | 전자신문 901·902·02 · 블로터 | 종합 피드 — 태그 필터로만 |
| ✗ | 한경 `/feed/car` · ITWorld | 404 |
| ○ | 야후 코스닥 `^KQ11` | 200 |
| ○ | CoinGecko `/en/coins/<id>` | 200 (`/ko/coins/` 는 404, `/ko/코인/` 은 200) |
| ○ | 업비트 마켓 목록 855 · CoinGecko KRW top20 | 200 |
| ○ | Naver 뉴스 검색 API | 키로 동작 확인("캠핑장 개장" 29,334건) |
| ✗ | data.go.kr·통계청·정책브리핑 RSS(추정 주소) | 404 — 공공 신규 데이터 목록 소스는 미해결 |

## 잔여 탐색 (키 발급 뒤)

data.go.kr: LH 분양·임대공고 · 온비드 공매물건 · 고캠핑 / FRED 키 / 기상청 API허브 / 가전·사무기기 피드 / KBS·IT조선 대체 주소
