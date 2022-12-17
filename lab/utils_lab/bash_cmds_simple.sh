#!/bin/bash
#

# Simple shell commands
echo
echo "<date> The date and time right now"
echo
date
echo 
echo "<cal> A current calendar"
echo
cal
echo
echo "<df> Free space on your disk drives"
echo 
df
echo
echo "<free> Free memory"
echo 
free
echo
echo "<pwd> What directory am I in?"
echo 
pwd
echo
echo "<cd> <pwd> Go to my home"
echo 
cd
pwd
echo
echo "<cd -> Go to the last dir I was in"
echo 
cd -
echo
echo "<ls> Show what is in the pwd"
echo 
ls
echo
echo "<ls ~ .. /var/www/html> Show what is in home and the upper dir and in /var/www/html"
echo 
ls ~ .. /var/www/html
echo
echo "<ls -tlh> Sort by modify date descending, list, human-readable size display"
echo 
ls -tlh
echo
echo "<file _filename_> Show information about the file"
echo 
file typescript
file bashvars.sh
file ~/Applications/processing-2.2.1/java/bin/java_vm
file ~/Applications/processing-2.2.1/java/bin/ControlPanel
echo
echo "<less _filename> or <more >"
echo "b	           scroll up (back) one page"
echo "<spacebar>   scroll down (forward) one page"
echo "<up arrow>   scroll up one line"
echo "<down arrow> scroll down one line"
echo "G            go to end of file"
echo "g or 1G      go to start of file (row 1)"
echo "/<chars>     search for next occurrence of <chars>"
echo "n     	   search for next occurrence of current <chars>"
echo "h			   help"
echo "q			   quit"
echo 
less bash_backup_example.sh
