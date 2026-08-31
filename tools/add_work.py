#!/usr/bin/env python3
"""
새 작업물을 포트폴리오에 추가하는 도구.

사진 폴더 하나를 주면 아래를 전부 자동으로 처리합니다.
  1. 원본을 최대 1600px 로 축소          (무단 인쇄 사용 방지)
  2. 워터마크 'H_yun_9u' 합성            (오른쪽 아래, 불투명도 60%)
  3. 저작권 정보 삽입                     (재인코딩 없이 파일 구조에 직접)
  4. 목록용 썸네일 최대 700px 생성        (워터마크 없음)
  5. index.html 에 카드·갤러리·제목 등록  (alt·접근성 속성 포함)

사용 예:
  python3 tools/add_work.py \\
    --key    hansam3 \\
    --title  "한샘교회 청소년 여름 수련회 스냅" \\
    --desc   "찬양과 기도의 순간을 따뜻한 톤으로 담았습니다." \\
    --tag    Photo \\
    --cat    visual \\
    --date   2026.08 \\
    --extra  "개인 작업 · Canon EOS 200D" \\
    --src    ~/Desktop/한샘수련회

되돌리려면:  git checkout -- . && git clean -fd images
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HTML = ROOT / "index.html"
FULL_DIR = ROOT / "images" / "full"
THUMB_DIR = ROOT / "images" / "thumb"
WM_SRC = ROOT / "tools" / "watermark.swift"
WM_BIN = ROOT / "tools" / ".watermark-bin"

COPYRIGHT = ("© 2026 강윤구 (Kang Yungu). All rights reserved. "
             "Unauthorized use, redistribution, or AI training prohibited. "
             "Contact: antzm123@naver.com")
PAYLOAD = COPYRIGHT.encode("utf-8")

FULL_MAX = 1600
THUMB_MAX = 700
WM_TEXT = "H_yun_9u"
WM_SIZE, WM_ALPHA, WM_MARGIN = "0.024", "0.60", "0.030"
PREVIEW_COUNT = 4
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".heic", ".heif", ".tif", ".tiff"}


# ── 유틸 ────────────────────────────────────────────────────────────
def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def die(msg):
    sys.exit(f"❌ {msg}")


def ensure_watermark_tool():
    """워터마크 실행파일이 없으면 Swift 소스에서 컴파일한다."""
    if WM_BIN.exists():
        return
    if not shutil.which("swiftc"):
        die("swiftc 가 없습니다. Xcode Command Line Tools 를 설치해주세요:\n"
            "   xcode-select --install")
    print("  워터마크 도구 컴파일 중…")
    r = run(["swiftc", "-O", "-o", str(WM_BIN), str(WM_SRC)])
    if r.returncode != 0:
        die("워터마크 도구 컴파일 실패:\n" + r.stderr)


def dimensions(path):
    r = run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", str(path)])
    w = h = 0
    for line in r.stdout.splitlines():
        if "pixelWidth:" in line:
            w = int(line.split()[-1])
        elif "pixelHeight:" in line:
            h = int(line.split()[-1])
    return w, h


def to_jpeg(src, dst, max_side):
    """JPEG 로 변환하면서 최대 변을 max_side 로 맞춘다 (확대는 하지 않음)."""
    w, h = dimensions(src)
    cmd = ["sips", "-s", "format", "jpeg", "-s", "formatOptions", "85"]
    if max(w, h) > max_side:
        cmd += ["-Z", str(max_side)]
    cmd += [str(src), "--out", str(dst)]
    r = run(cmd)
    if r.returncode != 0 or not dst.exists():
        die(f"이미지 변환 실패: {src}\n{r.stderr}")


def embed_copyright(path):
    """재인코딩 없이 저작권 문구를 파일 구조에 직접 삽입한다."""
    d = path.read_bytes()
    if PAYLOAD in d:
        return False
    if d[:2] == b"\xff\xd8":                      # JPEG → COM 세그먼트
        pos = 2
        while pos + 4 <= len(d) and d[pos] == 0xFF and 0xE0 <= d[pos + 1] <= 0xEF:
            pos += 2 + ((d[pos + 2] << 8) | d[pos + 3])
        out = (d[:pos] + b"\xff\xfe"
               + (len(PAYLOAD) + 2).to_bytes(2, "big") + PAYLOAD + d[pos:])
    elif d[:8] == b"\x89PNG\r\n\x1a\n":           # PNG → iTXt 청크
        data = b"Copyright" + b"\x00" * 5 + PAYLOAD
        chunk = (len(data).to_bytes(4, "big") + b"iTXt" + data
                 + zlib.crc32(b"iTXt" + data).to_bytes(4, "big"))
        i = d.rfind(b"IEND")
        out = d[:i - 4] + chunk + d[i - 4:]
    else:
        return False
    path.write_bytes(out)
    return True


def watermark(src, dst):
    r = run([str(WM_BIN), str(src), str(dst), WM_TEXT, WM_SIZE, WM_ALPHA, WM_MARGIN])
    if r.returncode != 0 or not dst.exists():
        die(f"워터마크 합성 실패: {src}\n{r.stderr}")


def preview_indices(total):
    """미리보기로 보여줄 사진 번호를 고르게 뽑는다."""
    if total <= PREVIEW_COUNT:
        return list(range(total))
    step = total / PREVIEW_COUNT
    return sorted({min(total - 1, int(i * step)) for i in range(PREVIEW_COUNT)})


def esc(text):
    return (text.replace("&", "&amp;").replace("<", "&lt;")
                .replace(">", "&gt;").replace('"', "&quot;"))


# ── 이미지 처리 ──────────────────────────────────────────────────────
def process_images(key, src_dir):
    files = sorted(p for p in src_dir.iterdir()
                   if p.suffix.lower() in IMAGE_EXTS and not p.name.startswith("."))
    if not files:
        die(f"사진을 찾을 수 없습니다: {src_dir}\n"
            f"   지원 형식: {', '.join(sorted(IMAGE_EXTS))}")

    FULL_DIR.mkdir(parents=True, exist_ok=True)
    THUMB_DIR.mkdir(parents=True, exist_ok=True)
    tmp = ROOT / ".add_work_tmp"
    tmp.mkdir(exist_ok=True)
    made = []
    try:
        for i, src in enumerate(files):
            full = FULL_DIR / f"{key}_{i}.jpg"
            thumb = THUMB_DIR / f"{key}_{i}.jpg"
            stage = tmp / f"{i}.jpg"

            to_jpeg(src, stage, FULL_MAX)      # 1) 축소 + JPEG
            watermark(stage, full)             # 2) 워터마크
            embed_copyright(full)              # 3) 저작권 정보

            to_jpeg(src, thumb, THUMB_MAX)     # 4) 썸네일 (워터마크 없음)
            embed_copyright(thumb)

            made.append((src.name, full, thumb))
            print(f"  [{i + 1}/{len(files)}] {src.name}"
                  f"  →  {full.name} ({full.stat().st_size // 1024}KB)"
                  f" / thumb {thumb.stat().st_size // 1024}KB")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return made


# ── HTML 수정 ────────────────────────────────────────────────────────
def build_card(a, total):
    idxs = preview_indices(total)
    more = total - len(idxs)
    first_hidden = next((n for n in range(total) if n not in idxs), 0)

    rows = []
    for n in idxs:
        rows.append(
            f'        <img class="g-thumb" data-gallery="{a.key}" loading="lazy" '
            f'src="images/thumb/{a.key}_{n}.jpg" data-index="{n}" '
            f'tabindex="0" role="button" '
            f'alt="{esc(a.title)} — {n + 1}번째 사진">')
    if more > 0:
        rows.append(
            f'        <div class="g-more" data-gallery="{a.key}" '
            f'data-index="{first_hidden}" role="button" tabindex="0" '
            f'aria-label="{esc(a.title)} 사진 {more}장 더 보기">'
            f'<span>+{more}</span><span class="more-label">MORE</span></div>')

    meta = f"{a.date} · {a.tag}"
    if a.extra:
        meta += f" · {a.extra}"

    return (
        f'    <div class="work-card show gallery-card" data-cat="{a.cat}">\n'
        f'      <div class="tag">{esc(a.tag)}</div>\n'
        f'      <h3>{esc(a.title)}</h3>\n'
        f'      <p>{esc(a.desc)}</p>\n'
        f'      <div class="gallery-preview" data-gallery="{a.key}">\n'
        + "\n".join(rows) + "\n"
        f'      </div>\n'
        f'      <div class="meta">{esc(meta)}</div>\n'
        f'    </div>\n')


def camel(key):
    parts = key.split("_")
    return parts[0] + "".join(p.capitalize() for p in parts[1:]) + "Images"


def update_html(a, total):
    s = HTML.read_text(encoding="utf-8")
    var = camel(a.key)

    if f'data-gallery="{a.key}"' in s:
        die(f"'{a.key}' 갤러리가 이미 있습니다. --key 를 다른 이름으로 바꿔주세요.")

    # 1) 이미지 배열
    arr = (f"const {var} = [\n"
           + "\n".join(f'  "images/full/{a.key}_{i}.jpg",' for i in range(total))
           + "\n];\n")
    anchor = "const galleries = {"
    if anchor not in s:
        die("index.html 에서 galleries 정의를 찾지 못했습니다.")
    s = s.replace(anchor, arr + "\n" + anchor, 1)

    # 2) galleries 등록
    s = re.sub(r"(const galleries = \{)", rf"\1 {a.key}: {var},", s, count=1)

    # 3) galleryTitles 등록
    if "const galleryTitles = {" not in s:
        die("index.html 에서 galleryTitles 정의를 찾지 못했습니다.")
    title_js = a.title.replace("\\", "\\\\").replace('"', '\\"')
    s = re.sub(r"(const galleryTitles = \{)",
               rf'\1"{a.key}": "{title_js}", ', s, count=1)

    # 4) 카드 삽입
    card = build_card(a, total)
    grid = '<div class="work-grid" id="workGrid">'
    if grid not in s:
        die("index.html 에서 work-grid 를 찾지 못했습니다.")
    if a.position == "top":
        s = s.replace(grid, grid + "\n" + card.rstrip("\n"), 1)
    else:
        i = s.index(grid)
        j = s.index("</div>\n  </section>", i)
        s = s[:j] + card + s[j:]

    HTML.write_text(s, encoding="utf-8")


# ── 메인 ─────────────────────────────────────────────────────────────
def main():
    p = argparse.ArgumentParser(
        description="새 작업물을 포트폴리오에 추가합니다.",
        formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    p.add_argument("--key", required=True,
                   help="영문 소문자 식별자 (예: hansam3). 파일명에 쓰입니다.")
    p.add_argument("--title", required=True, help="작업 제목")
    p.add_argument("--desc", required=True, help="한 줄 설명")
    p.add_argument("--src", required=True, help="사진이 들어있는 폴더 경로")
    p.add_argument("--date", required=True, help="예: 2026.08")
    p.add_argument("--tag", default="Photo",
                   help="Photo / Poster & Thumbnail / Logo Design (기본: Photo)")
    p.add_argument("--cat", default="visual", choices=["visual", "design"],
                   help="visual=사진 필터, design=포스터·디자인 필터 (기본: visual)")
    p.add_argument("--extra", default="개인 작업 · Canon EOS 200D",
                   help="날짜·태그 뒤에 붙는 추가 정보")
    p.add_argument("--position", default="top", choices=["top", "bottom"],
                   help="목록의 맨 위/맨 아래 (기본: top)")
    a = p.parse_args()

    if not re.fullmatch(r"[a-z][a-z0-9_]*", a.key):
        die("--key 는 영문 소문자·숫자·밑줄만 쓸 수 있습니다 (예: hansam3)")

    src_dir = Path(os.path.expanduser(a.src)).resolve()
    if not src_dir.is_dir():
        die(f"폴더를 찾을 수 없습니다: {src_dir}")

    print(f"\n📁 원본 폴더: {src_dir}")
    ensure_watermark_tool()
    print("\n🖼  이미지 처리 중…")
    made = process_images(a.key, src_dir)

    print("\n📝 index.html 수정 중…")
    update_html(a, len(made))

    print(f"""
✅ 완료 — '{a.title}' {len(made)}장 추가

   갤러리 키   {a.key}
   위치        목록 {'맨 위' if a.position == 'top' else '맨 아래'}
   분류        {'사진' if a.cat == 'visual' else '포스터·디자인'}

   확인:   미리보기 서버에서 새로고침
   되돌리기: git checkout -- . && git clean -fd images
""")


if __name__ == "__main__":
    main()
