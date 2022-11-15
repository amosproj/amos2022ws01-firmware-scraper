#!/bin/bash

LINKS="engenius_download_links.txt"
SAVE_PATH="/home/m1k3/firmware/firmware_downloaded/EnGenius/"

if ! [[ -d "$SAVE_PATH" ]]; then
  mkdir -p "$SAVE_PATH"
fi

URL='https://www.engeniustech.com/engenius-firmware-updates.html'
#lynx -dump -hiddenlinks=listonly https://www.engeniustech.com/engenius-firmware-updates.html | grep "\.zip\|\.bin"

lynx -dump -hiddenlinks=listonly "$URL" | grep "\.zip\|\.bin" | sed -e 's/^.*https/https/' >> $LINKS

sort -u "$LINKS" > "$LINKS".tmp
mv "$LINKS".tmp "$LINKS"

FILE_CNT="$(wc -l "$LINKS" | cut -d\  -f1)"
echo "[*] Detected $FILE_CNT firmware files for download"

i=0
while read URL; do
  i=$((i+1))
  FILENAME="$(basename "$URL")"
  echo "[*] Downloading $URL to file $FILENAME ($i/$FILE_CNT)"
  wget --no-check-certificate "$URL" -O "$SAVE_PATH"/"$FILENAME"
done < "$LINKS"

echo -e "[*] Finished downloading $FILE_CNT firmware files to $SAVE_PATH"
