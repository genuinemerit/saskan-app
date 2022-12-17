#!/bin/bash

## Configure Unix Fire Wall settings

## @fn config_ufw
config_ufw ()
{
  ##  Verify /etc/default/ufw settings
  ##    DEFAULT_OUTPUT_POLICY="ACCEPT"
  ##    DEFAULT_FORWARD_POLICY="ACCEPT"
  echo -e "Configuring UFW OUTPUT and FORWARD policies..."
  TS=`date "+%Y%m%d-%H%M%S"`
  UFWDFLT="/etc/default/ufw"
  OUTFND=$(grep -i 'DEFAULT_OUTPUT_POLICY="ACCEPT"' $UFWDFLT)
  FWDFND=$(grep -i 'DEFAULT_FORWARD_POLICY="ACCEPT"' $UFWDFLT)
  if [[ -z ${OUTFND} ]] || [[ -z ${FWDFND} ]]; then
    # Backup the UFW Default settings file
    cp $UFWDFLT $UFWDFLT".bak.${TS}"
    # Set OUTPUT Policy to ACCEPT if it is set to something else
    sed -i 's/DEFAULT_OUTPUT_POLICY="DROP"/DEFAULT_OUTPUT_POLICY="ACCEPT"/g' $UFWDFLT
    sed -i 's/DEFAULT_OUTPUT_POLICY="REJECT"/DEFAULT_OUTPUT_POLICY="ACCEPT"/g' $UFWDFLT
    # Set FORWARD Policy to ACCEPT if it is set to something else
    sed -i 's/DEFAULT_FORWARD_POLICY="DROP"/DEFAULT_FORWARD_POLICY="ACCEPT"/g' $UFWDFLT
    sed -i 's/DEFAULT_FORWARD_POLICY="REJECT"/DEFAULT_FORWARD_POLICY="ACCEPT"/g' $UFWDFLT
  fi
  OUTFND=$(grep -i 'DEFAULT_OUTPUT_POLICY="ACCEPT"' $UFWDFLT)
  FWDFND=$(grep -i 'DEFAULT_FORWARD_POLICY="ACCEPT"' $UFWDFLT)
  if [[ -z ${OUTFND} ]] || [[ -z ${FWDFND} ]]; then
    echo -e "Could not modify OUTPUT and FORWARD policies. Do it manually."; step_fail
    return 1
  else
    step_ok
    return 0
  fi
}

## @fn set_ufw
set_ufw ()
{
  # Read items from requirements_ufw.txt and allow them.
  echo -e "Allowing Ports..."
  while IFS= read -r MOD;
  do
    CMNT="${MOD:0:1}"
    if [[ ${CMNT} == "#" ]]; then
      echo -e "${MOD}"
    else
      echo -e "Allowing: ${MOD}"
      ufw allow ${MOD}
    fi
  done <"$REQPATH"
  ## Reload and enable
  ufw reload
  ufw enable
}

## @fn verify_ufw
verify_ufw ()
{
  echo -e "Verifying UFW Ports allowed..."
  # Currently allowed ports:"
  ufw status > /tmp/ufwlist
  NOTFOUND=0
  # Read items from requirements_ufw.txt. See if they are on the installed list
  while IFS= read -r MOD;
  do
    CMNT="${MOD:0:1}"
    if [[ ${CMNT} == "#" ]]; then
      echo -e "${MOD}"
    else
      echo -e "Open/allowed: ${MOD}"; step_ok
      FOUND=$(grep -i ${MOD} /tmp/ufwlist)
      if [[ -z ${FOUND} ]]; then
        echo -e "Not open/allowed: ${MOD}"; step_fail
        ((NOTFOUND+=1))
      fi
    fi
  done <"$REQPATH"
  rm -f /tmp/ufwlist
  if [[ ${NOTFOUND} -eq 0 ]]; then
      return 0
  else
      return ${NOTFOUND}
  fi
}

## ================= MAIN ===========================
SCRIPT="${WAXPATH}/build/"$(basename -- "$0")
REQPATH="${WAXPATH}/build/requirements_ufw.txt"
. ${WAXPATH}/build/status.sh

(bash ${WAXPATH}/build/install_status.sh ${SCRIPT} ${REQPATH}); RC=$?
if [[ ${RC} -gt 0 ]]; then exit 1; fi  # Continue if required file is present
config_ufw; RC=$?
if [[ ${RC} -gt 0 ]]; then exit 1; fi  # Continue if the configuration was successful
ufw enable
set_ufw
verify_ufw; RC=$?
if [[ ${RC} -eq 0 ]]; then echo "${SCRIPT} COMPLETE" >> $TRKPATH; fi
