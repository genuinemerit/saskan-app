#!/bin/bash

# A few small examples of how variables are used in bash scripts

# If bash is started with the -c option, then $0 is set to the first argument after the string to be executed, if one is present.
# Otherwise, it is set to the file name used to invoke bash, as given by argument zero

number=3
args=$1.$2
arg3=$3
date=$(date)
script=$0

combined="The number is $number, the args combined with dot make $args, it is now $date"
echo $number
echo $args
echo $arg3
echo $date
echo 
echo $combined

# Display the script type
echo Script type or name = $script
