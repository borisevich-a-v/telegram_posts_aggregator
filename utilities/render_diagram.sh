#!/usr/bin/env bash

DIR_DRAWIO="./documentaion/diagrams/drawio_sources"
DIR_IMAGES="./documentaion/diagrams"

shopt -s nullglob

for file in "$DIR_DRAWIO"/*.drawio; do
  echo "Processing: $file"

  xml_file="${file%.drawio}.xml"
  [ -f "$xml_file" ] && rm -f "$xml_file"

  drawio --export --format xml "$file"

  while [ ! -f "$xml_file" ]; do
    sleep 0.1
  done

  pages_count=$(xmlstarlet sel -t -v "count(//mxfile/diagram)" "$xml_file")

  file_name=$(basename "$file" .drawio)

  for ((i=0; i<pages_count; i++)); do
    png_file="${DIR_IMAGES}/${file_name}$((i+1)).png"
    echo "  -> Export to png (page $((i+1))/$pages_count): $png_file"
    drawio --export --border 10 --page-index $i --output "$png_file" "$file"
  done

  [ -f "$xml_file" ] && rm -f "$xml_file"

  drawio --export --format png --output "${DIR_IMAGES}/${file_name}.png" "$file"

  echo "$file Processed successfully."
  echo "----------------------------------"
done
