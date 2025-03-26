import unittest
from protobase.sourcebase.sourceblock import (
    SourceBlockSpec, SourceBlock, BlockParser, parse_source_blocks, parse_source_code
)


class TestSourceBlockParser(unittest.TestCase):
    """Test cases for the source block parser."""
    
    def test_simple_module_parsing(self):
        """Test parsing a simple module with functions."""
        source = """
mod test
# Test module

fn example
# Example function
takes:
    - a: int
        # First parameter
    - b: int
        # Second parameter
returns int
# Return value
suite:
    return a + b
"""
        parsed = parse_source_code(source)
        
        # Verify structure
        self.assertEqual(len(parsed.children), 1)
        mod_block = parsed.children[0]
        self.assertEqual(mod_block.spec.keyword, "mod")
        self.assertEqual(len(mod_block.children), 1)
        
        # Verify function block
        fn_block = mod_block.children[0]
        self.assertEqual(fn_block.spec.keyword, "fn")
        self.assertEqual(len(fn_block.children), 3)
        
        # Find children by keyword
        takes_block = next((block for block in fn_block.children if block.spec.keyword == "takes:"), None)
        returns_block = next((block for block in fn_block.children if block.spec.keyword == "returns"), None)
        suite_block = next((block for block in fn_block.children if block.spec.keyword == "suite:"), None)
        
        # Verify blocks exist
        self.assertIsNotNone(takes_block)
        self.assertIsNotNone(returns_block)
        self.assertIsNotNone(suite_block)
        
        # Verify parameters
        self.assertEqual(len(takes_block.children), 2)
    
    def test_error_handling(self):
        """Test the parser's ability to handle errors."""
        source = """
mod test
# Test module

fn example
# Example function
takes:
    - a: int
        # First parameter
        
This line is incorrectly indented
        
    - b: int
        # Second parameter
suite:
    return a + b
"""
        parsed = parse_source_code(source)
        
        # Verify we got a module
        self.assertEqual(len(parsed.children), 1)
        mod_block = parsed.children[0]
        
        # Verify we have a function with an error block
        fn_block = mod_block.children[0]
        takes_block = next((block for block in fn_block.children if block.spec.keyword == "takes:"), None)
        self.assertIsNotNone(takes_block)
        
        # Verify we have an error block and parameters within takes block
        error_block = next((block for block in takes_block.children if block.spec.keyword == "error-block"), None)
        self.assertIsNotNone(error_block)
        self.assertEqual(error_block.content, "This line is incorrectly indented")
        
        # Verify we still have the parameter blocks
        param_blocks = [block for block in takes_block.children if block.spec.keyword == "-"]
        self.assertEqual(len(param_blocks), 2)


if __name__ == "__main__":
    unittest.main()
