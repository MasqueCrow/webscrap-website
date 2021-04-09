#!/bin/bash
# run this script to open 3 seperate terminals to run the web app --> 1 for celery, 1 for redis and 1 for flask
cd '/mnt/c/users/ryan/work_ryan/y4s1/fyp/fyp_uc1/webscrap-website'
source '/mnt/c/users/ryan/work_ryan/y4s1/fyp/fyp_uc1/webscrap-website/linux_webvenv/bin/activate'
export DISPLAY_NUMBER="0.0"
export DISPLAY=$(grep -m 1 nameserver /etc/resolv.conf | awk '{print $2}'):$DISPLAY_NUMBER
export LIBGL_ALWAYS_INDIRECT=1
echo $DISPLAY
gnome-terminal --working-directory='/mnt/c/users/ryan/work_ryan/y4s1/fyp/fyp_uc1/webscrap-website' -x bash -c "source ./startredis.sh; exec bash"
gnome-terminal --working-directory='/mnt/c/users/ryan/work_ryan/y4s1/fyp/fyp_uc1/webscrap-website' -x bash -c "source ./startcelery.sh; exec bash"
gnome-terminal --working-directory='/mnt/c/users/ryan/work_ryan/y4s1/fyp/fyp_uc1/webscrap-website' -x bash -c "source ./startflask.sh; exec bash"

