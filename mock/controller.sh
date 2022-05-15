#!/bin/bash
# shellcheck disable=SC2009
# shellcheck disable=SC2207
#
## :command: controller.sh
## :synopsis: Starts the servers
## :platform: Linux
## :copyright: (c) 2021-2022 by Genuine Merit Software
## :version:. 0.0.1-beta
## :license: MIT, see LICENSE for more details.
## :author: GM <genuinemerit @ pm.me>
#
##  `chmod +x controller.sh` if not already executable
##  `set -v` in this script for verbose output
#   ===========================================================================
##  Run parameters:
##      $1 = command name --> see show_help() for details
##      $2 = service type --> in (data_admin, file, redis, etc.)

##  Recommend to run this script in the background with
##  stdout and stderr redirected to either a log file or
##  to /dev/null.
#
##  For example:
##      `bash controller.py --run redis &>> /dev/null &`
#
##  This script is intended to be run from the command line.
##  And only for starting up the servers.
##  The servers are long-running jobs.
##  The script should be run separately for each collection of services
##  (I think)
#
##  To aid in development, it has capability to show what
##  jobs are running, and to stop them.  But the system
##  design is to use controller_gui.py script to stop and
##  monitor the servers, with monitoring and logging data
##  handled via the wire_tap module `bow_tap.py`
#
## @DEV
## Information about the servers, such as host/port, and location
##  of the scripts, should be provided in a config file which is
##  managed by the admin_gui.py application.
#
show_help()
{
    ## `$0` is the name of the script
    echo -ne "\nStart servers for BowDataSchema\n"
    printf '=%.0s' {1..50}
    echo -ne "\nUsage: $0 [OPTION] [SERVICE]\n"
    echo -e "\n OPTIONS:"
    echo -e "  -h, --help \t\tdisplay Help"
    echo -e "  -r, --run\t\tRun server jobs"
    echo -e "  -j, --jobs\t\tshow running server Jobs"
    echo -e "  -k, --kill\t\tKill server jobs"
    echo -e "  -v, --version\t\tshow Version information"
    echo -e "\n SERVICE:"
    echo -e "  data_admin"
    echo -e "  file"
    echo -e "  redis"
    echo -e "\nEXAMPLE:"
    echo -e "  bash $0 --run redis\n"
    printf '=%.0s' {1..50}
    echo -e "\nReport bugs to <https://github.com/genuinemerit/bow-data-schema/issues>"
}

#
show_version()
{
    echo -n "BowDataSchema servers controller v.${VERSION}"
    echo -e "\nCopyright (C) 2021-2022 Genuine Merit Software"
    echo "License MIT: <https://mit-license.org/>"
    echo -n "This is free software: you are free to change and redistribute it "
    echo "as long as this notice is included."
    echo "There is NO WARRANTY, to the extent permitted by law."
    echo -e "\nWritten by GM <genuinemerit @ pm.me>"
}

check_running_server ()
{
    ##  :args:
    ##          $1:str in ("show", empty string)
    ##  :set global for 'return': 
    ##          $SERVERS:int --> 0 if nothing running, else 1
    SERVERS=0
    if [[ "$1" == "show" ]]; then
        LENGTH=${#SRVR}
        START=${LENGTH}-32
        echo -e "\nLooking for server like *..${SRVR:START}*"
    fi
    J=$(ps -ef | grep -v grep | grep "${SRVR}")
    if [[ -n ${J} ]]; then
        if [ "$1" == "show" ]; then
            echo -e "${J}"
        fi
        SERVERS=1
    fi
}

#
show_jobs ()
{
    check_running_server "show"
    if [[ ($SERVERS -eq 0) ]]; then
        echo -e "\nNo running servers found"
    fi
}

#
stop_servers ()
{
    # When a server gets killed, its requestors and responders die `naturally`.
    check_running_server ""
    if [[ ($SERVERS -gt 0) ]]; then
        declare -a PIDS
        echo "Getting PID for ${SRVR}"
        PIDCNT=0
        PIDCNT=$(ps -ef | grep -v grep | grep -c "${SRVR}")
        if [[ $PIDCNT -gt 0 ]]; then
            PIDS+=($(ps -ef | grep -v grep | grep "${SRVR}" | awk '{print $2}'))
        fi
        for PID in "${PIDS[@]}"; do
            IFS=$'\n'; read -r PIDNUM <<<"${PID}"
            kill -9 "${PIDNUM}"
            echo -e "Killed @PID ${PID}"
            sleep 0.5s
        done
    fi
    show_jobs
    if [[ ($SERVERS -gt 0) ]]; then
        echo "Something may be awry. Server jobs may still be running."
        echo "Do a manual kill if needed."
    fi
}

#
run_jobs ()
{
    check_running_server ""
    if [[ ($SERVERS -eq 0) ]]; then
        echo -e "Starting up servers and services..."
        for SV in "${SVNM[@]}"; do
            echo -e "\nStart ${SV}"
            if [[ -f "${SV}" ]]; then
                # python3 -u "${SV}" &
                # try this... seems nicer, cleaner, and more portable
                # The log is there after the server is shut down.
                # May be able to call this directly from the Python class
                # without issues. I will be wiretapping the services so
                # not too concerned about getting to the bash log file.
                nohup python3 -u "${SV}" > '/tmp/saskan_services.log' &
            else
                echo "File ${SV} not found"
            fi
            sleep 0.5s
        done
    else
        echo -e "\nServers and services are already running"
    fi
    show_jobs
}

#
## =================== MAIN ======================
ARGCNT=$#
SERVERS=0
VERSION="0.0.1-beta"
#
# echo -e "\nRequested service type: $2"
if [[ -z "$2" ]]; then
    SVTP="file"
else
    SVTP="$2"
fi
# @DEV --> The directory hierarchy needs to be a config item.
# Or better, handle everything in a python program.
SVTP="/home/dave/Dropbox/Apps/BoW/bow-data-schema/BowDataSchema/${SVTP}"
declare -a SVNM
SVNM[0]="${SVTP}_server.py"
SVNM[1]="${SVTP}_response.py"
SVNM[2]="${SVTP}_request.py"
SRVR="${SVNM[0]}"
#
if [[ ${1^^} == --HELP || ${1^^} == -H || ${ARGCNT} -gt 2 ]];
then
    show_help
elif [[ (${1^^} == --VERSION || ${1^^} == -V) ]]; then
    show_version
elif [[ (${1^^} == --JOBS || ${1^^} == -J) ]]; then
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
