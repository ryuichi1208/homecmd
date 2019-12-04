#!/bin/bash

if [ $# -ne 1 ]; then
  echo "Invalid arguments" 1>&2
  exit 1
fi

URL=$1

curl ${URL} -sLo /dev/null -w \
  "
Request URL       : %{url_effective}\n\
DNS Lookup        : %{time_namelookup} [s]\n\
TCP Connection    : %{time_connect} [s]\n\
SSL Connection    : %{time_appconnect} [s]\n\
Server Processing : %{time_pretransfer} [s]\n\
Content Transfer  : %{time_starttransfer} [s]\n\
Total TIme        : %{time_total} [s]\n\
===\n\
HTTP Status Code  : %{http_code}\n\
SSL Veryfi Code   : %{ssl_verify_result}\n\
Num Redirects     : %{num_redirects}\n\
Downloads Size    : %{size_download}\n"
