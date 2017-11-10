# -*- coding: utf-8 -*-
"""
"""
import getpass
import os
import signal
import sys
import termios
import time
import argparse
import multiprocessing
from collector import collect
from command import execute_with_result
from model import ProgressMonitor
from command import Command, CommandMode
from tools.utils.counter import SafeCounter
from tools.utils.printer import print_with_style, LogLevel, ConsoleColor


STATUS_FAILED = 256
TIMEOUT_MESSAGE = 'timed out.'
STATUS_UNKNOWN = 256
MESSAGE_REFRESH_INTERVAL = 5
SLOW_THRESHOLD = 5
UNKNOWN_ERROR_TEMPLATE = 'Unknown exception: %s.'
HOME = os.environ['HOME']


def prepare_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--directory', type=str, help='Target directory.')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode.')
    parser.add_argument('--exclude-directories', type=str, help='Exclude directories(absolute path).')
    parser.add_argument(CommandMode.CLEAN, '--clean-dirty', action='store_true',
                        help='Clean dirty changes. If --auto-stash specified, this option will not work.')
    parser.add_argument(CommandMode.AUTO_STASH, '--auto-stash', action='store_true', help='Auto stash.')
    parser.add_argument(Command.UPDATE, '--update-code', action='store_true', help='Update your code by "git pull -r".')
    parser.add_argument(Command.STATUS, '--status', action='store_true', help='Show status.')
    parser.add_argument(Command.EXPORT, '--export', action='store_true', help='Export remote url of repositories.')
    parser.add_argument('-t', '--timeout', type=int, default=120, help='Timeout for update single repository.')
    parser.add_argument('-p', '--process-number', type=int, default=multiprocessing.cpu_count() * 8,
                        help='Concurrent process number.')
    parser.add_argument('--remote-host', type=str, help='Remote dev host.')
    parser.add_argument('--user', type=str, help='User name for remote dev host.')
    parser.add_argument('--local-root-path', type=str, help='Local root path for rsync.')
    parser.add_argument('--remote-root-path', type=str, help='Remote root path for rsync.')
    args = parser.parse_args()
    return args


def get_input():
    fd = sys.stdin.fileno()
    old_tty_info = termios.tcgetattr(fd)
    new_tty_info = old_tty_info[:]
    new_tty_info[3] &= ~termios.ICANON
    new_tty_info[3] &= ~termios.ECHO
    termios.tcsetattr(fd, termios.TCSANOW, new_tty_info)
    answer = os.read(fd, 1)
    termios.tcsetattr(fd, termios.TCSANOW, old_tty_info)
    return answer


def add_alias():
    if sys.platform == 'darwin':
        bash_profile_name = '.bash_profile'
    else:
        bash_profile_name = '.bashrc'
    linux_bash_profile_path = os.path.join(HOME, bash_profile_name)
    exec_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'main.py')
    alias = 'alias updateall="python %s"' % exec_file_path
    if os.path.exists(linux_bash_profile_path):
        with open(linux_bash_profile_path, 'rw') as bashrc_file:
            bash_profile = bashrc_file.read()
            if bash_profile.find(alias) >= 0:
                return
            answer = ''
            while not answer or answer not in {'y', 'n'}:
                print_with_style('Add \'%s\' to your %s?(y/n)' % (alias, bash_profile_name), color=ConsoleColor.YELLOW)
                answer = get_input()
                if answer == 'n':
                    return
                elif answer == 'y':
                    break
            bash_profile = bash_profile + '\n' + alias
        with open(linux_bash_profile_path, 'w') as bashrc_file:
            bashrc_file.write(bash_profile)
            print_with_style('Alias added.', color=ConsoleColor.YELLOW)


def init_worker():
    signal.signal(signal.SIGINT, signal.SIG_IGN)


def manage():
    # add_alias()
    start_time = time.time()
    args = prepare_args()
    directories = collect(path=args.directory)
    max_dir_length = max([len(i) for i in directories])
    exclude_dirs = []
    if args.exclude_directories:
        exclude_dirs = args.exclude_directories.split(',')
    directories = set(directories) - set(exclude_dirs)
    progress_monitor = ProgressMonitor(SafeCounter(), len(directories), max_dir_length)
    async_results = {}
    success_repos = {}
    failed_repos = {}
    process_pool = multiprocessing.Pool(min(len(directories), args.process_number), init_worker)
    command = Command.UPDATE
    tips_text = 'updated'
    user = args.user or getpass.getuser()
    if args.status:
        command = Command.STATUS
        tips_text = 'clean'
    elif args.export:
        command = Command.EXPORT
        tips_text = 'exported'
    command_mode = CommandMode.NORMAL
    if args.auto_stash:
        command_mode = CommandMode.AUTO_STASH
    elif args.clean_dirty:
        command_mode = CommandMode.CLEAN
    text = 'Running'.center(80, '*')
    print_with_style(text, color=ConsoleColor.CYAN, prefix='')
    for directory in directories:
        print_with_style('running on %s...' % os.path.basename(directory))
        current_args = (directory, command, command_mode, user, args.remote_host, args.local_root_path,
                        args.remote_root_path, args.debug)
        async_results[directory] = process_pool.apply_async(execute_with_result, args=current_args,
                                                            callback=progress_monitor.increment)

    for directory in async_results:
        start = time.time()
        last_update = start
        current_time = start
        while time.time() - start < args.timeout and not async_results[directory].ready():
            async_results[directory].wait(0.1)
            cost = current_time - start
            if cost > SLOW_THRESHOLD and current_time - last_update > MESSAGE_REFRESH_INTERVAL:
                last_update = current_time
                progress_monitor.update_display_text(directory, cost, too_slow=True)
            current_time = time.time()
        try:
            result = async_results[directory].get(timeout=0.1)
            status, message, cost = result.status, result.message, result.cost
        except multiprocessing.TimeoutError:
            status, message, cost = STATUS_FAILED, TIMEOUT_MESSAGE, args.timeout
        except Exception as e:
            status, message, cost = STATUS_UNKNOWN, UNKNOWN_ERROR_TEMPLATE % e.message, None
        if status:
            failed_repos[directory] = message
        else:
            success_repos[directory] = message

    print_with_style('', color=ConsoleColor.GREEN)
    text = 'Completed'.center(80, '*')
    print_with_style(text, color=ConsoleColor.CYAN, prefix='')
    text = '%s/%s %s.' % (len(success_repos), len(directories), tips_text)
    print_with_style(text, color=ConsoleColor.GREEN, prefix=LogLevel.INFO)
    if failed_repos:
        text = 'Failed Repository'.center(80, '*')
        print_with_style(text, color=ConsoleColor.CYAN, prefix='')
    for directory in failed_repos:
        text = os.path.basename(directory).center(80, '-')
        print_with_style(text, color=ConsoleColor.CYAN, prefix='')
        text = '%s: %s\n%s' % (os.path.basename(directory), directory, failed_repos[directory])
        print_with_style(text, color=ConsoleColor.RED, prefix=LogLevel.ERROR)
    text = '%s repositories finished in %.2fs.' % (len(directories), time.time() - start_time)
    print_with_style(text, color=ConsoleColor.GREEN)
