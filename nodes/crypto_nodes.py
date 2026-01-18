"""Cryptographic operation nodes."""

import base64

from Crypto.Cipher import AES, ARC4
from Crypto.Util.Padding import pad, unpad
from Crypto.Util import Counter

from .base import ByteFlowNode


class Base64Node(ByteFlowNode):
    """Base64 encode/decode."""

    __identifier__ = 'byteflow.crypto'
    NODE_NAME = 'Base64'

    def __init__(self):
        super().__init__()
        self.add_input('data')
        self.add_output('output')
        self.add_combo_menu('mode', 'Mode', items=['Encode', 'Decode'])
        self.set_color(150, 100, 180)

    def process(self):
        data = self.get_input_data('data')
        if not data:
            self.set_output_data('output', b'')
            return

        mode = self.get_property('mode')
        try:
            if mode == 'Encode':
                result = base64.b64encode(data)
            else:
                result = base64.b64decode(data)
            self.set_output_data('output', result)
        except Exception as e:
            print(f"Base64 error: {e}")
            self.set_output_data('output', b'')


class XORNode(ByteFlowNode):
    """XOR data with a key."""

    __identifier__ = 'byteflow.crypto'
    NODE_NAME = 'XOR'

    def __init__(self):
        super().__init__()
        self.add_input('data')
        self.add_input('key')
        self.add_output('output')
        self.set_color(180, 70, 70)

    def process(self):
        data = self.get_input_data('data')
        key = self.get_input_data('key')

        if not data or not key:
            self.set_output_data('output', b'')
            return

        # XOR with repeating key
        result = bytes(d ^ key[i % len(key)] for i, d in enumerate(data))
        self.set_output_data('output', result)


class RC4Node(ByteFlowNode):
    """RC4 encrypt/decrypt."""

    __identifier__ = 'byteflow.crypto'
    NODE_NAME = 'RC4'

    def __init__(self):
        super().__init__()
        self.add_input('data')
        self.add_input('key')
        self.add_output('output')
        self.set_color(70, 130, 180)

    def process(self):
        data = self.get_input_data('data')
        key = self.get_input_data('key')

        if not data or not key:
            self.set_output_data('output', b'')
            return

        cipher = ARC4.new(key)
        result = cipher.encrypt(data)
        self.set_output_data('output', result)


class AESNode(ByteFlowNode):
    """AES encrypt/decrypt."""

    __identifier__ = 'byteflow.crypto'
    NODE_NAME = 'AES'

    def __init__(self):
        super().__init__()
        self.add_input('data')
        self.add_input('key')
        self.add_input('iv')
        self.add_output('output')
        self.add_combo_menu('mode', 'Mode', items=['CBC Encrypt', 'CBC Decrypt', 'ECB Encrypt', 'ECB Decrypt', 'CTR'])
        self.set_color(70, 180, 70)

    def process(self):
        data = self.get_input_data('data')
        key = self.get_input_data('key')
        iv = self.get_input_data('iv')

        if not data:
            self.set_output_data('output', b'')
            return

        # Default key/iv if not provided
        if not key:
            key = b'\x00' * 16
        if not iv:
            iv = b'\x00' * 16

        # Ensure valid key length
        if len(key) not in (16, 24, 32):
            key = key.ljust(16, b'\x00')[:16]

        mode_str = self.get_property('mode')

        try:
            if 'ECB' in mode_str:
                cipher = AES.new(key, AES.MODE_ECB)
                if 'Encrypt' in mode_str:
                    padded = pad(data, AES.block_size)
                    result = cipher.encrypt(padded)
                else:
                    decrypted = cipher.decrypt(data)
                    try:
                        result = unpad(decrypted, AES.block_size)
                    except ValueError:
                        result = decrypted
            elif 'CTR' in mode_str:
                # CTR mode uses full 16-byte IV as initial counter value
                if len(iv) != 16:
                    iv = iv.ljust(16, b'\x00')[:16]
                # Create counter with IV as initial value (matches CyberChef behavior)
                ctr = Counter.new(128, initial_value=int.from_bytes(iv, 'big'))
                cipher = AES.new(key, AES.MODE_CTR, counter=ctr)
                # CTR encrypt and decrypt are the same operation
                result = cipher.encrypt(data)
            else:  # CBC
                if len(iv) != 16:
                    iv = iv.ljust(16, b'\x00')[:16]
                cipher = AES.new(key, AES.MODE_CBC, iv)
                if 'Encrypt' in mode_str:
                    padded = pad(data, AES.block_size)
                    result = cipher.encrypt(padded)
                else:
                    decrypted = cipher.decrypt(data)
                    try:
                        result = unpad(decrypted, AES.block_size)
                    except ValueError:
                        result = decrypted

            self.set_output_data('output', result)
        except Exception as e:
            print(f"AES error: {e}")
            self.set_output_data('output', b'')
