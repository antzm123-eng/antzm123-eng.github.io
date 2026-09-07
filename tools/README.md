# tools — 명령 모음

`CLAUDE.md` 는 상태와 규칙만 담는다(10KB 한도). **실제로 치는 명령은 여기 있다.**
규칙 자체(이미지 크기·워터마크·품질 등)는 `CLAUDE.md` "이미지 규칙" 을 볼 것.

## 커버(대표 사진) 다시 만들기

```bash
python3 tools/regen_covers.py --src ~/원본폴더 [--apply]   # 카메라 원본이 있을 때
python3 tools/regen_covers.py --from-full [--apply]       # 없을 때 (아래 7% 잘라냄)
python3 tools/check_covers.py                             # 검수 (반드시)
```

⚠️ `--from-full` 은 **아래 7% 를 잘라낸다.** 아래쪽에 디자인이 있는 포스터는
`FULL_SKIP` 으로 건너뛴다(포스터 3장).

## 새 작업물 추가

```bash
python3 tools/add_work.py --key hansam3 --title "제목" --desc "한 줄 설명" \
  --src ~/Desktop/사진폴더 --date 2026.08 --tag Photo --cat visual
bash tools/to_avif.sh        # ← 반드시 이어서 (AVIF)
python3 tools/make_strip.py  # ← 띠 사진 240px (빠뜨리면 원본으로 떨어진다)
```

- `--cat visual` = 사진, `design` = 포스터. HEIC 지원.
- 원본은 `_originals/<키>/` 에 남는다(gitignore).
- 되돌리기 `git checkout -- . && git clean -fd images`

⚠️ `add_work.py` 는 **지금 없는 카드 구조**로 넣는다. 손으로 넣어야 하는 곳:

| 넣을 곳 | 무엇 |
|---|---|
| JS `DATA` | `key` · `title` · `desc` · `meta` · `tag` · `cat` · `shots` |
| JS `EXT` · `FULLEXT` | 썸네일 / 원본 확장자 |
| 목록 `.row` | 한 줄. `data-key`·`data-cat`·`data-year`·`data-q`(검색 색인, 소문자) |

`meta` 는 `날짜 · 태그 · 맥락 · 카메라` 순이고 **셋째 칸이 맥락**이다
(`외부 단체 요청` / `소속 팀 N/A` / `개인 작업`). `data-q` 에도 같은 값을 넣을 것 —
한쪽만 고치면 화면과 검색이 어긋난다.

`srcset` 폭은 **실제로 잴 것**(`sips -g pixelWidth`). 짐작해서 적지 말 것.

## 검사 3종

```bash
python3 tools/check_private.py   # 비공개 낱말 (커밋 전 반드시)
python3 tools/check_covers.py    # 커버 해상도
python3 tools/check_images.py    # 실제 디코딩 (Pillow 필요: pip3 install pillow)
```

셋 다 **`index.html` 의 `DATA` 표를 읽는다.** 구조를 바꾸면 이 셋도 같이 고칠 것 —
안 고치면 0개를 세고 조용히 통과한다.

## 저작권 문자열

재인코딩한 이미지에 다시 넣을 때 쓰는 문구. **한 글자도 바꾸지 말 것.**

```
© 2026 강윤구 (Kang Yungu). All rights reserved. Unauthorized use, redistribution, or AI training prohibited. Contact: antzm123@naver.com
```

넣는 방법은 `JPEG=COM` · `PNG=iTXt` 로 **재인코딩 없이 바이트 삽입**.
AVIF 는 `to_avif.swift` 가 변환하면서 자동으로 넣는다.
`sips -s copyright` 는 쓰지 말 것 — 실패하고 재인코딩까지 한다.
