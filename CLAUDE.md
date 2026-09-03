# gloudy — 강윤구 포트폴리오

## 프로젝트

사진가·디자이너 **강윤구**의 개인 포트폴리오. 단일 `index.html` 에 CSS/JS 가 모두 든 정적 사이트.
**빌드 도구 없음** — Node.js, npm 불필요. 브라우저로 열면 그대로 동작.

- 저장소 `antzm123-eng/antzm123-eng.github.io` (public) · `main` 하나
- **공개 주소 `https://antzm123-eng.github.io/`** (GitHub Pages 사용자 사이트).
  예전 `.../gloudy/` 주소는 더는 안 쓴다
- `canonical`·`og:*` 가 이 주소 기준 — 호스팅을 바꾸면 같이 고칠 것
- Netlify 는 **삭제됨**(비용). 되돌아가지 말 것 · `.nojekyll` 지우지 말 것

## 사용자 응대 방식 (중요)

강윤구님은 **개발자가 아닙니다.** 사진·포스터 디자인이 본업.

- "어린이한테 설명하듯" 쉬운 비유를 곁들여 달라고 요청함. 표·숫자 선호, 긴 산문 비선호
- 코드를 못 읽으므로 **검증은 대신 해주고 결과를 보고**(측정값·통과/실패)
- GUI(GitHub Desktop) 선호. 객관식 UI는 무시했음 → 본문으로 질문할 것
- 효과가 약한 방법(예: 우클릭 방지)은 **솔직하게** 약하다고 말할 것
- **사용자 브라우저는 네이버 웨일**(크롬 계열이나 버전이 뒤처짐). 검수는 여기에 맞출 것

## 파일 구조

```
index.html            본문 전체 (HTML + CSS + JS)
robots.txt            AI 학습 크롤러 24종 차단 (도메인 루트라 실제로 작동)
.nojekyll             Pages 가공 방지
og-image.jpg          공유 미리보기 1200×630
favicon.ico / favicon-32.png / apple-touch-icon.png
images/full/          라이트박스용 원본 1600px + .avif (워터마크 있음)
images/thumb/         카드 커버용 700px + .avif (워터마크 없음)
images/design/ oldtown/  사이트 미참조 보관용 (AVIF 없음)
_originals/              원본 보관 (gitignore, 로컬 전용)
tools/add_work.py·watermark.swift·crop.swift·to_avif.swift+.sh   작업물 추가 파이프라인
tools/check_private.py·check_covers.py·check_images.py           검사 3종
```

## 문서 3단 구조

`CLAUDE.md`(이 파일) = 매 세션 읽힘. 현재 상태 + 규칙만, **10KB 넘기지 말 것** ·
`WORKLOG.md` = 이력(최신순) · `DECISIONS.md` = 이유. 측정값·근거는 전부 이 둘에 있다.
작업이 끝나면 WORKLOG 맨 위에 요약 + 여기 "현재 상태 / 남은 일" 갱신. **여기 쌓지 말 것.**

## 이미지 규칙 (반드시)

| 항목 | 값 |
|---|---|
| 원본 최대 변 | 1600px (무단 인쇄 방지) |
| 커버(썸네일) | 700px + `@2x` 1280px 두 벌 · `srcset`. 포스터 3장만 아직 560px |
| 워터마크 | `H_yun_9u` · 오른쪽 아래 · 불투명도 0.60 · 크기 0.024 · 여백 0.030 |
| 워터마크 대상 | `full`·`design`·`oldtown` — **썸네일·투명 로고(na_logo, na_logo2) 제외** |
| JPEG 품질 0.80 / AVIF 품질 | 썸네일 0.60 · 원본 0.80 |
| 저작권 삽입 | JPEG=COM · PNG=iTXt 로 **재인코딩 없이** / **AVIF 는 변환 시 자동 삽입** |

```
© 2026 강윤구 (Kang Yungu). All rights reserved. Unauthorized use, redistribution, or AI training prohibited. Contact: antzm123@naver.com
```

**AVIF + 원본 두 벌로 관리한다.** 커버는 `<picture>`, 라이트박스는 `onerror` 폴백.
**원본을 지우지 말 것**(폴백이 사라진다). 전부 저작권 포함 — 재인코딩하면 다시 넣을 것.

