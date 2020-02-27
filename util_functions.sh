#!/bin/bash

[[ -n "$DEBUG" ]] && set -x

# ANSI Colors
function echoRed() { echo $'\e[0;31m'"$1"$'\e[0m'; }
function echoGreen() { echo $'\e[0;32m'"$1"$'\e[0m'; }
function echoYellow() { echo $'\e[0;33m'"$1"$'\e[0m'; }

function run_command_in_background() {
    # Usage: run_command_in_background ./some_script.sh
    (nohup "$@" &>/dev/null &)
}

function check_platform() {
    if [ "$(uname)" == "Darwin" ]; then
      echo Mac
    elif [ "$(expr substr $(uname -s) 1 5)" == "MINGW" ]; then
      echo Windows
    elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
      echo Linux
    else
      echo Unknown OS
    fi
}

function is_running() {
    ps -p "$1" &> /dev/null
}
