import libvirt
from .networkconfig import IsolatedNetworkConfig
from .domainconfig import DomainConfig
import logging
import xml.etree.ElementTree as ET
import subprocess
import tempfile
import os
import random
import string

class LibvirtNode(object):
    def __init__(self, libvirt_conn, image_file, wan_network_name):
        self._conn = libvirt_conn
        self._logger = logging.getLogger(__name__)
        self._client_net = None
        self.image_file = image_file
        self.wan_network_name = wan_network_name
        self.delete_transient_image = True
        self._generate_random_name()

    def _generate_random_name(self):
        random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        self.name = 'gluon-node-{}'.format(random_str)

    def create_client_network(self):
        if self._client_net:
            raise Exception("Client network already created")

        client_cfg = IsolatedNetworkConfig()

        self._client_net = self._conn.networkCreateXML(client_cfg.generate_xml())
        if self._client_net == None:
            raise Exception("Could not create client network")

        self._logger.info("Created client network %s", self._client_net.name())

    def start(self):
        self._make_transient_image_copy()

        dc = DomainConfig(image_path=self.transient_image_file, name=self.name)
        dc.add_interface_in_network(self.wan_network_name)
        dc.add_interface_in_network(self._client_net.name())
        config_xml = dc.generate_xml()

        self._dom = self._conn.createXML(config_xml, 0)
        if self._dom == None:
            raise Exception('Failed creating domain')
        self._logger.info("Created node domain %s", self._dom.name())

    def stop(self):
        self._dom.destroy()
        self._logger.info("Destroyed node domain %s", self._dom.name())

    def __enter__(self):
        self.create_client_network()
        self.start()

    def __exit__(self, type, value, traceback):
        self.stop()

        if self.delete_transient_image:
            os.remove(self.transient_image_file)

        return False

    def _make_transient_image_copy(self):
        self.transient_image_file = os.path.abspath(self.name + '-transient.qcow2')
        subprocess.check_call(['qemu-img', 'convert', '-O', 'qcow2', self.image_file, self.transient_image_file])

    """
    Attach a running VM to this node's client network
    """
    def attach_vm_to_client_network(self, vm, vm_interface_mac):
        vm_xml = ET.fromstring(vm.XMLDesc())

        interfaces = vm_xml.findall("./devices/interface/mac[@address='{}']/..".format(vm_interface_mac))
        if len(interfaces) != 1:
            raise Exception("Interface MAC {} did not yield any or more than one result".format(interface_mac))

        interface = interfaces[0]
        interface.find('source').set('network', self._client_net.name())

        vm.updateDeviceFlags(ET.tostring(interface).decode('utf-8'), libvirt.VIR_DOMAIN_AFFECT_LIVE)
        self._logger.info("Attached VM %s to virtual network %s", vm.name(), self._client_net.name())
