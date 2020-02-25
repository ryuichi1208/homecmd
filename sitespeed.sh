#!/bin/bash
set -euC

# 定数
readonly PROGNAME="$(basename $0)"
readonly DOCKER_CMD=$(which docker)
readonly DOCKER_RUN_OPTS="container run --shm-size=1g --rm -v $(pwd):/sitespeed.io"
readonly DOCKER_IMAGE="sitespeedio/sitespeed.io"

# オプション解析用変数
TEST_TARGET_URL=""
USER_AGENT=""
USER_AGENT_TYPE="pc"
USER_AGENT_FLG=false
SITESPEED_ITERATION=3

function log() {
  local fname=${BASH_SOURCE[1]##*/}
  echo -e "$(date '+%Y-%m-%dT%H:%M:%S') ${fname}:${BASH_LINENO[0]}:${FUNCNAME[1]} $@"
}

function stderr() {
  echo -e "\e[31m"${@}"\e[m" >&2
}

function usage() {
  cat << EOS >&2
Usage: ${PROGNAME} [-u, --test-url VALUE] [--user-agent]
EOS
  exit 1
}

function opt_parse() {
  for opt in "${@}"; do
    case "${opt}" in
      '-u' | '--test-url' )
        if [[ -z "$2" ]] || [[ "$2" =~ ^+ ]]; then
          usage
        fi
        TEST_TARGET_URL=$2
        shift 2
        ;;
      '-a'| '--user-agent' )
        if [[ -z "$2" ]] || [[ "$2" =~ ^+ ]]; then
          usage
        fi
        USER_AGENT_TYPE=$2
        USER_AGENT_FLG=true
        shift 2
        ;;
      '-h' | '--help' )
        usage
        ;;
      -* )
        stderr "${PROGNAME}: illegal option -- '$(echo $1 | sed 's/^-*//')'"
        exit 1
    esac
  done

  [[ -z ${TEST_TARGET_URL} ]] || [[ ! ${TEST_TARGET_URL} =~ ^http ]] && usage 1

  if [[ "${USER_AGENT_FLG}" == "true" ]]; then
    case "${USER_AGENT_TYPE}" in
      'pc' )
        USER_AGENT="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) "
        ;;
      'iPhone' )
        USER_AGENT="Mozilla/5.0 (iPhone; CPU iPhone OS 12_4_1 like Mac OS X)"
        ;;
      'line' )
        USER_AGENT="Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) Line/8.13.0"
        ;;
      * )
        stderr "sorry! Such user agent types are not supported."
        stderr ""
        stderr "Currently supported are PC, iPhone and Line."
        stderr "You can easily add it by adding it to the switch statement."
        exit 1
    esac
  fi
}

function main() {
  ${DOCKER_CMD} ${DOCKER_RUN_OPTS} ${DOCKER_IMAGE}:latest \
    --verbose \
    --browsertime.iterations ${SITESPEED_ITERATION} \
    --user-agent "${USER_AGENT}" \
    "${TEST_TARGET_URL}"
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  opt_parse "$@"
  main
fi
