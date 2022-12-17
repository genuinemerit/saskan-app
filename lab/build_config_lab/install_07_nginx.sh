#!/bin/bash

# Configure NGINX web server

## @fn deploy_bow_code
deploy_bow_code ()
{
  RC=0

  echo -e "Installing PLSQL code..."
  rm -Rf ${BOWROOT}/db
  mkdir ${BOWROOT}/db
  cp -R ${WAXPATH}/db/pg/* ${BOWROOT}/db
  if [[ ! -d ${BOWROOT}/db ]]; then
    echo -e "Could not create ${BOWROOT}/db"; step_fail
    return 1
  fi
  chown -R bow:bow ${BOWROOT}/db
  # Decrypt passwords
  bash /home/caja/utils/decrypt_file.sh /home/caja/data/enc/postgrespwd /dev/shm/postgrespwd
  bash /home/caja/utils/decrypt_file.sh /home/caja/data/enc/bowpwd /dev/shm/bowpwd
  PGPWD=$(cat /dev/shm/postgrespwd)
  BOWPWD=$(cat /dev/shm/bowpwd)
  ## Modify password in db/dbu/dbu_c03_superuser.psql
  sed -i "s/<postgrespw>/${PGPWD}/g" ${BOWROOT}/db/dbu/dbu_c03_superuser.psql
  sed -i "s/<bowpw>/${BOWPWD}/g" ${BOWROOT}/db/dbu/dbu_c03_superuser.psql
  ## Later we should delete this file.
  rm -Rf /dev/shm/postgrespwd
  rm -Rf /dev/shm/bowpwd
  step_ok

  echo -e "Installing Python code..."
  rm -Rf ${BOWROOT}/run
  mkdir ${BOWROOT}/run
  mkdir ${BOWROOT}/run/py
  cp -R ${WAXPATH}/run/py/* ${BOWROOT}/run/py
  if [[ ! -d ${BOWROOT}/run/py ]]; then
    echo -e "Could not create ${BOWROOT}/run/py"; step_fail
    return 1
  fi
  chown -R bow:bow ${BOWROOT}/run
  chmod 775 ${BOWROOT}/run/py/*
  chmod 775 ${BOWROOT}/run/py/__pycache__/*
  chmod 775 ${BOWROOT}/run/py/static/*
  chmod 775 ${BOWROOT}/run/py/templates/*
  chown -R bow:bow ${BOWROOT}/run/py/__pycache__
  chown -R bow:bow ${BOWROOT}/run/py/static
  chown -R bow:bow ${BOWROOT}/run/py/templates
  step_ok

## Static and Templates now reside under /run/py
#  echo -e "Installing Static Web resources..."
#  rm -Rf ${BOWROOT}/run/static
#  mkdir ${BOWROOT}/run/static
#  cp -R ${WAXPATH}/run/static/* ${BOWROOT}/run/static
#  if [[ ! -d ${BOWROOT}/run/static ]]; then
#    echo -e "Could not create ${BOWROOT}/run/static"; step_fail
#    return 1
#  fi
#  chown -R bow:bow ${BOWROOT}/run/static
#  step_ok

#  echo -e "Installing Templates resources..."
#  rm -Rf ${BOWROOT}/run/templates
#  mkdir ${BOWROOT}/run/templates
#  cp -R ${WAXPATH}/run/templates/* ${BOWROOT}/run/templates
#  if [[ ! -d ${BOWROOT}/run/templates ]]; then
#    echo -e "Could not create ${BOWROOT}/run/templates"; step_fail
#    return 1
#  fi
#  chown -R bow:bow ${BOWROOT}/run/templates
#  step_ok

  echo -e "Installing API resources..."
  rm -Rf ${BOWROOT}/run/api
  mkdir ${BOWROOT}/run/api
  cp -R ${WAXPATH}/run/api/* ${BOWROOT}/run/api
  if [[ ! -d ${BOWROOT}/run/api ]]; then
    echo -e "Could not create ${BOWROOT}/run/api"; step_fail
    return 1
  fi
  chown -R bow:bow ${BOWROOT}/run/api
  step_ok


  echo -e "Create SSL credentials directory..."
  rm -Rf ${BOWROOT}/run/api
  mkdir ${BOWROOT}/run/ssl
  if [[ ! -d ${BOWROOT}/run/ssl ]]; then
    echo -e "Could not create ${BOWROOT}/run/ssl"; step_fail
    return 1
  fi
  chown -R bow:bow ${BOWROOT}/run/ssl
  step_ok

  echo -e "Installing Bash scripts..."
  rm -Rf ${BOWROOT}/utils
  mkdir ${BOWROOT}/utils
  mkdir ${BOWROOT}/utils/sh
  cp ${WAXPATH}/utils/sh/apt_refresh.sh ${BOWROOT}/utils/sh
  cp ${WAXPATH}/utils/sh/nginx.sh ${BOWROOT}/utils/sh
  cp ${WAXPATH}/utils/sh/flask_wsgi.sh ${BOWROOT}/utils/sh
  cp ${WAXPATH}/utils/sh/flask_bow.sh ${BOWROOT}/utils/sh
  if [[ ! -d ${BOWROOT}/utils/sh ]]; then
    echo -e "Could not create ${BOWROOT}/utils/sh"; step_fail
    return 1
  fi
  chown -R bow:bow ${BOWROOT}/utils
  chmod 775 ${BOWROOT}/utils/sh/*.sh
  step_ok

  echo -e "Creating app level log directory..."
  rm -Rf ${BOWROOT}/log
  mkdir ${BOWROOT}/log
  if [[ ! -d ${BOWROOT}/log ]]; then
    echo -e "Could not create ${BOWROOT}/log"; step_fail
    return 1
  fi
  touch ${BOWROOT}/log/flask_bow.log
  touch ${BOWROOT}/log/flask_wsgi.log
  chown -R bow:bow ${BOWROOT}/log
  chmod 774 ${BOWROOT}/log/*
  step_ok

  return 0
}

## @fn enable_nginx
enable_nginx ()
{
    ## We assume that nginx was installed as part of the Python installs.
    echo -e "Starting up NGINX server and enabling it to start on reboot. Verifying..."
    service nginx start
    systemctl enable nginx
    NGSTAT=$(systemctl status nginx)
    if [[ ${NGSTAT} =~ "active (running)" ]]; then
        nginx -t
        step_ok
        return 0
    else
        step_fail
        return 1
    fi
}

## @fn config_nginx
config_nginx ()
{
    echo -e "Setting up /etc/nginx/sites-enabled/flask_bow --> /etc/nginx/sites-available/flask_bow"
    NGAVAIL="/etc/nginx/sites-available"
    NGENABL="/etc/nginx/sites-enabled"
    # Remove flaskbow nginx config file if it already exists.
    if [[ -f ${NGAVAIL}/flaskbow ]]; then
        rm ${NGAVAIL}/flaskbow
    fi
    # Copy flaskbow config file in from installer bowax
    cp ${WAXPATH}/utils/conf/flask_bow.nginx ${NGAVAIL}/flask_bow
    # Create a symlink to it in sites-enabled if one does not already exist
    if [[ ! -f ${NGENABL}/flask_bow ]]; then
        ln -s ${NGAVAIL}/flask_bow ${NGENABL}/flask_bow
    fi
    # Remove the default NGINX symlink set up in sites-enabled if it exists
    if [[ -f ${NGENABL}/default ]]; then
        rm ${NGENABL}/default
    fi
    nginx -t
    service nginx restart
    NGSTAT=$(systemctl status nginx)
    if [[ $NGSTAT =~ "active (running)" ]];then
        step_ok
        return 0
    else
        step_fail
        return 1
    fi
}

## @fn config_www_data
config_www_data ()
{
    echo -e "Verifying that user <bow> is a member of group <www-data>..."
# We do this so that we can use uWSGI to run apps located under the bow account
    usermod -aG www-data bow
    BOWGRPS=$(groups bow)
    if [[ ${BOWGRPS} =~ "www-data" ]]; then
        step_ok
        return 0
    else
        step_fail
        return 1
    fi
}

## @fn config_uswgi
config_uswgi ()
{
    # Couldn't get a proper service working yet, so just starting up uwsgi via a shell script.
    # Shell scripts have been deployed to bow account ~/utils/sh
    # WSGI .ini has been deployed to bow account ~/utils/ini
    echo -e "Starting up WSGI so Flask/wsgi app runs under NGINX...."
    # If /etc/uwsgi/vassals does not exist, create it and symlink to the flaskbow.ini file
    DIRWSG="/etc/uwsgi"
    DIRVAS="/etc/uwsgi/vassals"
    if [[ ! -d ${DIRWSG} ]]; then
        mkdir ${DIRWSG}
    fi
    if [[ ! -d ${DIRVAS} ]]; then
        mkdir ${DIRVAS}
    fi
    if [[ -L ${DIRVAS}/flask_bow.ini ]];then
        rm ${DIRVAS}/flask_bow.ini
    fi
    # Create vassals symlink to .ini file in directory where flask_wsgi.py resides
    ln -s ${BOWROOT}/run/py/flask_bow.ini ${DIRVAS}/flask_bow.ini
    # Run the script to start up the uwsgi app
    bash ${BOWROOT}/utils/sh/flask_bow.sh
    # Show process
    FBOWPID=$(ps -ef | grep wsgi)
    echo -e "WSGI process running: ${FBOWPID}"
    # Show log
    tail -5 ${BOWROOT}/log/flask_wsgi.log
    step_ok
    return 0
}

## @fn make_ssl_certs
config_ssl_certs ()
{
    echo -e "Create self-generated SSL certificates. Eventually need to register real ones.
Check out: https://letsencrypt.org/"
    ## This creates self-signed certificates for development purposes only.
    ## It expires after one year.
    ## For production-level certificates, need to create a CSR and receive certs
    ## back from the certification agency.
    ## Using self-generated certificates will still not work well with curl.
    ##  With most browsers, it will let you thru after a warning. This is actually what we want:
    ##   Encryption is working but certificate is not a "real" one
    ## Hardcoded to work with bow.genuinemerit.com.
    ## @DEV - will probably want to set domain alias as a parameter instead.
    BOWSSL="/home/bow/run/ssl"
    openssl req \
            -x509 -nodes -days 365 -new \
            -subj '/C=US/ST=Massachusetts/L=Boston/CN=bow.genuinemerit.com' \
            -newkey rsa:2048 -out ${BOWSSL}/bow.genuinemerit.com.crt -keyout ${BOWSSL}/bow.genuinemerit.com.key
    if [[ -f ${BOWSSL}/bow.genuinemerit.com.crt ]]; then
        step_ok
        return 0
    else
        step_fail
        return 1
    fi
}

## ================= MAIN ===========================
SCRIPT="${WAXPATH}/build/"$(basename -- "$0")
BOWROOT="/home/bow"
ENV_VARS=""
. ${WAXPATH}/build/status.sh

(bash ${WAXPATH}/build/install_status.sh ${SCRIPT}); RC=$?
if [[ ${RC} -gt 0 ]]; then exit 1; fi  # Continue if status is OK
deploy_bow_code
if [[ ${RC} -gt 0 ]]; then exit 1; fi  # Continue if status is OK
enable_nginx
if [[ ${RC} -gt 0 ]]; then exit 1; fi  # Continue if status is OK
config_nginx
if [[ ${RC} -gt 0 ]]; then exit 1; fi  # Continue if status is OK
config_www_data
if [[ ${RC} -gt 0 ]]; then exit 1; fi  # Continue if status is OK
config_uswgi
if [[ ${RC} -gt 0 ]]; then exit 1; fi  # Continue if status is OK
config_ssl_certs
if [[ ${RC} -eq 0 ]]; then echo "${SCRIPT} COMPLETE" >> $TRKPATH; fi
