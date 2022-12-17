#!/bin/bash
# Add -vx to bin/bash to run in verbose debug mode
# Run this script using sudo privileges on an Ubuntu or Mint server.
# Define environment variables.
. bc_env.sh
# Retrieve passwords from caja.genuinemerit.org
. bc_get_auth.sh
. $DIR_BOW_TMP/bow_auth.sh
# Remove decrypted passwords script
. bc_rm_auth.sh
#
# Install mongodb and configure it for Ball of Wax.
# Either copy relevant files to target server and run them there or execute via ssh.
#
## @fn stop_on_error
stop_on_error ()
{
    set -o errexit
}

## @fn stop_mongo
stop_mongo ()
{
    set +e
    sudo systemctl status mongodb
    sudo systemctl stop mongodb
    sudo systemctl disable mongodb
    sudo systemctl status mongodb
    stop_on_error
}

## @fn apt_uninstall_mongo
apt_uninstall_mongo ()
{
    set +e
    sudo rm -r /var/log/mongod*
    sudo rm -r /var/lib/mongod*
    stop_on_error
    sudo apt-get --yes purge mongodb*
    set +e
    sudo rm -r /etc/mongo*
    sudo rm -r /etc/init/mongo*
    sudo rm -r /etc/init.d/mongo*
    sudo rm -r /etc/ssl/mongo*
    sudo rm -r /etc/systemd/system/mongo*
    stop_on_error
}

## @fn install_mongo
apt_install_mongo ()
{
    sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv EA312927
    echo "deb http://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/3.2 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.2.list
    sudo apt-get update
    sudo apt-get --yes install mongodb-org
    whereis mongo
    whereis mongod
    mongo --help
}

## @fn create_service
create_service ()
{
    echo '# /etc/systemd/system/mongodb.service
[Unit]
Description=High-performance, schema-free document-oriented database
After=network.target

[Service]
User=mongodb
ExecStart=/usr/bin/mongod --quiet --config /etc/mongod.conf

[Install]
WantedBy=multi-user.target
' > /etc/systemd/system/mongodb.service

    cat /etc/systemd/system/mongodb.service

    echo '# /etc/systemd/system/mongodb-hugepage-fix.service
[Unit]
Description="Disable Transparent Hugepage before MongoDB boots"
Before=mongodb.service

[Service]
Type=oneshot
ExecStart=/bin/bash -c "echo never > /sys/kernel/mm/transparent_hugepage/enabled"
ExecStart=/bin/bash -c "echo never > /sys/kernel/mm/transparent_hugepage/defrag"

[Install]
RequiredBy=mongodb.service
' > /etc/systemd/system/mongodb-hugepage-fix.service

    cat /etc/systemd/system/mongodb-hugepage-fix.service
}

# Initial set-up of mongod.conf.
# It is extended to require authorization and to handle SSL/TLS in subsequent functions.
## @fn create_config
create_config ()
{
    echo "# /etc/mongod.conf
# for documentation of all options, see:
#   http://docs.mongodb.org/manual/reference/configuration-options/

# where and how to store data.
storage:
  dbPath: /var/lib/mongodb
  journal:
    enabled: true

# where to write logging data.
systemLog:
  destination: file
  logAppend: true
  path: /var/log/mongodb/mongod.log

# network interfaces
net:
  port: 27017
  bindIp: 127.0.0.1,'$IP'
" > /etc/mongod.conf
    cat /etc/mongod.conf
}

## fn create_ssl_keys
create_keys ()
{
    openssl req \
        -x509 -nodes -days 365 -new \
        -subj '/C=US/ST=Massachusetts/L=Boston/CN='$DOMAIN \
        -newkey rsa:2048 -out /etc/ssl/$DOMAIN.crt -keyout /etc/ssl/$DOMAIN.key
    cat /etc/ssl/$DOMAIN.key /etc/ssl/$DOMAIN.crt > /etc/ssl/$DOMAIN.pem
    cat /etc/ssl/$DOMAIN.pem
}

## @fn start_service
start_service ()
{
    sudo systemctl daemon-reload
    sudo systemctl enable mongodb
    sudo systemctl enable mongodb-hugepage-fix
    sudo systemctl start mongodb-hugepage-fix
    sudo systemctl start mongodb
    sudo systemctl status mongodb
}

## @fn start_service
restart_service ()
{
    sudo systemctl restart mongodb-hugepage-fix
    sudo systemctl restart mongodb
    sudo systemctl status mongodb
}

