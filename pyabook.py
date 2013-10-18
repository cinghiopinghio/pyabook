#!/usr/bin/env python3

import argparse

def main():
    print('pyabook')
    parser = argparse.ArgumentParser(description='Python Address Book')
    parser.add_argument('--datafile', action='store_const',\
                        const='~/.abook/addressbook',\
                        help='Use an alternative addressbook file (default is $HOME/.abook/addressbook).')
    parser.add_argument('-d','--duplicate', action='store_true',\
                        help='Find duplicate and merge them (Interactive)')

    args = parser.parse_args()
    print(args.accumulate(args.integers))

if __name__ == '__main__':
    main()
