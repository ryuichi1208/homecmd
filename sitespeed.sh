#!/bin/bash

#
# sitespeed.ioをjenkinsから実行する際のスクリプト
#

set -euC

# 定数
readonly DOCKER_CMD=$(which docker)
readonly DOCKER_RUN_OPTS="container run --shm-size=1g --rm -v $(pwd):/sitespeed.io"
readonly DOCKER_IMAGE="sitespeedio/sitespeed.io"

# テスト対象URL
TEST_URL=""
# テスト試行回数
EXEC_ITERATION=""
# sitespeed.ioのdockerイメージバージョン
SITESPEED_VERSION=""
# sitespeed.ioの実行時オプション
SITESPEED_OPTS=""
# sitespeed.ioのユーザアージェント

function usage()
{
    cat <<EOS >&2
Usage: $0 [-u テスト対象URL]
  -u              テスト対象のURLを指定
  -v              sitespeed.ioのdockerイメージバージョン
  -a              ユーザーエージェント
  -e              試行回数を指定
EOS
  exit 1
}

function paser_args()
{
  while getopts "u:v:a:e:h" OPT; do
    case $OPT in
      u) TEST_URL=${OPTARG} ;;
      v) SITESPEED_VERSION=${OPTARG} ;;
      a) SITESPEED_AGENT="${OPTARG}";;
      e) EXEC_ITERATION="{OPTARG}";;
      h) usage;;
      ?) usage;;
    esac
  done

  shift $((OPTIND - 1))

  if [[ "${TEST_URL}" == "" ]]; then
    usage
  fi

  EXEC_ITERATION="${EXEC_ITERATION:-3}"
  SITESPEED_VERSION="${SITESPEED_VERSION:-latest}"
  SITESPEED_AGENT="${SITESPEED_AGENT:-Chorme}"
}

function main()
{
  ${DOCKER_CMD} ${DOCKER_RUN_OPTS} ${DOCKER_IMAGE}:${SITESPEED_VERSION} \
    ${SITESPEED_OPTS} \
    -n ${EXEC_ITERATION} \
    --userAgent "${SITESPEED_AGENT}" \
    ${TEST_URL}
}


if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  paser_args "${@}"
  main
fi
