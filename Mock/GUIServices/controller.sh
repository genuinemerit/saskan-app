#!/bin/bash
# shellcheck disable=SC2009
# shellcheck disable=SC2207
#
## :command: controller.sh
## :synopsis: Start and stop the mock servers
## :platform: Linux
## :copyright: (c) 2021 by Genuine Merit Software
## :license: MIT, see LICENSE for more details.
## :author: GM <genuinemerit @ pm.me>
#
##  `chmod +x stop_mock.sh` if not already executable
##  `set -v` in this script for verbose output
#
##  Note that some sleep commands are used to allow the servers to start.
#
##  Initially, when running this, be sure to have two
##  terminals or terminal sessions open:
##      One to run and watch the output
##      Other to monitor and kill jobs
##  Eventually, use a monitoring tool / GUI to control
##    the mock servers, and then the real servers.
#
##  The first prototype sends a continuous stream of mock requests
##  to the server(s). Next, tweak that so that requests can be
##  sent from yet another terminal session.  Eventually incorporate
##  those into various services.
#
##  --> Need a schema for what servers should run on what ports.
##  --> Look into using Unix sockets instead of TCP ports?

#
show_help()
{
    ## `$0` is the name of the script
    echo -e "\nStart and stop (mock) servers for BowDataSchema"
    echo -ne "\nUsage: $0 [OPTION]..."
    printf '=%.0s' {1..50}
    echo -e "\n  -h, --help \t\tdisplay Help"
    echo -e "  -v, --version\t\tshow Version information"
    echo -e "  -j, --jobs\t\tshow running server Jobs"
    echo -e "  -r, --run\t\tRun server jobs"
    echo -e "  -k, --kill\t\tKill server jobs"
    echo -e "\nReport bugs to <https://github.com/genuinemerit/bow-data-schema/issues>"
}

#
show_version()
{
    echo -n "BowDataSchema mock servers control v.${VERSION}"
    echo -e "\nCopyright (C) 2021-2022 Genuine Merit Software"
    echo "License MIT: <https://mit-license.org/>"
    echo -n "This is free software: you are free to change and redistribute it "
    echo "as long as this notice is included."
    echo "There is NO WARRANTY, to the extent permitted by law."
    echo -e "\nWritten by GM <genuinemerit @ pm.me>"
}

check_running_servers ()
{
    ##  :args:
    ##          $1:str in ("show", empty string)
    ##  :set global for 'return': 
    ##          $SERVERS:int --> 0 if nothing running, else 1
    SERVERS=0
    for SRV in "${PYSRV[@]}"; do
        if [[ "$1" == "show" ]]; then
            echo -e "\nLooking for servers like *${SRV}*"
        fi
        J=$(ps -ef | grep -v grep | grep "${SRV}")
        if [[ -n ${J} ]]; then
            if [ "$1" == "show" ]; then
                echo -e "${J}"
            fi
            SERVERS=1
        fi
    done
}

#
show_jobs ()
{
    check_running_servers "show"
    if [[ ($SERVERS -eq 0) ]]; then
        echo -e "\nNo running jobs found"
    fi
}

#
stop_servers ()
{
    # When a server gets killed, its listeners and senders die too.
    check_running_servers ""
    if [[ ($SERVERS -gt 0) ]]; then
        declare -a PIDS
        for SRVR in "${PYSRV[@]}"; do
            echo "Getting PID for ${SRVR}"
            PIDCNT=0
            PIDCNT=$(ps -ef | grep -v grep | grep -c "${SRVR}")
            if [[ $PIDCNT -gt 0 ]]; then
                PIDS+=($(ps -ef | grep -v grep | grep "${SRVR}" | awk '{print $2}'))
            fi
        done
        for PID in "${PIDS[@]}"; do
            IFS=$'\n'; read -r PIDNUM <<<"${PID}"
            kill -9 "${PIDNUM}"
            echo -e "Killed @PID ${PID}"
            sleep 0.5s
        done
    fi
    check_running_servers ""
    if [[ ($SERVERS -eq 0) ]]; then
        echo "No server jobs are running."
    else
        echo "Something may be awry. Server jobs may still be running."
        echo "Do a manual kill if needed."
    fi
}

#
run_jobs ()
{
    check_running_servers ""
    if [[ ($SERVERS -eq 0) ]]; then
        echo -e "Starting up servers and services..."
        for PY in "${PYNM[@]}"; do
            echo -e "\nStart ${PY}"
            if [[ -f "${PY}" ]]; then
                python3 "${PY}" &
            else
                echo "File ${PY} not found"
            fi
            sleep 0.5s
        done
    else
        echo -e "\nServers and services are already running"
    fi
    check_running_servers "show"
}

#
## =================== MAIN ======================
ARGCNT=$#
SERVERS=0
# DAS="DataAdminServices"
IOS="../IOServices"
declare -a PYSRV
# PYSRV[0]="${DAS}/data_admin_server.py"
# PYSRV[1]="${IOS}/file_server.py"
PYSRV[2]="${IOS}/redis_server.py"
declare -a PYNM
# Start servers, then respoders, then requestors
# PYNM[0]="${DAS}/data_admin_server.py"
# PYNM[1]="${DAS}/data_admin_response.py"
# PYNM[2]="${DAS}/data_admin_request.py"
# PYNM[3]="${DAS}/data_admin_request.py"
# PYNM[4]="${IOS}/file_server.py"
# PYNM[5]="${IOS}/file_response.py"
# PYNM[6]="${IOS}/file_request.py"
PYNM[7]="${IOS}/redis_server.py"
PYNM[8]="${IOS}/redis_response.py"
PYNM[9]="${IOS}/redis_response.py"
PYNM[10]="${IOS}/redis_request.py"
VERSION="0.0.1"

if [[ ${1^^} == --HELP || ${1^^} == -H || ${ARGCNT} -gt 1 ]];
then
    show_help
elif [[ (${1^^} == --VERSION || ${1^^} == -V) ]]; then
    show_version
elif [[ (${1^^} == --SERVERS || ${1^^} == -J) ]]; then
    show_jobs
elif [[ (${1^^} == --KILL || ${1^^} == -K) ]]; then
    declare -a PIDS=()
    stop_servers
elif [[ (${1^^} == --RUN || ${1^^} == -R) ]]; then
    run_jobs
else
    show_help
fi
exit 0
