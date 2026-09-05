# gloudy — 강윤구 포트폴리오

## 프로젝트

사진가·디자이너 **강윤구**의 개인 포트폴리오. 단일 `index.html` 에 CSS/JS 가 다 든 정적
사이트. **빌드 도구 없음** — 브라우저로 열면 동작.

- 저장소 `antzm123-eng/antzm123-eng.github.io` (public) · `main` 하나
- **주소 `https://antzm123-eng.github.io/`** (Pages). 예전 `.../gloudy/` 는 안 씀 ·
  `canonical`·`og:*` 가 이 기준 — 호스팅 바꾸면 같이 고칠 것
- Netlify 는 **삭제됨**(비용). 되돌아가지 말 것 · `.nojekyll` 지우지 말 것

## 사용자 응대 방식 (중요)

강윤구님은 **개발자가 아닙니다.** 사진·포스터 디자인이 본업.

- "어린이한테 설명하듯" 쉬운 비유. 표·숫자 선호, 긴 산문 비선호
- 코드를 못 읽으므로 **검증은 대신 하고 결과를 보고**(측정값·통과/실패)
- 객관식 UI는 무시했음 → 본문으로 질문 · 효과가 약하면 솔직히
- **브라우저는 네이버 웨일**(크롬 계열, 버전이 뒤처짐) — 검수 기준

## 파일 구조

```
index.html    본문 전체 (HTML+CSS+JS) · robots.txt  AI 크롤러 24종 차단
.nojekyll     Pages 가공 방지 · og-image.jpg 1200×630 · favicon 3종
images/full/  라이트박스 1600px + .avif (워터마크 있음)
images/thumb/ 커버 700px + @2x 1280px + .avif (워터마크 없음)
images/strip/ 사진 띠 240px + .avif (화면엔 60×42)
images/design/ oldtown/  미참조 보관 · _originals/  원본(gitignore)
_sim/  리뉴얼 시뮬 A~L (gitignore) · tools/  add_work·watermark·crop·to_avif·
make_strip · check_private·check_covers·check_images (검사 3종)
```

## 문서 3단 구조

`CLAUDE.md`(이 파일) = 매 세션 읽힘. 현재 상태 + 규칙만, **10KB 넘기지 말 것** ·
`WORKLOG.md` = 이력(최신순) · `DECISIONS.md` = 이유. 측정값·근거는 이 둘에.
끝나면 WORKLOG 맨 위에 요약 + 여기 갱신. **쌓지 말 것.**

## 이미지 규칙 (반드시)

| 항목 | 값 |
|---|---|
| 원본 최대 변 | 1600px (무단 인쇄 방지) |
| 커버 | 700px + `@2x` 1280px · `srcset`. 포스터 3장만 560px · 띠 240px |
| 워터마크 | `H_yun_9u` · 오른쪽 아래 · 불투명 0.60 · 크기 .024 · 여백 .030 |
| 워터마크 대상 | `full`·`design`·`oldtown` — **썸네일·투명 로고(na_logo, na_logo2) 제외** |
| 품질 | JPEG 0.80(띠 0.70) · AVIF 썸네일 0.60 / 원본 0.80 / 띠 0.55 |
| 저작권 삽입 | JPEG=COM · PNG=iTXt **재인코딩 없이** / **AVIF 는 변환 시 자동** |

```
© 2026 강윤구 (Kang Yungu). All rights reserved. Unauthorized use, redistribution, or AI training prohibited. Contact: antzm123@naver.com
```

**AVIF + 원본 두 벌.** 커버는 `<picture>`, 라이트박스·띠는 `onerror` 폴백.
**원본을 지우지 말 것.** 재인코딩하면 저작권을 다시 넣을 것.
⚠️ **투명 PNG 를 JPEG 로 바꾸지 말 것** — 투명한 자리가 검게 변한다(로고 등 13장).

## 커버(대표 사진)

```bash
python3 tools/regen_covers.py --src ~/원본폴더 [--apply]  # 카메라 원본이 있을 때
python3 tools/regen_covers.py --from-full [--apply]      # 없을 때 (아래 7% 잘라냄)
python3 tools/check_covers.py                            # 검수 (반드시)
```

⚠️ `--from-full` 은 **아래 7% 를 잘라낸다** — 아래에 디자인이 있으면 `FULL_SKIP`(포스터 3장).

