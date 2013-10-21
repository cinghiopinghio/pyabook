#!/usr/bin/env python3

import argparse
import os
import email
import re

class Entry(dict):
    def __init__ (self):
        self = {'name':'','email':''}
    def set(self,key,value):
        self[key] = value
    def __str__(self):
        return "{0} <{1}>".format(self['name'],self['email'])
    def __eq__(self,other):
        name1 = set(self['name'].lower().split())
        name2 = set(other['name'].lower().split())
        return self['email'] == other['email'] or name1 == name2

class Databook(dict):
    def __init__(self):
        #self.entries = {}
        self.format = {}
        self.max_len = {}
    def set(self,key,value):
        self[key]=value
    def set_format(self,values):
        self.format = values
    def find_duplicates(self):
        merges = 0
        for id1,e1 in self.items():
            for id2,e2 in self.items():
                if id1 > id2:
                    if e1 == e2:
                        print (id1,id2,e1,e2)
                        self.merge(id1,id2)
                        merges += 1
        #if merge > 0:
        #    self.find_duplicates()
    def merge(self,id1,id2):
        pass


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
                    # Add old entry to database
                    if new_cod == 'format':
                        db.set_format(entry)
                    elif new_cod is not None:
                        db.set(int(new_cod),entry)

                    # get new id code
                    new_cod = line.strip().strip('[]')

                    # initialize new entry
                    entry = Entry()
                elif line.strip() != '':
                    # add item to entry
                    attr, val = line.split('=',1)
                    if attr == 'email':
                        vset = set([v.strip() for v in val.split(',')])
                        entry.set(attr,vset)
                        max_l = max([len(v) for v in vset])
                    else:
                        entry.set(attr,val.strip())
                        max_l = len(val.strip())
                    if attr not in db.max_len.keys():
                        db.max_len[attr] = max_l
                    elif db.max_len[attr] < max_l:
                        db.max_len[attr] = max_l
            # Add last entry to database
            if new_cod == 'format':
                db.set_format(entry)
            elif new_cod is not None:
                db.set(int(new_cod),entry)
    except IOError:
        print ('Datafile {} don\'t exist'.format(filename))
    return db

def print_db(db,limit=None):
    for k in db.keys():
        ems = db[k].item['email']
        if type(ems) == str:
            ems = [ems]
        for em in ems:
            max_mail = db.max_len['email']
            max_name = db.max_len['name']
            mail = '<'+em+'>'
            name = db[k].item['name']
            line = '{0:>{1}s} {2:{3}s}'.format(name,max_name,mail,max_mail)
            if limit is None:
                print (line)
            elif re.search(limit, line, flags=re.I|re.A):
                print (line)
    return 0

def get_sender_address(email):
    pass

def get_all_addresses(email):
    pass

def add_sender(email,db):
    pass

def add_all(email,db):
    pass

def main():
    parser = argparse.ArgumentParser(description='Python Address Book')
    parser.add_argument('--datafile',default='~/.abook/addressbook',\
                        help='Use an alternative addressbook file (default is $HOME/.abook/addressbook).')
    parser.add_argument('-d','--duplicates', action='store_true',\
                        help='Find duplicates and merge them (Interactive)')
    parser.add_argument('-p','--print-db', action='store_true',\
                        help='Print database content to stdout')
    parser.add_argument('--mutt-query', metavar='STRING',default=None,\
                        help='Find address in addressbook')
    parser.add_argument('--add-email',action='store_true',\
                        help='Read an e-mail message from stdin and add the sender to the addressbook.')
    parser.add_argument('--add-all-emails',action='store_true',\
                        help='Read an e-mail message from stdin and add\
                        addresses in headers to the addressbook.')

    args = parser.parse_args()

    db = read_datafile(args.datafile)
    if args.print_db:
        print_db(db)
    elif args.duplicates:
        db.find_duplicates()
    elif args.mutt_query is not None:
        print_db(db,limit=args.mutt_query)

if __name__ == '__main__':
    main()
