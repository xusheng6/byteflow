"""Headless pipeline executor for ByteFlow graphs.

This module allows you to load and execute ByteFlow transformation graphs
from Python scripts without the GUI.

Example usage:
    from pipeline import Pipeline

    # Load a saved graph
    pipeline = Pipeline('my_transform.json')

    # Execute with input data
    results = pipeline.execute(b'Hello World')

    # Results is a dict mapping output node names to their data
    print(results)
"""

import os
import sys

# Set Qt to offscreen mode before importing Qt modules
if 'QT_QPA_PLATFORM' not in os.environ:
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'

from PySide6.QtWidgets import QApplication
from NodeGraphQt import NodeGraph

from nodes import (
    XORNode, RC4Node, AESNode, Base64Node,
    MD5Node, SHA1Node, SHA256Node,
    URLEncodeNode, HexEncodeNode, ROTNode, AtbashNode,
    ReverseNode, ZlibNode, GzipNode, SubstringNode, RepeatNode, TakeBytesNode,
    HexInputNode, TextInputNode, FileInputNode, OutputNode
)

# All node classes for registration
ALL_NODE_CLASSES = [
    XORNode, RC4Node, AESNode, Base64Node,
    MD5Node, SHA1Node, SHA256Node,
    URLEncodeNode, HexEncodeNode, ROTNode, AtbashNode,
    ReverseNode, ZlibNode, GzipNode, SubstringNode, RepeatNode, TakeBytesNode,
    HexInputNode, TextInputNode, FileInputNode, OutputNode,
]

# Global QApplication instance (Qt requires exactly one)
_app = None


def _ensure_app():
    """Ensure a QApplication instance exists."""
    global _app
    if _app is None:
        _app = QApplication.instance()
        if _app is None:
            _app = QApplication(sys.argv)


class Pipeline:
    """A headless executor for ByteFlow transformation graphs.

    Load a saved graph and execute it programmatically without the GUI.
    """

    def __init__(self, graph_path: str = None):
        """Initialize the pipeline.

        Args:
            graph_path: Optional path to a saved .json graph file to load.
        """
        _ensure_app()

        self.graph = NodeGraph()
        for node_class in ALL_NODE_CLASSES:
            self.graph.register_node(node_class)

        if graph_path:
            self.load(graph_path)

    def load(self, graph_path: str):
        """Load a graph from a JSON file.

        Args:
            graph_path: Path to the saved .json graph file.
        """
        self.graph.load_session(graph_path)

    def save(self, graph_path: str):
        """Save the current graph to a JSON file.

        Args:
            graph_path: Path to save the graph to.
        """
        self.graph.save_session(graph_path)

    def get_input_nodes(self) -> dict:
        """Get all input nodes in the graph.

        Returns:
            Dict mapping node names to node objects.
        """
        inputs = {}
        for node in self.graph.all_nodes():
            if isinstance(node, (HexInputNode, TextInputNode, FileInputNode)):
                inputs[node.name()] = node
        return inputs

    def get_output_nodes(self) -> dict:
        """Get all output nodes in the graph.

        Returns:
            Dict mapping node names to node objects.
        """
        outputs = {}
        for node in self.graph.all_nodes():
            if isinstance(node, OutputNode):
                outputs[node.name()] = node
        return outputs

    def set_input(self, node_name: str, data: bytes):
        """Set data on a specific input node by name.

        Args:
            node_name: The name of the input node.
            data: The data to set (bytes).

        Raises:
            KeyError: If no input node with that name exists.
            TypeError: If the node type doesn't support the data format.
        """
        inputs = self.get_input_nodes()
        if node_name not in inputs:
            raise KeyError(f"No input node named '{node_name}'. "
                          f"Available: {list(inputs.keys())}")

        node = inputs[node_name]

        if isinstance(node, TextInputNode):
            node.set_property('text_data', data.decode('utf-8'))
        elif isinstance(node, HexInputNode):
            node.set_property('hex_data', data.hex())
        elif isinstance(node, FileInputNode):
            # For file input, data should be a path string
            node.set_property('file_path', data.decode('utf-8'))

    def set_inputs(self, **inputs):
        """Set multiple inputs by name.

        Args:
            **inputs: Keyword arguments mapping node names to data (bytes).

        Example:
            pipeline.set_inputs(
                Input_Text=b'Hello',
                Key=b'\\x42'
            )
        """
        for name, data in inputs.items():
            # Replace underscores with spaces for convenience
            # (node names often have spaces, but kwargs can't)
            name = name.replace('_', ' ')
            self.set_input(name, data)

    def execute(self, data: bytes = None, **inputs) -> dict:
        """Execute the pipeline and return outputs.

        Args:
            data: Optional data to set on the first TextInputNode found.
            **inputs: Named inputs to set (node_name=data).

        Returns:
            Dict mapping output node names to their result data (bytes).

        Example:
            # Simple usage with single input
            results = pipeline.execute(b'Hello World')

            # With named inputs
            results = pipeline.execute(Input_Text=b'Hello', Key=b'\\x42')
        """
        # Set named inputs
        if inputs:
            self.set_inputs(**inputs)

        # Set default input if provided
        if data is not None:
            # Find the first TextInputNode and set data on it
            for node in self.graph.all_nodes():
                if isinstance(node, TextInputNode):
                    node.set_property('text_data', data.decode('utf-8'))
                    break

        # Process all output nodes and collect results
        results = {}
        for node in self.graph.all_nodes():
            if isinstance(node, OutputNode):
                node.process()
                results[node.name()] = node.get_data()

        return results

    def __call__(self, data: bytes = None, **inputs) -> dict:
        """Allow calling the pipeline directly.

        Example:
            results = pipeline(b'Hello World')
        """
        return self.execute(data, **inputs)


def load(graph_path: str) -> Pipeline:
    """Convenience function to load a pipeline from a file.

    Args:
        graph_path: Path to the saved .json graph file.

    Returns:
        A Pipeline instance ready to execute.

    Example:
        from byteflow import pipeline

        p = pipeline.load('my_transform.json')
        results = p(b'Hello World')
    """
    return Pipeline(graph_path)
