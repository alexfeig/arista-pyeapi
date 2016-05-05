#!/usr/bin/env python

from getpass import getpass
import difflib
import pyeapi
import argparse
from paramiko import SSHClient
from scp import SCPClient
from datetime import datetime

# Gathers command line arguments.
# TODO: Enable password
parser = argparse.ArgumentParser(description='Upgrades a virtual machine running vEOS to another .swi version.')
parser.add_argument('-u', '--user', type=str, help='vEOS Username - must have privilege 15', required=True)
parser.add_argument('-i', '--ip', type=str, help='vEOS IP Address', required=True)
parser.add_argument('-s', '--swi', type=str, help='SWI Image', required=True)
args = parser.parse_args()

# Gathers password.
password = getpass("Enter your vEOS Password: ")


def connect():
    node = pyeapi.connect(host=args.ip, password=password, return_node=True)
    return node


def diff(node):
    running = node.get_config(config="running-config")
    startup = node.get_config(config="startup-config")

    diff = difflib.unified_diff(running, startup)
    for line in diff:
        print(line)

## TODO: Need to figure out how to go back to asking question if neither y or n is entered.
def write_config(node):
    overwrite = str(raw_input('Save configuration as shown? y/n: ')).lower().strip()
    if overwrite == 'y':
        node.enable('copy running-config startup-config')
        print "Writing configuration."
    elif overwrite == 'n':
        print "Aborting script."
    else:
        print "Aborting script. Please enter y or n."


def backup_config(node):
    startup = str(node.get_config(config="startup-config"))
    dt = datetime.now().strftime("%Y%m%d-%H%M%S")
    file = args.ip + '-startup-config-' + dt
    f = open(file,'w')
    f.write(startup)
    f.close()
    print "\n\nBacked up the current startup-config to " + file + ".\n"


def main():
    node = connect()
    diff(node)
    backup_config(node)
    write_config(node)


if __name__ == "__main__":
    main()
