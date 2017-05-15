# -*- coding: utf-8 -*-
"""
"""
import commands


class Command(object):

    UPDATE = 'u'
    CLEAN = 'c'


def update(path, clean_dirty):
    cd_cmd = 'cd %s' % path
    clean_cmd = 'git clean -fd && git reset --hard'
    update_cmd = 'git pull -r'
    if clean_dirty:
        cmd = ' && '.join((cd_cmd, clean_cmd, update_cmd))
    else:
        cmd = ' && '.join((cd_cmd, update_cmd))
    return commands.getstatusoutput(cmd)