# Create Linux user, or use existing account if found, as mongo admin.
# This user should have sudo privs and also be a member of mongodb user group
## @fn enable_user
enable_user ()
{
    if [ "`id -u "$USER" 2>/dev/null || echo -1`" -ge 0 ]; then
        echo "Found user $USER. Using it."
    else
        echo "User $USER not found. Creating it."
        adduser $USER --gecos "First Last,RoomNumber,WorkPhone,HomePhone" --disabled-password
        echo "$USER:$PWD" | chpasswd
        sudo usermod -aG sudo $USER
    fi
    sudo usermod -aG mongodb $USER
    id $USER
    sudo -su $USER
}

# Substitute user and password into javascript user set up and auth files.
# Execute the js files in mongo shell.
# This creates mongo root-level super user: $USER_root.
## @fn create_root_user
create_root_user ()
{
    USEA="use admin\n"
    CMD1=$(sed -e "s/%USER%/${USER}_root/g" -e "s/%PWD%/$PWD/g" ./mdb_create_root.js)
    echo -e $USEA$CMD1 | mongo

    CMD2=$(sed -e "s/%USER%/${USER}_root/g" -e "s/%PWD%/$PWD/g" ./mdb_auth.js)
    echo -e $USEA$CMD2 | mongo
}

# Create additional mongo user accounts to support Ball of Wax.
## @fn create_mongo_users
create_mongo_users ()
{
    role=()
    role[0]="root"
    role[1]="db_admin"
    role[2]="user_admin"
    role[3]="owner"

    dbase=()
    dbase[0]="usr"
    dbase[1]="sem"
    dbase[2]="int"
    dbase[3]="sess"
    dbase[3]="tech"

    priv=()
    priv[0]="ro"
    priv[1]="rw"

    # db.runCommand( {   dropUser: "%USER%_usr_ro" } );
    # db.runCommand( {   dropUser: "%USER%_sem_ro" } );
    # db.runCommand( {   dropUser: "%USER%_int_ro" } );
    # db.runCommand( {   dropUser: "%USER%_sess_ro" } );
    # db.runCommand( {   dropUser: "%USER%_tech_ro" } );
    # db.runCommand( {   dropUser: "%USER%_usr_rw" } );
    # db.runCommand( {   dropUser: "%USER%_sem_rw" } );
    # db.runCommand( {   dropUser: "%USER%_int_rw" } );
    # db.runCommand( {   dropUser: "%USER%_sess_rw" } );
    # db.runCommand( {   dropUser: "%USER%_tech_rw" } );

    echo "${usrnm[@]}"
    echo "${usrnm[*]}"
}

## @fn enable_security
enable_security ()
{
    echo '
# require user authorization
security:
  authorization: enabled
' > /etc/mongod_auth
    cp /etc/mongod.conf /etc/mongod.conf.bak
    cat /etc/mongod.conf.bak /etc/mongod_auth > /etc/mongod.conf
    rm /etc/mongod_auth
    cat /etc/mongod.conf
}

## @fn enable_tls
enable_tls ()
{
    echo '
net:
   ssl:
      mode: requireSSL
      PEMKeyFile: /etc/ssl/'$DOMAIN'.pem
' > /etc/mongod_net
    cp /etc/mongod.conf /etc/mongod.conf.bak
    cat /etc/mongod.conf.bak /etc/mongod_net > /etc/mongod.conf
    rm /etc/mongod_net
    cat /etc/mongod.conf
}


# MAIN ##############################
stop_on_error
SHHELP="sudo install_bow_mongo.sh [-h | --help] [--version] domain_nm admin_id
\nExample: sudo install bow_mongo.sh caja.genuinemerit.org bozo
\nThe admin_id will create a Linux admin account for mongo and provide the root for all
accounts created within mongodb. Passwords need to be set via the ba_auth.sh scripts."
SHVERS="\n
BoW Mongo Build, version 0.0.1-release (Ubuntu/Mint 16.04)\n
Copyright (C) 2016 Genuine Merit\n
License MIT License:  <https://opensource.org/licenses/MIT>\n\n
This is free software; you are free to change and redistribute it.\n
There is NO WARRANTY, to the extent permitted by law.
"
if [[ $1 == -h  || $1 == --help ]]
then
    echo $SHHELP
elif [[ $1 == --version ]]
then
    echo -e $SHVERS
elif [[ "$#" -lt 3 || "$#" -gt 3 ]]
then
    echo "Exactly 3 arguments are required: domain_nm admin_id admin_pwd."
else
    # Define variables
    DOMAIN=$1
    USER=$2
    # Execute logic under current user ID
    stop_mongo
    apt_uninstall_mongo
    apt_install_mongo
    create_service
    create_config
    # create_keys -- will need to work on this offline until I get it working
    start_service
    # enable_user moves into a shell under the new mongodb USER.
    # After running the script, type exit to return to parent user shell.
    enable_user
    create_root_user
    enable_security
    # enable_tls -- could not get this configured right
    restart_service
fi
set +e
