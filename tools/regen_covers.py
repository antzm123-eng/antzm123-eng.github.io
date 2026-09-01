#!/usr/bin/env python3
"""
카드 대표 사진(커버)을 원본에서 다시 만들어 선명하게 바꾸는 도구.

왜 필요한가
  커버 썸네일이 대부분 500px 이라, 화면 폭 800px 에서 623px 로 표시될 때
  늘려 그리게 되어 흐려진다. 레티나 화면은 어느 폭에서도 부족하다.
  images/full 은 워터마크가 합성돼 있어 재료로 쓸 수 없으므로,
  워터마크 없는 원본 사진 폴더에서 다시 만들어야 한다.

무엇을 하는가
  1. 원본 폴더를 뒤져 각 커버에 해당하는 사진을 그림 내용으로 찾아낸다
     (파일 이름·폴더 이름에 의존하지 않는다. 확신도를 함께 보고한다)
  2. 커버를 700px 로 다시 만들고, 1280px 짜리 @2x 를 새로 만든다
  3. 저작권 문구를 재인코딩 없이 삽입한다
  4. 낡은 .avif 를 지우고 다시 만든다  ← 이걸 빼먹으면 아무 효과가 없다
  5. index.html 의 커버를 srcset 으로 바꿔 화면에 맞는 크기를 고르게 한다

사용법
  python3 tools/regen_covers.py --src ~/사진원본폴더            # 미리보기(파일 안 건드림)
  python3 tools/regen_covers.py --src ~/사진원본폴더 --apply    # 실제 실행
  python3 tools/regen_covers.py --src ... --apply --key ocsu   # 한 작업만

되돌리기
  git checkout -- . && git clean -fd images
"""

import argparse
import os
import re
import shutil
import struct
import subprocess
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HTML = ROOT / "index.html"
THUMB_DIR = ROOT / "images" / "thumb"

COPYRIGHT = ("© 2026 강윤구 (Kang Yungu). All rights reserved. "
             "Unauthorized use, redistribution, or AI training prohibited. "
             "Contact: antzm123@naver.com")
PAYLOAD = COPYRIGHT.encode("utf-8")

SMALL_W = 700            # 기본 커버 (가로 폭 기준)
LARGE_W = 1280           # 레티나용 @2x (가로 폭 기준)
AVIF_Q = "0.60"          # 썸네일 AVIF 품질 (CLAUDE.md 규칙)
JPEG_Q = "85"
SIG = 32                 # 그림 대조용 축소 크기
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".heic", ".heif", ".tif", ".tiff", ".webp"}


def run(cmd):
    return subprocess.run([str(c) for c in cmd], capture_output=True, text=True)


def die(msg):
    sys.exit(f"❌ {msg}")


# ── 이미지 백엔드 ────────────────────────────────────────────────────
# macOS 에서는 sips + to_avif.swift (기존 도구와 같은 결과),
# 그 밖의 환경에서는 Pillow 를 쓴다. 없으면 무엇이 없는지 알려준다.
HAVE_SIPS = shutil.which("sips") is not None
try:
    from PIL import Image
    HAVE_PIL = True
except ImportError:
    HAVE_PIL = False


def backend_name():
    return "sips (macOS)" if HAVE_SIPS else ("Pillow" if HAVE_PIL else None)


def to_png_thumb(src, dst, size):
    """대조용으로 아주 작은 PNG 를 만든다."""
    if HAVE_SIPS:
        # -Z 는 비율을 지켜 32×21 처럼 나온다 → 지문 길이가 달라져 비교가 깨진다.
        # -z 로 가로세로를 정확히 같게 강제한다 (Pillow 쪽과 동일한 처리).
        r = run(["sips", "-s", "format", "png", "-z", size, size, src, "--out", dst])
        return r.returncode == 0 and Path(dst).exists()
    im = Image.open(src)
    im = im.convert("L").resize((size, size), Image.LANCZOS)
    im.save(dst, "PNG")
    return True


