#!/usr/bin/env python

import getpass
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
password = getpass.getpass("vEOS Password: ")

# Note - if you don't use return_node=True, enable is not available.
# See https://github.com/arista-eosplus/pyeapi/blob/develop/pyeapi/client.py#L386
# Also see https://github.com/arista-eosplus/pyeapi/issues/37
# Let's start by connecting to the vEOS VM
node = pyeapi.connect(host=args.ip,password=password,return_node=True)

# Copy running-config to startup-config
# TODO: Diff run/start and prompt to save.
node.enable('copy running-config startup-config')

ssh = SSHClient()
# If you don't do this below, it won't accept the host key.
ssh.load_system_host_keys()
# Connect to SSH
ssh.connect(hostname=args.ip,username=args.user,password=password)
# Paramiko - set transport to SSH
scp = SCPClient(ssh.get_transport())

# Backup Config
# TODO: Add exception here to catch non priv15.
datetime = datetime.now().strftime("%Y%m%d-%H%M%S")
scp.get('/mnt/flash/startup-config',args.ip + '-startup-config-' + datetime)

# Copy SWI Image
# TODO: Add in some sort of feedback here so folks know it's copying the file. Also, add error handling
scp.put(args.swi,remote_path='/mnt/flash/')

node.config(('boot system flash:/'+args.swi))

scp.close()

# If force isn't used, API will not allow for a reload.
node.enable('reload force')