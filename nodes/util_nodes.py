"""Utility operation nodes."""

import zlib
import gzip
import io

from .base import ByteFlowNode


class ReverseNode(ByteFlowNode):
    """Reverse bytes."""

    __identifier__ = 'byteflow.util'
    NODE_NAME = 'Reverse'

    def __init__(self):
        super().__init__()
        self.add_input('data')
        self.add_output('output')
        self.set_color(120, 120, 120)

    def process(self):
        data = self.get_input_data('data')
        self.set_output_data('output', data[::-1])


class ZlibNode(ByteFlowNode):
    """Zlib compress/decompress."""

    __identifier__ = 'byteflow.util'
    NODE_NAME = 'Zlib'

    def __init__(self):
        super().__init__()
        self.add_input('data')
        self.add_output('output')
        self.add_combo_menu('mode', 'Mode', items=['Decompress', 'Compress', 'Raw Inflate', 'Raw Deflate'])
        self.set_color(120, 120, 120)

    def process(self):
        data = self.get_input_data('data')
        if not data:
            self.set_output_data('output', b'')
            return

        mode = self.get_property('mode')
        try:
            if mode == 'Decompress':
                result = zlib.decompress(data)
            elif mode == 'Compress':
                result = zlib.compress(data)
            elif mode == 'Raw Inflate':
                # Raw deflate without header
                result = zlib.decompress(data, -zlib.MAX_WBITS)
            else:  # Raw Deflate
                compress = zlib.compressobj(zlib.Z_DEFAULT_COMPRESSION, zlib.DEFLATED, -zlib.MAX_WBITS)
                result = compress.compress(data) + compress.flush()
            self.set_output_data('output', result)
        except Exception as e:
            print(f"Zlib error: {e}")
            self.set_output_data('output', b'')


class GzipNode(ByteFlowNode):
    """Gzip compress/decompress."""

    __identifier__ = 'byteflow.util'
    NODE_NAME = 'Gzip'

    def __init__(self):
        super().__init__()
        self.add_input('data')
        self.add_output('output')
        self.add_combo_menu('mode', 'Mode', items=['Decompress', 'Compress'])
        self.set_color(120, 120, 120)

    def process(self):
        data = self.get_input_data('data')
        if not data:
            self.set_output_data('output', b'')
            return

        mode = self.get_property('mode')
        try:
            if mode == 'Decompress':
                result = gzip.decompress(data)
            else:
                buf = io.BytesIO()
                with gzip.GzipFile(fileobj=buf, mode='wb') as f:
                    f.write(data)
                result = buf.getvalue()
            self.set_output_data('output', result)
        except Exception as e:
            print(f"Gzip error: {e}")
            self.set_output_data('output', b'')


class SubstringNode(ByteFlowNode):
    """Extract substring/slice of bytes."""

    __identifier__ = 'byteflow.util'
    NODE_NAME = 'Substring'

    def __init__(self):
        super().__init__()
        self.add_input('data')
        self.add_output('output')
        self.add_text_input('start', 'Start', text='0')
        self.add_text_input('end', 'End (empty=all)', text='')
        self.set_color(120, 120, 120)

    def process(self):
        data = self.get_input_data('data')
        if not data:
            self.set_output_data('output', b'')
            return

        try:
            start = int(self.get_property('start'))
        except ValueError:
            start = 0

        end_str = self.get_property('end').strip()
        if end_str:
            try:
                end = int(end_str)
            except ValueError:
                end = None
        else:
            end = None

        if end is not None:
            result = data[start:end]
        else:
            result = data[start:]

        self.set_output_data('output', result)


class RepeatNode(ByteFlowNode):
    """Repeat data N times."""

    __identifier__ = 'byteflow.util'
    NODE_NAME = 'Repeat'

    def __init__(self):
        super().__init__()
        self.add_input('data')
        self.add_output('output')
        self.add_text_input('count', 'Count', text='2')
        self.set_color(120, 120, 120)

    def process(self):
        data = self.get_input_data('data')
        if not data:
            self.set_output_data('output', b'')
            return

        try:
            count = max(1, int(self.get_property('count')))
        except ValueError:
            count = 1

        self.set_output_data('output', data * count)


class TakeBytesNode(ByteFlowNode):
    """Take bytes from input using start+length or start+end (Python-style indexing).

    Supports negative indices like Python:
    - Negative start: counts from end (e.g., -5 = 5 bytes from end)
    - Negative end: counts from end (e.g., -1 = stop 1 before end)
    - Empty start: from beginning
    - Empty end/length: to the end
    """

    __identifier__ = 'byteflow.util'
    NODE_NAME = 'Take Bytes'

    def __init__(self):
        super().__init__()
        self.add_input('data')
        self.add_output('output')
        self.add_combo_menu('mode', 'Mode', items=['Start + Length', 'Start + End'])
        self.add_text_input('start', 'Start (empty=0)', text='')
        self.add_text_input('param2', 'Length / End (empty=all)', text='')
        self.set_color(120, 120, 120)

    def process(self):
        data = self.get_input_data('data')
        if not data:
            self.set_output_data('output', b'')
            return

        mode = self.get_property('mode')
        start_str = self.get_property('start').strip()
        param2_str = self.get_property('param2').strip()

        # Parse start (empty = 0 for start+length, None for start+end)
        if start_str:
            try:
                start = int(start_str)
            except ValueError:
                start = 0
        else:
            start = None if mode == 'Start + End' else 0

        # Parse param2 (length or end)
        if param2_str:
            try:
                param2 = int(param2_str)
            except ValueError:
                param2 = None
        else:
            param2 = None

        try:
            if mode == 'Start + Length':
                # start + length mode
                if start is None:
                    start = 0
                if param2 is None:
                    result = data[start:]
                else:
                    # Handle negative start
                    if start < 0:
                        actual_start = len(data) + start
                    else:
                        actual_start = start
                    result = data[actual_start:actual_start + param2]
            else:
                # Start + End mode (Python slice)
                result = data[start:param2]

            self.set_output_data('output', result)
        except Exception as e:
            print(f"Take bytes error: {e}")
            self.set_output_data('output', b'')
