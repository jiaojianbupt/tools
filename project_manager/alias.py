# -*- coding: utf-8 -*-
"""
Created by jiaojian at 2018/6/29 16:30
"""
import os
import sys
import termios
from tools.utils.basic_printer import print_with_style, ConsoleColor
HOME = os.environ['HOME']


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
