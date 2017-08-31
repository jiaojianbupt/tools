# -*- coding: utf-8 -*-
"""
"""
import commands
import os


class Status(object):

    NORMAL = 0
    ERROR = 255


class Command(object):

    UPDATE = '-u'
    STATUS = '-s'
    EXPORT = '-e'


class CommandMode(object):

    NORMAL = '-n'
    CLEAN = '-c'
    AUTO_STASH = '-a'


def execute_with_result(path, command=None, mode=None, user=None, remote_host=None, local_root_path=None,
                        remote_root_path=None):
    executor = CommandExecutor(path, command=command, mode=mode, user=user, remote_host=remote_host,
                               local_root_path=local_root_path, remote_root_path=remote_root_path)
    return executor.execute_command()


class CommandExecutor(object):
    def __init__(self, path, command=None, mode=None, user=None, remote_host=None, local_root_path=None,
                 remote_root_path=None):
        self.path = path
        self.command = command
        self.mode = mode
        self.user = user
        self.remote_host = remote_host
        if not self.command:
            self.command = Command.UPDATE
        self.local_root_path = local_root_path
        self.remote_root_path = remote_root_path

    def execute_command(self):
        if self.command == Command.UPDATE:
            return self.update()
        elif self.command == Command.STATUS:
            modified_files = self.get_modified()
            untracked_files = self.get_untracked()
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
        elif self.command == Command.EXPORT:
            return self.get_remote_url()
        raise Exception('Unknown command %s' % self.command)


    def get_remote_url(self):
        cd_cmd = 'cd %s' % self.path
        remote_url = 'git config --get remote.origin.url'
        status, message = commands.getstatusoutput(' && '.join((cd_cmd, remote_url)))
        if not message.startswith('git@') or not message.startswith('ssh://'):
            host, sub_path = message.split(':')
            hostname = self.get_ssh_params(host, 'hostname')
            port = self.get_ssh_params(host, 'port')
            user = self.get_ssh_params(host, 'user')
            print 'hostname: %s, user: %s' % (hostname, user)
            message = 'ssh://%s@%s:%s%s' % (user, hostname, port, sub_path)
        return status, message


    @staticmethod
    def get_ssh_params(host, param_name):
        ssh_hostname = 'ssh -G %s | grep \'^%s \'' % (host, param_name)
        message = commands.getoutput(ssh_hostname)
        return message.split(' ')[1]


    def update(self):
        cd_cmd = 'cd %s' % self.path
        clean_cmd = 'git clean -fd && git reset --hard'
        update_cmd = 'git pull -r'
        stash_cmd = 'git stash'
        stash_pop_cmd = 'git stash pop'
        diff_file_cmd = 'git diff --name-only'
        diff_files = commands.getoutput(' && '.join((cd_cmd, diff_file_cmd)))
        if self.mode == CommandMode.CLEAN:
            cmd = ' && '.join((cd_cmd, clean_cmd, update_cmd))
        elif self.mode == CommandMode.AUTO_STASH and diff_files:
            cmd = ' && '.join((cd_cmd, stash_cmd, update_cmd, stash_pop_cmd))
        else:
            cmd = ' && '.join((cd_cmd, update_cmd))

        if self.user and self.remote_host:
            relative_path = os.path.relpath(self.path, self.local_root_path)
            remote_path = os.path.dirname(os.path.join(self.remote_root_path, relative_path))
            cmd = ' && '.join((cmd, 'rsync -r --delete --force %s %s:%s' % (self.path, self.remote_host, remote_path)))
        return commands.getstatusoutput(cmd)


    def get_modified(self):
        cd_cmd = 'cd %s' % self.path
        modified_file_cmd = 'git diff --name-status'
        modified_files = commands.getoutput(' && '.join((cd_cmd, modified_file_cmd)))
        if not modified_files:
            return ''
        return modified_files.split('\n')


    def get_untracked(self):
        cd_cmd = 'cd %s' % self.path
        untracked_file_cmd = 'git ls-files --others --exclude-standard'
        untracked_files = commands.getoutput(' && '.join((cd_cmd, untracked_file_cmd)))
        if not untracked_files:
            return ''
        return untracked_files.split('\n')
