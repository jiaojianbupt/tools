#!/usr/bin/env bash

dev_host=$1
language=$2

python_local_path="~/repos"
python_remote_path="repos"
python_exclude_path=""
go_local_path="~/go"
go_remote_path="go"
go_exclude_path="$go_local_path/src/github.com/gin-gonic/gin,$go_local_path/src/code.byted.org/kite/kitool"

local_path=""
remote_path=""
exclude_path=""

if [ "$language" == "py" ]
then
    local_path="${python_local_path}"
    remote_path="${python_remote_path}"
elif [ "$language" == "go" ]
then
    local_path="${go_local_path}"
    remote_path="${go_remote_path}"
    exclude_path="${go_exclude_path}"
fi

sh "${PROJECT_MANAGER_PATH}"/generate_command.sh ${dev_host} ${local_path} ${remote_path} ${exclude_path}
