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
from tools.utils.basic_printer import print_with_style, LogLevel, ConsoleColor


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


def init_worker():
    signal.signal(signal.SIGINT, signal.SIG_IGN)


def concurrent_run(directories, command, command_mode, args, tips_text, user):
    start_time = time.time()
    async_results = {}
    success_repos = {}
    failed_repos = {}
    max_dir_length = max([len(i) for i in directories])
    progress_monitor = ProgressMonitor(SafeCounter(), len(directories), max_dir_length)
    process_pool = multiprocessing.Pool(min(len(directories), args.process_number), init_worker)
    print_with_style('Running'.center(80, '*'), color=ConsoleColor.CYAN, prefix='')
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
    return success_repos, failed_repos


def manage():
    # add_alias()
    args = prepare_args()
    directories = collect(path=args.directory)
    exclude_dirs = []
    if args.exclude_directories:
        exclude_dirs = args.exclude_directories.split(',')
    directories = set(directories) - set(exclude_dirs)

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
    success_repos, failed_repos = concurrent_run(directories, command, command_mode, args, tips_text, user)
    print success_repos
