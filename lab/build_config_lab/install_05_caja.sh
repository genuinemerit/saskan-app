#!/bin/bash

## The basic server configuration installs should have already been run,
## in particular set-up of accounts and groups.  Code should be cloned into <DEV>/bowax.

## @fn create_caja_dirs
create_caja_dirs ()
{
  ## Remove existing files. (re-)Create directories under the caja account.
  echo -e "Creating caja directories"
  cd ${CAJA}
  rm -Rf data
  rm -Rf utils
  mkdir data
  mkdir utils
  cd data
  mkdir enc
  mkdir raw
  step_ok
}

## @fn set_credentials
set_credentials ()
{
  echo -e "Setting credentials for Ball of Wax accounts"
  cd ${CAJA}
  # Copy shell scripts and make them executable
  cp ${WAXPATH}/utils/sh/encrypt_file.sh ${CAJA}/utils
  cp ${WAXPATH}/utils/sh/decrypt_file.sh ${CAJA}/utils
  chown caja ${CAJA}/utils/*.sh
  chmod 775 ${CAJA}/utils/*.sh
  ## Copy .ini files to data/raw and modify with correct credentials
  cp ${WAXPATH}/utils/ini/bowdb.ini ${CAJA}/data/raw
  cp ${WAXPATH}/utils/ini/config.ini ${CAJA}/data/raw
  cp ${WAXPATH}/utils/ini/credentials.ini ${CAJA}/data/raw
  ## Retrieve password from temp..
  BOWPWD=$(cat /tmp/bowpasswd)
  ## Search for and modify pwd tokens
  sed -i "s/<postgrespw>/${BOWPWD}/g" ${CAJA}/data/raw/bowdb.ini
  sed -i "s/<bowpw>/${BOWPWD}/g" ${CAJA}/data/raw/bowdb.ini
  sed -i "s/<bowpw>/${BOWPWD}/g" ${CAJA}/data/raw/credentials.ini
  sed -i "s/<cajapw>/${BOWPWD}/g" ${CAJA}/data/raw/credentials.ini
  sed -i "s/<postgrespw>/${BOWPWD}/g" ${CAJA}/data/raw/credentials.ini
  # Set passphrase for encryption
  PASSCHK=""
  PASSPHR=""
  PROMPT="Enter the passphrase to use for encryption of sensitive files. Minimum 16 chars:"
  while [[ -z ${PASSCHK} ]]; do
    while [[ -z ${PASSPHR} ]]; do
      tput setaf 6 #teal
      echo "$PROMPT"
      echo "Enter pass phrase:"
      tput setaf 7 #white
      read -re PASSPHR
    done
    PASSCHK=`echo "${PASSPHR}" | egrep "^.{16,255}"`
    if [[ -z ${PASSCHK} ]]; then
      echo -e "Sorry, passphrase not long enough or too long. Try again. (Ctrl-C to exit.)"; step_warn
      PASSPHR=""
    fi
  done
  echo -e "Passphrase accepted"
  echo ${PASSPHR} > /home/caja/data/raw/passphrase.txt
  step_ok
}

## @fn encrypt_files
encrypt_files ()
{
  echo -e "Creating encrypted caja files and deleting raw files"
  cd ${CAJA}
  ## Create encrypted versions of the .ini files and remove plaintext .ini's
  bash ${CAJA}/utils/encrypt_file.sh ${CAJA}/data/raw/bowdb.ini ${CAJA}/data/enc/bowdb
  bash ${CAJA}/utils/encrypt_file.sh ${CAJA}/data/raw/config.ini ${CAJA}/data/enc/config
  bash ${CAJA}/utils/encrypt_file.sh ${CAJA}/data/raw/credentials.ini ${CAJA}/data/enc/credentials
  rm ${CAJA}/data/raw/bowdb.ini*
  rm ${CAJA}/data/raw/config.ini*
  rm ${CAJA}/data/raw/credentials.ini*
  ## Create encyrpted versions of the passwords
  bash ${CAJA}/utils/encrypt_file.sh /tmp/bowpasswd ${CAJA}/data/enc/bowpwd
  bash ${CAJA}/utils/encrypt_file.sh /tmp/bowpasswd ${CAJA}/data/enc/cajapwd
  bash ${CAJA}/utils/encrypt_file.sh /tmp/bowpasswd ${CAJA}/data/enc/postgrespwd
  ## Delete the temp password:
  rm -f /tmp/bowpasswd
  step_ok
}

## ================= MAIN ===========================
SCRIPT="${WAXPATH}/build/"$(basename -- "$0")
CAJA="/home/caja"
REQPATH=""
. ${WAXPATH}/build/status.sh

(bash ${WAXPATH}/build/install_status.sh ${SCRIPT}); RC=$?
if [[ ${RC} -gt 0 ]]; then exit 1; fi  # Continue if status is OK
create_caja_dirs
set_credentials
encrypt_files
echo "${SCRIPT} COMPLETE" >> $TRKPATH
