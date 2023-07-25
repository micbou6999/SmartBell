#!/bin/bash

source pushover_cli.sh

for l in `cat user_list_for_notification`
do
    user=`echo $l | awk -F';' '{print $1}' | awk -F'=' '{print $2}'`
    token=`echo $l | awk -F';' '{print $2}' | awk -F'=' '{print $2}'`

    push_to_mobile from_Wave "Someone is outside your door." $user $token
done
