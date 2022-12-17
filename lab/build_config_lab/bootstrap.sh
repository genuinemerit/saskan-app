#!/bin/bash

## Run in a dev account, not the bow or caja account. 
## Installs and configures the whole Ball of Wax.
## Writes status and log data to same directory in which it is run.

## @fn step_ok
step_ok ()
{
    tput setaf 2 #green
    echo " [OK]"
    tput setaf 7 #white
}

## @fn step_warn
step_warn ()
{
    tput setaf 3 #yellow
    echo " [INFO]"
    tput setaf 7 #white
}

## @fn step_fail
step_fail ()
{
    tput setaf 1 #red
    echo " [FAIL]"
    tput setaf 7 #white
}

## @fn check_user_priv
check_user_priv ()
{
  if [[ "$(whoami)" != "root" ]]; then
    echo -e "Sorry, you must be root (or sudo) to run this script."; step_fail
    return 1
   fi
   return 0
}

## @fn check_script_status
check_script_status ()
{
  if [[ -f $TRKPATH ]]; then
    MYSTAT=$(grep ${SCRIPT} $TRKPATH)
    if [[ ${MYSTAT} =~ "COMPLETE" ]]; then
      echo -e "Installer script <$SCRIPT> is already in COMPLETE status.
To re-run all steps, use the --fresh option with bootstrap.sh."; step_warn
      return 1
    fi
  fi
  return 0
}

## @fn check_sudo
check_sudo ()
{
  echo -e "Verifying that user <${DEVUSER}> is in group sudo"
  SUDOERS=$(grep sudo /etc/group)
  if [[ ! ${SUDOERS:9:50} =~ ${DEVUSER} ]]; then
    echo -e "User is not a sudoer. Add user to sudo."; step_fail
    return 1
  fi
  step_ok
  return 0
}

## @fn check_git
check_git ()
{
  echo -e "Verifying that git is installed"
  GITVERS=$(git --version)
  if [[ ! ${GITVERS} ]]; then
    echo -e "Git is not installed. Please install it."; step_fail
    return 1
  fi
  step_ok
  return 0
}

## @fn check_git_config
check_git_config ()
{
  GITLIST=$(git config --list)
  if [[ ${GITLIST} =~ "user.name" && ${GITLIST} =~ "user.email" ]]; then
    GITCFGSET=0
  fi
}

## @fn set_git_config
set_git_config ()
{
  GITCHECK=''
  GITEMAIL=""
  echo -e "Setting up developer credentials for Ball of Wax GitHub"
  PROMPT="Provide a developer email address to use with Git and GitHub."
  while [[ -z ${GITCHECK} ]]; do
    while [[ -z ${GITEMAIL} ]]; do
      echo "$PROMPT"
      echo "Enter email: "
      read -e GITEMAIL
    done
    GITCHECK=`echo ${GITEMAIL} | egrep "^[a-zA-Z0-9]+@[a-zA-Z0-9]+.[a-z]{2,}"`
    if [[ -z ${GITCHECK} ]]; then
      echo -e "Sorry, not a valid email address. Try again (Ctl-C to exit.)"; step_warn
      GITEMAIL=""
    fi
  done
  git config --global user.email "${GITEMAIL}"
  HOSTNM=$(hostname)
  git config --global user.name "${DEVPATH}@${HOSTNM}"
}

## @fn check_ssh
check_ssh ()
{
  echo -e "Verifying that ssh is installed and available on port 22"
  SSHSTAT=$(/etc/init.d/ssh status)
  if [[ ! ${SSHSTAT} =~ "running" ]]; then
    echo -e "SSH is not running. Please install and enable it."; step_fail
    return 1
  fi

  PORT22STAT=$(netstat -aln | grep ":22" | grep LISTEN | grep "tcp ")
  if [[ ! ${PORT22STAT} ]]; then
    echo -e "If netstat is not installed, install it using apt-get install net-tools.
Port 22 is not available for TCP. Check firewall settings."; step_fail
    return 1
  fi
  step_ok
  return 0
}

## @fn check_environment
check_environment ()
{
  echo -e "Running step # 0: bootfn_check - Verify git, ssh, net-tools. Clone bowax Git repo."
  sleep 1.5s
  check_sudo; RC=$?
  if [[ ${RC} -eq 0 ]]; then check_git; RC=$?; fi
  if [[ ${RC} -eq 0 ]]; then
      GITLIST=$(git config --list)
      if [[ ! ${GITLIST} =~ "user.name" || ! ${GITLIST} =~ "user.email" ]]; then
         set_git_config
      fi
      check_ssh; RC=$?
  fi
  return $RC
}

