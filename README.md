# 모닝브리프 v3

배포: https://morning-brief-omega-topaz.vercel.app (정식 주소 — 해시 붙은 배포 주소는 로그인이 필요하다)

공개 데이터로 만드는 아침 대시보드 — 날씨·환율·뉴스·지수·코인·부동산·IT·자동차·공공데이터.
계산은 아침에 클라우드(GitHub Actions)가 미리 끝내고 JSON 으로 굳히며, Vercel 은 그 JSON 을 폰 화면으로 뿌린다.

- 개인 정보·회사 정보 없음(공개 URL 전제) · 무료 등급만 사용 · 비상업
- 규칙은 `CLAUDE.md`, 데이터 계약은 `docs/CONTRACT.md`, 진행은 `docs/BOARD.md`

```
py -X utf8 tools/run_all.py      # 수집 + 빌드
py -m http.server 8524           # http://localhost:8524
```
