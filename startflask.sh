#!/bin/bash
#Run flask in current terminal
cd '/mnt/c/users/ryan/work_ryan/y4s1/fyp/fyp_uc1/webscrap-website'
source '/mnt/c/users/ryan/work_ryan/y4s1/fyp/fyp_uc1/webscrap-website/linux_webvenv/bin/activate'
#bash --rcfile '/mnt/c/users/ryan/work_ryan/y4s1/fyp/fyp_uc1/webscrap-website/linux_webvenv/bin/activate'
export FLASK_APP=application.py
flask run