## 커버(대표 사진)

```bash
python3 tools/regen_covers.py --src ~/원본폴더 [--apply]   # 카메라 원본이 있을 때
python3 tools/regen_covers.py --from-full [--apply]       # 없을 때 (아래 7% 잘라냄)
python3 tools/check_covers.py                             # 검수 (반드시)
```

⚠️ `--src` 는 **카메라 원본 폴더**. `--from-full` 은 `images/full` 을 쓰되 워터마크가 있는
**아래 7% 를 잘라낸다** — 아래에 디자인이 있는 커버는 `FULL_SKIP` 으로 제외(지금 포스터 3장).

## 새 작업물 추가

```bash
python3 tools/add_work.py --key hansam3 --title "제목" --desc "한 줄 설명" \
  --src ~/Desktop/사진폴더 --date 2026.08 --tag Photo --cat visual
bash tools/to_avif.sh      # ← 반드시 이어서 실행 (AVIF 생성)
```

`--cat visual`=사진, `design`=포스터. HEIC 지원. 되돌리기 `git checkout -- . && git clean -fd images`.

`add_work.py` 는 원본을 `_originals/<키>/` 에 **자동 보관**한다(로컬 전용, 지우지 말 것).

⚠️ `add_work.py` 는 **구버전 카드 구조**로 넣는다 — 현재 구조(`card-cover`+`<picture>`
+@2x)로 바꾸고, 발행 순서(최신→과거)에 맞게 `work-grid` 안 위치도 옮길 것.
`--position` 은 top/bottom만 지원한다. **세로(tall) 커버는 `_0.jpg` 를 폭 700 기준으로
다시 만들 것**(함정 7번) — 최대 변 700px 라 세로 사진은 폭이 모자라 `700w` 와 안 맞는다.

## 미리보기·검사

`.claude/launch.json` 설정됨 → `preview_start` 로 `localhost:8765`.

⚠️ **크기만 재고 끝내지 말 것.** 실제로 눌러보는 시뮬레이션까지 (버그 2건을 그렇게 놓쳤다).

⚠️ **창이 숨겨져 있으면 검사 환경이 거짓말을 한다** — 전환이 얼어붙고(스크린샷 검게),
`rAF` 가 안 돌고, 디코딩이 미뤄져 `naturalWidth` 가 0 이 된다. 코드 탓이 아니다.
`*{transition:none!important;animation:none!important}` 주입 + 타이머 없이 잴 것.

## 공개 저장소 주의

저장소가 **public** 이라 `CLAUDE.md`·`docs/`·`tools/` 도 인터넷에서 읽힌다.
**사이트에 안 넣기로 한 정보(사명·공간명 등)는 문서에도 적지 말 것** — 두 번 실수했다.

```bash
python3 tools/check_private.py
```

## 커밋 / 푸시

- 커밋 메시지는 한글, 대괄호 머리말 (`[버그]`·`[디자인]`·`[성능]` 등)
- **맥 로컬 세션은 푸시 불가**(토큰이 GitHub Desktop 안에만 있음). 커밋까지만 하고
  `Push origin` 클릭을 안내할 것
- **클라우드 세션(claude.ai/code)은 `claude/...` 브랜치로만 푸시된다.** 사용자가 GitHub
  Desktop 에서 `main` 에 합쳐야 실제 사이트에 반영된다 — 끝날 때 반드시 안내할 것

## 코드상 주의점 (이미 겪은 함정)

**배경과 재현 방법은 `docs/DECISIONS.md` 와 `WORKLOG.md` 에 있다. 여기는 규칙만 적는다.**

1. `nav` 에 `backdrop-filter` 금지 — 자식 `position:fixed` 가 갇혀 모바일 메뉴가 안 열린다.
   blur 는 `nav::before` 에.
2. 라이트박스 배경 잠금은 `body{position:fixed}` + `scrollbar-gutter:stable`.
3. 포커스 이동은 `focus({preventScroll:true})` 필수.
4. zsh 는 `$변수` 를 단어분리하지 않는다. 파일 목록은 파일에 써서 넘길 것.
5. `sips -s copyright` 쓰지 말 것 (실패하거나 재인코딩됨). 바이트 삽입을 쓴다.
   `sips --cropOffset` 도 **조용히 무시되고 늘 가운데를 자른다** → `tools/crop.swift` 를 쓸 것.