def resize_to(src, dst, target_w, as_png):
    """가로 폭을 target_w 로 맞춘다 (확대는 하지 않는다). 실제 가로 폭을 돌려준다."""
    w, h = dimensions(src)
    if not w:
        die(f"이미지 크기를 읽지 못했습니다: {src}")
    scale = min(1.0, target_w / w)
    out_w, out_h = max(1, round(w * scale)), max(1, round(h * scale))
    if HAVE_SIPS:
        fmt = "png" if as_png else "jpeg"
        cmd = ["sips", "-s", "format", fmt]
        if not as_png:
            cmd += ["-s", "formatOptions", JPEG_Q]
        if scale < 1.0:
            # -Z 는 "최대 변" 기준이라 세로 사진에서는 가로가 목표보다 작아진다.
            # --resampleWidth 로 가로를 직접 지정한다.
            cmd += ["--resampleWidth", out_w]
        cmd += [src, "--out", dst]
        r = run(cmd)
        if r.returncode != 0 or not Path(dst).exists():
            die(f"이미지 변환 실패: {src}\n{r.stderr}")
        return dimensions(dst)[0]
    im = Image.open(src)
    im = im.resize((out_w, out_h), Image.LANCZOS)
    if as_png:
        im.save(dst, "PNG", optimize=True)
    else:
        im.convert("RGB").save(dst, "JPEG", quality=int(JPEG_Q), optimize=True)
    return out_w


AVIF_BIN = Path("/tmp/gloudy_to_avif")


def to_avif(src, dst):
    if HAVE_SIPS:
        if not AVIF_BIN.exists():
            if not shutil.which("swiftc"):
                die("swiftc 가 없습니다. Xcode Command Line Tools 를 설치해주세요:\n"
                    "   xcode-select --install")
            r = run(["swiftc", "-O", "-o", AVIF_BIN, ROOT / "tools" / "to_avif.swift"])
            if r.returncode != 0:
                die("AVIF 변환기 컴파일 실패:\n" + r.stderr)
        r = run([AVIF_BIN, src, dst, AVIF_Q])
        if r.returncode != 0 or not Path(dst).exists():
            die(f"AVIF 변환 실패: {src}\n{r.stderr}")
        return
    # 맥이 아닌 환경(시험용). Pillow q65 ≈ CoreGraphics 0.60 — 실측 오차 2%.
    # to_avif.swift 는 TIFF/IPTC 에 넣지만 Pillow 는 그 경로가 없어 XMP 로 넣는다.
    im = Image.open(src)
    im.save(dst, "AVIF", quality=65, xmp=PAYLOAD)


# ── 파일 구조 읽기 (외부 도구 없이) ──────────────────────────────────
def dimensions(path):
    if HAVE_SIPS:
        r = run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", path])
        w = h = 0
        for line in r.stdout.splitlines():
            if "pixelWidth:" in line:
                w = int(line.split()[-1])
            elif "pixelHeight:" in line:
                h = int(line.split()[-1])
        if w and h:
            return w, h
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
    elif b"ispe" in d[:4096]:
        i = d.index(b"ispe")
        return struct.unpack(">II", d[i + 8:i + 16])
    return (0, 0)


