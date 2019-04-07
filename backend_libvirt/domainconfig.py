import xml.etree.ElementTree as ET

class DomainConfig(object):
    def __init__(self, image_path, name):
        self.name = name
        self.mem = 128 * 1024
        self.image_path = image_path
        self._interfaces = []

    def add_interface_in_network(self, source_network_name):
        self._interfaces.append({
            'network_name': source_network_name
        })

    def generate_xml(self):
        self._xml_root = ET.Element('domain', {'type': 'kvm'})
        ET.SubElement(self._xml_root, 'name').text = self.name
        ET.SubElement(self._xml_root, 'memory').text = str(self.mem)
        self._create_os_config()

        self._xml_devices = ET.SubElement(self._xml_root, 'devices')
        self._create_disk()
        self._create_interfaces()
        ET.SubElement(self._xml_devices, 'console', {'type': 'pty'})

        return ET.tostring(self._xml_root).decode('utf-8')

    def _create_os_config(self):
        os = ET.SubElement(self._xml_root, 'os')
        ET.SubElement(os, 'type', {'arch': 'x86_64', 'machine': 'pc'}).text = 'hvm'
        ET.SubElement(os, 'boot', {'dev': 'hd'})

    def _create_disk(self):
        disk = ET.SubElement(self._xml_devices, 'disk', {
            'type': 'file',
            'device': 'disk'
        })
        ET.SubElement(disk, 'source', {'file': self.image_path})
        ET.SubElement(disk, 'driver', {'name': 'qemu', 'type': 'qcow2'})
        ET.SubElement(disk, 'target', {'dev': 'hda'})

    def _create_interfaces(self):
        for if_info in self._interfaces:
            if_xml = ET.SubElement(self._xml_devices, 'interface', {'type': 'network'})
            ET.SubElement(if_xml, 'source', {'network': if_info['network_name']})

