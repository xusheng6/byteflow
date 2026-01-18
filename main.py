#!/usr/bin/env python3
"""ByteFlow - A node-based data transformation tool."""

import sys
from PySide6 import QtWidgets, QtCore, QtGui
from NodeGraphQt import NodeGraph, PropertiesBinWidget

from nodes import (
    XORNode, RC4Node, AESNode, Base64Node,
    HexInputNode, TextInputNode, FileInputNode, OutputNode
)


class PanEventFilter(QtCore.QObject):
    """Event filter to enable left-click panning on the graph background."""

    def __init__(self, viewer):
        super().__init__(viewer)
        self.viewer = viewer
        self.panning = False
        self.last_pos = None

    def eventFilter(self, obj, event):
        event_type = event.type()

        if event_type == QtCore.QEvent.MouseButtonPress:
            if event.button() == QtCore.Qt.LeftButton:
                item = self.viewer.itemAt(event.position().toPoint())
                if item is None:
                    self.panning = True
                    self.last_pos = event.pos()
                    return True

        elif event_type == QtCore.QEvent.MouseMove:
            if self.panning and self.last_pos is not None:
                # Map to scene coordinates like NodeGraphQt does internally
                previous_pos = self.viewer.mapToScene(self.last_pos)
                current_pos = self.viewer.mapToScene(event.pos())
                delta = previous_pos - current_pos
                self.last_pos = event.pos()
                # Use NodeGraphQt's native pan method with scene delta
                self.viewer._set_viewer_pan(delta.x(), delta.y())
                return True

        elif event_type == QtCore.QEvent.MouseButtonRelease:
            if event.button() == QtCore.Qt.LeftButton and self.panning:
                self.panning = False
                self.last_pos = None
                return True

        return False


