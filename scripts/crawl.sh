#!/bin/sh

# Crawl a website with wget
# param the domain and address

wget \
     --recursive \
     --no-clobber \ # no overwrite of existing
     --html-extension \ 
     --convert-links \
     --restrict-file-names=windows \
     --domains $1 \
     --no-parent \
     -e robots=off \ # acts like not a crawler
     -c \ # resume a previous download
     -U mozilla \ # acts like a browser (mozilla)
     --random-wait \ # wait between download
     -E \ # get the right file extension
     #--page-requisites \ #no need
         $2