#!/bin/sh
for name in "$@"
do
    cp "$name" "$name"~ && tr -d '\r' < "$name"~ > "$name" && rm "$name"~
done