class ByteFlowApp:
    """Main application class."""

    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.app.setApplicationName('ByteFlow')

        # Create main window
        self.window = QtWidgets.QMainWindow()
        self.window.setWindowTitle('ByteFlow - Node-based Data Transformation')
        self.window.setGeometry(100, 100, 1400, 900)

        # Create node graph
        self.graph = NodeGraph()

        # Register custom nodes
        self.register_nodes()

        # Create central widget with splitter
        central = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(central)

        # Create splitter for graph and properties
        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)

        # Node graph widget
        graph_widget = self.graph.widget
        splitter.addWidget(graph_widget)

        # Properties panel with title
        props_container = QtWidgets.QWidget()
        props_layout = QtWidgets.QVBoxLayout(props_container)
        props_layout.setContentsMargins(0, 0, 0, 0)

        props_label = QtWidgets.QLabel('Node Properties')
        props_label.setStyleSheet('font-weight: bold; padding: 5px; background: #333; color: #fff;')
        props_layout.addWidget(props_label)

        self.props_bin = PropertiesBinWidget(node_graph=self.graph)
        props_layout.addWidget(self.props_bin)

        props_container.setMinimumWidth(300)
        splitter.addWidget(props_container)

        splitter.setSizes([1000, 400])
        layout.addWidget(splitter)

        # Process button
        btn_layout = QtWidgets.QHBoxLayout()

        process_btn = QtWidgets.QPushButton('Process (F5)')
        process_btn.clicked.connect(self.process_graph)
        process_btn.setShortcut(QtGui.QKeySequence('F5'))
        btn_layout.addWidget(process_btn)

        clear_btn = QtWidgets.QPushButton('Clear')
        clear_btn.clicked.connect(self.clear_graph)
        btn_layout.addWidget(clear_btn)

        fit_btn = QtWidgets.QPushButton('Fit View (F)')
        fit_btn.clicked.connect(self.fit_to_view)
        fit_btn.setShortcut(QtGui.QKeySequence('F'))
        btn_layout.addWidget(fit_btn)

        btn_layout.addSpacing(20)

        save_btn = QtWidgets.QPushButton('Save')
        save_btn.clicked.connect(self.save_graph)
        save_btn.setShortcut(QtGui.QKeySequence.Save)
        btn_layout.addWidget(save_btn)

        load_btn = QtWidgets.QPushButton('Load')
        load_btn.clicked.connect(self.load_graph)
        load_btn.setShortcut(QtGui.QKeySequence.Open)
        btn_layout.addWidget(load_btn)

        # Delete shortcut
        delete_action = QtGui.QAction(self.window)
        delete_action.setShortcuts([QtGui.QKeySequence.Delete, QtGui.QKeySequence('Backspace')])
        delete_action.triggered.connect(self.delete_selected)
        self.window.addAction(delete_action)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self.window.setCentralWidget(central)

        # Setup custom context menu
        self.setup_context_menu()

        # Connect to port connection signals to update property states
        self.graph.port_connected.connect(self.on_port_connected)
        self.graph.port_disconnected.connect(self.on_port_disconnected)

        # Enable left-click drag to pan the view
        viewer = self.graph.viewer()
        if viewer:
            self.pan_filter = PanEventFilter(viewer)
            viewer.viewport().installEventFilter(self.pan_filter)

        # Create a demo graph
        self.create_demo_graph()

    def register_nodes(self):
        """Register all custom nodes."""
        self.graph.register_node(XORNode)
        self.graph.register_node(RC4Node)
        self.graph.register_node(AESNode)
        self.graph.register_node(Base64Node)
        self.graph.register_node(HexInputNode)
        self.graph.register_node(TextInputNode)
        self.graph.register_node(FileInputNode)
        self.graph.register_node(OutputNode)

    def setup_context_menu(self):
        """Setup right-click context menu for creating nodes."""
        # Get NodeGraphQt's built-in graph context menu
        graph_menu = self.graph.get_context_menu('graph')

        # I/O submenu
        io_menu = graph_menu.add_menu('Input/Output')
        io_menu.add_command('Hex Input', lambda g: self.create_node('byteflow.io.HexInputNode'))
        io_menu.add_command('Text Input', lambda g: self.create_node('byteflow.io.TextInputNode'))
        io_menu.add_command('File Input', lambda g: self.create_node('byteflow.io.FileInputNode'))
        io_menu.add_command('Output', lambda g: self.create_node('byteflow.io.OutputNode'))

        # Crypto submenu
        crypto_menu = graph_menu.add_menu('Crypto')
        crypto_menu.add_command('XOR', lambda g: self.create_node('byteflow.crypto.XORNode'))
        crypto_menu.add_command('RC4', lambda g: self.create_node('byteflow.crypto.RC4Node'))
        crypto_menu.add_command('AES', lambda g: self.create_node('byteflow.crypto.AESNode'))
        crypto_menu.add_command('Base64', lambda g: self.create_node('byteflow.crypto.Base64Node'))

    def create_node(self, node_type):
        """Create a new node at the cursor position."""
        node = self.graph.create_node(node_type)
        # Position at center of current view if no cursor pos available
        viewer = self.graph.viewer()
        if viewer:
            pos = viewer.mapToScene(viewer.rect().center())
            node.set_pos(pos.x(), pos.y())
        return node

    def process_graph(self):
        """Process all output nodes in the graph."""
        for node in self.graph.all_nodes():
            if isinstance(node, OutputNode):
                node.process()
                data = node.get_data()
                print(f"Output '{node.name()}': {len(data)} bytes")
                if data:
                    print(f"  Hex: {data.hex()}")
                    try:
                        print(f"  Text: {data.decode('utf-8', errors='replace')}")
                    except:
                        pass

    def clear_graph(self):
        """Clear all nodes from the graph."""
        self.graph.clear_session()

    def save_graph(self):
        """Save the graph to a JSON file."""
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self.window,
            'Save Graph',
            '',
            'ByteFlow Graph (*.json);;All Files (*)'
        )
        if file_path:
            if not file_path.endswith('.json'):
                file_path += '.json'
            self.graph.save_session(file_path)

    def load_graph(self):
        """Load a graph from a JSON file."""
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self.window,
            'Load Graph',
            '',
            'ByteFlow Graph (*.json);;All Files (*)'
        )
        if file_path:
            self.graph.load_session(file_path)
            # Update all nodes' property states after loading
            QtCore.QTimer.singleShot(100, self.update_all_node_properties)

    def fit_to_view(self):
        """Fit all nodes in the view."""
        all_nodes = self.graph.all_nodes()
        if not all_nodes:
            return

        viewer = self.graph.viewer()
        if not viewer:
            return

        # Calculate bounding rect from node view items
        from PySide6.QtCore import QRectF
        rect = QRectF()
        for node in all_nodes:
            if node.view:
                rect = rect.united(node.view.sceneBoundingRect())

        if rect.isNull():
            return

        # Add padding
        padding = 50
        rect.adjust(-padding, -padding, padding, padding)

        # Update NodeGraphQt's internal scene range so panning works correctly
        viewer._scene_range = rect
        viewer._update_scene()

    def delete_selected(self):
        """Delete selected nodes."""
        selected = self.graph.selected_nodes()
        if selected:
            for node in selected:
                self.graph.remove_node(node)

    def on_port_connected(self, input_port, output_port):
        """Handle port connection - disable corresponding property widget."""
        node = input_port.node()
        self.update_node_property_state(node)

    def on_port_disconnected(self, input_port, output_port):
        """Handle port disconnection - re-enable corresponding property widget."""
        node = input_port.node()
        self.update_node_property_state(node)

    def update_node_property_state(self, node):
        """Update property widget states based on port connections."""
        if not hasattr(node, 'PORT_TO_PROPERTY'):
            return

        for port_name, prop_name in node.PORT_TO_PROPERTY.items():
            input_port = node.get_input(port_name)
            widget = node.view.get_widget(prop_name) if node.view else None

            if input_port and input_port.connected_ports():
                # Port is connected - disable widget and show indicator
                if widget:
                    widget.setEnabled(False)
                    widget.set_value('(connected)')
            else:
                # Port is not connected - enable widget
                if widget:
                    widget.setEnabled(True)
                    # Restore value from property if it was showing '(connected)'
                    if widget.get_value() == '(connected)':
                        # Get default or stored value
                        current = node.get_property(prop_name)
                        if current == '(connected)':
                            widget.set_value('00')  # Default fallback
                        else:
                            widget.set_value(current)

    def update_all_node_properties(self):
        """Update all nodes' property states after loading."""
        for node in self.graph.all_nodes():
            self.update_node_property_state(node)

    def create_demo_graph(self):
        """Create a demo graph showing XOR operation."""
        # Create nodes
        text_input = self.graph.create_node('byteflow.io.TextInputNode')
        text_input.set_name('Input Text')
        text_input.set_pos(-200, 0)
        text_input.set_property('text_data', 'Hello ByteFlow!')

        xor_node = self.graph.create_node('byteflow.crypto.XORNode')
        xor_node.set_name('XOR Encrypt')
        xor_node.set_pos(100, 0)
        xor_node.set_property('key_hex', 'FF')

        output = self.graph.create_node('byteflow.io.OutputNode')
        output.set_name('Result')
        output.set_pos(400, 0)

        # Connect nodes
        text_input.output(0).connect_to(xor_node.input(0))
        xor_node.output(0).connect_to(output.input(0))

        # Fit graph to view
        QtCore.QTimer.singleShot(100, self.fit_to_view)

    def run(self):
        """Run the application."""
        self.window.show()
        return self.app.exec()


def main():
    app = ByteFlowApp()
    sys.exit(app.run())


if __name__ == '__main__':
    main()
