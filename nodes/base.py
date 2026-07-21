"""Base node class with data flow support."""

from PySide6 import QtWidgets, QtCore
from NodeGraphQt import BaseNode
from NodeGraphQt.widgets.node_widgets import NodeBaseWidget


class NodeLabel(NodeBaseWidget):
    """A read-only text display embedded in a node.

    Unlike ``add_text_input`` this is not backed by a custom property, so it is
    not editable, not shown in the properties dialog, and not serialized to disk.
    It is meant purely for derived/computed status text (e.g. byte counts).
    """

    def __init__(self, parent=None, name='', label='', text=''):
        super().__init__(parent, name, label)
        label_widget = QtWidgets.QLabel(text)
        label_widget.setAlignment(QtCore.Qt.AlignCenter)
        label_widget.setWordWrap(True)
        # Fixed width + word wrap keeps a long value (e.g. preview text) from
        # blowing out the node width and overflowing off the right edge.
        label_widget.setFixedWidth(130)
        label_widget.setStyleSheet(
            'QLabel { color: rgba(255, 255, 255, 150); font-size: 10pt; padding: 2px; }'
        )
        self.set_custom_widget(label_widget)

    @property
    def type_(self):
        return 'LabelNodeWidget'

    def get_value(self):
        return str(self.get_custom_widget().text())

    def set_value(self, text=''):
        self.get_custom_widget().setText(str(text))


class ByteFlowNode(BaseNode):
    """Base class for all ByteFlow nodes with data processing."""

    __identifier__ = 'byteflow'

    def __init__(self):
        super().__init__()
        self._output_data = {}
        self._displays = {}

    def add_display(self, name: str, label: str = '', text: str = ''):
        """Add a read-only display field to the node.

        The value is computed state, so it is intentionally not registered as a
        custom property (keeps it out of the properties dialog and saved files).
        """
        widget = NodeLabel(self.view, name, label, text)
        self._displays[name] = widget
        self.view.add_widget(widget)
        self.view.draw_node()

    def set_display(self, name: str, text: str):
        """Update the text of a read-only display field."""
        widget = self._displays.get(name)
        if widget:
            widget.set_value(text)

    def update_model(self):
        """Sync view widgets to the model, skipping read-only displays.

        Display widgets have no backing custom property, so the default
        implementation would raise when it tries to store their value.
        """
        for name, val in self.view.properties.items():
            if name in ('inputs', 'outputs'):
                continue
            self.model.set_property(name, val)
        for name, widget in self.view.widgets.items():
            if name in self._displays:
                continue
            self.model.set_property(name, widget.get_value())

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
