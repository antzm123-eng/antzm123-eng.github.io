# gloudy — 강윤구 포트폴리오

이 파일은 새 세션이 시작될 때 자동으로 읽힙니다. 여기 있는 내용은 다시 조사하지 마세요.

## 프로젝트

사진가·디자이너 **강윤구**의 개인 포트폴리오. 단일 `index.html`(약 68KB)에 CSS/JS가 모두 들어있는
정적 사이트. **빌드 도구 없음** — Node.js, npm 불필요. 브라우저로 열면 그대로 동작.

- 저장소 `antzm123-eng/gloudy` (public), `main` 하나 / 로컬 `/Users/yg_92/gloudy`
- **공개 주소: `https://antzm123-eng.github.io/gloudy/`** (GitHub Pages, 2026-09-01 이전)
- `canonical` / `og:*` 가 이 주소 기준 — 호스팅을 바꾸면 반드시 같이 고칠 것
- 이전 호스팅 Netlify 는 **삭제됨** (배포 1회 15크레딧/월 300). 되돌아가지 말 것
- `.nojekyll` 이 있어야 Pages 가 파일을 가공하지 않음 — 지우지 말 것

## 사용자 응대 방식 (중요)

강윤구님은 **개발자가 아닙니다.** 사진·포스터 디자인이 본업.

- "어린이한테 설명하듯" 쉬운 비유를 곁들여 설명해 달라고 명시적으로 요청함
- 표와 before/after 숫자를 선호. 긴 산문은 비선호
- 코드를 못 읽으므로 **검증은 대신 해주고 결과를 보고** (측정값·통과/실패)
- 터미널보다 GUI(GitHub Desktop) 선호. 객관식 UI는 무시했음 → 본문으로 질문할 것
- 효과가 약한 방법(예: 우클릭 방지)은 **솔직하게** 약하다고 말할 것

## 파일 구조

```
index.html            본문 전체 (HTML + CSS + JS)
robots.txt            AI 학습 크롤러 24종 차단
.nojekyll             Pages 가공 방지
og-image.jpg          공유 미리보기 1200×630
favicon.ico / favicon-32.png / apple-touch-icon.png
images/full/          라이트박스용 원본 1600px + .avif (워터마크 있음)
images/thumb/         카드 커버용 700px + .avif (워터마크 없음)
images/design/ oldtown/   사이트 미참조 보관용 (AVIF 없음)
tools/add_work.py     새 작업물 추가 자동화
tools/watermark.swift 워터마크 합성 (CoreGraphics)
tools/to_avif.swift + .sh   AVIF 변환 (저작권 동시 삽입)
tools/check_private.py 비공개 낱말 검사 (목록은 .claude/, 미공개)
tools/regen_covers.py  커버를 원본에서 다시 생성 (선명도) — 맥에서 실행
tools/check_covers.py  커버 검수 (크기·저작권·낡은 AVIF·선명도)
docs/WORKLOG.md       날짜별 작업 이력
docs/DECISIONS.md     왜 그렇게 정했는지
```

## 문서 3단 구조

| 파일 | 언제 읽히나 | 담는 것 |
|---|---|---|
| `CLAUDE.md` (이 파일) | **매 세션 자동** | 현재 상태 + 규칙. **10KB 넘기지 말 것** |
| `docs/WORKLOG.md` | 필요할 때 | 날짜별 이력 (최신순) |
| `docs/DECISIONS.md` | 필요할 때 | 결정의 이유. **설정을 바꾸기 전 반드시 확인** |

작업이 끝나면 `WORKLOG.md` 맨 위에 요약을 넣고(최신순) 이 파일의 "현재 상태 / 남은 일" 을
갱신한 뒤 커밋한다. **과거 이력을 이 파일에 쌓지 말 것.**

## 이미지 규칙 (반드시 지킬 것)

| 항목 | 값 |
|---|---|
| 원본 최대 변 | 1600px (무단 인쇄 방지) |
| 썸네일 최대 변 | 신규는 700px(`add_work.py`). **기존 파일은 섞여 있다** — 500px 68 · 700px 20 · 480px 8 · 675px 4 · 750px 4 |
| 워터마크 | `H_yun_9u` · 오른쪽 아래 · 불투명도 0.60 · 크기 0.024 · 여백 0.030 |
| 워터마크 대상 | `full`·`design`·`oldtown` — **썸네일·투명 로고(na_logo) 제외** |
| JPEG 품질 0.80 / AVIF 품질 | 썸네일 0.60 · 원본 0.80 |
| 저작권 삽입 | JPEG=COM · PNG=iTXt 로 **재인코딩 없이** / **AVIF 는 변환 시 자동 삽입** |