## 새 작업물 추가

```bash
python3 tools/add_work.py --key hansam3 --title "제목" --desc "한 줄 설명" \
  --src ~/Desktop/사진폴더 --date 2026.08 --tag Photo --cat visual
bash tools/to_avif.sh        # ← 반드시 이어서 (AVIF)
python3 tools/make_strip.py  # ← 띠 사진 240px (빠뜨리면 원본으로 떨어짐)
```

`--cat visual`=사진, `design`=포스터. HEIC 지원. 원본은 `_originals/<키>/`.
되돌리기 `git checkout -- . && git clean -fd images`.

⚠️ `add_work.py` 는 **구버전 카드 구조**로 넣는다 — 현재 구조(`card-cover`+`<picture>`+@2x)
로 바꾸고 발행 순서에 맞게 옮길 것. **세로 커버는 `srcset` 폭을 실제로 잴 것.**

## 미리보기·검사

`.claude/launch.json` → `preview_start` 로 `localhost:8765`.

⚠️ **크기만 재고 끝내지 말 것.** 눌러보고 **눈으로도 볼 것** — 숫자는 맞는데 사진이
누워 있던 적이 있다(함정 9).


⚠️ **창이 숨겨져 있으면 검사 환경이 거짓말을 한다** — 전환·`rAF`·`smooth`·`lazy` 가 멈추고
`naturalWidth` 0, 화면 사진이 새까맣게 나온다. 코드 탓 아님.
콘솔은 이전 로드 오류까지 쌓이니 `performance` 로 볼 것.

## 공개 저장소 주의

저장소가 **public** 이라 `CLAUDE.md`·`docs/`·`tools/` 도 읽힌다.
**사이트에 안 넣기로 한 정보(사명·공간명 등)는 문서에도 적지 말 것** — 두 번 실수.
커밋 전 `check_private.py`.

## 커밋 / 푸시

- 커밋 메시지는 한글, 대괄호 머리말(`[버그]`·`[디자인]`·`[성능]` 등)
- **맥 로컬 세션은 푸시 불가**(토큰이 GitHub Desktop 안) → 커밋까지만, `Push origin` 안내
- **클라우드 세션은 `claude/...` 브랜치로만 푸시** → 사용자가 GitHub Desktop 에서 `main` 에
  합쳐야 반영. 끝날 때 반드시 안내할 것

## 코드상 주의점 (이미 겪은 함정)

**배경·재현은 `docs/DECISIONS.md`·`WORKLOG.md` 에. 여기는 규칙만.**

1. `nav` 에 `backdrop-filter` 금지 — 자식 `position:fixed` 가 갇힌다(blur 는 `::before`).
   `body{overflow-x:hidden}` 도 금지 — 앵커 이동이 안 먹는다(`html` 에).
2. 라이트박스 배경 잠금 `body{position:fixed}`+`scrollbar-gutter:stable` ·
   포커스는 `focus({preventScroll:true})`.
3. `sips -s copyright` 금지(실패·재인코딩) → 바이트 삽입. `sips --cropOffset` 은 조용히
   무시되고 늘 가운데를 자름 → `crop.swift`. zsh 는 `$변수` 단어분리 안 함(목록은 파일로).
4. **칼럼 경계는 사진 표시 크기를 재보고 정한다** — `≤800 1 / 801~1280 2 / 1281+ 3칼럼`.
5. **`srcset`** — `w` 는 **가로 폭**(최대 변 아님) · `@2x` 가 1280px 미만이면 실제 폭대로 ·
   `naturalWidth` 는 **화면 밀도로 나눈 값**, 파일 폭이 아니다.
6. 원본만 다시 만들고 **낡은 `.avif` 를 안 지우면 효과 0**(`to_avif.sh` 가 건너뜀).
7. **AVIF 는 지원 감지를 기다리지 않는다** — AVIF 먼저, `onerror` 로 원본 복귀. 다 받기
   전까진 감추되(`.ready`) 캐시된 사진은 `load` 가 안 뜨니 `complete` 도 볼 것
8. **파일이 있고 크기가 맞아도 안 열릴 수 있다** → `check_images.py` 로 실제 디코딩.
   홀수 픽셀이면 AVIF 가 깨진다(브라우저만 거부) — `to_avif.swift` 가 짝수로 잘라 방지.
