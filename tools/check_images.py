#!/usr/bin/env python3
"""
사이트가 쓰는 이미지가 전부 "정말로 열리는지" 검사한다. 필요하면 다시 만든다.

왜 필요한가
  2026-09-01, 라이트박스에서 성탄절·성서인의 밤 사진이 안 보이는 문제가 있었다.
  파일은 있었고 크기도 정상이었지만, AVIF 17개가 **일부 디코더에서 안 읽히는**
  상태였다. 파일 목록만 확인하는 검사로는 절대 못 잡는다. 실제로 열어봐야 한다.

무엇을 하는가
  1. index.html 이 가리키는 모든 이미지를 실제로 디코딩해 본다
  2. AVIF 는 짝이 되는 JPEG/PNG 와 크기가 같은지도 본다 (낡은 AVIF 찾기)
  3. --fix 를 주면 깨진 AVIF 를 원본 JPEG/PNG 에서 다시 만든다

사용법
  python3 tools/check_images.py           # 검사만
  python3 tools/check_images.py --fix     # 깨진 AVIF 다시 만들기

⚠️ 디코더가 필요하다. 맥이면  pip3 install pillow  로 설치한다.
   맥 기본 도구(sips)는 이 문제를 만든 것과 같은 디코더라서 못 잡는다.
"""

import argparse
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HTML = ROOT / "index.html"

COPYRIGHT = ("© 2026 강윤구 (Kang Yungu). All rights reserved. "
             "Unauthorized use, redistribution, or AI training prohibited. "
             "Contact: antzm123@naver.com")
PAYLOAD = COPYRIGHT.encode("utf-8")

# CoreGraphics 품질과 용량을 맞춘 Pillow 값 (실측 오차 2%)
AVIF_Q = {"full": 75, "thumb": 65, "design": 75, "oldtown": 75}

try:
    from PIL import Image
    HAVE_PIL = True
except ImportError:
    HAVE_PIL = False


def referenced():
    """index.html 이 쓰는 이미지. HTML 에 적힌 주소만 모으면 안 된다 —
    라이트박스는 JPEG 주소에서 `.avif` 를 **JS 로 만들어낸다**. 그 파일들이
    검사에서 빠지는 바람에 깨진 AVIF 17개를 오래 못 잡았다."""
    text = HTML.read_text(encoding="utf-8")
    out = set(re.findall(r'images/[a-z]+/[A-Za-z0-9_@.]+?\.(?:jpg|png|avif)', text))
    for r in list(out):                      # showImage() 가 만들어내는 주소를 더한다
        if r.endswith((".jpg", ".png")):
            out.add(re.sub(r"\.(jpe?g|png)$", ".avif", r))
    return sorted(out)


def real_size(path):
    """AVIF 는 격자(grid) 타일 크기가 먼저 나오므로 가장 큰 ispe 를 전체 크기로 본다."""
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
        return (0, 0)
    if d[:8] == b"\x89PNG\r\n\x1a\n":
        return struct.unpack(">II", d[16:24])
    sizes, pos = [], 0
    while True:                                  # ispe 를 전부 모은다
        i = d.find(b"ispe", pos)
        if i < 0:
            break
        sizes.append(struct.unpack(">II", d[i + 8:i + 16]))
        pos = i + 4
    return max(sizes, key=lambda s: s[0] * s[1]) if sizes else (0, 0)


def decodes(path):
    try:
        im = Image.open(path)
        im.load()
        return True, ""
    except Exception as e:
        return False, f"{type(e).__name__}: {str(e)[:60]}"


def source_for(avif):
    for ext in (".jpg", ".png"):
        p = avif.with_suffix(ext)
        if p.exists():
            return p
    return None


