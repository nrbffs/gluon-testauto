#!/usr/bin/python3

import argparse
import configparser
import sys
import logging
from backend_libvirt.backend import LibvirtBackend

ap = argparse.ArgumentParser()
ap.add_argument('config_file', type=argparse.FileType('r'))
args = ap.parse_args()

logging.basicConfig(level=logging.INFO)


config = configparser.ConfigParser()
config.read_file(args.config_file)

backend = LibvirtBackend(connect_uri=config['libvirt']['connect_uri'],
        wan_network_name=config['wan_network']['name'])
test_node = backend.create_node(image_file='/home/nrb/ffs-fw-ci/test.img')
with test_node:
    client_vm = backend.find_vm_by_name(config['client_vm']['name'])
    test_node.attach_vm_to_client_network(client_vm, config['client_vm']['client_interface_mac'])

    sys.stdin.readline()
