#!/usr/bin/env python3

import argparse
import os

class Entry():
    def __init__ (self):
        self.item={'name':'','email':''}
    def set(self,key,value):
        self.item[key]=value
    def __str__(self):
        return "{0} <{1}>".format(self.item['name'],self.item['email'])

class Databook():
    def __init__(self):
        self.entries = {}
        self.format = {}
        self.max_len = {}
    def set(self,key,value):
        self.entries[key]=value
    def set_format(self,values):
        self.format = values

def read_datafile(filename):
    datafile = os.path.expanduser(filename)
    db = Databook()
    try:
        with open(datafile) as fin:
            new_cod = None
            for line in fin:
                char = line[0]
                if char in ['#','"']:
                    continue
                elif char == '[':
                    if new_cod == 'format':
                        db.set_format(entry)
                    elif new_cod is not None:
                        db.set(int(new_cod),entry)

                    new_cod = line.strip().strip('[]')

                    entry = Entry()
                elif line.strip() != '':
                    attr, val = line.split('=',1)
                    if len(val.split(',')) > 1:
                        entry.set(attr,[v.strip() for v in val.split(',')])
                    else:
                        entry.set(attr,val.strip())
    except IOError:
        print ('Datafile {} don\'t exist'.format(filename))
    return db

def print_db(db):
    for k in db.entries:
        #print ('{0:>20s}: {1:<20s}'.format(db.entries[k].item['name'],db.entries[k].item['email']))
        print (db.entries[k])
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
