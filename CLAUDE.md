# morning-brief — 이 저장소에서 일하는 규칙

계획·배경은 볼트 `wiki/projects/Personal-Jarvis-모닝브리프-v3-Vercel-2026Q3.md`. 여기엔 지킬 것만 적는다.

## 구조
```
tools/   수집(fetch_*.py) → 검증(validate.py) → 빌드(build.py) → 진입점 run_all.py · 실측 probe_sources.py
config/  site.yaml(위치·탭) · sources.yaml(소스 레지스트리) · thresholds.yaml(임계값) · interests.yaml(관심 키워드)
data/    raw/(git 제외) → <module>.json + index.json (커밋·배포) · history/(반복 판정, 배포 제외)
docs/    CONTRACT.md(계약) · BOARD.md(모듈 보드) · SOURCES.md(실측 이력) · FEEDBACK.md · CHANGELOG.md
index.html · app.js · style.css   브라우저는 JSON 을 그리기만 한다
```

## 규칙
1. **값을 코드에 박지 않는다.** 소스 주소·임계값·좌표·탭·키워드는 `config/*.yaml`. 바꾸면 `docs/CHANGELOG.md` 한 줄.
2. **비밀은 경로만.** `tools/common.get_secret(NAME)` = 환경변수 → `~/jarvis/secrets/<name>.txt`. 값을 읽어 출력·커밋·채팅에 올리지 않는다. 금지어 목록도 `BANNED_WORDS` 비밀로만.
3. **공개 URL이다.** 회사명·거래처·인명·볼트 경로·개인 주소 0. 위치는 동 단위 좌표와 "집" 같은 이름만.
4. **계약을 지킨다.** 모든 모듈은 `docs/CONTRACT.md` 형식으로 끝나고 `py -X utf8 tools/validate.py <모듈>` 을 통과해야 커밋한다.
5. **한 세션 = 보드 한 행.** `docs/BOARD.md`에서 빈 행을 잡고 그 모듈 파일만 만진다. 다른 모듈 파일은 열지 않는다.
6. **한 모듈의 실패가 전체를 막지 않는다.** 수집기는 `run_fetcher()`로 감싸고, 소스 하나가 죽어도 나머지는 진행.
7. **계산에 현재 시각을 쓰지 않는다.** 기준일은 오늘 날짜 문자열. 시각은 `fetched_at`·`built_at`에만.
8. **막히면 20분.** 넘기면 보드 `막힘`에 적고 다음 사람에게.
9. 파이썬 실행은 `py -X utf8`, 콘솔 출력에 이모지·화살표 금지(Windows cp949).
10. 커밋 접두어: `mod(<모듈>)` · `build` · `ui` · `config` · `docs` · `ci`.

## 로컬 실행
```
py -X utf8 tools/run_all.py            # 수집 + 빌드 (--no-net 이면 링크 확인 생략)
py -X utf8 tools/validate.py weather fx
py -m http.server 8524                 # 폰 폭으로 확인 (index.html 더블클릭은 JSON 을 못 읽는다)
```
