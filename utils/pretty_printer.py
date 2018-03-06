# -*- coding: utf-8 -*-
"""
Created by jiaojian at 2017/11/22 14:39
"""
from collections import defaultdict
import sys
from basic_printer import safe_convert2str


class PrettyPrinter(object):
    CSI = '\x1b['

    @classmethod
    def draw_table(cls, title, rows, refresh):
        if refresh:
            sys.stdout.write('%s%dA' % (cls.CSI, len(rows) + 1))
        column_length_map = defaultdict(int)
        lines = []
        for row in rows:
            for index, field in enumerate(row):
                field = safe_convert2str(field)
                column_length_map[index] = max(len(field), column_length_map[index])
        lines.append(title.center(sum(column_length_map.values()) + len(column_length_map) * 3 + 1, '*'))
        for row in rows:
            line = '| %s |' % ' | '.join([safe_convert2str(field).ljust(column_length_map[index]) for index, field in enumerate(row)])
            lines.append(line)
        return '\n'.join(lines)


if __name__ == '__main__':
    import time
    print PrettyPrinter.draw_table('test', [
        ['name', 'sex', 'age'],
        ['jk', 'male', 99],
        ['jkkk', 'female', 99]
    ], False)
    time.sleep(1)
    print PrettyPrinter.draw_table('test', [
        ['name', 'sex', 'age'],
        ['asd', 'fff', 12],
        ['dsa', 'femgggale', 321]
    ], True)

