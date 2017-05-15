# -*- coding: utf-8 -*-
"""
"""
import os
import sys
import termios
import argparse
import multiprocessing
from collector import collect
from command import update
from model import ProgressMonitor
from tools.utils.counter import SafeCounter
from tools.utils.printer import print_with_style, LogLevel, ConsoleColor


STATUS_FAILED = 256
TIMEOUT_MESSAGE = 'timeout.'
STATUS_UNKNOWN = 256
UNKNOWN_ERROR_TEMPLATE = 'Unknown exception: %s.'
HOME = os.environ['HOME']


def prepare_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--directory', type=str, help='Target directory.')
    parser.add_argument('-c', '--clean-dirty', action='store_true', help='Clean dirty changes.')
    parser.add_argument('-u', '--update-code', action='store_true', help='Update your code by "git pull -r".')
    parser.add_argument('-t', '--timeout', type=int, default=60, help='Timeout for update single repository.')
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
    alias = 'alias updateall="python %s "' % exec_file_path
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


def manage():
    add_alias()
    args = prepare_args()
    directories = collect(path=args.directory)
    progress_monitor = ProgressMonitor(SafeCounter(), len(directories))
    async_results = {}
    success_repos = {}
    failed_repos = {}
    process_pool = multiprocessing.Pool(multiprocessing.cpu_count())
    text = 'Running'.center(80, '*')
    print_with_style(text, color=ConsoleColor.CYAN, prefix='')
    for directory in directories:
        print 'updating %s...' % os.path.basename(directory)
        async_results[directory] = process_pool.apply_async(update, args=(directory, args.clean_dirty),
                                                            callback=progress_monitor.increment)

    for directory in async_results:
        try:
            status, message = async_results[directory].get(timeout=args.timeout)
        except multiprocessing.TimeoutError:
            status, message = STATUS_FAILED, TIMEOUT_MESSAGE
        except Exception as e:
            status, message = STATUS_UNKNOWN, UNKNOWN_ERROR_TEMPLATE % e.message
        if status:
            failed_repos[directory] = message
        else:
            success_repos[directory] = message
    print_with_style('', color=ConsoleColor.GREEN)
    text = 'Completed'.center(80, '*')
    print_with_style(text, color=ConsoleColor.CYAN, prefix='')
    text = '%s/%s updated.' % (len(success_repos), len(directories))
    print_with_style(text, color=ConsoleColor.GREEN, prefix=LogLevel.INFO)
    if failed_repos:
        text = 'Failed Repository'.center(80, '*')
        print_with_style(text, color=ConsoleColor.CYAN, prefix='')
    for directory in failed_repos:
        text = os.path.basename(directory).center(80, '-')
        print_with_style(text, color=ConsoleColor.CYAN, prefix='')
        text = '%s: %s\n%s' % (os.path.basename(directory), directory, failed_repos[directory])
        print_with_style(text, color=ConsoleColor.RED, prefix=LogLevel.ERROR)
