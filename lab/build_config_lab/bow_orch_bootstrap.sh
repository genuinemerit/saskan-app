#!/bin/bash
## bow_orch_bootstrap.sh

## Run in a dev account with sudo privileges or in a root account.
## Do not run from within accounts named "bow_orch" or "caja".
## Installs and configures contained runtime environment for bow_orch app.

show_help ()
{
    tput setaf "${YELLOW}"
    echo -e "You must be root (or sudo) to run bootstrap commands"

    tput setaf "${WHITE}"
    echo -e "Options:
      \t-h |--help\tShow help
      \t-s |--show\tShow current set-up status
      \t-b |--boot\tBoot set-up for bow_orch
      \t-v |--verbose\tDisplay verbose output"

    if [[ ${VERBOSE} -eq 1 ]]; then
        tput setaf "${CYAN}"
        echo -e "
    script: ${SCRIPT}
   version: ${VERSION}
    argcnt: ${ARGCNT}
      args: ${ARGS}
   runpath: ${RUNPATH}
   runuser: ${RUNUSER}
      user: ${USER}
       log: ${LOG}
    domain: ${DOMAIN}
    "
    fi

    tput setaf "${WHITE}"
}

show_status () {
    echo -e "
    Tag: Show status
    "
}

boot_orch () {
    echo -e "
    Tag: Boot bow_orch
    "
}

## =================== MAIN ======================
SCRIPT=$(basename -- "$0")
VERSION="v0.1.proto"
USER=$(whoami)
ARGCNT=$#
ARGS=${*}
RUNPATH=$PWD
RUNUSER=$(echo "$RUNPATH" | cut -d "/" -f 3)
DOMAIN="bow.genuinemerit.org"
LOG="/dev/shm/bow_orch_bootstrap.log"
VERBOSE=0
HELP=0
SHOW=0
BOOT=0
# shellcheck disable=SC1090
source "${RUNPATH}/tput_colors.sh"
if [[ "${USER}" != "root" ]]; then show_help; exit; fi
for P in ${ARGS}; do
    if [[ ${P^^} == --VERBOSE || ${P^^} == -V  ]]; then VERBOSE=1; fi;
    if [[ ${P^^} == --HELP || ${P^^} == -H  ]]; then HELP=1; fi;
    if [[ ${P^^} == --SHOW || ${P^^} == -S  ]]; then SHOW=1; fi;
    if [[ ${P^^} == --BOOT || ${P^^} == -B  ]]; then BOOT=1; fi;
done
if [[ ${HELP} -eq 1 ]]; then show_help; fi
if [[ ${SHOW} -eq 1 ]]; then show_status; fi
if [[ ${BOOT} -eq 1 ]]; then boot_orch; fi