6. **칼럼 경계는 사진 표시 크기를 재보고 정한다.** 지금은
   `≤800 1칼럼 / 801~1280 2칼럼 / 1281+ 3칼럼`. 중단점을 바꾸면 커버 px 를 반드시 잴 것.
7. **`srcset` 의 `w` 는 가로 폭**이다(최대 변 아님). 세로 사진에서 틀리면 흐림이 남는다.
8. 원본만 다시 만들고 **낡은 `.avif` 를 안 지우면 효과가 0** (`to_avif.sh` 가 건너뜀).
9. 라이트박스는 AVIF 지원 감지를 기다리지 않는다. AVIF 를 먼저 넣고 `onerror` 로 원본 복귀.
10. 라이트박스는 다 받기 전까지 사진을 감춘다(`.ready`). 캐시된 사진은 `load` 가 안 뜨므로
   `complete` 도 봐야 한다.
11. **파일이 있고 크기가 맞아도 안 열릴 수 있다.** `check_images.py` 로 실제 디코딩할 것.
   라이트박스 AVIF 주소는 HTML 에 없고 JS 가 만든다 — 목록 검사에서 빠진다.
12. **가로·세로 홀수면 AVIF 가 깨진다.** `sips` 는 열리는데 브라우저(libavif)는 거부한다.
   `to_avif.swift` 가 짝수로 잘라 막았다.
13. **`@2x` 원본이 1280px 보다 작으면 실제 폭대로 `srcset` 을 써야 한다.** 1080px 원본을
   그대로 "1280w" 라고 적으면 함정 7번과 같은 문제가 된다 — 실제로 만든 폭을 확인할 것.

## 현재 상태 (2026-09-03)

작업·갤러리 54개 / 사진 277장.

- 카드 = 대표 사진 1장 + 장수 배지 + 라이트박스. 프레임 `data-ratio="wide|square|tall"`
  (3:2/1:1/4:5). 표시 폭 390화면=262px · 800=623 · 1440=335
- 커버 21장은 아래 7% 잘라 다시 만듦. 레티나 최저 83%. **포스터 3장만 예전**(44%)
- 섹션 순서 `about → work → career → contact`
- 전환 곡선은 `--ease` 변수 하나로 통일, 클릭 가능한 요소엔 `:active` 눌림 반응 있음
- 콘솔 오류 0 · alt 100% · 대비 AA · 가로 스크롤 0 · 라이트박스 277장 표시 검증

## 남은 일

1. 🔴 검색 노출을 일부러 막아둔 상태(`noindex`). **퇴사 시점에 공개** —
   그때 `index, follow` 로 되돌리고 Search Console 등록
2. (보류) **퇴사 후** — 회사 작업물 업로드 + 사명 공개 여부 재검토

포스터 3장 화질(44%)은 원본 소실로 영구 확정(이유는 WORKLOG). 히어로 배경 사진·
스크롤 모션은 **사용자가 하지 말라고 했음.**

## 경력 섹션 (완료)

`#work` 다음 `#contact` 앞. 한 항목 = `.career-item`, 마크업은 기존 항목을 복사할 것.
받을 정보: 회사명(공개 가능 여부)·직무·기간·담당 업무 3~5줄·성과(숫자 우선)·도구.

**바꾸기 전에 `docs/DECISIONS.md` 의 "경력 섹션 서술 규칙" 을 읽을 것.** 요약:

- ⚠️ **기밀·계약 문제** 소지가 있다. 사명·공간명·지역 비공개(재직 중),
  회사 작업물도 **공개 불가**. 공개 범위는 반드시 사용자에게 확인할 것
- 담당 업무·성과 순서는 **공간기획 → 마케팅 → 교육(보조)**. 바꾸지 말 것
- "운영"은 `공간 운영` 처럼 범위를 한정할 것 (카페 현장 운영은 사용자 담당 아님)
- **검증 불가능한 수치는 넣지 말 것**
