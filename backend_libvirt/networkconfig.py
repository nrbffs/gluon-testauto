import random
import string
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod

class AbstractNetworkConfig(ABC):
    def __init__(self, name=None):
        self.name = self._generate_random_name() if name is None else name

    def _generate_random_name(self):
        random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        return 'gluon-{}'.format(random_str)

    def generate_xml(self):
        self._xml_root = ET.Element('network')
        ET.SubElement(self._xml_root, 'name').text = self.name
        ET.SubElement(self._xml_root, 'bridge', {'stp': 'off', 'delay': '0'})
        self._create_forward_config()

        return ET.tostring(self._xml_root).decode('utf-8')

    @abstractmethod
    def _create_forward_config(self):
        pass

class NatNetworkConfig(AbstractNetworkConfig):
    def __init__(self, name=None):
        super().__init__(name=name)

    def _create_forward_config(self):
        ET.SubElement(self._xml_root, 'forward', {'type': 'nat'})

class IsolatedNetworkConfig(AbstractNetworkConfig):
    def _create_forward_config(self):
        pass
