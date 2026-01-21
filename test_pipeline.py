#!/usr/bin/env python3
"""Test script for the headless pipeline executor."""

import os
import sys
import tempfile

# Ensure we can import from the current directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pipeline import Pipeline, load
from nodes import OutputNode


def test_programmatic_pipeline():
    """Test creating and executing a pipeline programmatically."""
    print("Test 1: Programmatic pipeline creation")

    pipeline = Pipeline()

    # Create a simple graph: TextInput -> XOR -> Output
    text_input = pipeline.graph.create_node('byteflow.io.TextInputNode')
    text_input.set_name('Input')
    text_input.set_property('text_data', 'Hello')

    key_input = pipeline.graph.create_node('byteflow.io.HexInputNode')
    key_input.set_name('Key')
    key_input.set_property('hex_data', 'FF')

    xor_node = pipeline.graph.create_node('byteflow.crypto.XORNode')
    xor_node.set_name('XOR')

    output = pipeline.graph.create_node('byteflow.io.OutputNode')
    output.set_name('Result')

    # Connect nodes
    text_input.output(0).connect_to(xor_node.input(0))  # data
    key_input.output(0).connect_to(xor_node.input(1))   # key
    xor_node.output(0).connect_to(output.input(0))

    # Execute
    results = pipeline.execute()

    print(f"  Input: 'Hello' XOR 0xFF")
    print(f"  Output: {results['Result'].hex()}")

    # Verify: 'Hello' XOR 0xFF should give specific bytes
    expected = bytes(b ^ 0xFF for b in b'Hello')
    assert results['Result'] == expected, f"Expected {expected.hex()}, got {results['Result'].hex()}"
    print("  PASSED\n")


def test_save_and_load():
    """Test saving and loading a graph."""
    print("Test 2: Save and load graph")

    # Create a pipeline with a graph
    pipeline1 = Pipeline()

    text_input = pipeline1.graph.create_node('byteflow.io.TextInputNode')
    text_input.set_name('Input')
    text_input.set_property('text_data', 'Test')

    b64_node = pipeline1.graph.create_node('byteflow.crypto.Base64Node')
    b64_node.set_name('Base64')
    b64_node.set_property('mode', 'Encode')

    output = pipeline1.graph.create_node('byteflow.io.OutputNode')
    output.set_name('Output')

    text_input.output(0).connect_to(b64_node.input(0))
    b64_node.output(0).connect_to(output.input(0))

    # Save to temp file
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
        temp_path = f.name

    try:
        pipeline1.save(temp_path)
        print(f"  Saved to: {temp_path}")

        # Load into new pipeline
        pipeline2 = load(temp_path)
        results = pipeline2.execute()

        print(f"  Input: 'Test' -> Base64 Encode")
        print(f"  Output: {results['Output'].decode('utf-8')}")

        import base64
        expected = base64.b64encode(b'Test')
        assert results['Output'] == expected, f"Expected {expected}, got {results['Output']}"
        print("  PASSED\n")

    finally:
        os.unlink(temp_path)


def test_set_inputs():
    """Test setting inputs dynamically."""
    print("Test 3: Dynamic input setting")

    pipeline = Pipeline()

    # Create graph
    text_input = pipeline.graph.create_node('byteflow.io.TextInputNode')
    text_input.set_name('My Input')
    text_input.set_property('text_data', 'default')

    output = pipeline.graph.create_node('byteflow.io.OutputNode')
    output.set_name('Result')

    text_input.output(0).connect_to(output.input(0))

    # Execute with default
    results = pipeline.execute()
    assert results['Result'] == b'default'
    print(f"  Default input: {results['Result']}")

    # Execute with custom input using set_input
    pipeline.set_input('My Input', b'custom1')
    results = pipeline.execute()
    assert results['Result'] == b'custom1'
    print(f"  Custom input via set_input: {results['Result']}")

    # Execute with data parameter
    results = pipeline.execute(b'custom2')
    assert results['Result'] == b'custom2'
    print(f"  Custom input via execute(): {results['Result']}")

    # Execute with kwargs (underscore -> space)
    results = pipeline.execute(My_Input=b'custom3')
    assert results['Result'] == b'custom3'
    print(f"  Custom input via kwargs: {results['Result']}")

    print("  PASSED\n")


def test_callable():
    """Test calling pipeline directly."""
    print("Test 4: Callable pipeline")

    pipeline = Pipeline()

    text_input = pipeline.graph.create_node('byteflow.io.TextInputNode')
    text_input.set_name('Input')

    reverse = pipeline.graph.create_node('byteflow.util.ReverseNode')
    reverse.set_name('Reverse')

    output = pipeline.graph.create_node('byteflow.io.OutputNode')
    output.set_name('Result')

    text_input.output(0).connect_to(reverse.input(0))
    reverse.output(0).connect_to(output.input(0))

    # Call directly
    results = pipeline(b'Hello')
    assert results['Result'] == b'olleH'
    print(f"  Input: 'Hello' -> Reverse -> '{results['Result'].decode()}'")
    print("  PASSED\n")


def test_multiple_outputs():
    """Test graph with multiple output nodes."""
    print("Test 5: Multiple outputs")

    pipeline = Pipeline()

    text_input = pipeline.graph.create_node('byteflow.io.TextInputNode')
    text_input.set_name('Input')
    text_input.set_property('text_data', 'Test')

    # Two different transforms
    b64_node = pipeline.graph.create_node('byteflow.crypto.Base64Node')
    b64_node.set_property('mode', 'Encode')

    reverse_node = pipeline.graph.create_node('byteflow.util.ReverseNode')

    output1 = pipeline.graph.create_node('byteflow.io.OutputNode')
    output1.set_name('Base64 Output')

    output2 = pipeline.graph.create_node('byteflow.io.OutputNode')
    output2.set_name('Reversed Output')

    text_input.output(0).connect_to(b64_node.input(0))
    text_input.output(0).connect_to(reverse_node.input(0))
    b64_node.output(0).connect_to(output1.input(0))
    reverse_node.output(0).connect_to(output2.input(0))

    results = pipeline.execute()

    print(f"  Input: 'Test'")
    print(f"  Base64 Output: {results['Base64 Output'].decode()}")
    print(f"  Reversed Output: {results['Reversed Output'].decode()}")

    import base64
    assert results['Base64 Output'] == base64.b64encode(b'Test')
    assert results['Reversed Output'] == b'tseT'
    print("  PASSED\n")


if __name__ == '__main__':
    print("=" * 50)
    print("ByteFlow Pipeline Tests")
    print("=" * 50 + "\n")

    test_programmatic_pipeline()
    test_save_and_load()
    test_set_inputs()
    test_callable()
    test_multiple_outputs()

    print("=" * 50)
    print("All tests passed!")
    print("=" * 50)
