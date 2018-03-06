#!/usr/bin/env bash
root_dir="$HOME/.custom_complete/"
cache_dir="$root_dir/cache/"
lock_file="$root_dir/lock"
target_dir="$HOME/repos/ss_conf_aws/ss/"
_foo() {
    _init
    COMPREPLY=()
    local cur=${COMP_WORDS[COMP_CWORD]};
    local cmd=${COMP_WORDS[COMP_CWORD-1]};
    case ${cmd} in
    'foo')
        COMPREPLY=( $(compgen -W 'help test read' -- ${cur}) )
    ;;
    'test')
        local candidates=()
        for conf_file in ~/repos/ss_conf_aws/ss/*.conf; do
            candidates+=( $(awk '{print $1}' ${conf_file}) )
        done
        COMPREPLY=( $(compgen -W '${candidates[@]}' -- ${cur}) )
    ;;
    '*')
    ;;
    esac
    if [[ "${COMP_WORDS[1]}" == "read" && ${COMP_CWORD} -eq 2 ]]; then
        local pro=$(pwd)
        cd /data
        compopt -o nospace
        COMPREPLY=($(compgen -d -f -- ${cur}))
        cd ${pro}
  fi
  return 0
}
_init() {
    if [ ! -d "$root_dir" ]; then
        mkdir ${root_dir}
    fi
    if [ ! -d "$cache_dir" ]; then
        mkdir ${cache_dir}
    fi
    current_dir=$("pwd")
    cd ${target_dir}
    current_version=$(git rev-parse HEAD)
    cache_file="$cache_dir$current_version"
    if [ -f ${cache_file} ]; then
        return 0
    fi
    # Remove old cache file.
    rm cache_file
    local conf_list=""
    for conf_file in `ls ${target_dir}`; do
        conf_list+="$conf_file\n"
    done
    echo ${conf_list} > "$cache_file"
}
_acquire_lock() {
    if [ -f ${lock_file} ] &&
    if [! -f "$lock_file" ]; then

    fi

}

complete -F _foo foo
