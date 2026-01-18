"""Hash operation nodes."""

import hashlib

from .base import ByteFlowNode


class MD5Node(ByteFlowNode):
    """Compute MD5 hash."""

    __identifier__ = 'byteflow.hash'
    NODE_NAME = 'MD5'

    def __init__(self):
        super().__init__()
        self.add_input('data')
        self.add_output('hash')
        self.add_combo_menu('format', 'Output', items=['Hex', 'Raw'])
        self.set_color(100, 80, 120)

    def process(self):
        data = self.get_input_data('data')
        if not data:
            self.set_output_data('hash', b'')
            return

        digest = hashlib.md5(data).digest()
        if self.get_property('format') == 'Hex':
            self.set_output_data('hash', digest.hex().encode())
        else:
            self.set_output_data('hash', digest)


class SHA1Node(ByteFlowNode):
    """Compute SHA1 hash."""

    __identifier__ = 'byteflow.hash'
    NODE_NAME = 'SHA1'

    def __init__(self):
        super().__init__()
        self.add_input('data')
        self.add_output('hash')
        self.add_combo_menu('format', 'Output', items=['Hex', 'Raw'])
        self.set_color(100, 80, 120)

    def process(self):
        data = self.get_input_data('data')
        if not data:
            self.set_output_data('hash', b'')
            return

        digest = hashlib.sha1(data).digest()
        if self.get_property('format') == 'Hex':
            self.set_output_data('hash', digest.hex().encode())
        else:
            self.set_output_data('hash', digest)


class SHA256Node(ByteFlowNode):
    """Compute SHA256 hash."""

    __identifier__ = 'byteflow.hash'
    NODE_NAME = 'SHA256'

    def __init__(self):
        super().__init__()
        self.add_input('data')
        self.add_output('hash')
        self.add_combo_menu('format', 'Output', items=['Hex', 'Raw'])
        self.set_color(100, 80, 120)

    def process(self):
        data = self.get_input_data('data')
        if not data:
            self.set_output_data('hash', b'')
            return

        digest = hashlib.sha256(data).digest()
        if self.get_property('format') == 'Hex':
            self.set_output_data('hash', digest.hex().encode())
        else:
            self.set_output_data('hash', digest)