def png_gray(path):
    """PNG 를 회색조 픽셀 목록으로 읽는다 (Pillow 없이)."""
    d = Path(path).read_bytes()
    pos, idat, w = 8, b"", 0
    depth = ctype = 0
    plte = b""
    while pos < len(d):
        ln = struct.unpack(">I", d[pos:pos + 4])[0]
        typ = d[pos + 4:pos + 8]
        body = d[pos + 8:pos + 8 + ln]
        if typ == b"IHDR":
            w, h, depth, ctype = (*struct.unpack(">II", body[:8]), body[8], body[9])
            if body[12]:                      # 인터레이스 PNG 는 다루지 않는다
                return None
        elif typ == b"PLTE":
            plte = body
        elif typ == b"IDAT":
            idat += body
        elif typ == b"IEND":
            break
        pos += 12 + ln
    if depth != 8 or ctype not in (0, 2, 3, 6):
        return None
    ch = {0: 1, 2: 3, 3: 1, 6: 4}[ctype]
    if ctype == 3 and len(plte) < 3:
        return None
    raw = zlib.decompress(idat)
    stride = w * ch
    out, prev = [], bytearray(stride)
    p = 0
    while p < len(raw):
        f = raw[p]; p += 1
        line = bytearray(raw[p:p + stride]); p += stride
        for x in range(stride):
            a = line[x - ch] if x >= ch else 0
            b = prev[x]
            c = prev[x - ch] if x >= ch else 0
            if f == 1: line[x] = (line[x] + a) & 255
            elif f == 2: line[x] = (line[x] + b) & 255
            elif f == 3: line[x] = (line[x] + (a + b) // 2) & 255
            elif f == 4:
                pp = a + b - c
                pa, pb, pc = abs(pp - a), abs(pp - b), abs(pp - c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[x] = (line[x] + pr) & 255
        for x in range(0, stride, ch):
            if ctype == 3:
                i3 = line[x] * 3
                r_, g_, b_ = plte[i3], plte[i3 + 1], plte[i3 + 2]
            elif ch == 1:
                out.append(line[x]); continue
            else:
                r_, g_, b_ = line[x], line[x + 1], line[x + 2]
            out.append((r_ * 299 + g_ * 587 + b_ * 114) // 1000)
        prev = line
    return out


def signature(path, tmp):
    """그림 내용을 32×32 회색조 지문으로 만든다 (밝기 차이는 정규화)."""
    p = tmp / "sig.png"
    if p.exists():
        p.unlink()
    if not to_png_thumb(path, p, SIG):
        return None
    px = png_gray(p)
    if not px:
        return None
    n = len(px)
    mean = sum(px) / n
    var = sum((v - mean) ** 2 for v in px) / n
    sd = var ** 0.5 or 1.0
    return [(v - mean) / sd for v in px]


def distance(a, b):
    if a is None or b is None or len(a) != len(b):
        return 9e9
    return sum(abs(x - y) for x, y in zip(a, b)) / len(a)


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


# ── index.html 다루기 ────────────────────────────────────────────────
# 화면 폭에 따라 커버가 실제로 몇 px 로 그려지는지를 브라우저에게 알려준다.
#   ≤800px  1칼럼: 88vw − 카드 안쪽 여백 64px
#   ≤1280px 2칼럼: (90vw − 간격 24px)/2 − 64px
#   그 위    3칼럼: (88vw − 간격 48px)/3 − 64px
SIZES = ("(max-width:800px) calc(88vw - 64px),"
         "(max-width:1280px) calc(45vw - 76px),"
         "calc(29.33vw - 80px)")

# 커버 마크업을 찾는다. 아직 안 고친 형태와 이미 srcset 으로 고친 형태를
# 둘 다 잡아야 한다 (그래야 두 번 돌려도 동작한다).
COVER_RE = re.compile(
    r'<picture>(?:(?!</picture>).)*?<img class="cover-img"'
    r'(?:(?!</picture>).)*?src="images/thumb/(?P<key>[A-Za-z0-9_]+)\.(?P<ext>jpg|png)"'
    r'(?:(?!</picture>).)*?alt="(?P<alt>[^"]*)"(?:(?!</picture>).)*?</picture>',
    re.S)


def html_covers():
    """index.html 이 커버로 쓰는 (키, 확장자) 목록."""
    text = HTML.read_text(encoding="utf-8")
    return [(m.group("key"), m.group("ext")) for m in COVER_RE.finditer(text)]


def patch_html(widths):
    """widths = {키: (작은 파일 가로, @2x 가로)} — 실제 만들어진 폭을 그대로 적는다."""
    text = HTML.read_text(encoding="utf-8")

    def sub(m):
        key, ext, alt = m.group("key"), m.group("ext"), m.group("alt")
        if key not in widths:
            return m.group(0)
        w1, w2 = widths[key]
        a1, a2 = f"images/thumb/{key}.avif", f"images/thumb/{key}@2x.avif"
        o1, o2 = f"images/thumb/{key}.{ext}", f"images/thumb/{key}@2x.{ext}"
        big = f", {a2} {w2}w" if w2 > w1 else ""
        bigo = f", {o2} {w2}w" if w2 > w1 else ""
        return (f'<picture>'
                f'<source type="image/avif" srcset="{a1} {w1}w{big}" sizes="{SIZES}">'
                f'<img class="cover-img" loading="lazy" decoding="async" '
                f'src="{o1}" srcset="{o1} {w1}w{bigo}" sizes="{SIZES}" '
                f'alt="{alt}"></picture>')

    new, n = COVER_RE.subn(sub, text)
    if n:
        HTML.write_text(new, encoding="utf-8")
    return n


# ── 본 작업 ─────────────────────────────────────────────────────────
def collect_sources(src_dir):
    files = [p for p in sorted(src_dir.rglob("*"))
             if p.suffix.lower() in IMAGE_EXTS and not p.name.startswith(".")
             and ROOT not in p.parents and p.parent != ROOT]
    if not files:
        die(f"원본 사진을 찾지 못했습니다: {src_dir}\n"
            f"   지원 형식: {', '.join(sorted(IMAGE_EXTS))}")
    return files


def main():
    ap = argparse.ArgumentParser(description="커버 사진을 원본에서 다시 만들어 선명하게 한다")
    ap.add_argument("--src", required=True, help="워터마크 없는 원본 사진이 든 폴더 (하위 폴더까지 찾습니다)")
    ap.add_argument("--apply", action="store_true", help="실제로 파일을 바꾼다 (없으면 미리보기만)")
    ap.add_argument("--key", action="append", help="이 작업만 처리 (여러 번 쓸 수 있음)")
    ap.add_argument("--max-distance", type=float, default=0.45,
                    help="원본을 같은 사진으로 인정할 최대 차이 (작을수록 엄격, 기본 0.45)")
    args = ap.parse_args()

    if backend_name() is None:
        die("이미지 변환 도구가 없습니다. macOS 라면 sips 가 있어야 하고,\n"
            "   그 밖의 환경이라면  pip install pillow  가 필요합니다.")
    src_dir = Path(args.src).expanduser().resolve()
    if not src_dir.is_dir():
        die(f"폴더가 아닙니다: {src_dir}")

    covers = html_covers()
    if args.key:
        want = set(args.key)
        covers = [(k, e) for k, e in covers if k.rsplit("_", 1)[0] in want or k in want]
        if not covers:
            die(f"해당하는 커버가 없습니다: {', '.join(sorted(want))}")

    print(f"이미지 처리: {backend_name()}")
    print(f"커버 {len(covers)}장 · 원본 폴더 {src_dir}")

    tmp = ROOT / ".regen_tmp"
    tmp.mkdir(exist_ok=True)
    try:
        sources = collect_sources(src_dir)
        print(f"원본 후보 {len(sources)}장 — 지문 만드는 중…")
        src_sig = []
        for i, p in enumerate(sources):
            s = signature(p, tmp)
            if s:
                src_sig.append((p, s))
            if (i + 1) % 25 == 0:
                print(f"   {i + 1}/{len(sources)}")
        if not src_sig:
            die("원본 사진의 지문을 만들지 못했습니다.")

        print()
        print(f"{'커버':<18}{'찾은 원본':<34}{'차이':>7}{'2등과':>8}  판정")
        print("─" * 78)
        plan, skipped = [], []
        for key, ext in covers:
            cur = THUMB_DIR / f"{key}.{ext}"
            tgt = signature(cur, tmp)
            ranked = sorted(((distance(tgt, s), p) for p, s in src_sig), key=lambda x: x[0])
            d0, p0 = ranked[0]
            d1 = ranked[1][0] if len(ranked) > 1 else 9e9
            ok = d0 <= args.max_distance and d0 < d1 * 0.6
            mark = "✅ 확실" if ok else ("⚠️  애매 — 건너뜀" if d0 <= args.max_distance else "❌ 못 찾음")
            print(f"{key:<18}{p0.name[:33]:<34}{d0:7.3f}{d1:8.3f}  {mark}")
            (plan if ok else skipped).append((key, ext, cur, p0))

        # 이 저장소가 내보낸 파일(<키>_<번호>.jpg)을 원본으로 착각하는 실수를 막는다.
        # images/full 은 워터마크가 합성돼 있어서, 그걸 재료로 쓰면 커버에 워터마크가 찍힌다.
        # 카메라 파일도 IMG_0031.jpg 처럼 생겼으므로 "밑줄+숫자" 로 판단하면 안 된다.
        # 파일 이름이 커버의 이름과 똑같을 때만 (= 우리가 내보낸 파일) 막는다.
        looks_exported = [(k, p0.name) for k, ext, cur, p0 in plan if p0.stem == k]
        if looks_exported:
            die("원본이 아니라 이 사이트가 내보낸 파일을 가리키고 있는 것 같습니다:\n"
                + "\n".join(f"   {k} ← {n}" for k, n in looks_exported[:5])
                + f"\n   ({len(looks_exported)}건)\n"
                "   images/full 은 워터마크가 합성돼 있어 재료로 쓸 수 없습니다.\n"
                "   카메라에서 받은 원본 사진 폴더를 --src 로 지정해주세요.")

        if skipped:
            print()
            print(f"⚠️  {len(skipped)}장은 원본을 확신할 수 없어 건드리지 않습니다: "
                  + ", ".join(k for k, *_ in skipped))

        if not args.apply:
            print()
            print("미리보기만 했습니다. 실제로 바꾸려면  --apply  를 붙여 다시 실행하세요.")
            return

        print()
        print(f"{'커버':<16}{'전':>16}{'후 (기본)':>16}{'후 (@2x)':>16}")
        print("─" * 64)
        widths = {}
        for key, ext, cur, origin in plan:
            before_px = dimensions(cur)[0]
            before_kb = (cur.stat().st_size
                         + (cur.with_suffix('.avif').stat().st_size
                            if cur.with_suffix('.avif').exists() else 0)) // 1024
            as_png = (ext == "png")
            small = THUMB_DIR / f"{key}.{ext}"
            large = THUMB_DIR / f"{key}@2x.{ext}"
            w1 = resize_to(origin, small, SMALL_W, as_png)
            w2 = resize_to(origin, large, LARGE_W, as_png)
            for p in (small, large):
                embed_copyright(p)
                av = p.with_suffix(".avif")
                if av.exists():          # 낡은 AVIF 를 반드시 지우고 다시 만든다
                    av.unlink()
                to_avif(p, av)
            s_kb = (small.stat().st_size + small.with_suffix('.avif').stat().st_size) // 1024
            l_kb = (large.stat().st_size + large.with_suffix('.avif').stat().st_size) // 1024
            print(f"{key:<16}{f'{before_px}px {before_kb}KB':>16}"
                  f"{f'{w1}px {s_kb}KB':>16}{f'{w2}px {l_kb}KB':>16}")
            widths[key] = (w1, w2)

        n = patch_html(widths)
        print()
        print(f"index.html 커버 {n}개를 srcset 으로 바꿨습니다.")
        print("이제 확인 도구를 돌려주세요:  python3 tools/check_covers.py")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
