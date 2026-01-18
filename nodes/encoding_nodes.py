"""Encoding/decoding operation nodes."""

import urllib.parse

from .base import ByteFlowNode


class URLEncodeNode(ByteFlowNode):
    """URL encode/decode."""

    __identifier__ = 'byteflow.encoding'
    NODE_NAME = 'URL Encode'

    def __init__(self):
        super().__init__()
        self.add_input('data')
        self.add_output('output')
        self.add_combo_menu('mode', 'Mode', items=['Encode', 'Decode'])
        self.set_color(180, 140, 60)

    def process(self):
        data = self.get_input_data('data')
        if not data:
            self.set_output_data('output', b'')
            return

        mode = self.get_property('mode')
        try:
            text = data.decode('utf-8', errors='replace')
            if mode == 'Encode':
                result = urllib.parse.quote(text, safe='').encode()
            else:
                result = urllib.parse.unquote(text).encode()
            self.set_output_data('output', result)
        except Exception as e:
            print(f"URL encode error: {e}")
            self.set_output_data('output', b'')


class HexEncodeNode(ByteFlowNode):
    """Hex encode/decode (convert bytes to/from hex string)."""

    __identifier__ = 'byteflow.encoding'
    NODE_NAME = 'Hex'

    def __init__(self):
        super().__init__()
        self.add_input('data')
        self.add_output('output')
        self.add_combo_menu('mode', 'Mode', items=['Encode', 'Decode'])
        self.set_color(180, 140, 60)

    def process(self):
        data = self.get_input_data('data')
        if not data:
            self.set_output_data('output', b'')
            return

        mode = self.get_property('mode')
        try:
            if mode == 'Encode':
                result = data.hex().encode()
            else:
                # Decode hex string to bytes
                hex_str = data.decode('utf-8', errors='replace')
                hex_str = hex_str.replace(' ', '').replace('\n', '')
                result = bytes.fromhex(hex_str)
            self.set_output_data('output', result)
        except Exception as e:
            print(f"Hex encode error: {e}")
            self.set_output_data('output', b'')


class ROTNode(ByteFlowNode):
    """ROT-N cipher (Caesar cipher)."""

    __identifier__ = 'byteflow.encoding'
    NODE_NAME = 'ROT'

    def __init__(self):
        super().__init__()
        self.add_input('data')
        self.add_output('output')
        self.add_text_input('shift', 'Shift (0-25)', text='13')
        self.set_color(180, 140, 60)

    def process(self):
        data = self.get_input_data('data')
        if not data:
            self.set_output_data('output', b'')
            return

        try:
            shift = int(self.get_property('shift')) % 26
        except ValueError:
            shift = 13

        result = []
        for byte in data:
            char = chr(byte)
            if 'a' <= char <= 'z':
                result.append((ord(char) - ord('a') + shift) % 26 + ord('a'))
            elif 'A' <= char <= 'Z':
                result.append((ord(char) - ord('A') + shift) % 26 + ord('A'))
            else:
                result.append(byte)

        self.set_output_data('output', bytes(result))


class AtbashNode(ByteFlowNode):
    """Atbash cipher (reverse alphabet)."""

    __identifier__ = 'byteflow.encoding'
    NODE_NAME = 'Atbash'

    def __init__(self):
        super().__init__()
        self.add_input('data')
        self.add_output('output')
        self.set_color(180, 140, 60)

    def process(self):
        data = self.get_input_data('data')
        if not data:
            self.set_output_data('output', b'')
            return

        result = []
        for byte in data:
            char = chr(byte)
            if 'a' <= char <= 'z':
                result.append(ord('z') - (byte - ord('a')))
            elif 'A' <= char <= 'Z':
                result.append(ord('Z') - (byte - ord('A')))
            else:
                result.append(byte)

        self.set_output_data('output', bytes(result))
