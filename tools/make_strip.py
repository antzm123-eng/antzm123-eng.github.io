#!/usr/bin/env python3
"""사진 띠(작업 안 사진 넘기는 작은 미리보기)에 쓸 240px 이미지를 만든다.

  사용법:  python3 tools/make_strip.py [--force]

라이트박스·커버와 달리, 띠는 화면에서 60x42px 로만 보인다.
그런데 images/thumb/ 에는 대표 사진(_0) 한 장만 있어서, 나머지는 1600px 원본을
가져다 쓰고 있었다 — 사진 13장짜리 작업 하나를 여는 데 7.1MB 가 나갔다.

  images/full/<키>_<번호>.jpg|png  →  images/strip/<키>_<번호>.jpg + .avif

- 가장 긴 변 240px (고화질 화면의 4배율까지 감당)
- JPEG 0.70 / AVIF 0.55 · 저작권은 JPEG=COM 바이트, AVIF=변환 시 자동
- 이미 .avif 가 있으면 건너뛴다 (--force 로 다시 만듦)
- 원본이 워터마크가 찍힌 images/full/ 이라 마크가 같이 줄어들지만,
  240px 에서 6px, 실제 표시 크기 60px 에서는 1.4px 라 보이지 않는다.
"""
import subprocess, sys, zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC, OUT = ROOT / "images/full", ROOT / "images/strip"
LONG_SIDE, JPEG_Q, AVIF_Q = 240, 70, "0.55"
COPYRIGHT = ("© 2026 강윤구 (Kang Yungu). All rights reserved. "
             "Unauthorized use, redistribution, or AI training prohibited. "
             "Contact: antzm123@naver.com")
PAYLOAD = COPYRIGHT.encode("utf-8")
BIN = Path("/tmp/gloudy_to_avif")


def embed_copyright(path):
    d = Path(path).read_bytes()
    if PAYLOAD in d:
        return False
    if d[:2] == b"\xff\xd8":
        pos = 2
        while pos + 4 <= len(d) and d[pos] == 0xFF and 0xE0 <= d[pos + 1] <= 0xEF:
            pos += 2 + ((d[pos + 2] << 8) | d[pos + 3])
        out = (d[:pos] + b"\xff\xfe"
               + (len(PAYLOAD) + 2).to_bytes(2, "big") + PAYLOAD + d[pos:])
    elif d[:8] == b"\x89PNG\r\n\x1a\n":
        data = b"Copyright" + b"\x00" * 5 + PAYLOAD
        chunk = (len(data).to_bytes(4, "big") + b"iTXt" + data
                 + zlib.crc32(b"iTXt" + data).to_bytes(4, "big"))
        i = d.rfind(b"IEND")
        out = d[:i - 4] + chunk + d[i - 4:]
    else:
        return False
    Path(path).write_bytes(out)
    return True


def main():
    force = "--force" in sys.argv
    if not BIN.exists():
        print("AVIF 변환기를 컴파일합니다…")
        subprocess.run(["swiftc", "-O", "-o", str(BIN), str(ROOT / "tools/to_avif.swift")],
                       check=True)
    OUT.mkdir(parents=True, exist_ok=True)

    srcs = sorted(p for p in SRC.iterdir() if p.suffix.lower() in (".jpg", ".jpeg", ".png"))
    made = skipped = failed = 0
    for p in srcs:
        # 투명한 PNG(로고 등)를 JPEG 로 바꾸면 투명한 자리가 검게 변한다.
        # 원본이 PNG 면 PNG 로 남긴다.
        is_png = p.suffix.lower() == ".png"
        ext = ".png" if is_png else ".jpg"
        jpg, avif = OUT / (p.stem + ext), OUT / (p.stem + ".avif")
        if avif.exists() and not force:
            skipped += 1
            continue
        fmt = ["-s", "format", "png"] if is_png else \
              ["-s", "format", "jpeg", "-s", "formatOptions", str(JPEG_Q)]
        r = subprocess.run(["sips", "-Z", str(LONG_SIDE), str(p), "--out", str(jpg)] + fmt,
                           capture_output=True)
        if r.returncode != 0 or not jpg.exists():
            print(f"  ✗ 크기 줄이기 실패 {p.name}"); failed += 1; continue
        embed_copyright(jpg)
        r = subprocess.run([str(BIN), str(jpg), str(avif), AVIF_Q], capture_output=True)
        if r.returncode != 0 or not avif.exists():
            print(f"  ✗ AVIF 실패 {p.name}"); failed += 1; continue
        made += 1

    tot = sum(f.stat().st_size for f in OUT.iterdir())
    print(f"\n만듦 {made}쌍 · 건너뜀 {skipped} · 실패 {failed}")
    print(f"images/strip/ 전체 {len(list(OUT.iterdir()))}개 · {tot/1048576:.1f}MB")


if __name__ == "__main__":
    main()
