# 모듈 보드 — 한 세션은 한 행만 잡는다

> 시작: 계획서(볼트 `wiki/projects/Personal-Jarvis-모닝브리프-v3-Vercel-2026Q3.md`) §12 → 여기서 빈 행 하나 → `담당`에 모델·날짜 적고 커밋 → 그 모듈 파일만 만진다.
> 끝: 상태 갱신 + 실측 건수 + 막힌 것. 20분 넘게 막히면 `막힘`에 적고 넘긴다.

| 모듈 | 담당(모델·날짜) | 상태 | 소스 실측 | 항목 수 | 막힘 |
|---|---|---|---|---|---|
| 골격·계약·빌드 (Phase 1) | Fable 5.1 · 2026-09-19 | **완료** — config 4 · tools 6 · 화면 3 · docs 5 · Actions 골격 · 배포 https://morning-brief-omega-topaz.vercel.app (push → 자동 배포 확인, 제외 파일 404 확인) | — | — | — |
| 날씨·대기·공휴일 | Fable 5.1 · 2026-09-19 | **완료**(공휴일 표시는 미구현) | ○ Open-Meteo 2종 | 7 | 기상청 API허브 키(2순위) |
| 환율 | Fable 5.1 · 2026-09-19 | **완료** | ○ Frankfurter | 3 | — |
| 뉴스·반드시 알아야 할 것 | — | 대기 | ○ 9 · ✗ KBS | — | `fetch_news.py` — RSS 9곳 + 교차 매체 점수 |
| 지수 | — | 대기 | ○ 야후 4(비공식) | — | `fetch_markets.py` — FRED 키 있으면 2순위 |
| 코인 | — | 대기 | ○ 5/5 | — | `fetch_crypto.py` — big_move_pct 는 thresholds |
| 부동산 | — | 대기 | △ 3 | — | data.go.kr 키 발급 뒤 |
| IT·가전·사무기기 | — | 대기 | ○ 2 · ✗ 2 · △ 1 | — | 가전 피드 미탐색 · `fetch_rss_tagged.py`(IT·자동차 공용) |
| 자동차·프로모션 | — | 대기 | ○ 2 · ✗ 1 | — | 프로모션 페이지 구조 |
| 공공데이터 소식 | — | 대기 | △ | — | 포털 신규 목록 소스 |
| 레저·캠핑 | — | 대기 | △ 고캠핑 | — | data.go.kr 키 |
| 관심 키워드 태깅 | — | 대기 | ○ Naver 키 있음 | — | `config/interests.yaml` 적용은 뉴스 모듈과 함께 |
| 편집층 (Phase 3) + 와일드카드 | — | 대기 | — | — | Gemini 키 (`~/jarvis/secrets/gemini_api_key.txt`) |
| 자동화 (Phase 4) | — | 골격만 | — | — | Actions Secrets 4종 · cron 주석 해제 |
| 자기검토 (Phase 5) | — | 대기 | — | — | `docs/FEEDBACK.md` · 주간 REVIEW 루틴 |
| 과거 보기 `?d=` | — | 대기 | — | — | 일별 스냅샷 보존 방식 결정 |
