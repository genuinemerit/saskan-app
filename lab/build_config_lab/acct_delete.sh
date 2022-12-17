#!/bin/bash
## conf/acct_delete.sh

## $fn find_home
find_home ()
{
    # List /home
    FHOME="$(ls /home | grep $ACCT)"
}

## @fn del_acct
del_acct ()
{
    ACCT=$1
    find_home
    if [[ $FHOME ]]; then
        echo -e "Removing account $ACCT..."
        # Lock the password
        passwd --lock $ACCT
        # See all running processes
        pgrep -u $ACCT
        ps -f --pid "$(pgrep -u $ACCT)"
        # Kill all user processes
        killall -9 -u $ACCT
        # Should see no processes for this user now
        pgrep -u $ACCT
        # Remove the user and its home directory
        deluser --remove-home $ACCT
        find_home
        if [[ $FHOME ]]; then
            echo -e "Crap. Something didn't work. Account $ACCT not removed."
        else
            echo -e "Account $ACCT removed."
        fi

    else
        echo -e "No account found in /home named $ACCT"
    fi
}

## ================= MAIN ===========================
HELP="delete_acct.sh [-h|--help]  or  [-v|--version]  or  <acctname>\n
    Run under root account or with sudo privs."
VERS="delete_acct.sh v0.0.1\nRemove an account from a Linux server.\n"

if [[ ${1^^} == --HELP || ${1^^} == -H ]];      then echo -e "$HELP"
elif [[ ${1^^} == --VERSION || ${1^^} == -V ]]; then echo -e "$VERS"
elif [[ ${1^^} ]]; then 
   if [[ "$(whoami)" != "root" ]]; then
  	 echo "Sorry, you must be root (or sudo) to run this script."
  	 exit 1
  fi
  del_acct $1
else echo -e "$HELP"
fi
