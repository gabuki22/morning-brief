# 데이터 계약 — 수집과 화면을 잇는 한 장

모든 모듈은 같은 형식을 낸다. 화면은 여기 없는 필드를 기대하지 않고, 모듈이 이 형식을 어기면 `tools/validate.py`가 막는다.
**병렬 작업의 계약이 이 파일이다.** 바꾸려면 `CHANGELOG.md`에 이유를 적고, `tools/validate.py`·`app.js`를 같이 고친다.

## 모듈 파일 `data/raw/<module>.json` → 빌드 후 `data/<module>.json`

```json
{
  "module": "news",
  "fetched_at": "2026-09-20T06:21:04+09:00",
  "source": {"name": "연합뉴스", "url": "https://www.yna.co.kr/rss/news.xml", "kind": "rss"},
  "items": [
    {
      "id": "sha1(url 정규화) 앞 16자",
      "title": "제목 그대로",
      "url": "https://... (반드시 있어야 한다 — 링크 없는 카드는 만들지 않는다)",
      "published_at": "2026-09-20T05:40:00+09:00 (날짜만이어도 됨)",
      "summary": "본문 첫 문장 또는 RSS description 120자",
      "tags": ["경제", "부동산"],
      "metrics": {},
      "is_new": true,
      "streak_days": 1
    }
  ],
  "status": {"ok": true, "count": 120, "warn": [], "error": null}
}
```

- `id`: `tools/common.item_id()` — url 이면 추적 파라미터를 뗀 정규화 url 의 sha1, 시계열 항목은 `모듈:이름:키` 같은 고정 키(매일 같은 id 가 정상 → `sources.yaml` 의 `same_ids_ok`).
- `is_new`·`streak_days`: 수집기는 `true`·`1`로 두고, **빌드가 어제 이력과 비교해 덮어쓴다.**
- 시계열 모듈(지수·코인·날씨·환율)은 `metrics`에 `{"series": [[날짜, 값], …], "series2": …(선택), "last": 값, "chg_1d": %}` — 화면은 이걸로 스파크라인만 그린다.
- `status.error`가 있으면 그 모듈은 차단(카드 대신 "수집 실패"). 한 모듈의 실패가 다른 모듈을 막지 않는다.

## 매니페스트 `data/index.json` (빌드가 만든다)

```json
{
  "built_at": "…", "date": "2026-09-20",
  "site": {"title": "모닝브리프", "locations": ["집"], "tabs": [{"module": "weather", "label": "날씨"}]},
  "modules": {"weather": {"level": "ok|warn|block|off", "count": 7, "warn": [], "block": [], "fetched_at": "…", "repeat_ratio": 0.0}},
  "must_know": [{"item_ids": ["…"], "why": "한 줄", "module": "news"}],
  "banned_hits": 0
}
```

`banned_hits > 0` 이면 빌드 종료코드 2 → GitHub Actions 가 실패해 커밋·배포가 안 된다.

## 이력 `data/history/YYYY-MM-DD.json`

`{"date": "…", "ids": {"news": {"<id>": streak_days, …}}}` — 반복 판정의 재료. `site.yaml history_days` 만큼 보존.

## 판정 규칙 (`config/thresholds.yaml`)

| 판정 | 언제 | 결과 |
|---|---|---|
| 차단 | 필드 없음 · id 중복 · 수집 실패 · 0건 · 금지어 | 그 모듈만 "수집 실패" 카드 |
| 경고 | 하한 미달 · 링크 표본 실패 · 어제 동일 비율 초과 | 카드는 뜨고 상태줄에 표시 |
| 통과 | 그 외 | — |

금지어 목록은 저장소에 두지 않는다 — 비밀 경로 `BANNED_WORDS`(쉼표 구분)에서만 읽고, 걸려도 단어는 출력하지 않는다.
