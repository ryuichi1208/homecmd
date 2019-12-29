#!/bin/bash

set -euC

function log() {
  local fname=${BASH_SOURCE[1]##*/}
  echo -e "$(date '+%Y-%m-%dT%H:%M:%S') ${fname}:${BASH_LINENO[0]}:${FUNCNAME[1]} $@"
}

function cleanup()
{
  return
}

function main()
{
  return
}

trap cleanup EXIT

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  main
fi