def rebuild(avif):
    src = source_for(avif)
    if src is None:
        return False, "짝이 되는 JPEG/PNG 가 없습니다"
    q = AVIF_Q.get(avif.parent.name, 75)
    im = Image.open(src)
    im = im.convert("RGBA" if (im.mode in ("RGBA", "LA", "P") and src.suffix == ".png") else "RGB")
    im.save(avif, "AVIF", quality=q, xmp=PAYLOAD)
    ok, why = decodes(avif)
    return (True, f"{src.name} 에서 다시 만듦 (q={q})") if ok else (False, f"다시 만들었지만 여전히 안 열림: {why}")


def main():
    ap = argparse.ArgumentParser(description="사이트 이미지가 실제로 열리는지 검사한다")
    ap.add_argument("--fix", action="store_true", help="깨진 AVIF 를 원본에서 다시 만든다")
    ap.add_argument("--all", action="store_true",
                    help="index.html 이 안 쓰는 이미지까지 전부 검사한다")
    args = ap.parse_args()

    if not HAVE_PIL:
        sys.exit("❌ 디코더가 없습니다.  pip3 install pillow  를 먼저 실행해주세요.\n"
                 "   (맥 기본 sips 는 이 문제를 만든 것과 같은 디코더라 검사에 쓸 수 없습니다)")

    if args.all:
        paths = sorted(p for p in (ROOT / "images").rglob("*")
                       if p.suffix.lower() in (".jpg", ".png", ".avif"))
    else:
        paths = [ROOT / r for r in referenced()]

    missing = [p for p in paths if not p.exists()]
    broken, stale, no_copy = [], [], []
    for p in paths:
        if not p.exists():
            continue
        ok, why = decodes(p)
        if not ok:
            broken.append((p, why))
            continue
        if p.suffix == ".avif":
            src = source_for(p)
            # AVIF 는 색차 정보 때문에 짝수로 맞춰지므로 1~2px 차이는 정상이다.
            if src:
                a, b_ = real_size(p), real_size(src)
                if abs(a[0] - b_[0]) > 2 or abs(a[1] - b_[1]) > 2:
                    stale.append((p, a, b_))
        if PAYLOAD not in p.read_bytes():
            no_copy.append(p)

    print(f"검사한 이미지 {len([p for p in paths if p.exists()])}개"
          f"{' (index.html 이 쓰는 것만)' if not args.all else ' (전체)'}")
    print(f"  없는 파일        {len(missing)}개")
    print(f"  안 열리는 파일   {len(broken)}개")
    print(f"  낡은 AVIF        {len(stale)}개")
    print(f"  저작권 없는 파일 {len(no_copy)}개")

    for p in missing:
        print(f"❌ 없음: {p.relative_to(ROOT)}")
    for p, why in broken:
        print(f"❌ 안 열림: {p.relative_to(ROOT)} — {why}")
    for p, a, b in stale:
        print(f"❌ 낡은 AVIF: {p.relative_to(ROOT)} — AVIF {a} vs 원본 {b}")
    for p in no_copy[:10]:
        print(f"⚠️  저작권 없음: {p.relative_to(ROOT)}")

    if args.fix and broken:
        print(f"\n깨진 AVIF {len(broken)}개를 다시 만듭니다…")
        fixed = 0
        for p, _ in broken:
            if p.suffix != ".avif":
                print(f"  ❌ {p.name}: AVIF 가 아니라 자동으로 못 고칩니다")
                continue
            before = p.stat().st_size
            ok, msg = rebuild(p)
            print(f"  {'✅' if ok else '❌'} {p.name}: {msg}"
                  f"{f' — {before//1024}KB → {p.stat().st_size//1024}KB' if ok else ''}")
            fixed += ok
        print(f"\n{fixed}/{len(broken)}개를 고쳤습니다. 다시 검사해주세요.")
        return

    if missing or broken or stale or no_copy:
        print("\n문제가 있습니다." + ("  --fix 로 깨진 AVIF 를 다시 만들 수 있습니다." if broken else ""))
        sys.exit(1)
    print("\n✅ 문제 없음")


if __name__ == "__main__":
    main()
