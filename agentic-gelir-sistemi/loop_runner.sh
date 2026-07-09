#!/usr/bin/env bash
# Arka plan lead tarama döngüsü — bu oturum/konteyner açık olduğu sürece çalışır.
# 10 dk'da bir: tara -> Excel'e ekle -> git commit -> push. Çıktı loop.log'a yazılır.
# NOT: Kalıcı 7/24 çalışma için gerçek yer VPS + cron'dur (bkz. docs/.../PLAN.md).
set -u
REPO="/home/user/bloody"
BR="claude/agentic-system-200k-income-ara9zi"
INTERVAL="${INTERVAL:-600}"   # saniye (varsayılan 10 dk)
cd "$REPO" || exit 1

while true; do
  sleep "$INTERVAL"
  LLM_MODE=mock python3 agentic-gelir-sistemi/scan.py agentic-gelir-sistemi/data/live_listings.json \
    >> agentic-gelir-sistemi/reports/loop.log 2>&1
  git add agentic-gelir-sistemi/reports/lead_scan.xlsx
  git commit -q -m "Automated lead scan cycle (background loop, TRT)" 2>/dev/null || true
  git push -q origin "$BR" 2>/dev/null || true
done
