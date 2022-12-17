#!/bin/sh
# The account executing this script must have sudo on the local machine
rmtpwd=the_password
echo
echo dave@ananda
sshpass -p $rmtpwd ssh dave@ananda echo $rmtpwd | sudo -S apt-get update
sshpass -p $rmtpwd ssh dave@ananda echo $rmtpwd | sudo -S apt-get -y dist-upgrade
sshpass -p $rmtpwd ssh dave@ananda echo $rmtpwd | sudo -S apt-get autoclean
sshpass -p $rmtpwd ssh dave@ananda echo $rmtpwd | sudo -S apt-get autoremove
rmtpwd=the_password
echo
echo dave@subhuti
sshpass -p $rmtpwd ssh dave@subhuti echo $rmtpwd | sudo -S apt-get update
sshpass -p $rmtpwd ssh dave@subhuti echo $rmtpwd | sudo -S apt-get -y dist-upgrade
sshpass -p $rmtpwd ssh dave@subhuti echo $rmtpwd | sudo -S apt-get autoclean
sshpass -p $rmtpwd ssh dave@subhuti echo $rmtpwd | sudo -S apt-get autoremove