9. **세로로 든 사진(RAW·EXIF)은 픽셀이 가로다** — `watermark.swift` 가 회전 표시를 버려
   사진이 눕는다. **워터마크 전에 `sips -r 90`**, 썸네일은 표시를 바이트로 `1` 로 되돌리고
   `data-ratio`·`srcset` 재측정. `sips -g`=회전 전, `mdls`=회전 후.
10. **한 줄에 놓을 사진 비율은 `images/thumb` 기준** — 커버는 아래 7% 를 잘라 원본과 다름.
11. 한글 조판 `.sent`(문장)·`.cl`(쉼표) 은 **`display:block`** — `inline-block` 은 줄이
   꽉 찰 때만 넘어감. 태그가 열린 자리에서 자르지 말 것.
12. `<img>` 는 `top`·`bottom` 둘 다 줘도 **원본 높이가 이긴다** — 크기 명시.

## 현재 상태 (2026-09-06)

작업·갤러리 70개(사진 37·디자인 33) / 사진 324장.

- 카드 = 대표 사진 1장 + 장수 배지 + 라이트박스. `data-ratio="wide|square|tall"`
  (3:2/1:1/4:5). 커버 21장은 아래 7% 잘라 재생성 · **포스터 3장만 예전**(44%)
- 섹션 순서 `about → work → career → contact` · 전환은 `--ease` 하나, `:active` 있음
- 콘솔 오류 0 · alt 100% · 대비 AA · 가로 스크롤 0 · 날짜 역순 검증
- **AI 배경 3개**(유튜브 썸네일)는 카드 설명·경력란에 구분 표기 — 추가 시 동일하게 ·
  파나소닉 LX2 5묶음은 **의도적 무보정**이라 설명에 명시
- **리뉴얼은 L안**(`_sim/renewal-l.html`, gitignore) — K안 뼈대 + 확정 디자인 +
  검수 10건 전부 해결. **`index.html` 은 아직 그대로**

## 남은 일

1. 🟡 **리뉴얼 L안** — ① **대표작 고르기**(첫 화면에 4.5초마다 도는 6장. 지금 건 임의) →
   ② **`index.html` 에 옮기기.** ⚠️ 중립화·N/A 통일은 **시뮬에만, 사이트엔 미반영**
2. 🔴 `noindex` 로 검색 노출 차단 중. **퇴사 시점에 공개** —
   `index, follow` 로 되돌리고 Search Console 등록
3. (보류) **퇴사 후** — 회사 작업물 업로드 · 사명 공개 재검토

포스터 3장 화질(44%)은 원본 소실로 확정(WORKLOG).
⚠️ "히어로 배경·스크롤 모션 금지" 는 2026-09-04 폐기 — 모션을 원하는 쪽.

## 리뉴얼 확정 디자인 (2026-09-05 · L안 적용됨)

바탕 `#1A1917` · 강조 `#EE6A2F` · **글씨색 2단계** `#EDE8DF`(제목·본문) / `#A69F95`(나머지),
눈금 막대만 `#8C867C` · **글씨 6가지**(display·h2·`20·15·13·11px`, **9.5·10px 금지**) ·
여백 8px 배수 · **모션 3가지** `.15/.3/.8s` · 첫 화면 **4.5초**(JS `HOLD`+CSS `--hold` 둘 다).

위계는 색이 아니라 **크기·굵기**가 만든다 — 회색을 늘리지 말 것. 작품 제목 4건
(`bureuneun1·2`·`bureusim`·`bureusim_info`)은 **중립화 대상 아님.**
검수 내역 `_sim/K안-검수와-초기디자인-기획.md`

## 경력 섹션 (완료)

`#work` 다음 `#contact` 앞. 한 항목 = `.career-item`, 마크업은 기존 것을 복사.
**바꾸기 전에 `docs/DECISIONS.md` 의 "경력 섹션 서술 규칙" 을 읽을 것.** 요약:

- ⚠️ **기밀·계약 문제** 소지. 사명·공간명·지역 비공개(재직 중), 회사 작업물도 공개 불가
- 업무·성과 순서 **공간기획 → 마케팅 → 교육(보조)**. 바꾸지 말 것
- "운영"은 `공간 운영` 처럼 범위 한정 · **검증 불가능한 수치 금지**
