#!/bin/bash
#

# Standard evironment variables
# For a very detailed guide, see: https://wiki.archlinux.org/index.php/environment_variables

# Using the -e flag with echo enables interpretation of backslash escapes in bash.

# HISTFILE 	The name of the file in which command history is saved
# HISTFILESIZE 	The maximum number of lines contained in the history file
# HOSTNAME 	The system's host name
# LD_LIBRARY_PATH 	It is a colon-separated set of directories where libraries should be searched for
# PS1 	Your default (first) shell prompt
# USER 	Current logged in user's name.
# PATH 	Colon separated list of directories to search for binaries.
# DISPLAY 	Network name of the X11 display to connect to, if available.
# SHELL 	The current shell.
# TERM 	The name of the user's terminal. Used to determine the capabilities of the terminal.
# TERMCAP 	Database entry of the terminal escape codes to perform various terminal functions.
# OSTYPE 	Type of operating system.
# MACHTYPE 	The CPU architecture that the system is running on.
# EDITOR 	The user's preferred text editor.
# PAGER 	The user's preferred text pager.
# MANPATH 	Colon separated list of directories to search for manual pages.

# history 	List all commands in the commnd history buffer
# history -c  	Clear command history (buffer)
# ~/.bash_history	Is a file that stores command history.
#			To make sure it is cleared:  cat /dev/null > ~/.bash_history

# To define global variables, use of the following directories is UNIX-standard:
#  /etc/profile, /etc/bash.bashrc and /etc/environment.

# To define variables for use under my account only, modify one or more of the following:
# ~/.bashrc, ~/.profile, ~/.bash_login and ~/.bash_logout

# To modify a variable for a session only, use the export command, e.g.:
#  export PATH="${PATH}:/home/my_user/tmp/usr/bin"
# This change will last only as long as the session in which the export was run.

echo -e "printenv:\n"
printenv

echo -e "\n=========================================="
echo -e "\nSome indivudal settings:\n"
echo -e "Active shell: "$SHELL"\n"
echo -e "BASH version: "$BASH_VERSION"\n"
echo -e "Available shells:\n"
cat /etc/shells
echo -e "\nPATH: "$PATH
echo -e "\nHISTFILE: "$HISTFILE
echo -e "\nHISTFILESIZE: "$HISTFILESIZE
echo -e "\nHOSTNAME: "$HOSTNAME
echo -e "\nLD_LIBRARY_PATH: "$LD_LIBRARY_PATH
echo -e "\nPS1 (Default shell prompt): "$PS1
echo -e "\nUSER: "$USER
echo -e "\nDISPLAY (X11 display, network name): "$DISPLAY
echo -e "\nTERM: "$TERM
echo -e "\nTERMCAP (Escape codes for Terminal functions): "$TERMCAP
echo -e "\nOSTYPE: "$OSTYPE
echo -e "\nlsb_release -a:"
lsb_release -a
echo -e "\nMACHTYPE (CPU architecture): "$MACHTYPE
echo -e "\nEDITOR (Preferred text editor): "$EDITOR
echo -e "\nPAGER (Preferred text pager): "$PAGER
echo -e "\nMANPATH: "$MANPATH

echo -e "\n=========================================="
echo -e "\nCurrent command history:\n"
history

echo -e "\n=========================================="
echo -e "\nGlobal Profile files and dirs:"
echo -e "\nls -lsa /etc/pro*:\n"
ls -lsa /etc/pro*
echo -e "\ncat /etc/profile\n"
cat /etc/profile

echo -e "\nls -lsa /etc/env*:\n"
ls -lsa /etc/env*
echo -e "\ncat /etc/environment\n"
cat /etc/environment

echo -e "\n=========================================="
echo -e "\nLocal User Profile files:"
echo -e "\nls -lsa ~/.prof*"
ls -lsa ~/.prof*
echo -e "\nls -lsa ~/.bash*"
ls -lsa ~/.bash*
echo -e "\ncat ~/.profile"
cat ~/.profile
echo -e "\ncat ~/.bash_logout"
cat ~/.bash_logout

echo -e "\ncat ~/.bash_history"
echo -e "\n=========================================="
cat ~/.bash_history
