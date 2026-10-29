#!/bin/bash
[ $1 ] || {
    echo "passe o pacote como parametro".
    exit 0 
}

AAPT=$(find "$HOME/Android/Sdk/build-tools" -name aapt -type f | sort -V | tail -1)

echo $("$AAPT" dump badging $1 | grep "^package:"|egrep '^package')|sed -re 's/ /\n/g'
