#!/bin/bash
# shellcheck disable=SC2009
#
## :command: start_stop_mock.sh
## :synopsis: Start and stop the mock server
## :platform: Linux
## :copyright: (c) 2021 by Genuine Merit Software
## :license: MIT, see LICENSE for more details.
## :author: GM <genuinemerit @ pm.me>
#
##  `chmod +x stop_mock.sh` if not already executable
##  `bash start_stop_mock.sh [OPTION]` to run
##  `set -v` in this script for verbose output

#
show_help()
{
    echo "Usage: $0 [OPTION]..."
    echo "Start and stop the Data Admin Services mock server"
    echo
    echo "  -h, --help              display this help and exit"
    echo "  -s, --start             start the mock server jobs"
    echo "  -t, --stop              stop the mock server jobs"
    echo "  -r, --restart           restart the mock server jobs"
    echo "  -j, --jobs              show running mock server jobs"
    echo "  -v, --version           output version information and exit"
    echo
    echo "Report bugs to <https://github.com/genuinemerit/bow-data-schema/issues>"
}

#
show_job ()
{
    if [[ ($SHOWTAG -eq 1) ]]; then
        echo -n "Looking for Data Admin Server jobs like "
        tput setaf "${YELLOW}"
        tput bold
        echo "${PYNM}"
        tput setaf "${DEFAULT}"
        tput sgr0
    fi

    # Get the job name:
    JOBS=$(ps -ef | grep -v grep | grep root | grep "${PYNM}")
    if [[ ! -z ${JOBS} ]]; then
        echo -e "${JOBS} running"
        JOBS=1
    else
        if [[ ($SHOWTAG -eq 1) ]]; then
            echo -e "No jobs found"
        fi
        JOBS=0
    fi
}

#
## =================== MAIN ======================
ARGCNT=$#
PYNM="data_admin_"
JOBS=0
SHOWTAG=0

export BLACK=0
export RED=1
export GREEN=2
export YELLOW=3
export BLUE=4
export MAGENTA=5
export CYAN=6
export WHITE=7
export DEFAULT=9

if [[ ${1^^} == --HELP || ${1^^} == -H || ${ARGCNT} -gt 1 ]];
then
    show_help
elif [[ (${1^^} == --JOBS || ${1^^} == -J) ]]; then
    SHOWTAG=1
    show_job
else
    show_help
fi
exit 0
