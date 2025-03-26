#%%
"""
This module provides classes and methods for parsing text into hierarchical
source blocks, allowing nested structures with specified keywords, child
matching, and indentation-based relationships.
"""
from __future__ import annotations
import re
from abc import ABC
from functools import cached_property
from re import Pattern, compile, escape
from typing import Any, Callable, Dict, List, NamedTuple, Optional, Self, Type

from protobase import Object


class SourceBlock[T = Any](Object):
    """
    Represents a block of source code or text with a specific keyword, 
    content, and potentially nested child blocks.
    
    The SourceBlock stores both raw text content and a structured tree
    of child blocks, enabling hierarchical parsing of indented, keyword-based
    text formats.
    
    Type Parameters:
        T: The return type of the processor function, defaulting to Any.
    
    Attributes:
        spec: The specification object that defined this block
        content: The raw content text of this block
        children: List of nested child blocks
    """

    type Processor[T = Any] = Callable[[SourceBlock[T]], T]
    """
    Type definition for processor functions that can be applied to source blocks.
    
    A processor transforms a SourceBlock into a value of type T.
    """

    class Spec[T = Any](Object):
        """
        Defines the specification for a particular source block type.
        
        Each specification includes a keyword for identification, a processor
        function to handle the content, and optional child specifications for
        deeper nesting.
        
        Type Parameters:
            T: The return type of the processor function, defaulting to Any.
            
        Attributes:
            keyword: The regular expression pattern used to identify this block type
            processor: The function that processes blocks of this type
            subspecs: List of child specifications that can be nested within this block
            increase_indent: Boolean indicating whether this block expects increased indentation
        """
        keyword: str  
        processor: SourceBlock.Processor[T]
        subspecs: List[SourceBlock.Spec[Any]] = []
        increase_indent: bool = False

        @cached_property
        def child_pattern(self) -> Pattern:
            """
            Compiles a combined regex pattern from all child specifications.
            
            Returns:
                A compiled regex pattern that matches any of the child keywords.
            """
            if not self.subspecs:
                return compile(r"^$")  # Will never match
            
            return compile(
                "|".join(f"({escape(subspec.keyword)})" for subspec in self.subspecs)
            )

        def match_children(self, line:str) -> Optional[SourceBlock.Spec]:
            """
            Checks if a line matches any child specification keywords.
            
            Args:
                line: The line to check against child patterns
                
            Returns:
                The matching child specification if found, otherwise None
            """
            if not self.subspecs:
                return None

            if m := self.child_pattern.match(line):
                return self.subspecs[m.lastindex - 1] 
            return None

        def __repr__(self):
            """
            Returns a string representation of this specification.
            
            Returns:
                A string showing the spec's keyword
            """
            return f"<BlockSpec {self.keyword}>"

    spec: Spec[T]
    content: str
    children: List[SourceBlock[Any]]

    def __repr__(self):
        """
        Returns a string representation of this SourceBlock.
        
        Returns:
            A string showing the block's keyword and child count
        """
        return f"<SourceBlock {self.spec.keyword} {len(self.children)} children>"

    @cached_property
    def processed(self) -> T:
        """
        Processes the block by calling the associated processor function.
        
        Returns:
            The result of applying the processor function to this block
        """
        return self.spec.processor(self)

    class Parser(Object):
        """
        Orchestrates the parsing of text into structured SourceBlock objects.
        
        The parser manages a stack mechanism for handling nested blocks based on
        indentation and matched keywords.
        """
        
        class StackEntry(NamedTuple):
            """
            Stores the state for a single layer of the block stack.
            
            Attributes:
                spec: The specification for this stack entry
                ident: The indentation string for this level
                content: List of content lines for this block
                children: List of child blocks
            """
            spec: SourceBlock.Spec
            ident: str
            content: list[str]
            children: List[SourceBlock]

            def block(self):
                """
                Creates a SourceBlock from the stored information.
                
                Returns:
                    A complete SourceBlock object with content and children
                """
                return SourceBlock(
                    spec=self.spec,
                    content='\n'.join(c[len(self.ident):] for c in self.content),
                    children=self.children,
                )

        stack: list[SourceBlock.Parser.StackEntry]

        @classmethod
        def from_root(cls, root_spec: SourceBlock.Spec):
            """
            Creates a parser instance with a root specification.
            
            Args:
                root_spec: The specification serving as the root block
                
            Returns:
                A Parser instance initialized with the root specification
            """
            return cls(
                stack=[cls.StackEntry(spec=root_spec, ident="", content=[], children=[])]
            )

        @property
        def current_entry(self):
            """
            Retrieves the topmost entry in the parsing stack.
            
            Returns:
                The current StackEntry object
            """
            return self.stack[-1]

        def reversed_stack(self):
            """
            Yields stack entries from top to bottom in reverse order.
            
            This allows inspection of previous stack levels for potential matching.
            
            Yields:
                Tuples of (index, StackEntry) for each level
            """
            offset = len(self.stack) - 1
            while offset >= 0:
                yield offset, self.stack[offset]
                offset -= 1

        def vaccum_stack(self, idx: int=0):
            """
            Collapses the stack above the given index into child blocks.
            
            This method converts higher-level stack entries into SourceBlock objects
            and attaches them to the specified level's children.
            
            Args:
                idx: The index up to which the stack is maintained
            """
            while len(self.stack) > (idx+1):
                block = self.stack.pop().block()
                self.current_entry.children.append(block)

        def parse(self, buffer: str) -> SourceBlock:
            """
            Parses a multiline string buffer into structured SourceBlock objects.
            
            This builds a nested hierarchy based on matched keywords and indentation,
            handling line matching and stack management within a single method.
            
            Args:
                buffer: The multiline string to parse
                
            Returns:
                A fully constructed SourceBlock representing the parsed structure
            """
            for line_n, line in enumerate(buffer.splitlines()):

                line_matched = False
                
                for idx, entry in self.reversed_stack():
                    stripped_line = line.lstrip(' \t')
                    identation = line[:len(line) - len(stripped_line)]
                    if not identation.startswith(entry.ident):
                        continue

                    increase_ident = len(identation[len(self.current_entry.ident):]) > 0

                    if (subspec := entry.spec.match_children(stripped_line)) and \
                        entry.spec.increase_indent == increase_ident:

                        line_matched = True

                        self.vaccum_stack(idx)

                        self.stack.append(
                            self.StackEntry(
                                spec=subspec,
                                ident=identation,
                                content=[line],
                                children=[],
                            )
                        )
                        # Match found and processed, no need to continue checking stack
                        break

                if not line_matched:
                    self.current_entry.content.append(line)
                

            self.vaccum_stack(0)
            return self.current_entry.block()



