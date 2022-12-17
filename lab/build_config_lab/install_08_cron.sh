#!/bin/bash

## Copy auto-run cron instructions to /etc/cron.d
## install_07_nginx has already run successfully and moved scripts to /home/bow/utils/sh


## @fn setup_apt_cronjob
setup_apt_cronjob ()
{
  echo -e "Setting up daily cron job to refresh APTs nightly at 4 AM"
  if [[ -f  ${BOWUTILS}/apt_refresh.sh ]]; then
    cp ${WAXPATH}/utils/cron/apt-refresh-sched /etc/cron.d
    step_ok
    return 0
  else
    echo -e "Unable to set up APT cron job."; step_fail
    return 1
  fi
}

## @fn setup_wsgi_cronjob
setup_wsgi_cronjob ()
{
  echo -e "Setting up daily cron job to refresh wsgi nightly at 3 AM"
  if [[ -f ${BOWUTILS}/wsgi.sh && -f ${BOWUTILS}/flaskbow.sh ]]; then
    cp ${WAXPATH}/utils/cron/wsgi-refresh-sched /etc/cron.d
    step_ok
    return 0
  else
    echo -e "Unable to set up WSGI cron job."; step_fail
    return 1
  fi
}

## @fn setup_nginx_cronjob
setup_nginx_cronjob ()
{
  echo -e "Setting up daily cron job to restart NGINX nightly at 3:02 AM "
  if [[ -f  ${BOWUTILS}/nginx.sh ]]; then
    cp ${WAXPATH}/utils/cron/nginx-refresh-sched /etc/cron.d
    step_ok
    return 0
  else
    echo -e "Unable to set up NGINX cron job."; step_fail
    return 1
  fi
}

## ================= MAIN ===========================
SCRIPT="${WAXPATH}/build/"$(basename -- "$0")
BOWUTILS="/home/bow/utils/sh"
. ${WAXPATH}/build/status.sh

(bash ${WAXPATH}/build/install_status.sh ${SCRIPT}); RC=$?
if [[ ${RC} -gt 0 ]]; then exit 1; fi  # Continue if status is OK
setup_apt_cronjob; RC=$?
if [[ ${RC} -gt 0 ]]; then exit 1; fi  # Continue if status is OK
setup_wsgi_cronjob; RC=$?
if [[ ${RC} -gt 0 ]]; then exit 1; fi  # Continue if job was setup OK
setup_nginx_cronjob; RC=$?
if [[ ${RC} -gt 0 ]]; then exit 1; fi  # Continue if job was setup OK

echo -e "/etc/cron.d jobs:"
ls -lsa /etc/cron.d
echo -e "${BOWUTILS} scripts:"
ls -lsa ${BOWUTILS}
echo "${SCRIPT} COMPLETE" >> $TRKPATH
