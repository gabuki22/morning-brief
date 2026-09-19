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
