#!/usr/bin/env bash
# Resumable download of an IDD dataset package that needs an INSAAN login.
# Usage:  bash idd_download.sh "https://idd.insaan.iiit.ac.in/dataset/download/<id>/" [output_dir]
# Re-run the same command at any time: it logs in again and resumes the partial file.
set -uo pipefail
LINK="${1:?give the dataset download link}"
OUT="${2:-data/idd3d}"
BASE="https://idd.insaan.iiit.ac.in"
mkdir -p "$OUT"; OUT="$(cd "$OUT" && pwd)"; cd "$OUT" || exit 1
JAR="$OUT/.idd_cookies.txt"
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"

login () {
  rm -f "$JAR"
  [ -n "${IDD_USER:-}" ] || read -rp "INSAAN username: " IDD_USER
  [ -n "${IDD_PASS:-}" ] || { read -rsp "INSAAN password: " IDD_PASS; echo; }
  curl -s -A "$UA" -c "$JAR" -b "$JAR" "$BASE/accounts/login/" -o /dev/null
  CSRF=$(awk '$6=="csrftoken"{print $7}' "$JAR" | tail -1)
  curl -s -A "$UA" -c "$JAR" -b "$JAR" -X POST "$BASE/accounts/login/" \
       -H "Referer: $BASE/accounts/login/" \
       --data-urlencode "csrfmiddlewaretoken=$CSRF" \
       --data-urlencode "username=$IDD_USER" --data-urlencode "password=$IDD_PASS" -o /dev/null
  if grep -q sessionid "$JAR"; then echo "Logged in."; else echo "Login failed (check username/password)."; exit 1; fi
}

probe () {   # prints content-type and file name of what the link returns
  curl -sIL -A "$UA" -b "$JAR" -c "$JAR" "$LINK" | tr -d '\r' > .idd_headers.txt
  CTYPE=$(grep -i '^content-type:' .idd_headers.txt | tail -1 | cut -d' ' -f2- | cut -d';' -f1)
  FNAME=$(grep -io 'filename="\?[^";]*' .idd_headers.txt | tail -1 | sed 's/filename="\{0,1\}//I')
  SIZE=$(grep -i '^content-length:' .idd_headers.txt | tail -1 | awk '{print $2}')
}

login
probe
if [[ "$CTYPE" == text/html* ]]; then
  curl -sL -A "$UA" -b "$JAR" -c "$JAR" "$LINK" -o idd_link_page.html
  echo "The link returns a web page, not the file (probably the licence page)."
  echo "Saved it as $OUT/idd_link_page.html - upload that file so the script can be adapted."
  exit 2
fi
OUTFILE="${FNAME:-IDD3D_download.bin}"; TOTAL="${SIZE:-}"
echo "File: $OUTFILE   type: $CTYPE   size: ${SIZE:-unknown} bytes"
rm -f index.html

while true; do
  caffeinate -i curl -L -A "$UA" -b "$JAR" -c "$JAR" -C - --retry 0 --speed-limit 1000 --speed-time 120 -o "$OUTFILE" "$LINK"
  rc=$?
  HAVE=$(stat -f%z "$OUTFILE" 2>/dev/null || stat -c%s "$OUTFILE" 2>/dev/null || echo 0)
  if [ "$rc" -eq 0 ] && { [ -z "$TOTAL" ] || [ "$HAVE" -ge "$TOTAL" ]; }; then
    echo "Done: $OUTFILE ($HAVE bytes)"; break
  fi
  echo "Interrupted (curl code $rc, $HAVE bytes so far). Retrying in 30 s..."
  sleep 30
  probe; [[ "${CTYPE:-}" == text/html* ]] && login     # session expired -> log in again
done
