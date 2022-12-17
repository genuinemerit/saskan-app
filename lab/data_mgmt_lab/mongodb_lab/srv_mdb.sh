#!/bin/bash
## Run this script using sudo privileges.
## Define shell-level environment variables
## Create log and app (mdb) directories if they don't already exist.
## Start up the Mongo Server API for Ball of Wax.
## We assume for now that the Mongo server itself is already running.
## Will probably want scripts to configure the server itself, set auth on, etc.
## And possibly install mongohacker and a modified ~/.mongorc.js.
##
## @fn srvbow
srvmdb ()
{
    cd $BOW/srvmdb
    BOWLOG="/var/log/bow"
    mkdir -p $BOWLOG
    MDBBIN="/var/lib/bow/mdb"
    MDBLOG="$BOWLOG/bowmdb.json"
    LOGLEVEL="DEBUG"
    export MDBEMAIL
    export MDBDATA
    export MDBLOG
    export LOGLEVEL
    rm -R $MDBBIN
    mkdir -p $MDBBIN
    rm $MDBLOG
    cp ./python/*.py $MDBBIN
    cp ./shell/*.sh $MDBBIN
    cd $MDBBIN
    python srv_mdb_status.py
}
srvmdb
