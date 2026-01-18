"""Input/Output nodes for data sources and sinks."""

from .base import ByteFlowNode


class HexInputNode(ByteFlowNode):
    """Input node that accepts hex-encoded data."""

    __identifier__ = 'byteflow.io'
    NODE_NAME = 'Hex Input'

    def __init__(self):
        super().__init__()
        self.add_output('output')
        self.add_text_input('hex_data', 'Hex Data', text='48656c6c6f')
        self.set_color(200, 150, 50)

    def process(self):
        hex_str = self.get_property('hex_data')
        try:
            data = bytes.fromhex(hex_str.replace(' ', '').replace('\n', ''))
        except ValueError:
            data = b''
        self.set_output_data('output', data)


class TextInputNode(ByteFlowNode):
    """Input node that accepts plain text (UTF-8)."""

    __identifier__ = 'byteflow.io'
    NODE_NAME = 'Text Input'

    def __init__(self):
        super().__init__()
        self.add_output('output')
        self.add_text_input('text_data', 'Text', text='Hello')
        self.set_color(200, 180, 50)

    def process(self):
        text = self.get_property('text_data')
        self.set_output_data('output', text.encode('utf-8'))


class FileInputNode(ByteFlowNode):
    """Input node that reads from a file."""

    __identifier__ = 'byteflow.io'
    NODE_NAME = 'File Input'

    def __init__(self):
        super().__init__()
        self.add_output('output')
        self.add_text_input('file_path', 'File Path', text='')
        self.set_color(200, 100, 50)

    def process(self):
        path = self.get_property('file_path')
        if not path:
            self.set_output_data('output', b'')
            return
        try:
            with open(path, 'rb') as f:
                data = f.read()
            self.set_output_data('output', data)
        except Exception as e:
            print(f"File read error: {e}")
            self.set_output_data('output', b'')


class OutputNode(ByteFlowNode):
    """Output node - shows preview, full output in Output Viewer panel."""

    __identifier__ = 'byteflow.io'
    NODE_NAME = 'Output'

    PREVIEW_BYTES = 64  # Max bytes to show in preview

    def __init__(self):
        super().__init__()
        self.add_input('input')
        self.add_text_input('length', 'Length', text='0 bytes')
        self.add_text_input('preview', 'Preview', text='')
        self._data = b''
        self.set_color(100, 100, 150)

    def process(self):
        self._data = self.get_input_data('input')

        # Update length display
        length = len(self._data)
        self.set_property('length', f'{length} bytes')

        # Update preview - show raw bytes as text
        if self._data:
            preview_data = self._data[:self.PREVIEW_BYTES]
            # Use latin-1 for 1:1 byte to char mapping (no conversion errors)
            preview = preview_data.decode('latin-1')
            if len(self._data) > self.PREVIEW_BYTES:
                preview += '...'
            self.set_property('preview', preview)
        else:
            self.set_property('preview', '')

    def get_data(self) -> bytes:
        """Get the data flowing into this output node."""
        return self._data
