#!/usr/bin/env python3
"""커밋 전에 비공개 낱말이 파일에 섞여 들어갔는지 검사한다.

    python3 tools/check_private.py

낱말 목록은 .claude/private_terms.txt 에 있고, 그 폴더는 .gitignore 로 제외되어
GitHub 에 올라가지 않는다. 목록 파일이 없으면 조용히 통과한다.
"""
import os, sys, io

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIST = os.path.join(ROOT, '.claude', 'private_terms.txt')
SKIP_DIRS = {'.git', '.claude', 'node_modules'}
BINARY_EXT = {'.jpg', '.jpeg', '.png', '.avif', '.ico', '.woff', '.woff2', '.heic', '.pdf'}

if not os.path.exists(LIST):
    print(f'⚠️  {LIST} 없음 — 검사를 건너뜁니다.')
    sys.exit(0)

terms = []
for line in io.open(LIST, encoding='utf-8'):
    t = line.strip()
    if t and not t.startswith('#'):
        terms.append(t)

if not terms:
    print('⚠️  검사할 낱말이 없습니다.')
    sys.exit(0)

hits = []
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
    for fn in filenames:
        if os.path.splitext(fn)[1].lower() in BINARY_EXT:
            continue
        path = os.path.join(dirpath, fn)
        try:
            text = io.open(path, encoding='utf-8', errors='ignore').read()
        except OSError:
            continue
        for i, line in enumerate(text.splitlines(), 1):
            for t in terms:
                if t in line:
                    hits.append((os.path.relpath(path, ROOT), i, t, line.strip()[:70]))

if hits:
    print(f'❌ 비공개 낱말이 {len(hits)}곳에서 발견됐습니다 — 커밋하지 마세요.\n')
    for f, i, t, line in hits:
        print(f'   {f}:{i}  [{t}]  {line}')
    sys.exit(1)

print(f'✅ 비공개 낱말 {len(terms)}개 검사 — 발견 없음. 커밋해도 안전합니다.')