if __name__ == "__main__":

    def srcblock_processor(block: SourceBlock):
        return block

    doc_spec = SourceBlock.Spec(
        keyword="#",
        processor=srcblock_processor,
    )

    mod_spec = SourceBlock.Spec(
        keyword="mod",
        processor=srcblock_processor,
        subspecs=[
            SourceBlock.Spec(
                keyword="fn",
                processor=srcblock_processor,
                subspecs=[
                    SourceBlock.Spec(
                        keyword="takes:",
                        processor=srcblock_processor,
                        increase_indent=True,
                        subspecs=[
                            SourceBlock.Spec(
                                keyword="-",
                                processor=srcblock_processor,
                                subspecs=[],
                            ),
                        ],
                    ),
                    SourceBlock.Spec(
                        keyword="returns",
                        processor=srcblock_processor,
                        subspecs=[],
                    ),
                    SourceBlock.Spec(
                        keyword="suite:",
                        processor=srcblock_processor,
                        increase_indent=True,
                        subspecs=[],
                    ),
                ],
            ),
            SourceBlock.Spec(
                keyword="class",
                processor=srcblock_processor,
                subspecs=[],
            ),
        ],
    )

    parser = SourceBlock.Parser.from_root(mod_spec)

    block = parser.parse(
        """

fn init
# initializes the application and 
  sets up configurations.

takes:
    - config: Config
      # Configuration object containing application settings.

returns Void


# No return value.

suite:
    ...

fn compute
#    Computes complex values based on an operation mode.
takes:
    - a: Number
        #     The first operand.
    - b: Number
        #     The second operand.
    - mode: String
        #    Operation mode; valid values include "add", "subtract", "multiply".
returns Number
#   The computed result.
suite:
    if mode == "add":
         return a + b
    elif mode == "subtract":
         return a - b
    elif mode == "multiply":
         return a * b
    else:
         error: Unsupported operation mode

fn recursiveFactorial
#    Computes the factorial of a number recursively.
takes:
    - n: Number
        # A non-negative integer.
returns Number
# Factorial of n.
suite:
    if n <= 1:
         return 1
    else:
         return n * recursiveFactorial(n - 1)

fn divide
#    Divides two numbers and handles division by zero.
takes:
    - numerator: Number
        # The numerator.
    - denominator: Number
        # The denominator; must not be zero.
returns Number
#    The result of the division.
suite:
    if denominator == 0:
         error: Division by zero encountered.
    else:
         return numerator / denominator
"""
    )
