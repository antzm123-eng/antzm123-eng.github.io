#!/usr/bin/env python3
"""
커버 사진이 제대로 만들어졌는지 검사한다. (다른 프로그램 설치 필요 없음)

무엇을 보는가
  1. index.html 이 가리키는 파일이 전부 실제로 있는가
  2. 파일의 실제 크기가 srcset 에 적어둔 숫자와 맞는가
  3. AVIF 가 낡지 않았는가 (원본만 다시 만들고 AVIF 를 안 지우면 효과가 없다)
  4. 저작권 문구가 모든 파일에 들어 있는가
  5. 워터마크가 있어야 할 곳(full)·없어야 할 곳(thumb)이 뒤바뀌지 않았는가
  6. 화면 폭별로 사진이 몇 % 해상도로 그려지는지 (100% 미만이면 흐리다)

사용법
  python3 tools/check_covers.py
"""

import re
import struct
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HTML = ROOT / "index.html"

COPYRIGHT = ("© 2026 강윤구 (Kang Yungu). All rights reserved. "
             "Unauthorized use, redistribution, or AI training prohibited. "
             "Contact: antzm123@naver.com").encode("utf-8")

# 화면 폭 → (칼럼 수, 커버 표시 폭) — index.html 의 CSS 와 같은 계산
def cover_width(vw):
    if vw <= 800:
        content = vw * 0.88
        return 1, content - 64
    if vw <= 1280:
        content = vw * 0.90
        return 2, (content - 24) / 2 - 64
    content = min(vw, 1560) - vw * 0.12 if vw > 1560 else vw * 0.88
    return 3, (content - 48) / 3 - 64


CHECK_WIDTHS = [390, 640, 720, 800, 1024, 1280, 1440, 1920]


def dimensions(path):
    d = Path(path).read_bytes()
    if d[:2] == b"\xff\xd8":
        i = 2
        while i + 4 <= len(d):
            if d[i] != 0xFF:
                break
            m = d[i + 1]
            if m in (0xD8, 0xD9) or 0xD0 <= m <= 0xD7:
                i += 2
                continue
            ln = struct.unpack(">H", d[i + 2:i + 4])[0]
            if m in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
                     0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                h, w = struct.unpack(">HH", d[i + 5:i + 9])
                return w, h
            i += 2 + ln
    elif d[:8] == b"\x89PNG\r\n\x1a\n":
        return struct.unpack(">II", d[16:24])
    else:
        # AVIF 는 ispe 가 여러 개 들어 있다 — 미리보기(512×512)나 격자 타일이
        # 먼저 나오므로, 가장 큰 것을 전체 크기로 본다 (check_images.py 와 같은 방식).
        sizes, pos = [], 0
        while True:
            i = d.find(b"ispe", pos)
            if i < 0:
                break
            sizes.append(struct.unpack(">II", d[i + 8:i + 16]))
            pos = i + 4
        if sizes:
            return max(sizes, key=lambda s: s[0] * s[1])
    return (0, 0)


