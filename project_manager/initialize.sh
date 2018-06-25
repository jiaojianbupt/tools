#!/usr/bin/env bash
export PROJECT_MANAGER_PATH=$(cd "$( dirname "${BASH_SOURCE[0]-$0}" )" && pwd)
update_repos(){
     echo `${PROJECT_MANAGER_PATH}/default_generate.sh $1 $2`
}
source ${PROJECT_MANAGER_PATH}/conf.local
cmd_tmp=`update_repos ${VA_DEV} py`
alias usp=${cmd_tmp}
cmd_tmp=`update_repos ${CN_DEV} py`
alias uspcn=${cmd_tmp}
cmd_tmp=`update_repos ${SG_DEV} py`
alias uspsg=${cmd_tmp}
cmd_tmp=`update_repos ${ALIVA_DEV} py`
alias uspaliva=${cmd_tmp}
cmd_tmp=`update_repos ${VA_DEV} go`
alias usg=${cmd_tmp}
cmd_tmp=`update_repos ${CN_DEV} go`
alias usgcn=${cmd_tmp}
cmd_tmp=`update_repos ${SG_DEV} go`
alias usgsg=${cmd_tmp}
cmd_tmp=`update_repos ${ALIVA_DEV} go`
alias usgaliva=${cmd_tmp}
