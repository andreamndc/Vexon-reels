#!/usr/bin/env bash
# Encode the render for Instagram/TikTok upload (H.264 high, CRF 20, <=16 Mbps, faststart).
# Usage: finalize.sh <render.mp4> <final.mp4> [licensed_music.wav|mp3] [music_offset_seconds]
# Without music a silent AAC track is added (client adds trending sound in-app).
set -euo pipefail
IN="$1"; OUT="$2"; MUSIC="${3:-}"; OFF="${4:-0}"
V="-c:v libx264 -preset slow -crf 20 -maxrate 16M -bufsize 32M -pix_fmt yuv420p -profile:v high"
if [[ -n "$MUSIC" ]]; then
  D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$IN")
  ffmpeg -v error -y -i "$IN" -ss "$OFF" -i "$MUSIC" -map 0:v -map 1:a $V -c:a aac -b:a 192k \
    -af "afade=t=out:st=$(python3 -c "print($D-0.8)"):d=0.8" -shortest -movflags +faststart "$OUT"
else
  ffmpeg -v error -y -i "$IN" -f lavfi -i anullsrc=r=44100:cl=stereo $V -c:a aac -b:a 128k -shortest -movflags +faststart "$OUT"
fi
ffprobe -v error -show_entries format=duration,size -of compact "$OUT"
