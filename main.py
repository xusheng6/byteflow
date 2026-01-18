#!/usr/bin/env python3
"""ByteFlow - A node-based data transformation tool."""

import sys
from PySide6 import QtWidgets, QtCore, QtGui
from NodeGraphQt import NodeGraph

from nodes import (
    XORNode, RC4Node, AESNode, Base64Node,
    MD5Node, SHA1Node, SHA256Node,
    URLEncodeNode, HexEncodeNode, ROTNode, AtbashNode,
    ReverseNode, ZlibNode, GzipNode, SubstringNode, RepeatNode,
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
                previous_pos = self.viewer.mapToScene(self.last_pos)
                current_pos = self.viewer.mapToScene(event.pos())
                delta = previous_pos - current_pos
                self.last_pos = event.pos()
                self.viewer._set_viewer_pan(delta.x(), delta.y())
                return True

        elif event_type == QtCore.QEvent.MouseButtonRelease:
            if event.button() == QtCore.Qt.LeftButton and self.panning:
                self.panning = False
                self.last_pos = None
                return True

        return False


class SingleOutputViewer(QtWidgets.QWidget):
    """Widget for viewing a single output node's contents."""

    VIEW_RAW = 0
    VIEW_HEX = 1
    VIEW_HEXDUMP = 2

    def __init__(self, parent=None):
        super().__init__(parent)
        self._data = b''
        self._node_name = ''

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header bar with info, view mode, and copy buttons
        header = QtWidgets.QHBoxLayout()
        header.setContentsMargins(3, 3, 3, 3)
        header.setSpacing(5)

        self.info_label = QtWidgets.QLabel('No output')
        self.info_label.setStyleSheet('color: #aaa; font-weight: bold;')
        header.addWidget(self.info_label)

        header.addStretch()

        # View as dropdown
        header.addWidget(QtWidgets.QLabel('View:'))
        self.view_combo = QtWidgets.QComboBox()
        self.view_combo.addItems(['Raw', 'Hex', 'Hex Dump'])
        self.view_combo.setFixedWidth(80)
        self.view_combo.currentIndexChanged.connect(self._refresh_display)
        header.addWidget(self.view_combo)

        # Copy buttons
        copy_btn = QtWidgets.QPushButton('Copy')
        copy_btn.setFixedWidth(50)
        copy_btn.clicked.connect(self._copy_displayed)
        header.addWidget(copy_btn)

        copy_raw_btn = QtWidgets.QPushButton('Copy Raw')
        copy_raw_btn.setFixedWidth(70)
        copy_raw_btn.clicked.connect(self._copy_raw)
        header.addWidget(copy_raw_btn)

        header_widget = QtWidgets.QWidget()
        header_widget.setLayout(header)
        header_widget.setStyleSheet('background: #2a2a2a;')
        layout.addWidget(header_widget)

        # Text display
        self.text_display = QtWidgets.QPlainTextEdit()
        self.text_display.setReadOnly(True)
        self.text_display.setFont(QtGui.QFont('Menlo', 16))
        self.text_display.setStyleSheet('background: #1e1e1e; color: #ddd;')
        layout.addWidget(self.text_display)

    def show_data(self, data: bytes, node_name: str = ''):
        """Display data in the viewer."""
        self._data = data
        self._node_name = node_name
        self._refresh_display()

    def _refresh_display(self):
        """Refresh the display based on current view mode."""
        if not self._data:
            self.info_label.setText(f'{self._node_name}: empty')
            self.text_display.setPlainText('')
            return

        self.info_label.setText(f'{self._node_name}: {len(self._data)} bytes')

        view_mode = self.view_combo.currentIndex()
        if view_mode == self.VIEW_RAW:
            # Raw bytes as text (latin-1 for 1:1 mapping)
            self.text_display.setPlainText(self._data.decode('latin-1'))
        elif view_mode == self.VIEW_HEX:
            # Plain hex string
            self.text_display.setPlainText(self._data.hex())
        else:  # VIEW_HEXDUMP
            # Hex dump with offset, hex, and ASCII
            lines = []
            for i in range(0, len(self._data), 16):
                chunk = self._data[i:i+16]
                hex_part = ' '.join(f'{b:02x}' for b in chunk)
                ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
                lines.append(f'{i:08x}  {hex_part:<48}  {ascii_part}')
            self.text_display.setPlainText('\n'.join(lines))

    def _copy_displayed(self):
        """Copy the displayed text to clipboard."""
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(self.text_display.toPlainText())

    def _copy_raw(self):
        """Copy the raw bytes to clipboard (as latin-1 text)."""
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(self._data.decode('latin-1'))


class OutputViewerPanel(QtWidgets.QWidget):
    """Panel for viewing multiple output nodes simultaneously."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        header = QtWidgets.QLabel('Output Viewer')
        header.setStyleSheet('font-weight: bold; padding: 5px; background: #333; color: #fff;')
        layout.addWidget(header)

        # Splitter to show multiple outputs vertically
        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        layout.addWidget(self.splitter)

        # Store viewer widgets keyed by node id
        self.viewers = {}

    def update_outputs(self, output_nodes):
        """Update the panel to show all output nodes."""
        # Get current node ids
        current_ids = set(self.viewers.keys())
        new_ids = set(node.id for node in output_nodes)

        # Remove viewers for nodes that no longer exist
        for node_id in current_ids - new_ids:
            viewer = self.viewers.pop(node_id)
            viewer.setParent(None)
            viewer.deleteLater()

        # Add viewers for new nodes
        for node in output_nodes:
            if node.id not in self.viewers:
                viewer = SingleOutputViewer()
                self.viewers[node.id] = viewer
                self.splitter.addWidget(viewer)

        # Update all viewers with current data
        for node in output_nodes:
            viewer = self.viewers.get(node.id)
            if viewer:
                data = node.get_data()
                viewer.show_data(data, node.name())

    def clear(self):
        """Clear all viewers."""
        for viewer in self.viewers.values():
            viewer.setParent(None)
            viewer.deleteLater()
        self.viewers.clear()


# List of all node classes for registration
ALL_NODE_CLASSES = [
    # Crypto
    XORNode, RC4Node, AESNode, Base64Node,
    # Hash
    MD5Node, SHA1Node, SHA256Node,
    # Encoding
    URLEncodeNode, HexEncodeNode, ROTNode, AtbashNode,
    # Utility
    ReverseNode, ZlibNode, GzipNode, SubstringNode, RepeatNode,
    # I/O
    HexInputNode, TextInputNode, FileInputNode, OutputNode,
]


class GraphTab(QtWidgets.QWidget):
    """A single tab containing a node graph and output viewer."""

    def __init__(self, app, parent=None):
        super().__init__(parent)
        self.app = app
        self._tab_name = 'Untitled'

        # Create node graph
        self.graph = NodeGraph()

        # Register nodes
        for node_class in ALL_NODE_CLASSES:
            self.graph.register_node(node_class)

        # Layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Horizontal splitter for graph and output viewer
        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)

        # Node graph widget
        splitter.addWidget(self.graph.widget)

        # Output viewer panel
        self.output_viewer = OutputViewerPanel()
        self.output_viewer.setMinimumWidth(300)
        splitter.addWidget(self.output_viewer)

        splitter.setSizes([900, 400])
        layout.addWidget(splitter)

        # Setup context menu
        self.setup_context_menu()

        # Connect signals
        self.graph.port_connected.connect(self.on_port_connected)
        self.graph.port_disconnected.connect(self.on_port_disconnected)
        self.graph.node_double_clicked.connect(self.on_node_double_clicked)
        self.graph.property_changed.connect(self.on_property_changed)

        # Enable left-click panning
        viewer = self.graph.viewer()
        if viewer:
            self.pan_filter = PanEventFilter(viewer)
            viewer.viewport().installEventFilter(self.pan_filter)

    def setup_context_menu(self):
        """Setup right-click context menu for creating nodes."""
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

        # Hash submenu
        hash_menu = graph_menu.add_menu('Hash')
        hash_menu.add_command('MD5', lambda g: self.create_node('byteflow.hash.MD5Node'))
        hash_menu.add_command('SHA1', lambda g: self.create_node('byteflow.hash.SHA1Node'))
        hash_menu.add_command('SHA256', lambda g: self.create_node('byteflow.hash.SHA256Node'))

        # Encoding submenu
        enc_menu = graph_menu.add_menu('Encoding')
        enc_menu.add_command('URL Encode', lambda g: self.create_node('byteflow.encoding.URLEncodeNode'))
        enc_menu.add_command('Hex', lambda g: self.create_node('byteflow.encoding.HexEncodeNode'))
        enc_menu.add_command('ROT', lambda g: self.create_node('byteflow.encoding.ROTNode'))
        enc_menu.add_command('Atbash', lambda g: self.create_node('byteflow.encoding.AtbashNode'))

        # Utility submenu
        util_menu = graph_menu.add_menu('Utility')
        util_menu.add_command('Reverse', lambda g: self.create_node('byteflow.util.ReverseNode'))
        util_menu.add_command('Zlib', lambda g: self.create_node('byteflow.util.ZlibNode'))
        util_menu.add_command('Gzip', lambda g: self.create_node('byteflow.util.GzipNode'))
        util_menu.add_command('Substring', lambda g: self.create_node('byteflow.util.SubstringNode'))
        util_menu.add_command('Repeat', lambda g: self.create_node('byteflow.util.RepeatNode'))

    def create_node(self, node_type):
        """Create a new node at the cursor position."""
        node = self.graph.create_node(node_type)
        viewer = self.graph.viewer()
        if viewer:
            pos = viewer.mapToScene(viewer.rect().center())
            node.set_pos(pos.x(), pos.y())
        if self.app.auto_process:
            self.process_graph()
        return node

    def process_graph(self):
        """Process all output nodes in the graph."""
        for node in self.graph.all_nodes():
            if isinstance(node, OutputNode):
                node.process()
        self.update_output_viewer()

    def update_output_viewer(self):
        """Update output viewer with all output nodes."""
        output_nodes = [node for node in self.graph.all_nodes() if isinstance(node, OutputNode)]
        self.output_viewer.update_outputs(output_nodes)

    def clear_graph(self):
        """Clear all nodes from the graph."""
        self.graph.clear_session()
        self.output_viewer.clear()

    def fit_to_view(self):
        """Fit all nodes in the view."""
        all_nodes = self.graph.all_nodes()
        if not all_nodes:
            return

        viewer = self.graph.viewer()
        if not viewer:
            return

        from PySide6.QtCore import QRectF
        rect = QRectF()
        for node in all_nodes:
            if node.view:
                rect = rect.united(node.view.sceneBoundingRect())

        if rect.isNull():
            return

        padding = 50
        rect.adjust(-padding, -padding, padding, padding)
        viewer._scene_range = rect
        viewer._update_scene()

    def delete_selected(self):
        """Delete selected nodes."""
        selected = self.graph.selected_nodes()
        if selected:
            for node in selected:
                self.graph.remove_node(node)
        if self.app.auto_process:
            self.process_graph()

    def on_port_connected(self, input_port, output_port):
        """Handle port connection."""
        node = input_port.node()
        self.update_node_property_state(node)
        if self.app.auto_process:
            self.process_graph()

    def on_port_disconnected(self, input_port, output_port):
        """Handle port disconnection."""
        node = input_port.node()
        self.update_node_property_state(node)
        if self.app.auto_process:
            self.process_graph()

    def on_node_double_clicked(self, node_id):
        """Handle node double-click - show properties dialog."""
        node = self.graph.get_node_by_id(node_id)
        if node:
            self.show_properties_dialog(node)

    def on_property_changed(self, node_id, prop_name, prop_value):
        """Handle property change - trigger auto-process."""
        if self.app.auto_process:
            self.process_graph()

    def show_properties_dialog(self, node):
        """Show a properties dialog for the node."""
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle(f'Properties: {node.name()}')
        dialog.setMinimumWidth(350)

        layout = QtWidgets.QVBoxLayout(dialog)

        # Create property widgets
        props = node.model.custom_properties
        widgets = {}

        for prop_name, prop_value in props.items():
            row = QtWidgets.QHBoxLayout()
            label = QtWidgets.QLabel(prop_name + ':')
            label.setMinimumWidth(80)
            row.addWidget(label)

            # Check if this property has a connected port
            is_connected = False
            if hasattr(node, 'PORT_TO_PROPERTY'):
                for port_name, mapped_prop in node.PORT_TO_PROPERTY.items():
                    if mapped_prop == prop_name:
                        input_port = node.get_input(port_name)
                        if input_port and input_port.connected_ports():
                            is_connected = True
                            break

            if is_connected:
                edit = QtWidgets.QLineEdit('(connected)')
                edit.setEnabled(False)
            else:
                edit = QtWidgets.QLineEdit(str(prop_value))
            widgets[prop_name] = edit
            row.addWidget(edit)
            layout.addLayout(row)

        # Buttons
        btn_layout = QtWidgets.QHBoxLayout()
        ok_btn = QtWidgets.QPushButton('OK')
        cancel_btn = QtWidgets.QPushButton('Cancel')
        btn_layout.addStretch()
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        def apply_changes():
            for prop_name, widget in widgets.items():
                if widget.isEnabled():
                    node.set_property(prop_name, widget.text())
            dialog.accept()
            if self.app.auto_process:
                self.process_graph()

        ok_btn.clicked.connect(apply_changes)
        cancel_btn.clicked.connect(dialog.reject)

        dialog.exec()

    def update_node_property_state(self, node):
        """Update property widget states based on port connections."""
        if not hasattr(node, 'PORT_TO_PROPERTY'):
            return

        for port_name, prop_name in node.PORT_TO_PROPERTY.items():
            input_port = node.get_input(port_name)
            widget = node.view.get_widget(prop_name) if node.view else None

            if input_port and input_port.connected_ports():
                if widget:
                    widget.setEnabled(False)
                    widget.set_value('(connected)')
            else:
                if widget:
                    widget.setEnabled(True)
                    if widget.get_value() == '(connected)':
                        current = node.get_property(prop_name)
                        if current == '(connected)':
                            widget.set_value('00')
                        else:
                            widget.set_value(current)

    def update_all_node_properties(self):
        """Update all nodes' property states after loading."""
        for node in self.graph.all_nodes():
            self.update_node_property_state(node)


class ByteFlowApp:
    """Main application class."""

    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.app.setApplicationName('ByteFlow')

        # Auto-process flag
        self.auto_process = True

        # Tab counter for naming
        self._tab_counter = 0

        # Create main window
        self.window = QtWidgets.QMainWindow()
        self.window.setWindowTitle('ByteFlow - Node-based Data Transformation')
        self.window.setGeometry(100, 100, 1400, 900)

        # Create central widget
        central = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)

        # Tab widget
        self.tab_widget = QtWidgets.QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        layout.addWidget(self.tab_widget)

        # Button bar
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.setContentsMargins(5, 5, 5, 5)

        new_tab_btn = QtWidgets.QPushButton('New Tab (Ctrl+T)')
        new_tab_btn.clicked.connect(self.new_tab)
        btn_layout.addWidget(new_tab_btn)

        process_btn = QtWidgets.QPushButton('Process (F5)')
        process_btn.clicked.connect(self.process_current)
        btn_layout.addWidget(process_btn)

        # Auto-process checkbox (enabled by default)
        self.auto_checkbox = QtWidgets.QCheckBox('Auto')
        self.auto_checkbox.setToolTip('Automatically process when changes are made')
        self.auto_checkbox.setChecked(True)
        self.auto_checkbox.toggled.connect(self.on_auto_process_toggled)
        btn_layout.addWidget(self.auto_checkbox)

        clear_btn = QtWidgets.QPushButton('Clear')
        clear_btn.clicked.connect(self.clear_current)
        btn_layout.addWidget(clear_btn)

        fit_btn = QtWidgets.QPushButton('Fit View (F)')
        fit_btn.clicked.connect(self.fit_current)
        btn_layout.addWidget(fit_btn)

        btn_layout.addSpacing(20)

        save_btn = QtWidgets.QPushButton('Save')
        save_btn.clicked.connect(self.save_current)
        btn_layout.addWidget(save_btn)

        load_btn = QtWidgets.QPushButton('Load')
        load_btn.clicked.connect(self.load_graph)
        btn_layout.addWidget(load_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self.window.setCentralWidget(central)

        # Setup shortcuts
        self._setup_shortcuts()

        # Create initial tab with demo graph
        self.new_tab(demo=True)

    def _setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        # New tab
        new_tab_action = QtGui.QAction(self.window)
        new_tab_action.setShortcut(QtGui.QKeySequence('Ctrl+T'))
        new_tab_action.triggered.connect(self.new_tab)
        self.window.addAction(new_tab_action)

        # Close tab
        close_tab_action = QtGui.QAction(self.window)
        close_tab_action.setShortcut(QtGui.QKeySequence('Ctrl+W'))
        close_tab_action.triggered.connect(self.close_current_tab)
        self.window.addAction(close_tab_action)

        # Process
        process_action = QtGui.QAction(self.window)
        process_action.setShortcut(QtGui.QKeySequence('F5'))
        process_action.triggered.connect(self.process_current)
        self.window.addAction(process_action)

        # Fit view
        fit_action = QtGui.QAction(self.window)
        fit_action.setShortcut(QtGui.QKeySequence('F'))
        fit_action.triggered.connect(self.fit_current)
        self.window.addAction(fit_action)

        # Save
        save_action = QtGui.QAction(self.window)
        save_action.setShortcut(QtGui.QKeySequence.Save)
        save_action.triggered.connect(self.save_current)
        self.window.addAction(save_action)

        # Load
        load_action = QtGui.QAction(self.window)
        load_action.setShortcut(QtGui.QKeySequence.Open)
        load_action.triggered.connect(self.load_graph)
        self.window.addAction(load_action)

        # Delete
        delete_action = QtGui.QAction(self.window)
        delete_action.setShortcuts([QtGui.QKeySequence.Delete, QtGui.QKeySequence('Backspace')])
        delete_action.triggered.connect(self.delete_selected_current)
        self.window.addAction(delete_action)

    def current_tab(self) -> GraphTab:
        """Get the current tab."""
        return self.tab_widget.currentWidget()

    def new_tab(self, demo=False):
        """Create a new tab."""
        self._tab_counter += 1
        tab = GraphTab(self)
        name = f'Graph {self._tab_counter}'
        self.tab_widget.addTab(tab, name)
        self.tab_widget.setCurrentWidget(tab)

        if demo:
            self._create_demo_graph(tab)

        return tab

    def close_tab(self, index):
        """Close a tab by index."""
        if self.tab_widget.count() > 1:
            widget = self.tab_widget.widget(index)
            self.tab_widget.removeTab(index)
            widget.deleteLater()
        else:
            # Don't close the last tab, just clear it
            self.current_tab().clear_graph()

    def close_current_tab(self):
        """Close the current tab."""
        self.close_tab(self.tab_widget.currentIndex())

    def on_auto_process_toggled(self, checked):
        """Handle auto-process checkbox toggle."""
        self.auto_process = checked
        if checked:
            tab = self.current_tab()
            if tab:
                tab.process_graph()

    def process_current(self):
        """Process the current tab's graph."""
        tab = self.current_tab()
        if tab:
            tab.process_graph()

    def clear_current(self):
        """Clear the current tab's graph."""
        tab = self.current_tab()
        if tab:
            tab.clear_graph()

    def fit_current(self):
        """Fit view in the current tab."""
        tab = self.current_tab()
        if tab:
            tab.fit_to_view()

    def delete_selected_current(self):
        """Delete selected nodes in the current tab."""
        tab = self.current_tab()
        if tab:
            tab.delete_selected()

    def save_current(self):
        """Save the current tab's graph."""
        tab = self.current_tab()
        if not tab:
            return

        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self.window,
            'Save Graph',
            '',
            'ByteFlow Graph (*.json);;All Files (*)'
        )
        if file_path:
            if not file_path.endswith('.json'):
                file_path += '.json'
            tab.graph.save_session(file_path)
            # Update tab name
            import os
            name = os.path.basename(file_path)
            self.tab_widget.setTabText(self.tab_widget.currentIndex(), name)

    def load_graph(self):
        """Load a graph into a new tab."""
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self.window,
            'Load Graph',
            '',
            'ByteFlow Graph (*.json);;All Files (*)'
        )
        if file_path:
            tab = self.new_tab()
            tab.graph.load_session(file_path)
            # Update tab name
            import os
            name = os.path.basename(file_path)
            self.tab_widget.setTabText(self.tab_widget.currentIndex(), name)
            QtCore.QTimer.singleShot(100, tab.update_all_node_properties)
            if self.auto_process:
                QtCore.QTimer.singleShot(150, tab.process_graph)

    def _create_demo_graph(self, tab):
        """Create a demo graph in the given tab."""
        text_input = tab.graph.create_node('byteflow.io.TextInputNode')
        text_input.set_name('Input Text')
        text_input.set_pos(-200, 0)
        text_input.set_property('text_data', 'Hello ByteFlow!')

        xor_node = tab.graph.create_node('byteflow.crypto.XORNode')
        xor_node.set_name('XOR Encrypt')
        xor_node.set_pos(100, 0)
        xor_node.set_property('key_hex', 'FF')

        output = tab.graph.create_node('byteflow.io.OutputNode')
        output.set_name('Result')
        output.set_pos(400, 0)

        text_input.output(0).connect_to(xor_node.input(0))
        xor_node.output(0).connect_to(output.input(0))

        QtCore.QTimer.singleShot(100, tab.fit_to_view)

    def run(self):
        """Run the application."""
        self.window.show()
        return self.app.exec()


def main():
    app = ByteFlowApp()
    sys.exit(app.run())


if __name__ == '__main__':
    main()
