#!/usr/bin/env python3

import argparse
import os

def read_datafile(filename):
    datafile = os.path.expanduser(filename)
    db = {}
    try:
        with open(datafile) as fin:
            new_cod = None
            for line in fin:
                char = line[0]
                if char in ['#','"']:
                    continue
                elif char == '[':
                    new_cod = line.strip().strip('[]')
                    if new_cod != 'format':
                        new_cod = int(new_cod)
                        db[new_cod] = dict()
                elif type(new_cod) == int and line.strip() != '':
                    attr, val = line.split('=',1)
                    if len(val.split(',')) > 1:
                        db[new_cod][attr]=[v.strip() for v in val.split(',')]
                    else:
                        db[new_cod][attr]=val.strip()
    except IOError:
        print ('Datafile {} don\'t exist'.format(filename))
    return db

def print_db(db):
    for k in db:
        if 'name' in db[k].keys() and 'email' in db[k].keys():
            print ('{0:>20s}: {1:<20s}'.format(db[k]['name'],db[k]['email']))
    return 0

def main():
    parser = argparse.ArgumentParser(description='Python Address Book')
    parser.add_argument('--datafile',default='~/.abook/addressbook',\
                        help='Use an alternative addressbook file (default is $HOME/.abook/addressbook).')
    parser.add_argument('-d','--duplicate', action='store_true',\
                        help='Find duplicate and merge them (Interactive)')
    parser.add_argument('-p','--print-db', action='store_true',\
                        help='Print database content to stdout')


    args = parser.parse_args()

    print (args)
    db = read_datafile(args.datafile)
    if args.print_db:
        print_db(db)

if __name__ == '__main__':
    main()
