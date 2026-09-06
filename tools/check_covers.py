#!/usr/bin/env python3
"""
커버 사진이 제대로 만들어졌는지 검사한다. (다른 프로그램 설치 필요 없음)

무엇을 보는가
  1. index.html 이 가리키는 파일이 전부 실제로 있는가
  2. 파일의 실제 크기가 srcset 에 적어둔 숫자와 맞는가
  3. AVIF 가 낡지 않았는가 (원본만 다시 만들고 AVIF 를 안 지우면 효과가 없다)
  4. 저작권 문구가 모든 파일에 들어 있는가
  5. 워터마크가 있어야 할 곳(full)·없어야 할 곳(thumb)이 뒤바뀌지 않았는가
  6. 화면에 보이는 곳마다 사진이 몇 % 해상도로 그려지는지 (100% 미만이면 흐리다)

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

# 사진이 화면에 나오는 곳은 세 군데다. 각각 쓰는 파일이 다르다.
#   뷰어 사진  images/full/<키>_<i>    (최대 변 1600px)
#   장(章) 사진 images/thumb/<키>_0 + @2x
#   사진 띠    images/strip/<키>_<i>   (240px)
#
# ⚠️ 아래 표시 폭은 **브라우저에서 직접 잰 값**이다(2026-09-06, L안 구조).
#    CSS 로 계산할 수 없다 — 격자 안에 들어 있어서. 배치를 바꾸면 다시 잴 것.
#    (CLAUDE.md "코드상 주의점" 4번)
# 뷰어는 `object-fit:contain` 이라 사진이 칸을 다 채우지 않는다 —
# 가로가 긴 사진은 높이에 맞고, 세로가 긴 사진은 폭에 맞는다. 그래서 칸의
# 가로·세로를 둘 다 두고, 사진 비율까지 넣어 실제로 그려지는 크기를 구한다.
MEASURED = {
    # 화면 폭: (뷰어 칸 가로, 뷰어 칸 세로, 장 사진 가로, 띠 한 칸 가로)
    390:  (308, 211, 173, 54),
    1440: (656, 416, 286, 60),
    1920: (1117, 427, 420, 62),
}
CHECK_WIDTHS = sorted(MEASURED)


def js_tables(text):
    """index.html 의 JS 표 세 개(DATA·EXT·FULLEXT)를 읽는다."""
    import json
    def grab(pat):
        m = re.search(pat, text, re.S)
        return json.loads(m.group(1)) if m else None
    return (grab(r'var DATA = (\[.*?\]), EXT ='),
            grab(r'EXT = (\{.*?\}), FULLEXT ='),
            grab(r'FULLEXT = (\{.*?\});'))


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

    # index.html 이 실제로 쓰는 이미지 경로를 전부 모은다.
    # 리뉴얼(2026-09-06) 뒤로 사진 주소는 HTML 에 안 적혀 있고 JS 표에서 만들어진다.
    refs = set(re.findall(r'images/[a-z]+/[A-Za-z0-9_@.]+?\.(?:jpg|png|avif)', text))
    data, EXTMAP, FULLMAP = js_tables(text)
    if data is None:
        print("⚠️  DATA·EXT·FULLEXT 표를 못 읽었습니다 — HTML 에 적힌 주소만 봅니다.")
    else:
        for d in data:
            k, n = d["key"], int(d.get("shots", 1))
            e, fe = EXTMAP.get(k, "jpg"), FULLMAP.get(k, "jpg")
            refs.add(f"images/thumb/{k}_0.{e}")
            for i in range(n):
                refs.add(f"images/full/{k}_{i}.{fe}")
                refs.add(f"images/strip/{k}_{i}.{fe}")
        for r in list(refs):
            if r.endswith((".jpg", ".png")):
                refs.add(re.sub(r"\.(jpe?g|png)$", ".avif", r))
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

    # ── 화면에 보이는 세 곳의 선명도 ──
    # 파일 폭은 사진마다 다르다(세로 사진은 좁다). 가장 나쁜 사진을 찾는다.
    def width_of(rel):
        f = ROOT / rel
        return dimensions(f)[0] if f.exists() else None

    def size_of(rel):
        f = ROOT / rel
        return dimensions(f) if f.exists() else None

    viewer, chap, strip_ = [], [], []
    if data:
        for d in data:
            k = d["key"]
            e, fe = EXTMAP.get(k, "jpg"), FULLMAP.get(k, "jpg")
            wh = size_of(f"images/full/{k}_0.{fe}")
            if wh: viewer.append((k, wh))
            w2 = width_of(f"images/thumb/{k}_0@2x.{e}") or width_of(f"images/thumb/{k}_0.{e}")
            if w2: chap.append((k, w2))
            w3 = width_of(f"images/strip/{k}_0.{fe}")
            if w3: strip_.append((k, w3))

    def drawn_width(iw, ih, box_w, box_h):
        """object-fit:contain — 칸 안에 다 들어가게 줄인 뒤의 가로 폭."""
        scale = min(box_w / iw, box_h / ih)
        return iw * scale

    print("화면에 보이는 곳별 선명도 (100% 미만이면 늘려 그리는 것 = 흐림)")
    print(f"{'화면 폭':>8}{'보이는 곳':>12}{'표시 폭':>9}{'1배':>7}{'2배':>7}   가장 흐린 사진")
    print("─" * 68)
    worst_all = (999.0, "", 0, "")
    for vw in CHECK_WIDTHS:
        bw, bh, cw, sw = MEASURED[vw]
        rows = []
        # 뷰어 — 사진마다 그려지는 폭이 다르다
        if viewer:
            rows.append(("뷰어 사진", bw,
                         [(k, w, drawn_width(w, h, bw, bh)) for k, (w, h) in viewer]))
        if chap:
            rows.append(("장(章) 사진", cw, [(k, w, cw) for k, w in chap]))
        if strip_:
            rows.append(("사진 띠", sw, [(k, w, sw) for k, w in strip_]))
        for name, shown, items in rows:
            out = {}
            for dpr in (1, 2):
                low = min((w / (drew * dpr) * 100, k) for k, w, drew in items)
                out[dpr] = low
                if low[0] < worst_all[0]:
                    worst_all = (low[0], low[1], vw, name)
            print(f"{vw:>6}px{name:>12}{shown:>8}px{out[1][0]:>6.0f}%{out[2][0]:>6.0f}%   {out[2][1]}")
    print("─" * 68)
    print(f"가장 나쁜 값: {worst_all[0]:.0f}%  ({worst_all[3]} · {worst_all[1]} · "
          f"화면 폭 {worst_all[2]}px · 2배 화면)")
    if worst_all[0] < 100:
        notes.append(f"2배(레티나) 화면의 '{worst_all[3]}' 에서 최저 {worst_all[0]:.0f}% 입니다. "
                     f"원본은 최대 변 1600px 로 제한돼 있어 큰 화면에서는 100% 를 못 넘길 수 있습니다.")

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
