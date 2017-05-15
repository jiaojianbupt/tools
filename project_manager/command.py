# -*- coding: utf-8 -*-
"""
"""
import commands


class Command(object):

    UPDATE = 'u'
    CLEAN = 'c'


def update(path, clean_dirty):
    cmd = 'cd %s && git pull -r' % path
    if clean_dirty:
        cmd = 'git clean -fd && ' + cmd
    return commands.getstatusoutput(cmd)
