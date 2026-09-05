#!/bin/bash
# Resumable + integrity-checked Zenodo downloader. Single instance. Safe to re-run any time.
cd "F:/d app/research paper" || exit 1
LOCK=workspace/datasets/.download.lock
if [ -f "$LOCK" ] && kill -0 "$(cat "$LOCK" 2>/dev/null)" 2>/dev/null; then
  echo "downloader already running (pid $(cat "$LOCK"))"; exit 0
fi
echo $$ > "$LOCK"; trap 'rm -f "$LOCK"' EXIT
M=workspace/datasets/manifest.tsv
for pass in $(seq 1 30); do
  incomplete=0
  while IFS=$'\t' read -r path size url md5; do
    [ -z "$path" ] && continue
    have=0; [ -f "$path" ] && have=$(stat -c %s "$path")
    if [ "$have" -eq "$size" ]; then
      got=$(md5sum "$path" | cut -d' ' -f1)
      if [ "$got" = "$md5" ]; then continue; fi
      echo "  !! $(basename "$path") md5 mismatch - re-downloading"; rm -f "$path"; have=0
    fi
    incomplete=$((incomplete+1))
    for try in $(seq 1 12); do
      now=0; [ -f "$path" ] && now=$(stat -c %s "$path")
      if [ "$now" -gt "$size" ]; then echo "  !! $(basename "$path") overshot - restarting"; rm -f "$path"; now=0; fi
      before=$now
      curl -sfL -C - --retry 5 --retry-delay 3 --retry-all-errors \
           --connect-timeout 30 --speed-time 45 --speed-limit 20480 \
           -A "research-corpus/1.0" -o "$path" "$url"
      now=0; [ -f "$path" ] && now=$(stat -c %s "$path")
      if [ "$now" -eq "$size" ]; then
        got=$(md5sum "$path" | cut -d' ' -f1)
        if [ "$got" = "$md5" ]; then echo "  DONE $(basename "$path") $((now/1000000)) MB (md5 ok)"; break; fi
        echo "  !! $(basename "$path") completed but md5 bad - discarding"; rm -f "$path"; now=0
      fi
      echo "  .. $(basename "$path") $((now/1000000))/$((size/1000000)) MB (try $try)"
      [ "$now" -le "$before" ] && sleep 8
    done
  done < "$M"
  [ "$incomplete" -eq 0 ] && { echo "ALL DATASETS COMPLETE AND VERIFIED"; exit 0; }
  echo "[pass $pass] $incomplete file(s) outstanding"
done
echo "STOPPED after 30 passes - re-run to continue"
