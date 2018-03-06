#! /usr/bin/env python

''' Simple demo of using ANSI escape codes to move the cursor '''

import sys
from time import sleep
from string import ascii_letters

#ANSI Control Sequence Introducer
csi = '\x1b['

def put(s): sys.stdout.write(s)

#Build a simple table row
def row(c, m, n):
    return '| ' + ' | '.join(n * [m*c]) + ' |'


def main():
    #Some data to make a table with
    data = ascii_letters

    #The number of rows per table section
    numrows = 6

    #Adjust data length to a multiple of numrows
    newlen = (len(data) // numrows) * numrows
    data = data[:newlen]

    m, n = 5, 7
    width = (m + 3) * n + 4

    print 'Table'.center(width, '-')
    for i, c in enumerate(data):
        if i and not i % numrows:
            sleep(2)
            #Move cursor up by numrows
            put('%s%dA' % (csi, numrows)) 
        print "%2d %s" % (i, row(c, m, n))


if __name__ == '__main__':
    main()
