#!/usr/bin/env python

"""This script will update a vEOS virtual machine to a different vEOS image.

It leverages a few different modules, so please make sure they are installed prior to running - you
can use pip install -r requirements.txt to do that.

It also requires a user with privilege 15 access and http transport, and does not support an enable
password at this time.

Example:
    ./veos-update.py -u admin -i 192.168.56.10 -s vEOS-lab-4.15.6M.swi

"""


from getpass import getpass
import difflib
import pyeapi
import argparse
from paramiko import SSHClient
from scp import SCPClient
from datetime import datetime
import sys

# TODO: Enable password
parser = argparse.ArgumentParser(description='Upgrades a virtual machine running vEOS to another .swi version.')
parser.add_argument('-u', '--user', type=str, help='vEOS Username - must have privilege 15', required=True)
parser.add_argument('-i', '--ip', type=str, help='vEOS IP Address', required=True)
parser.add_argument('-s', '--swi', type=str, help='SWI Image', required=True)
args = parser.parse_args()

password = getpass("Enter your vEOS Password: ")

# TODO: Figure out HTTPS access, enable passwords
def connect():
    """Connects to pyeapi using http transport and creates a node from it (required for
    enable commands."""
    node = pyeapi.connect(host=args.ip, password=password, return_node=True)
    return node


def config_diff(node):
    """Diffs the running-config and the startup-config. Requires a node as input
    so it can connect and get the configuration."""
    running = node.get_config(config="running-config")
    startup = node.get_config(config="startup-config")

    diff = difflib.unified_diff(running, startup)
    for line in diff:
        if 'boot' in line:
            for line in diff:
                print(line)


def config_backup(node):
    """Backs up the startup-configuration to a file with the IP address and timestamp
    in the filename. Takes node as input to get the configuration"""
    startup = str(node.get_config(config="startup-config"))
    dt = datetime.now().strftime("%Y%m%d-%H%M%S")
    file = args.ip + '-startup-config-' + dt
    f = open(file, 'w')
    f.write(startup)
    f.close()
    print "\n\nBacked up the current startup-config to " + file + ".\n"


def config_write(node):
    """Copies the running-config to the startup-config. Takes node as input to issue
    the copy command."""
    question = str(raw_input('Save configuration as shown? y/n: ')).lower().strip()
    while not question in ['y','n']:
        question = str(raw_input('Save configuration as shown? y/n: ')).lower().strip()
    if question == 'y':
        node.enable('copy running-config startup-config')
        config_backup(node)
        print "Writing configuration."
    if question == 'n':
        print "Aborting script."
        sys.exit()


def reload(node):
    """Reloads the switch. Note that "reload force" is required - normal reload requires user input.
    Takes node as input to issue the reload command."""
    question = str(raw_input('Reload now? y/n: ')).lower().strip()
    while not question in ['y','n']:
        question = str(raw_input('Save configuration as shown? y/n: ')).lower().strip()
    if question == 'y':
        node.enable('reload force')
        print "Reloading vEOS."
    if question == 'n':
        print "Aborting script. Please reload the switches for changes to take effect."
        sys.exit()


def scp(file, path):
    """Uses paramiko and scp module built on top of it to SCP vEOS to the VM.
    Inputs are the .swi filename from arguments, and a path."""
    ssh = SSHClient()
    ssh.load_system_host_keys()
    ssh.connect(hostname=args.ip, username=args.user, password=password)
    scp = SCPClient(ssh.get_transport())
    print "\nWriting " + file + " to " + path
    scp.put(file, remote_path=path)
    scp.close()


def config_boot(node):
    """Configures the boot parameter. Note that it doesn't require a save of the configuration.
    Takes node as an input to issue the commad."""
    node.config(('boot system flash:/' + args.swi))


def main():
    node = connect()
    config_diff(node)
    config_write(node)
    scp(args.swi, '/mnt/flash/')
    config_boot(node)
    reload(node)


if __name__ == "__main__":
    main()
