#!/bin/bash

URL='https://www.foscam.com/downloads/file.html?cate=firmware&id='
#-> pageNumber .. 14

SAVE_PATH="/home/m1k3/firmware_results/Firmware_images/Foscam"
if ! [[ -d "$SAVE_PATH" ]]; then
  mkdir -p "$SAVE_PATH"
fi

echo "[*] Downloading firmware files from Foscam"
for i in $(seq 500); do
  echo "[*] Download firmware #$i"
  wget --content-disposition "$URL""$i" -P "$SAVE_PATH"
done

echo -e "[*] Downloaded $(find "$SAVE_PATH" -type f | wc -l) firmware files to $SAVE_PATH"

