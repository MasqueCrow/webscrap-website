#!/bin/bash
#Open new terminal window to run celery
cd '/mnt/c/users/ryan/work_ryan/y4s1/fyp/fyp_uc1/webscrap-website'
source '/mnt/c/users/ryan/work_ryan/y4s1/fyp/fyp_uc1/webscrap-website/linux_webvenv/bin/activate'
#bash --rcfile '/mnt/c/users/ryan/work_ryan/y4s1/fyp/fyp_uc1/webscrap-website/linux_webvenv/bin/activate'
celery -A application.celery worker -l info -Q queue1,queue2,queue3,queue4,queue5
