#!/bin/bash
## Run this script using docker privileges.
## One valid arugment required: build, run, stop, exec, push, pull, mongo
## This is a Build Admin script. Should not be stored with application code.

## - build  -- Build local docker container for bowmdb.
## Logging level is set at runtime, not at build time.
## @fn build_mdbbow
function build_mdbbow ()
{
    docker build -t $MDBDOCKCONT .
    docker images
    docker inspect $MDBDOCKCONT
}

## - runmongo -- Run the 'mongosrv' (mongo engine) container.
##  Start it up with --auth and wiredTiger.
##  Get into the admin database and create the root admin user interactively.
##  No matter how many times I have tried passing this in as script, it was unhappy.
##  use admin
##  db.createUser( { user: 'bowadmin', pwd: ## 'sdf9087ADJ', roles: [ { role: \"userAdminAnyDatabase\", db: \"admin\"} ] } );
## copy/paste this from srv_mdb_admin.js ^^
## Even then I still couldn't get the linked app's authentication call to work.
## So trying without it for now..
## All of this was probably due to the fact that I had not bound the IP of the Mongo
## host to the Mongo port, so no external connections could be made. It still probably
## makes sense to create the base "root" account directly rather than thru an API --
## and for that matter the other "admin" level accounts too. But a lot of the "issues" I
## was having initially were probably due to just not fully grasping the mongod.conf file.
## At any rate, having a node just devoted to Mongo (and maybe to MySQL later) is probably
## not a terrible idea.  Can use UFW to lock down the port connections so that only specific
## clients can use them. Can configure mongo to use SSL/TLS (though that will require getting
## adept at PKI). And could configure file-system level encryption if I really want to.
## exit
## @fn run_mongo
function run_mongo ()
{
    docker rm -f $MONGODOCKNM
    # docker run --name $MONGODOCKNM -d mongo --auth --storageEngine wiredTiger
    docker run --name $MONGODOCKNM -d mongo --storageEngine wiredTiger
    # docker exec -it $MONGODOCKNM mongo admin
    ## sudo docker exec -it $MONGODOCKNM mongo --eval "db.createUser( { user: 'bowadmin', pwd: ## 'sdf9087ADJ', roles: [ { role: \"userAdminAnyDatabase\", db: \"admin\"} ] } );"
    docker ps
    echo BoW Engine running
}

## - run    -- Run the app 'mdb' container. Mount host log directory to "/bowlog".
## Set host name and logging level as environment variables.
## Credentials for admin-level connection are set as envirnment variables.
## @fn run_mdbbow
function run_mdbbow ()
{
    docker rm -f $MDBDOCKNAME
    docker run -d -e LOGLEVEL="$LOGLEVEL" -e MONGOHOST="$MONGOHOST" -e ADMINID="$ADMINID" -e ADMINPWD="$ADMINPWD" -e DBADMINID="$DBADMINID" -e DBADMINPWD="$DBADMINPWD" -e DBOWNERID="$DBOWNERID" -e DBOWNERPWD="$DBOWNERPWD" -v /var/log/bow:/bowlog --name $MDBDOCKNAME $MDBDOCKCONT
    docker ps
    echo "BoW Mongo API running"
}

## - stop mongo  -- Stop running the mongo engine container and remove it.
## @fn stop_mongo
function stop_mongo ()
{
    docker stop $MONGODOCKNM
    docker rm -f $MONGODOCKNM
    docker ps
}


## - stop    -- Stop running the mdbbow container and remove it.
## @fn stop_mdbbow
function stop_mdbbow ()
{
    docker stop $MDBDOCKNAME
    docker rm -f $MDBDOCKNAME
    docker ps
}


## - push    -- Login to dockerhub and push the container.
## @fn push_mdbbow
function push_mdbbow ()
{
    docker images
    docker login
    docker push $MDBDOCKCONT
}

## - pull    -- Login to dockerhub and pull the container.
## @fn pull_mdbbow
function pull_mdbbow ()
{
    docker login
    docker pull $MDBDOCKCONT
    docker inspect $MDBDOCKCONT
}

## - pullmongo    -- Pull in a mongo container.
## @fn pull_mongo
function pull_mongo ()
{
    docker login
    docker pull mongo
    docker inspect mongo
}

## Main
cd $BOW/srvmdb
MDBDOCKCONT="genmerit/bowmdb:latest"
MONGODOCKNM="mongosrv"
MDBDOCKNAME="mdbbow"
APIHELP="srv_mdb_docker.sh [ help | build | runmongo | runmdb | stopmongo | stopmdb | push | pull | mongo ]"
LOGLEVEL="DEBUG"
MONGOHOST="data.genuinemerit.net:27017"
ADMINID="bow_root"
ADMINPWD="ananda23"
DBADMINID="bow_db_admin"
DBADMINPWD="ananda23"
DBOWNERID="bow_owner"
DBOWNERPWD="ananda23"
export MONGOHOST
export ADMINID
export ADMINPWD
export DBADMINID
export DBADMINPWD
export DBOWNERID
export DBOWNERPWD

if [[ $1 == help ]]
then
    echo $APIHELP
elif [[ $1 == build ]]
then
    build_mdbbow
elif [[ $1 == runmongo ]]
then
    run_mongo
elif [[ $1 == runmdb ]]
then
    run_mdbbow
elif [[ $1 == stopmongo ]]
then
    stop_mongo
elif [[ $1 == stopmdb ]]
then
    stop_mdbbow
elif [[ $1 == exec ]]
then
    exec_mdbbow
elif [[ $1 == push ]]
then
    push_mdbbow
elif [[ $1 == pull ]]
then
    pull_mdbbow
elif [[ $1 == mongo ]]
then
    pull_mongo
else
    echo $APIHELP
fi
