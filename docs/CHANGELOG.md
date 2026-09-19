# 변경 이력 — 설정·계약이 바뀌면 누가·언제·무엇을·어떤 값에서 어떤 값으로

| 날짜 | 누가 | 무엇 | 전 → 후 | 왜 |
|---|---|---|---|---|
| 2026-09-19 | Fable 5.1 | 저장소 신설 · 계약 v1 · 날씨·환율 모듈 | — → v0.1 | 계획서 Phase 1 |
| 2026-09-19 | 기쁨(결정) | `site.yaml locations` | — → 집 37.32,126.82 | 안산 단원구, 동 단위 좌표 |
| 2026-09-19 | Fable 5.1 | `thresholds.yaml` | — → 실측 건수의 절반 | 2주 뒤 재조정 |
| 2026-09-19 | Fable 5.1 | 모듈 8종 추가(뉴스·지수·코인·부동산·IT·자동차·레저·공공데이터) · `site.yaml tabs` 전부 켬 | v0.1 → v0.2 | 기쁨 "모든 화면 구현" |
| 2026-09-19 | Fable 5.1 | `thresholds.yaml must_know.tag_weights` | — → 정치 -4 · 경제/부동산/IT +2 · 자동차 +1 · max_per_tag 2 | 매체 수만으로 정치 기사가 상위 독점 |
| 2026-09-19 | Fable 5.1 | `sources.yaml crypto page` | `/ko/coins/` → `/en/coins/` | 404 실측 |
| 2026-09-19 | Fable 5.1 | `sources.yaml it` | 연합 IT·과학(실은 산업 종합) → 한경 IT 추가 + 종합 피드 `require_tags` | 농촌·지역 기사 혼입 |
| 2026-09-19 | Fable 5.1 | `tools/rss.py tag_by_rules` | 부분 일치 → 영문 토큰은 단어 경계 | "gmail" 안의 ai 가 AI 태그로 |
| 2026-09-19 | Fable 5.1 (기쁨 폰 피드백) | 화면: 탭 상단 고정(sticky)·줄바꿈 · 칩 줄바꿈 + 카드만 다시 그림 · 날씨 7일 두 줄 · 긴 영문 줄바꿈 | 가로 스크롤 → 줄바꿈·고정 | 탭 누르려면 위로 올라가야 했고, 칩 누르면 맨 왼쪽으로 튀고, 칸이 잘렸다 |
| 2026-09-19 | Fable 5.1 | `.github/workflows/daily.yml schedule` | 주석 → `20 21 * * *`(06:20 KST) | 기쁨 "매일 갱신되는 거지?" — 그 전까진 수동뿐이었다 |
| 2026-09-19 | Fable 5.1 | `daily.yml` actions/checkout v4→v6 · setup-python v5→v6 | Node 20 경고 | 클라우드 첫 실행 경고 |
| 2026-09-19 | Fable 5.1 | `tools/build.py` 수집기 경고 보존 | 검증 경고로 덮어씀 → 앞에 이어 붙임 | 클라우드 빌드에서 레저 1건인 이유(Naver 키 없음)가 화면에 안 보였다 |
