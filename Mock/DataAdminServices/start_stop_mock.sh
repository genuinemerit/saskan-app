#!/bin/bash
# shellcheck disable=SC2009
# shellcheck disable=SC2207
#
## :command: start_stop_mock.sh
## :synopsis: Start and stop the mock server
## :platform: Linux
## :copyright: (c) 2021 by Genuine Merit Software
## :license: MIT, see LICENSE for more details.
## :author: GM <genuinemerit @ pm.me>
#
##  `chmod +x stop_mock.sh` if not already executable
##  `set -v` in this script for verbose output
#
##  Have two terminal sessions open:
##      One to run and watch the output
##      Other to monitor and kill jobs
#
show_help()
{
    ## `$0` is the name of the script
    echo -e "\nStart and stop the Data Admin Services mock server"
    echo -ne "\nUsage: "
    tput setaf "${CYAN}"; echo -e "$0 [OPTION]..."
    tput sgr0; printf '=%.0s' {1..50}
    tput setaf "${CYAN}"; echo -ne "\n  -h, --help"
    tput sgr0; echo -e "\t\tdisplay help"
    tput setaf "${CYAN}"; echo -n "  -v, --version"
    tput sgr0; echo -e "\t\tshow version information"
    tput setaf "${CYAN}"; echo -n "  -j, --jobs"
    tput sgr0; echo -e "\t\tshow running mock server jobs"
    tput setaf "${CYAN}"; echo -n "  -r, --run"
    tput sgr0; echo -e "\t\tstart/run mock server jobs"
    tput setaf "${CYAN}"; echo -n "  -k, --kill"
    tput sgr0; echo -e "\t\tstop/kill mock server jobs"
    echo -e "\nReport bugs to <https://github.com/genuinemerit/bow-data-schema/issues>"
}

#
show_version()
{
    echo -n "Data Admin Services mock server v."
    tput setaf "${CYAN}"
    tput bold
    echo "${VERSION}"
    tput setaf "${DEFAULT}"
    tput sgr0
    echo -e "\nCopyright (C) 2021 Genuine Merit Software"
    echo "License MIT: <https://mit-license.org/>"
    echo -n "This is free software: you are free to change and redistribute it "
    echo "as long as this notice is included."
    echo "There is NO WARRANTY, to the extent permitted by law."
    echo -e "\nWritten by GM <genuinemerit @ pm.me>"
}

#
show_jobs ()
{
    if [[ ($SHOWTAG -eq 1) ]]; then
        echo -n "Looking for Data Admin Server jobs like "
        tput setaf "${YELLOW}"
        tput bold
        echo "${JOBNMS}"
        tput setaf "${DEFAULT}"
        tput sgr0
    fi

    # Get the job name:
    JOBS=$(ps -ef | grep -v grep | grep "${JOBNMS}")
    if [[ -n ${JOBS} ]]; then
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
stop_jobs ()
{
    # When the server gets killed, the listeners and senders die too.
    show_jobs
    if [[ ($JOBS -gt 0) ]]; then

        # Get the number of jobs running:
        PIDCNT=$(ps -ef | grep -v grep | grep -c "${PYSRV}")

        if [[ $PIDCNT -gt 0 ]]; then
            PIDS+=($(ps -ef | grep -v grep | grep "${PYSRV}" | awk '{print $2}'))
        fi

        for PID in "${PIDS[@]}"; do

            # IFS=$'\n'; read -a PIDNUM <<<"${PID}"
            IFS=$'\n'; read -r PIDNUM <<<"${PID}"
            kill -9 "${PIDNUM}"
            tput setaf "${RED}"
            tput bold
            echo -e "Killed @PID ${PID}"
            tput setaf "${DEFAULT}"
            tput sgr0
        done
    else
        echo "No jobs named like ${PYSRV} are running"
    fi
}

#
run_jobs ()
{
    show_jobs
    if [[ ($JOBS -eq 0) ]]; then
        echo -n "Starting up jobs "

        for PY in "${PYNMS[@]}"; do
            echo -e "Trying to start ${PY}..."
            tput setaf "${YELLOW}"; tput bold; echo "${PY}"
            tput setaf "${DEFAULT}"; tput sgr0
            RUNME="./${PY}"
            if [[ -f "${RUNME}" ]]; then
                python3 "${RUNME}" &
            else
                echo -e "File ${RUNME} not found"
            fi
        done
        show_jobs
    fi
}


#
## =================== MAIN ======================
ARGCNT=$#
JOBS=0
declare -a PYNMS
PYSRV="data_admin_server.py"
PYNMS[0]="data_admin_server.py"
PYNMS[1]="data_admin_listener.py"
PYNMS[2]="data_admin_listener.py"
PYNMS[3]="data_admin_sender.py"
JOBNMS="data_admin_"
SHOWTAG=0
VERSION="0.0.1"

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
elif [[ (${1^^} == --VERSION || ${1^^} == -V) ]]; then
    show_version
elif [[ (${1^^} == --JOBS || ${1^^} == -J) ]]; then
    SHOWTAG=1
    show_jobs
elif [[ (${1^^} == --KILL || ${1^^} == -K) ]]; then
    declare -a PIDS=()
    stop_jobs
elif [[ (${1^^} == --RUN || ${1^^} == -R) ]]; then
    run_jobs
else
    show_help
fi
exit 0
