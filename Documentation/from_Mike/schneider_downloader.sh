#!/bin/bash

LINKS="schneider_download_links.txt"
URL='https://www.se.com/ww/en/download/search/firmware/?docTypeGroup=3541958-Software+%26+Firmware&keyword=firmware&sortByField=Document_Date_New&itemsPerPage=100'
#'https://www.se.com/ww/en/download/search/firmware/?docTypeGroup=3541958-Software+%26+Firmware&keyword=firmware&sortByField=Document_Date_New&itemsPerPage=100&pageNumber=2'
#-> pageNumber .. 14
# -> lynx -dump -hiddenlinks=listonly $URL | grep "Archive_Name" >> $ABB_LINKS

SAVE_PATH="/home/m1k3/firmware/firmware_downloaded/schneider/"
if ! [[ -d "$SAVE_PATH" ]]; then
  mkdir -p "$SAVE_PATH"
fi

echo "[*] Generating URL list for Schneider Electrics"
for i in $(seq 15); do
  echo "[*] Download page #$i"
  if [[  "$i" -eq 1 ]]; then
    lynx -dump -hiddenlinks=listonly "$URL" | grep "Archive_Name" | grep -i "firmware" | sed -e 's/^.*https/https/' >> "$LINKS"
  else
    lynx -dump -hiddenlinks=listonly "$URL""&pageNumber=$i" | grep "Archive_Name" | grep -i "firmware" | sed -e 's/^.*https/https/' >> "$LINKS"
  fi
done

sort -u "$LINKS" > "$LINKS".tmp
mv "$LINKS".tmp "$LINKS"

FILE_CNT="$(wc -l "$LINKS" | cut -d\  -f1)"
echo "[*] Detected $FILE_CNT firmware files for download"

i=0
while read URL; do
  i=$((i+1))
  FILENAME="$(echo $URL | sed 's/.*p_Archive_Name=//' | sed 's/&p_enDocType.*//' | tr "/" "_")"
  echo "[*] Downloading $URL to $FILENAME ($i/$FILE_CNT)"
  if [[ -f "$FILENAME" ]]; then 
    echo "[*] skipping $FILENAME"
    continue
  fi
  wget "$URL" -O "$SAVE_PATH"/"$FILENAME"
done < "$LINKS"

echo -e "[*] Finished downloading $FILE_CNT firmware files to $SAVE_PATH"

