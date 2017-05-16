# -*- coding: utf-8 -*-
"""
"""
import commands


class Command(object):

    UPDATE = 'u'
    CLEAN = 'c'
    AUTO_STASH = 'a'


def update(path, mode):
    cd_cmd = 'cd %s' % path
    clean_cmd = 'git clean -fd && git reset --hard'
    update_cmd = 'git pull -r'
    stash_cmd = 'git stash'
    stash_pop_cmd = 'git stash pop'
    diff_file_cmd = 'git diff --name-only'
    diff_files = commands.getoutput(diff_file_cmd)
    if mode == Command.CLEAN:
        cmd = ' && '.join((cd_cmd, clean_cmd, update_cmd))
    elif mode == Command.AUTO_STASH and diff_files:
        cmd = ' && '.join((cd_cmd, stash_cmd, update_cmd, stash_pop_cmd))
    else:
        cmd = ' && '.join((cd_cmd, update_cmd))
    return commands.getstatusoutput(cmd)
