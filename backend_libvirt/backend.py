import libvirt
from .node import LibvirtNode
import logging
import xml.etree.ElementTree as ET

class LibvirtBackend(object):
    def __init__(self, connect_uri, wan_network_name):
        self._logger = logging.getLogger(__name__)

        self._logger.info("Connecting to libvirt on %s", connect_uri)
        self._conn = libvirt.open(connect_uri)
        if self._conn == None:
            raise Exception("Could not connect to libvirt")

        self.wan_network_name = wan_network_name

    def create_node(self, image_file):
        return LibvirtNode(self._conn, image_file=image_file, wan_network_name=self.wan_network_name)

    def find_vm_by_name(self, name):
        vm = self._conn.lookupByName(name)
        if vm == None:
            raise Exception("Could not find vm")

        return vm