```
© 2026 강윤구 (Kang Yungu). All rights reserved. Unauthorized use, redistribution, or AI training prohibited. Contact: antzm123@naver.com
```

**이미지는 AVIF + 원본 두 벌로 관리한다.** 브라우저가 AVIF 를 지원하면 AVIF, 아니면 원본
JPEG/PNG(커버는 `<picture>`, 라이트박스는 `onerror` 폴백). **원본을 지우지 말 것** — 폴백이 사라진다.

원본 277장 + AVIF 264장 **전부** 저작권 포함. JPEG/PNG 를 재인코딩하면 다시 넣을 것(AVIF 는 불필요).

## 커버(대표 사진)

가로 폭 **700px + `@2x` 1280px** 두 벌을 `srcset` 으로 화면에 맞게 고르게 한다.

```bash
python3 tools/regen_covers.py --src ~/원본사진폴더           # 미리보기
python3 tools/regen_covers.py --src ~/원본사진폴더 --apply   # 실행
python3 tools/check_covers.py                               # 검수 (반드시)
```

⚠️ `--src` 는 **카메라 원본 폴더**여야 한다. `images/full` 은 워터마크가 합성돼 있다.
함정은 "코드상 주의점" 7·8 번.

## 새 작업물 추가

```bash
python3 tools/add_work.py --key hansam3 --title "제목" --desc "한 줄 설명" \
  --src ~/Desktop/사진폴더 --date 2026.08 --tag Photo --cat visual
bash tools/to_avif.sh      # ← 반드시 이어서 실행 (AVIF 생성)
```

`--cat visual`=사진, `design`=포스터. HEIC 지원. 되돌리기 `git checkout -- . && git clean -fd images`.

⚠️ `add_work.py` 는 **구버전 카드 구조(썸네일 5개)로 HTML 을 넣는다.** 현재 구조는
`.card-cover` 1장 + `<picture>` + `data-ratio` 이므로 **실행 후 기존 카드를 보고 고칠 것.**

## 미리보기 · 검사

`.claude/launch.json` 설정됨. `preview_start` 로 `gloudy` 실행 → `http://localhost:8765`.

⚠️ **창이 숨겨져 있으면(`visibilityState==='hidden'`) CSS 전환이 얼어붙는다.** 모바일 메뉴가
안 열리고 스크린샷이 검게 나오는데 **전부 검사 환경 탓이다.** 측정 전에 반드시 주입할 것:

```js
document.head.insertAdjacentHTML('beforeend','<style>*{transition:none!important;animation:none!important}</style>');
```

## 공개 저장소 주의

저장소가 **public** 이라 `CLAUDE.md`·`docs/`·`tools/` 도 인터넷에서 읽힌다.
**사이트에 안 넣기로 한 정보(사명·공간명 등)는 문서에도 적지 말 것.** 두 번 실수했다.
**커밋 전에 반드시 실행한다.**

```bash
python3 tools/check_private.py
```

## 커밋 / 푸시

- 커밋 메시지는 한글, 대괄호 머리말로 분류 (`[버그]`, `[디자인]`, `[성능]` 등)
- **푸시는 Claude가 할 수 없음.** GitHub Desktop이 토큰을 앱 내부에만 보관해서 터미널 git이 인증 불가.
  커밋까지만 하고, 사용자에게 GitHub Desktop의 `Push origin` 클릭을 안내할 것
- 저장소 이력이 전부 `main` 직접 커밋 → 브랜치 만들지 말 것

## 코드상 주의점 (이미 겪은 함정)

자세한 배경은 `docs/DECISIONS.md` 참고.

1. **`nav` 에 `backdrop-filter` 를 걸면 안 됨.** 자식의 `position:fixed` 기준점이 화면이 아닌
   nav 박스가 되어 모바일 메뉴가 갇힘. 현재 blur는 `nav::before` 에 있음.
2. **라이트박스 배경 잠금**은 `body{position:fixed}` 방식. `scrollbar-gutter:stable` 로
   레이아웃 밀림(30px)을 막고 있음. 미지원 브라우저용 JS 보정도 있음.
