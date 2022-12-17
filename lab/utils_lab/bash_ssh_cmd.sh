#!/bin/sh
# for machine in dave@subhuti dave@ananda
# do
	# execute remote command 'w' on each machine
#	ssh $machine /usr/bin/w
#done
echo
echo dave@subhuti
sshpass -p ananda23 ssh dave@subhuti w
echo
echo dave@ananda
sshpass -p subhuti23 ssh dave@ananda w

