# gloudy — 강윤구 포트폴리오

이 파일은 새 세션이 시작될 때 자동으로 읽힙니다. 여기 있는 내용은 다시 조사하지 마세요.

## 프로젝트

사진가·디자이너 **강윤구**의 개인 포트폴리오. 단일 `index.html`(약 68KB)에 CSS/JS가 모두 들어있는
정적 사이트. **빌드 도구 없음** — Node.js, npm 불필요. 브라우저로 열면 그대로 동작.

- 저장소: `antzm123-eng/gloudy` (public), 브랜치 `main` 하나
- 로컬: `/Users/yg_92/gloudy`
- 아직 **인터넷에 공개되지 않음** (GitHub Pages 미설정 → `antzm123-eng.github.io/gloudy/` 는 404)
- 공개 예정 주소 기준으로 og 태그가 작성되어 있음

## 사용자 응대 방식 (중요)

강윤구님은 **개발자가 아닙니다.** 사진·포스터 디자인이 본업.

- "어린이한테 설명하듯" 쉬운 비유를 곁들여 설명해 달라고 명시적으로 요청함
- 표와 before/after 숫자를 선호. 긴 산문은 비선호
- 코드를 읽지 못하므로 **검증은 대신 해주고 결과를 보고**할 것 (스크린샷·측정값·통과/실패)
- 터미널보다 GUI(GitHub Desktop)를 선호
- 객관식 선택지 UI는 한 번 무시했음 → 본문으로 질문하는 편이 나음
- 효과가 약한 방법(예: 우클릭 방지)은 **솔직하게** 약하다고 말할 것

## 파일 구조

```
index.html            본문 전체 (HTML + CSS + JS)
robots.txt            AI 학습 크롤러 24종 차단
og-image.jpg          공유 미리보기 1200×630
favicon-32.png / apple-touch-icon.png
images/full/          라이트박스용 원본 (최대 1600px, 워터마크 있음)
images/thumb/         목록용 썸네일 (최대 700px, 워터마크 없음)
images/design/        사이트 미참조 — 보관용
images/oldtown/       사이트 미참조 — 보관용
tools/add_work.py     새 작업물 추가 자동화
tools/watermark.swift 워터마크 합성 (CoreGraphics)
docs/WORKLOG.md       날짜별 작업 이력
docs/DECISIONS.md     왜 그렇게 정했는지
```

## 문서 3단 구조

| 파일 | 언제 읽히나 | 담는 것 |
|---|---|---|
| `CLAUDE.md` (이 파일) | **매 세션 자동** | 현재 상태 + 규칙. **10KB 넘기지 말 것** |
| `docs/WORKLOG.md` | 필요할 때만 | 날짜별 작업 이력 |
| `docs/DECISIONS.md` | 필요할 때만 | 결정의 이유. **기존 설정을 바꾸기 전에 반드시 확인** |

작업이 한 덩어리 끝나면 `WORKLOG.md` 에 요약을 추가하고 이 파일의
"현재 상태 / 남은 일" 을 갱신한 뒤 커밋한다. 과거 이력을 이 파일에 쌓지 않는다.

## 이미지 규칙 (반드시 지킬 것)

| 항목 | 값 |
|---|---|
| 원본 최대 변 | 1600px (무단 인쇄 방지) |
| 썸네일 최대 변 | 700px (표시 176px @2x 기준) |
| 워터마크 | `H_yun_9u` · 오른쪽 아래 · 불투명도 0.60 · 크기 0.024 · 여백 0.030 |
| 워터마크 대상 | `images/full`, `design`, `oldtown` — **썸네일과 투명 로고(na_logo)는 제외** |
| JPEG 품질 | 0.80 |
| 저작권 문구 | 아래 문자열, JPEG=COM 세그먼트 / PNG=iTXt 청크로 **재인코딩 없이** 삽입 |

```
© 2026 강윤구 (Kang Yungu). All rights reserved. Unauthorized use, redistribution, or AI training prohibited. Contact: antzm123@naver.com
```

현재 이미지 277장 **전부** 저작권 정보 포함(100%). 이미지를 재인코딩하는 작업 후에는
**반드시 저작권 정보를 다시 삽입**할 것 (재인코딩 시 지워짐).

## 새 작업물 추가

