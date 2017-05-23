# -*- coding: utf-8 -*-
"""
"""
import commands


class Status(object):

    NORMAL = 0
    ERROR = 255


class Command(object):

    UPDATE = '-u'
    STATUS = '-s'


class CommandMode(object):

    NORMAL = '-n'
    CLEAN = '-c'
    AUTO_STASH = '-a'


def execute_command(path, command=None, mode=None):
    if not command:
        command = Command.UPDATE
    if command == Command.UPDATE:
        return update(path, mode)
    if command == Command.STATUS:
        modified_files = get_modified(path)
        untracked_files = get_untracked(path)
        if not modified_files and not untracked_files:
            return Status.NORMAL, None
        message = ''
        if modified_files:
            message += 'Changes not staged for commit:\n'
            message += '\n'.join(['\t%s' % i for i in modified_files])
        if untracked_files:
            message += '\nUntracked files:\n'
            message += '\n'.join(['\t%s' % i for i in untracked_files])
        return Status.ERROR, message


def update(path, mode):
    cd_cmd = 'cd %s' % path
    clean_cmd = 'git clean -fd && git reset --hard'
    update_cmd = 'git pull -r'
    stash_cmd = 'git stash'
    stash_pop_cmd = 'git stash pop'
    diff_file_cmd = 'git diff --name-only'
    diff_files = commands.getoutput(' && '.join((cd_cmd, diff_file_cmd)))
    if mode == CommandMode.CLEAN:
        cmd = ' && '.join((cd_cmd, clean_cmd, update_cmd))
    elif mode == CommandMode.AUTO_STASH and diff_files:
        cmd = ' && '.join((cd_cmd, stash_cmd, update_cmd, stash_pop_cmd))
    else:
        cmd = ' && '.join((cd_cmd, update_cmd))
    return commands.getstatusoutput(cmd)


def get_modified(path):
    cd_cmd = 'cd %s' % path
    modified_file_cmd = 'git diff --name-status'
    modified_files = commands.getoutput(' && '.join((cd_cmd, modified_file_cmd)))
    if not modified_files:
        return ''
    return modified_files.split('\n')


def get_untracked(path):
    cd_cmd = 'cd %s' % path
    untracked_file_cmd = 'git ls-files --others --exclude-standard'
    untracked_files = commands.getoutput(' && '.join((cd_cmd, untracked_file_cmd)))
    if not untracked_files:
        return ''
    return untracked_files.split('\n')
