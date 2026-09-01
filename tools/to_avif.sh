#!/bin/bash
# 이미지를 AVIF 로 변환한다. 저작권 정보는 변환하면서 같이 심긴다.
#   사용법:  bash tools/to_avif.sh
#   새 작업물을 add_work.py 로 추가한 뒤 이 스크립트를 한 번 돌리면 된다.
#   이미 .avif 가 있는 파일은 건너뛴다.
set -e
cd "$(dirname "$0")/.."
BIN="/tmp/gloudy_to_avif"
[ -x "$BIN" ] || swiftc -O -o "$BIN" tools/to_avif.swift
n=0
for f in images/thumb/* images/full/*; do
  case "$f" in *.avif) continue;; esac
  out="${f%.*}.avif"
  [ -f "$out" ] && continue
  case "$f" in images/thumb/*) q=0.60;; *) q=0.80;; esac
  "$BIN" "$f" "$out" $q >/dev/null && n=$((n+1))
done
echo "새로 변환한 이미지: ${n}장"
