#!/bin/bash

URL="https://library.abb.com/r?dkg=dkg_software&q=firmware"
LINKS="abb_download_links.txt"
SAVE_PATH="/home/m1k3/firmware/firmware_downloaded/abb/"

if ! [[ -d "$SAVE_PATH" ]]; then
  mkdir -p "$SAVE_PATH"
fi

echo "[*] Generating URL list for ABB firmware"
lynx -dump -hiddenlinks=listonly "$URL"  | sed 's/^.*\.\ https/https/' | grep "DocumentID" > "$LINKS"

FILE_CNT="$(wc -l "$LINKS" | cut -d\  -f1)"
echo "[*] Detected $FILE_CNT firmware files for download"

while read URL; do
  FILENAME="$(echo $URL | sed 's/.*DocumentID=//' | sed 's/&LanguageCode.*//' | tr "/" "_")"
  echo "[*] Downloading $URL to $FILENAME"
  wget "$URL" -O "$SAVE_PATH"/"$FILENAME"
done < "$LINKS"

echo -e "[*] Finished downloading $FILE_CNT firmware files to $SAVE_PATH"
