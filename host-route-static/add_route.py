#!/usr/bin/env python

"""This script creates static host routes based on user inputs.
Please don't use this in production without testing"""

# TODO: Authentication? nodes.conf vs prompt for username/password
# TODO: Multiple switches per side
# TODO: Make nexthop not hard coded in function add_route

from __future__ import print_function

import pyeapi
import argparse
import sys
from getpass import getpass


def get_args():
    parser = argparse.ArgumentParser(description='Configures a static host route (/32).')
    parser.add_argument('-u', '--user',
                        type=str,
                        help='vEOS Username - must have privilege 15',
                        required=True)
    parser.add_argument('-s', '--side',
                        type=str,
                        help='Switch side to configure host route.',
                        required=True)
    parser.add_argument('-ho', '--host',
                        type=str,
                        help='Host to create host route for. A /32 is appended to this IP to create a static route.',
                        required=True)
    args = parser.parse_args()
    return args


def get_side(side):
    ip = '192.168.56.10' if side == 'right' else '192.168.56.11' if side == 'left' else sys.exit('Invalid side.')
    return ip


def add_route(node, hr):
    routes = node.api('staticroute')

    hostroute = hr + '/32'

    routes.create(hostroute, '12.12.12.12')

    print('Creating a host route for', hostroute)


def main():
    args = get_args()

    ip = get_side(args.side)

    password = getpass("Enter your vEOS Password: ")

    node = pyeapi.connect(host=ip, password=password, return_node=True)

    add_route(node, args.host)


if __name__ == "__main__":
    main()
