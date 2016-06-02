#!/usr/bin/env python

"""This script will update a vEOS virtual machine to a different vEOS image.

It leverages a few different modules, so please make sure they are installed prior to running - you
can use pip install -r requirements.txt to do that.

It also requires a user with privilege 15 access and https transport, and does not support an enable
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


def get_args():
    parser = argparse.ArgumentParser(description='Upgrades a virtual machine running vEOS to another .swi version.')
    parser.add_argument('-u', '--user',
                        type=str,
                        help='vEOS Username - must have privilege 15',
                        required=True)
    parser.add_argument('-i', '--ip',
                        type=str,
                        help='vEOS IP Address',
                        required=True)
    parser.add_argument('-s', '--swi',
                        type=str,
                        help='SWI Image',
                        required=True)
    args = parser.parse_args()
    return args


def config_diff(node):
    """Diffs the running-config and the startup-config.

    Requires node to set the device."""
    running = node.get_config(config="running-config")
    startup = node.get_config(config="startup-config")

    diff = difflib.unified_diff(running, startup)
    for line in diff:
        if 'boot' in line:
            for line in diff:
                print(line)


def config_write(node, ip):
    """Copies the running-config to the startup-config.

    Requires node to set the device.
    Requires IP to backup the configuration."""
    question = str(raw_input('Save configuration as shown? y/n: ')).lower().strip()
    while not question in ['y', 'n']:
        question = str(raw_input('Save configuration as shown? y/n: ')).lower().strip()
    if question == 'y':
        node.enable('copy running-config startup-config')
        config_backup(node, ip)
        print "Writing configuration."
    if question == 'n':
        print "Aborting script."
        sys.exit()


def config_backup(node, ip):
    """Backs up the startup-configuration to a file with the IP address and timestamp
    in the filename.

    Requires node to set the device.
    Requires IP to set the filename for the backup file."""
    startup = str(node.get_config(config="startup-config"))
    dt = datetime.now().strftime("%Y%m%d-%H%M%S")
    file = ip + '-startup-config-' + dt
    f = open(file, 'w')
    f.write(startup)
    f.close()
    print "\n\nBacked up the current startup-config to " + file + ".\n"


def reload(node):
    """Reloads the switch. Note that "reload force" is required - normal reload requires user input.

    Requires node to set the device."""
    question = str(raw_input('Reload now? y/n: ')).lower().strip()
    while not question in ['y', 'n']:
        question = str(raw_input('Save configuration as shown? y/n: ')).lower().strip()
    if question == 'y':
        node.enable('reload force')
        print "Reloading vEOS."
    if question == 'n':
        print "Aborting script. Please reload the switches for changes to take effect."
        sys.exit()


def scp(file, path, ip, user, password):
    """Uses paramiko and scp module built on top of it to SCP vEOS to the VM.

    Requires filename to set the SWI image.
    Requires path to set the path to copy the file to on the remote system (hardcoded to /mnt/flash).
    Requires user for the SCP username.
    Requires password for the SCP password."""
    ssh = SSHClient()
    ssh.load_system_host_keys()
    ssh.connect(hostname=ip, username=user, password=password)
    scp = SCPClient(ssh.get_transport())
    print "\nWriting " + file + " to " + path
    scp.put(file, remote_path=path)
    scp.close()


def config_boot(node, swi):
    """Configures the boot parameter. Note that it doesn't require a save of the configuration.

    Requires node to set the device.
    Requires swi to set the boot variable to the new image"""
    node.config(('boot system flash:/' + swi))


def main():
    args = get_args()

    password = getpass("Enter your vEOS Password: ")

    node = pyeapi.connect(host=args.ip, password=password, return_node=True)
    config_diff(node)
    config_write(node, args.ip)
    scp(args.swi, '/mnt/flash/', args.ip, args.user, password)
    config_boot(node, args.swi)
    reload(node)


if __name__ == "__main__":
    main()