```bash
python3 tools/add_work.py --key hansam3 --title "제목" --desc "한 줄 설명" \
  --src ~/Desktop/사진폴더 --date 2026.08 --tag Photo --cat visual
```

`--cat visual`=사진 필터, `design`=포스터·디자인 필터. HEIC 지원. 되돌리기는
`git checkout -- . && git clean -fd images`. 축소·워터마크·저작권·썸네일·HTML 등록을 전부 자동 처리.

## 미리보기

`.claude/launch.json` 에 설정됨. `preview_start` 로 `gloudy` 실행 → `http://localhost:8765`.
(`python3 -m http.server 8765`)

## 커밋 / 푸시

- 커밋 메시지는 한글, 대괄호 머리말로 분류 (`[버그]`, `[접근성]` 등)
- **푸시는 Claude가 할 수 없음.** GitHub Desktop이 토큰을 앱 내부에만 보관해서 터미널 git이 인증 불가.
  커밋까지만 하고, 사용자에게 GitHub Desktop의 `Push origin` 클릭을 안내할 것
- 저장소 이력이 전부 `main` 직접 커밋 → 브랜치 만들지 말 것

## 코드상 주의점 (이미 겪은 함정)

각 항목의 자세한 배경은 `docs/DECISIONS.md` 참고.

1. **`nav` 에 `backdrop-filter` 를 걸면 안 됨.** 자식의 `position:fixed` 기준점이 화면이 아닌
   nav 박스가 되어 모바일 메뉴가 갇힘. 현재 blur는 `nav::before` 에 있음.
2. **라이트박스 배경 잠금**은 `body{position:fixed}` 방식. `scrollbar-gutter:stable` 로
   스크롤바 폭 변화에 의한 레이아웃 밀림(30px)을 막고 있음. 미지원 브라우저용 JS 보정도 있음.
3. 포커스 이동 시 화면이 밀리므로 `focus({preventScroll:true})` 필수.
4. zsh에서는 `$변수`가 자동 단어분리되지 않음. 파일 목록은 파일에 써서 넘길 것.
5. `sips -s copyright` 는 일부 JPEG에서 실패하고, 성공해도 **재인코딩되어 용량이 늘어남.**
   바이트 단위 삽입(현재 방식)을 쓸 것.

## 현재 상태

작업 24개 / 사진 160장 / 이미지 277장. 첫 화면 로딩 3.8MB.
콘솔 오류 0, 이미지 alt 100%, 색상 대비 WCAG AA 통과, 가로 스크롤 없음.
필터·라이트박스(24갤러리)·모바일 메뉴 전부 검증 완료.
섹션 순서: `about` → `work` → `career` → `contact`.

## 남은 일

1. 미업로드 작업물 추가 (사용자가 폴더 준비 중)
2. 전체 검수
3. 푸시 (사용자가 GitHub Desktop 에서)
4. GitHub Pages 공개 (사용자 결정 사항)

경력이 더 생기면 `#career` 의 `.career-item` 블록을 복사해 위에 추가하면 된다.

## 경력 섹션 (구현 완료)

`#work` 다음, `#contact` 앞. 사진 없이 글로만 경력을 기록한다. 현재 1개 항목.

한 항목 = `.career-item` 하나. 왼쪽 `.career-period`(기간) + 오른쪽 `.career-body`
(`h3` 회사명 · `.career-role` 직무 · `.career-tasks` 담당 업무 · `.career-result` 성과 ·
`.career-tools` 도구). 모바일에서는 1열로 전환된다.

항목을 추가할 때 필요한 정보:

```
회사명 (공개 가능 여부 확인) · 직무 · 기간
담당 업무 3~5줄
성과 (숫자가 있으면 우선)
사용 도구
```

⚠️ 회사 업무는 **기밀·계약 문제**가 있을 수 있음. 공개 범위를 사용자에게 반드시 확인할 것.
현재 항목은 사용자 요청으로 사명을 밝히지 않고 `식물 기반 사회적기업` + `사명 비공개` 칩으로 표기했다.
사명·공간명·지역은 본문에 넣지 않는다. 회사에서 만든 작업물도 **공개 불가**(2026-08-31 확인).

⚠️ **성과 수치는 사용자가 보내온 추정치**이며 실제 기록과 대조되지 않았다.
사용자 확인 전까지 푸시하지 말 것.
