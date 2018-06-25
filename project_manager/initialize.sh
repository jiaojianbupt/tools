#!/usr/bin/env bash
export PROJECT_MANAGER_PATH=$(cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)
update_repos(){
     echo `${PROJECT_MANAGER_PATH}/default_generate.sh $1 $2`
}
source ${PROJECT_MANAGER_PATH}/conf.local
alias usp=`update_repos ${VA_DEV} py`
alias uspcn=`update_repos ${CN_DEV} py`
alias uspsg=`update_repos ${SG_DEV} py`
alias uspaliva=`update_repos ${ALIVA_DEV} py`
alias usg=`update_repos ${VA_DEV} go`
alias usgcn=`update_repos ${CN_DEV} go`
alias usgsg=`update_repos ${SG_DEV} go`
alias usgaliva=`update_repos ${ALIVA_DEV} go`