## @fn check_privileges
check_privileges ()
{
  # Check for bootstrap.sh not being COMPLETE
  check_script_status; RC=$?
  if [[ ${RC} -gt 0 ]]; then return 1; fi
  # Check for privilege_check being COMPLETE
  SVSCRIPT=$SCRIPT
  SCRIPT="privilege_check"
  check_script_status; RC=$?
  SCRIPT=$SVSCRIPT
  if [[ ${RC} -gt 0 ]]; then
    echo -e "privilege_checks already completed."; step_ok
    return 1
  else
      # Check to make sure we are running as sudo
      check_user_priv; RC=$?
      if [[ ${RC} -gt 0 ]]; then return 1; fi
      check_environment; RC=$?
      if [[ ${RC} -gt 0 ]]; then return 1; fi
      return 0
  fi
}

## @fn clone_bowax
clone_bowax ()
{
  echo -e "Refreshing local bowax git clone and setting build scripts to executable"
  cd $DEVPATH
  rm -Rf bowax
  git clone https://github.com/${BOWREPO}
  chmod 775 ${WAXPATH}/build/*.sh
  step_ok
}

## @fn step_status
step_status ()
{
  if [[ -f $TRKPATH ]]; then
    MYSTAT=$(grep ${RUNSCRIPT} $TRKPATH)
    if [[ ${MYSTAT} =~ "COMPLETE" ]]; then
      return 0 
    fi
    echo -e "Step <${RUNSCRIPT}> did not complete successfully."
  else
    echo -e "Tracker log file not found."
  fi
  return 1
}

## @fn run_install
run_install ()
{
  declare -a RUNARY=()
  RUNARY+=("/build/install_01_apts.sh Update, upgrade, install APT modules")
  RUNARY+=("/build/install_02_python.sh Update, upgrade, install Python3 modules")
  RUNARY+=("/build/install_03_ufw.sh Set Unix Firewall (UFW) ports")
  RUNARY+=("/build/install_04_accts.sh Verify, create, credential BoW accounts")
  RUNARY+=("/build/install_05_caja.sh Set up credentials vault in Caja")
  RUNARY+=("/build/install_06_docs.sh Set up Sphinx and other documentation")
  RUNARY+=("/build/install_07_nginx.sh Install NGINX web server")
  RUNARY+=("/build/install_08_cron.sh Schedule nightly cron job to auto-refresh APTs")
  RUNARY+=("/build/install_09_postgres.sh Install Postgres database")
  RUNARY+=("/build/install_10_bowdb_pg.sh Install postgres db objects")
  RUNARY+=("/build/install_11_bowdb_bow.sh Install bowdb db objects")
  STEPNUM=0
  for RUNME in "${RUNARY[@]}"
  do
    RUNSCRIPT=$(echo ${RUNME} | awk '{print $1}')
    SCRLEN=${#RUNSCRIPT}+1
    SCRINFO=${RUNME:$SCRLEN}  # Pull substring from SCRLEN to end of string
    ((STEPNUM=STEPNUM+1))
    RUNSCRIPT="${WAXPATH}${RUNSCRIPT}"
    echo -e "
${STARS}    
Running step # ${STEPNUM}: ${RUNSCRIPT} - ${SCRINFO}
${STARS}"
    sleep 1.5s
    bash ${RUNSCRIPT} $WAXPATH $TRKPATH
    step_status; RC=$?
    # This step did not complete successfully, STOP:
    if [[ ${RC} > 0 ]]; then
      return 1
    fi
  done
}

## ================= MAIN ===========================
export STARS="*******************************************"
export DEVPATH=$PWD
export DEVUSER=$(echo $DEVPATH | cut -d "/" -f 3)
export WAXPATH="${DEVPATH}"/bowax
export TRKPATH="${DEVPATH}"/bowax_tracker.log
export BOWREPO="GenuineMeritSoftware/bowax"
SCRIPT=$(basename -- "$0")

HELP="${SCRIPT} v0.0.3 [-h|--help]  or   [-f|--fresh]\n  Initial install of BoW software and setup.\nUse -f/--fresh option to force re-run of steps previously completed successfully.\nIf -f is used, all steps are re-run.\nIf -f is not used, then only steps that were not run or failed previously are run."
if [[ ${1^^} == --HELP || ${1^^} == -H ]]; then echo -e "$HELP"
else
   cd $DEVPATH
   # Force everything fresh
   if [[ ${1^^} == --FRESH || ${1^^} == -F ]]; then rm $TRKPATH; fi
   # Tracker file not found, so create new one
   if [[ ! -f $TRKPATH ]]; then 
      touch $TRKPATH; 
      chown ${DEVUSER} $TRKPATH
   fi
   check_privileges; RC=$?
   if [[ ${RC} -eq 0 ]]; then echo "privilege_check COMPLETE" >> $TRKPATH; fi
   # Refresh the local bowax code repository even it was done previously.
   clone_bowax
   # Run the installer scripts
   run_install; RC=$?
   # If all ran OK, then update the tracker indicating bootstrap is COMPLETE
   if [[ ${RC} -eq 0 ]]; then echo "${DEVPATH}/${SCRIPT} COMPLETE" >> $TRKPATH; fi
   # Display current status of the install tracker.
   echo -e "
Current status of Ball of Wax Installer
${STARS}
$(cat $TRKPATH)
      "
fi