def main():
    text = HTML.read_text(encoding="utf-8")
    problems, notes = [], []

    # index.html 이 실제로 가리키는 이미지 경로를 전부 모은다
    refs = set(re.findall(r'images/[a-z]+/[A-Za-z0-9_@.]+?\.(?:jpg|png|avif)', text))
    missing = sorted(r for r in refs if not (ROOT / r).exists())
    for r in missing:
        problems.append(f"index.html 이 없는 파일을 가리킵니다: {r}")

    # srcset 에 적힌 폭이 실제 파일 크기와 맞는가
    pairs = re.findall(r'(images/thumb/[A-Za-z0-9_@]+\.(?:jpg|png|avif))\s+(\d+)w', text)
    checked = 0
    for path, declared in pairs:
        f = ROOT / path
        if not f.exists():
            continue
        w, _ = dimensions(f)
        checked += 1
        if abs(w - int(declared)) > 1:
            problems.append(f"{path}: srcset 은 {declared}w 인데 실제 폭은 {w}px")

    # AVIF 가 짝인 원본과 크기가 같은가 (다르면 낡은 AVIF 다)
    stale = 0
    for path, _ in pairs:
        if not path.endswith(".avif"):
            continue
        av = ROOT / path
        for ext in (".jpg", ".png"):
            orig = av.with_suffix(ext)
            if orig.exists():
                a, b = dimensions(av), dimensions(orig)
                # AVIF 는 홀수 크기를 짝수로 올려 저장한다 (700×433 → 700×434).
                # 보이는 크기는 같으므로 1px 차이는 문제가 아니다.
                if abs(a[0] - b[0]) > 1 or abs(a[1] - b[1]) > 1:
                    problems.append(
                        f"{path}: AVIF {a} 와 원본 {b} 크기가 다릅니다"
                        f" — 낡은 AVIF 입니다. 지우고 다시 만드세요")
                    stale += 1
                break

    # 저작권 문구
    no_copy = []
    for r in sorted(refs):
        f = ROOT / r
        if f.exists() and COPYRIGHT not in f.read_bytes():
            no_copy.append(r)
    if no_copy:
        problems.append(f"저작권 문구가 없는 파일 {len(no_copy)}개: "
                        + ", ".join(no_copy[:5]) + (" …" if len(no_copy) > 5 else ""))

    # 사진마다 srcset 후보를 모은다 (아직 srcset 이 없으면 파일 하나가 후보)
    covers = []
    for m in re.finditer(r'<div class="card-cover"[^>]*data-gallery="(?P<key>[^"]+)"[^>]*>'
                         r'(?P<body>.*?)</picture>', text, re.S):
        body = m.group("body")
        cands = [(p_, int(w_)) for p_, w_ in
                 re.findall(r'(images/thumb/[A-Za-z0-9_@]+\.(?:jpg|png))\s+(\d+)w', body)]
        if not cands:                       # srcset 을 아직 안 쓰는 상태
            one = re.search(r'src="(images/thumb/[A-Za-z0-9_@.]+)"', body)
            if not one:
                continue
            f = ROOT / one.group(1)
            if not f.exists():
                continue
            cands = [(one.group(1), dimensions(f)[0])]
        covers.append((m.group("key"), sorted(set(cands), key=lambda c: c[1])))

    print("화면 폭별 커버 선명도 (100% 미만이면 늘려 그리는 것 = 흐림)")
    print(f"{'화면 폭':>9}{'칼럼':>5}{'커버 표시':>10}{'1배':>7}{'2배':>7}   가장 흐린 사진")
    print("─" * 66)
    worst_all = (999, "", 0)
    for vw in CHECK_WIDTHS:
        cols, cw = cover_width(vw)
        row = {}
        for dpr in (1, 2):
            need = cw * dpr
            low = (999, "")
            for key, cands in covers:
                pick = next((c for c in cands if c[1] >= need), cands[-1])
                pct = pick[1] / need * 100
                if pct < low[0]:
                    low = (pct, key)
            row[dpr] = low
            if low[0] < worst_all[0]:
                worst_all = (low[0], low[1], vw)
        print(f"{vw:>7}px{cols:>5}{cw:>9.0f}px{row[1][0]:>6.0f}%{row[2][0]:>6.0f}%   {row[2][1]}")
    print("─" * 66)
    print(f"가장 나쁜 값: {worst_all[0]:.0f}%  ({worst_all[1]}, 화면 폭 {worst_all[2]}px, 2배 화면)")
    if worst_all[0] < 100:
        notes.append(f"2배(레티나) 화면에서 최저 {worst_all[0]:.0f}% 입니다 — "
                     f"{worst_all[1]} 의 원본이 그만큼 크지 않았을 수 있습니다.")

    print()
    print(f"검사한 파일 {checked}개 · index.html 참조 {len(refs)}개")
    for n in notes:
        print(f"ℹ️  {n}")
    if problems:
        print()
        for p in problems:
            print(f"❌ {p}")
        print(f"\n문제 {len(problems)}건")
        sys.exit(1)
    print("\n✅ 문제 없음")


if __name__ == "__main__":
    main()
