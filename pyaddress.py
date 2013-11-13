#!/usr/bin/env python3

import argparse
import os
import email
import re
import itertools as it
import yaml
import difflib
import tempfile
import subprocess as sp

ADDR = 'buddies'
CUTOFF=0.8
DL = 0

class DB(dict):
    def __init__(self,db=None):
        if db is not None:
            self[ADDR] = db.copy()
        else:
            self[ADDR] = []
        self.__to_print__ = ['email','name','nick']
    def item_len(self):
        self.max_len = {}
        for k in self.__to_print__:
            self.max_len[k] = 0
        for entry in self[ADDR]:
            for k in self.__to_print__:
                if k == 'email':
                    maxl = max([len(em) for em in entry[k]])
                else:
                    maxl = len(entry[k])
                if maxl > self.max_len[k]:
                    self.max_len[k] = maxl

def check_file(filename):
    try:
        with open(filename):
            pass
    except IOError:
        print('The file {0} doesn\'t exist'.format(filename))
        exit(1)

def read_datafile(filename,db_type):
    datafile = os.path.expanduser(filename)
    check_file(datafile)
    if db_type == 'yaml':
        with open(datafile,'r') as fin:
            db_loc = yaml.load(fin)
        db = db_loc[ADDR]
    elif db_type == 'abook':
        db = read_datafile_abook(datafile)
    return DB(db)

def read_datafile_abook(filename):
    db = []
    with open(filename,'r') as fin:
        e_id = None
        for line in fin:
            line = line.strip()
            if len(line)>0:
                char = line[0]
                if char in ['#']:
                    continue
                elif char == '[':
                    # Add old entry to database
                    if e_id != 'format' and e_id is not None:
                        db.append(entry)

                    # initialize new entry
                    e_id = line.strip('[]')
                    entry = {}
                else:
                    # add item to entry
                    attr, val = line.split('=',1)
                    if attr == 'email':
                        item = [v.strip() for v in val.split(',')]
                    else:
                        item = val.strip()
                    entry[attr] = item

        # Add last entry to database
        if entry != {}:
            db.append(entry)
    return db

def fuzzy_match(s1, s2, dl=DL,cutoff=CUTOFF):
    match = []
    if len(s1) >= len(s2)+dl:
        match.append(difflib.SequenceMatcher(None,s1,s2).ratio())
    else:
        for n in range(len(s2)-dl+1-len(s1)):
            s3 = s2[n:len(s1)+dl+n]
            match.append(difflib.SequenceMatcher(None,s1,s3).ratio())
    return max(match)

def fuzzy_match_entry(string, entry ,keys, cutoff=CUTOFF):
    match = [0]
    for k in keys:
        if k in entry.keys():
            if k == 'email':
                for em in entry[k]:
                    match.append(fuzzy_match(string,em,dl=DL,cutoff=CUTOFF))
            elif type(entry[k]) == str:
                    match.append(fuzzy_match(string,entry[k],dl=DL,cutoff=CUTOFF))
    return max(match) > cutoff

def get_emails(db):
    ems = []
    for e in db[ADDR]:
        ems = ems + e['email']
    return ems

def get_list_to_print(db,limit=None,lens=False):
    l = []
    for e in db[ADDR]:
        if limit is None or fuzzy_match_entry (limit, e, db.__to_print__):
            if 'email' in db.__to_print__ and 'email' in e.keys():
                for em in e['email']:
                    loc = []
                    for k in db.__to_print__:
                        if k == 'email':
                            loc.append(em)
                        elif k in e.keys():
                            loc.append(str(e[k]))
                        else:
                            loc.append('')
                    l.append(loc)
            else:
                loc = []
                for k in db.__to_print__:
                    if k in e.keys():
                        loc.append(str(e[k]))
                    else:
                        loc.append('')
                l.append(loc)
    if lens:
        mlen = [1]*len(db.__to_print__)
        for ll in l:
            mlen = [max(len(_ll),_mlen) for _ll,_mlen in zip(ll,mlen)]
        return l,mlen
    return l

def print_db(db,limit=None):
    l,max_len = get_list_to_print(db,limit,lens=True)

    for ll in l:
        s = ''
        for lll,mlen in zip(ll,max_len):
            s = s + '{0:{1}} '.format(lll,mlen)
        print (s)
            
def write_db(db,filename='~/.abook/addressbook.yaml'):
    datafile = os.path.expanduser(filename)
    loc_db={}
    loc_db[ADDR] = db[ADDR]
    with open(datafile,'w') as fout:
        yaml.dump(loc_db,fout)

def merge_dbs(db1, db2):
    raise NotImplementedError()
    pass

def merge_entries(db, e1, e2):
    raise NotImplementedError()
    pass

def get_sender_address(email):
    raise NotImplementedError()
    pass

def get_all_addresses(email):
    raise NotImplementedError()
    pass

def add_sender(email,db):
    s = sys.stdin.read()
    msg = email.message_from_string(s)
    ss = msg['From']
    ss = ss.split('<')
    ss = [_ss.strip(' <>\t\n"') for _ss in ss]
    if len(ss) == 1:
        ss = ['']+ ss

    entry = {'name':ss[0], 'email':ss[1]}
    return entry

def add_all(email,db):
    raise NotImplementedError()
    pass

def edit_entry(entry={'name':'', 'email':['','']}):
    # prepare tmp file
    tmpf = tempfile.NamedTemporaryFile(prefix='address-entry')

    # prepare template
    document = yaml.dump(entry, default_flow_style=False)
    document = '# Edit this, save and exit\n' + document
    tmpf.write(bytes(document, 'UTF-8'))
    tmpf.flush()

    # open with $EDITOR
    editor = os.environ['EDITOR']
    sp.call([editor,tmpf.name])

    # read it
    tmpf.seek(0)
    new_entry = yaml.load(tmpf)
    tmpf.close()

    return new_entry

def clear_screen():
    os.system('cls' if os.name=='nt' else 'clear')

def main():
    parser = argparse.ArgumentParser(description='Python Address Book')
    parser.add_argument('--datafile',default='~/.addressbook.yaml',\
                        help='Use an alternative addressbook file (default \
                        is $HOME/.addressbook.yaml).')
    parser.add_argument('-d','--duplicates', action='store_true',\
                        help='Find duplicates and merge them (Interactive)')
    parser.add_argument('-p','--print-db', action='store_true',\
                        help='Print database content to stdout')
    parser.add_argument('-q','--mutt-query', metavar='STRING',default=None,\
                        help='Find address in addressbook')
    parser.add_argument('--add-email',action='store_true',\
                        help='Read an e-mail message from stdin and add the sender to the addressbook.')
    parser.add_argument('--add-all-emails',action='store_true',\
                        help='Read an e-mail message from stdin and add\
                        addresses in headers to the addressbook.')
    parser.add_argument('--db-type', default='yaml',\
                        help='addressbook type (default = YAML)')

    args = parser.parse_args()

    db = read_datafile(args.datafile,args.db_type)
    is_changed = False
    if args.print_db:
        print_db(db)
    elif args.duplicates:
        db.find_duplicates()
        is_changed = True
    elif args.mutt_query is not None:
        print_db(db,limit=args.mutt_query)

    if is_changed:
        write_db(db,filename='~/.abook/addressbook.yaml')

if __name__ == '__main__':
    main()
