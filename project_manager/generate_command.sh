#!/usr/bin/env bash

dev_host=$1
local_path=$2
remote_path=$3
exclude_path=$4

command="python "${PROJECT_MANAGER_PATH}"/main.py -d $local_path --remote-host $dev_host --local-root-path $local_path --remote-root-path $remote_path"
if [ -n "${exclude_path}" ]
then
    command+=" --exclude-directories $exclude_path"
fi
echo ${command}
