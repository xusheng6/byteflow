"""Base node class with data flow support."""

from NodeGraphQt import BaseNode


class ByteFlowNode(BaseNode):
    """Base class for all ByteFlow nodes with data processing."""

    __identifier__ = 'byteflow'

    def __init__(self):
        super().__init__()
        self._output_data = {}

    def get_input_data(self, port_name: str) -> bytes:
        """Get data from an input port by following the connection."""
        input_port = self.get_input(port_name)
        if not input_port:
            return b''

        connected = input_port.connected_ports()
        if not connected:
            return b''

        source_port = connected[0]
        source_node = source_port.node()

        if hasattr(source_node, 'get_output_data'):
            return source_node.get_output_data(source_port.name())
        return b''

    def get_output_data(self, port_name: str) -> bytes:
        """Get the computed output data for a port."""
        self.process()
        return self._output_data.get(port_name, b'')

    def set_output_data(self, port_name: str, data: bytes):
        """Set output data for a port."""
        self._output_data[port_name] = data

    def process(self):
        """Override this to implement node logic."""
        pass
