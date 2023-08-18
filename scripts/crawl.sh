#!/bin/sh

# Crawl a website with wget
# param the domain and address

echo "Downloading $2 from $1"

wget \
     --recursive \
     --continue \
     --no-clobber \
     --html-extension \
     --restrict-file-names=windows \
     --domains $1 \
     --no-parent \
     -e robots=off \
     -U mozilla \
     --random-wait \
     -E \
         $2