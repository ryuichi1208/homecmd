#!/bin/bash

case $directmode in
  0) exec awk "$awkcode" ${file:+"$file"}
     ;;
  *) printf '%s' "$directstr" | awk "$awkcode"
     exit $?
     ;;
esac
