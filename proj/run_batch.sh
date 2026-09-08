#!/bin/bash
# download -> aggregate -> delete, for each "id label ext" line passed on stdin
# GKEY must be exported in the environment before running (never hardcode a key here):
#   export GKEY="<google-drive-api-key>"
: "${GKEY:?set GKEY env var with the Google Drive API key}"
cd /home/user/claude/proj
while read -r id label ext; do
  [ -z "$id" ] && continue
  f="raw/dmr_${label}.${ext}"
  echo ">>> $label : downloading..."
  curl -sS -m 1800 -o "$f" "https://www.googleapis.com/drive/v3/files/${id}?alt=media&key=${GKEY}"
  sz=$(du -h "$f" | cut -f1)
  echo ">>> $label : $sz downloaded, aggregating..."
  python3 aggregate.py "$f" "$label" && rm -f "$f"
done
echo "=== batch done ==="; ls -la agg/