3. 포커스 이동 시 화면이 밀리므로 `focus({preventScroll:true})` 필수.
4. zsh에서는 `$변수`가 자동 단어분리되지 않음. 파일 목록은 파일에 써서 넘길 것.
5. `sips -s copyright` 는 실패하거나 재인코딩된다. 바이트 삽입을 쓸 것.
6. **칼럼 경계는 사진 표시 크기를 재보고 정한다.** 칼럼을 늘리면 사진이 작아진다.
   현재 `≤800px 1칼럼 / 801~1280 2칼럼 / 1281 이상 3칼럼(1500+ 는 3 고정)`.
   중단점을 새로 만들면 그 폭에서 커버 px 를 반드시 측정할 것.
7. **`srcset` 의 `w` 는 가로 폭**이다(최대 변 아님). 세로 사진에서 틀리면 흐림이 남는다.
8. 원본만 다시 만들고 **낡은 `.avif` 를 안 지우면 효과가 0 이다** (`to_avif.sh` 는 건너뜀).
9. 라이트박스는 AVIF **지원 감지를 기다리지 않는다.** 항상 AVIF 를 먼저 넣고
   `onerror` 로 원본에 복귀한다. 비동기 감지로 분기하면 첫 장이 JPEG 로 나간다.

## 현재 상태 (2026-09-01)

작업 24개 / 갤러리 24개 / 사진 160장 / 원본 이미지 277장 + AVIF 264장.
**첫 화면 로딩 0.44MB** (개선 전 3.77MB, −88%).

- 작업 카드 = **대표 사진 1장 크게** + 장수 배지 + 라이트박스. 커버 프레임은
  `data-ratio="wide|square|tall"` (3:2/1:1/4:5). 표시 폭 390화면=262px · 800=623 · 1440=335
- 섹션 순서 `about → work → career → contact`
- 콘솔 오류 0 · alt 100% · 색 대비 AA · 가로 스크롤 0(320~1920) · 실사이트 검증 완료

## 남은 일

1. **미업로드 개인 작업물 추가** (사용자가 폴더 준비 중) ← 다음 차례
2. **구글 검색 등록** (Search Console). 공개는 됐으나 검색에 아직 안 잡힘
3. **커버 선명도 — 도구 준비 완료, 사용자가 Mac 에서 실행하면 끝** ← 다음 차례
   지금 최악은 `yeonseup` 이 폭 800px·2배에서 **28%**(파일이 352px 뿐). 도구를 돌리면
   전 구간 100% 이상, 첫 화면 로딩 **+27~30%**. 근거는 `WORKLOG.md`.
4. **`robots.txt` 가 지금 주소에서 무효** — 크롤러는 도메인 루트에서만 읽는데
   `antzm123-eng.github.io/robots.txt` 는 404. **AI 크롤러 24종 차단이 안 걸려 있다.**
   (메타 태그 `noai`/`tdm-reservation` 은 정상 작동)
   해결: `antzm123-eng.github.io` 저장소를 새로 만들어 `robots.txt` 하나만 두기
5. **안 쓰이는 썸네일 160장(4.6MB)** — 카드가 커버 1장 구조가 되며 `_1`~ 썸네일이 미참조
   (`.g-thumb` 마크업 0개). 로딩엔 영향 없고 저장소만 무겁다.
6. (보류) **퇴사 결정 후** — 회사 작업물 업로드 + 사명 공개 여부 재검토

3단계(히어로 배경 사진·스크롤 모션)는 **사용자가 하지 말라고 했음.**

## 경력 섹션 (구현 완료, 항목 1개)

`#work` 다음 `#contact` 앞. 글로만 기록. 한 항목 = `.career-item` 하나이며 마크업은
`index.html` 의 기존 항목을 복사해 쓸 것. 받을 정보: 회사명(공개 가능 여부)·직무·기간·
담당 업무 3~5줄·성과(숫자 우선)·도구.

⚠️ 회사 업무는 **기밀·계약 문제** 소지가 있음. 공개 범위를 반드시 확인할 것.

**바꾸기 전에 `docs/DECISIONS.md` 의 "경력 섹션 서술 규칙" 을 반드시 읽을 것.** 요약:

- 사명·공간명·지역 비공개(재직 중). 회사 작업물도 **공개 불가**
- 담당 업무·성과 순서는 **공간기획 → 마케팅 → 교육(보조)**. 바꾸지 말 것
- "운영"은 `공간 운영` 처럼 범위를 한정할 것 (카페 현장 운영은 사용자 담당 아님)
- **검증 불가능한 수치는 넣지 말 것**
