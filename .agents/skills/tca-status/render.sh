#!/usr/bin/env bash
# Render the TCA status board: render.sh <body-file> [width] [title]
# Each body line is padded to the frame, one column less per emoji, so the
# right edge stays straight. Section rules follow body lines 1, 3, 6 and 8.
set -euo pipefail
# Pad by character count, not by printf's width rules, which differ between
# shells and glibc versions for emoji; ${#var} counts characters in a UTF-8 locale.
: "${LANG:=C.UTF-8}"; export LANG
body=$1
W=${2:-84}
title=${3:-"─ 🟦 TCA · outcome 2 "}
emoji='🟢\|🟡\|🔴\|▶️\|📝\|📄\|📋\|🔁\|⏰\|🔀\|✅\|⏳\|⬜\|🧪\|💾\|📈\|🧾\|❌\|🔧\|🔙\|🆕\|🧮\|🚪\|🟦'
rule() { printf '%s' "$1"; printf '─%.0s' $(seq 1 "$W"); printf '%s\n' "$2"; }
emoji_count() { printf '%s' "$1" | grep -o "$emoji" | wc -l; }
pad() { local n=$1; [ "$n" -gt 0 ] && printf '%*s' "$n" '' || true; }
te=$(emoji_count "$title")
printf '┌%s' "$title"; printf '─%.0s' $(seq 1 $((W - ${#title} - te))); printf '┐\n'
i=0
while IFS= read -r line; do
  i=$((i + 1))
  e=$(emoji_count "$line")
  printf '│%s' "$line"; pad $((W - e - ${#line})); printf '│\n'
  case $i in 1|3|6|8) rule '├' '┤' ;; esac
done < "$body"
rule '└' '┘'
