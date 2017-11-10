# -*- coding: utf-8 -*-
"""
"""
import commands
import os
import time
from tools.utils.printer import print_with_style, LogLevel, ConsoleColor


class Status(object):
    NORMAL = 0
    ERROR = 255


class Command(object):
    UPDATE = '-u'
    STATUS = '-s'
    EXPORT = '-e'


class CommandResult(object):
    def __init__(self, status, message, cost, path):
        self.status = status
        self.message = message
        self.cost = cost
        self.path = path


class CommandMode(object):
    NORMAL = '-n'
    CLEAN = '-c'
    AUTO_STASH = '-a'


def execute_with_result(path, command=None, mode=None, user=None, remote_host=None, local_root_path=None,
                        remote_root_path=None, is_debug=False):
    executor = CommandExecutor(path, command=command, mode=mode, user=user, remote_host=remote_host,
                               local_root_path=local_root_path, remote_root_path=remote_root_path, is_debug=is_debug)
    return executor.execute_command()


class CommandExecutor(object):
    def __init__(self, path, command=None, mode=None, user=None, remote_host=None, local_root_path=None,
                 remote_root_path=None, is_debug=False):
        self.path = path
        self.command = command
        self.mode = mode
        self.user = user
        self.remote_host = remote_host
        if not self.command:
            self.command = Command.UPDATE
        self.local_root_path = local_root_path
        self.remote_root_path = remote_root_path
        self.is_debug = is_debug

    def execute_command(self):
        start = time.time()
        status, message = Status.ERROR, 'Unknown Error'
        if self.command == Command.UPDATE:
            status, message = self.update()
        elif self.command == Command.STATUS:
            modified_files = self.get_modified()
            untracked_files = self.get_untracked()
            if not modified_files and not untracked_files:
                status, message = Status.NORMAL, None
            else:
                message = ''
                if modified_files:
                    message += 'Changes not staged for commit:\n'
                    message += '\n'.join(['\t%s' % i for i in modified_files])
                if untracked_files:
                    message += '\nUntracked files:\n'
                    message += '\n'.join(['\t%s' % i for i in untracked_files])
                status, message = Status.ERROR, message
        elif self.command == Command.EXPORT:
            status, message = self.get_remote_url()
        else:
            raise Exception('Unknown command %s' % self.command)
        result = CommandResult(
            status=status,
            message=message,
            cost=time.time() - start,
            path=self.path
        )
        return result

    def get_remote_url(self):
        cd_cmd = 'cd %s' % self.path
        remote_url = 'git config --get remote.origin.url'
        status, message = self.getstatusoutput(' && '.join((cd_cmd, remote_url)))
        if not message.startswith('git@') or not message.startswith('ssh://'):
            host, sub_path = message.split(':')
            hostname = self.get_ssh_params(host, 'hostname')
            port = self.get_ssh_params(host, 'port')
            user = self.get_ssh_params(host, 'user')
            print 'hostname: %s, user: %s' % (hostname, user)
            message = 'ssh://%s@%s:%s%s' % (user, hostname, port, sub_path)
        return status, message

    def get_ssh_params(self, host, param_name):
        ssh_hostname = 'ssh -G %s | grep \'^%s \'' % (host, param_name)
        message = self.getoutput(ssh_hostname)
        return message.split(' ')[1]

    def update(self):
        status = Status.ERROR
        message = 'Unknown error.'
        retry = 3
        while status and retry > 0:
            status, message = self._update()
        return status, message

    def _update(self):
        cd_cmd = 'cd %s' % self.path
        clean_cmd = 'git clean -fd && git reset --hard'
        update_cmd = 'git pull -r'
        stash_cmd = 'git stash'
        stash_pop_cmd = 'git stash pop'
        diff_file_cmd = 'git diff --name-only'
        diff_files = self.getoutput(' && '.join((cd_cmd, diff_file_cmd)))
        current_branch = self.get_current_branch()

        if self.mode == CommandMode.CLEAN:
            cmd = ' && '.join((clean_cmd, update_cmd))
        elif self.mode == CommandMode.AUTO_STASH and diff_files:
            cmd = ' && '.join((stash_cmd, update_cmd, stash_pop_cmd))
        else:
            cmd = update_cmd

        if current_branch != 'master':
            cmd = ' && '.join(('git checkout master', cmd, 'git checkout %s' % current_branch))

        cmd = ' && '.join((cd_cmd, cmd))

        if self.user and self.remote_host:
            cmd = ' && '.join((cmd, 'cd %s' % self.local_root_path))
            relative_path = os.path.relpath(self.path, self.local_root_path)
            args = (relative_path, self.remote_host, self.remote_root_path)
            cmd = ' && '.join((cmd, 'rsync -a -r --relative %s --delete --force %s:%s' % args))

        return self.getstatusoutput(cmd)

    def get_modified(self):
        cd_cmd = 'cd %s' % self.path
        modified_file_cmd = 'git diff --name-status'
        modified_files = self.getoutput(' && '.join((cd_cmd, modified_file_cmd)))
        if not modified_files:
            return ''
        return modified_files.split('\n')

    def get_untracked(self):
        cd_cmd = 'cd %s' % self.path
        untracked_file_cmd = 'git ls-files --others --exclude-standard'
        untracked_files = self.getoutput(' && '.join((cd_cmd, untracked_file_cmd)))
        if not untracked_files:
            return ''
        return untracked_files.split('\n')

    def get_current_branch(self):
        cd_cmd = 'cd %s' % self.path
        current_branch_cmd = 'git rev-parse --abbrev-ref HEAD'
        current_branch = self.getoutput(' && '.join((cd_cmd, current_branch_cmd)))
        return current_branch

    def getoutput(self, cmd):
        return self.getstatusoutput(cmd)[1]

    def getstatusoutput(self, cmd):
        log_text_part = []
        status, message = commands.getstatusoutput(cmd)
        if self.is_debug:
            log_text_part.append(('Host %s Debug Info Start' % self.remote_host).center(80, '-'))
            log_text_part.append('Command: %s' % cmd)
            log_text_part.append('Result: %s' % message)
            log_text_part.append(('Host %s Debug Info End' % self.remote_host).center(80, '-'))
            log_text = '\n'.join(log_text_part)
            print_with_style(log_text, color=ConsoleColor.MAGENTA, prefix='')
        return status, message
