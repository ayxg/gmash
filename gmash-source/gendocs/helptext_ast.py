"""
#@doc-------------------------------------------------------------------------#
SPDX-License-Identifier: AGPL-3.0-or-later
Copyright(c) 2025 Anton Yashchenko
#-----------------------------------------------------------------------------#
@project: [gmash] Git Smash
@author(s): Anton Yashchenko
@website: https://www.acpp.dev
#-----------------------------------------------------------------------------#
@file `helptext_ast.py`
@created: 2025/09/13
@brief Command Line Help Notation token and abstract syntax tree.
#-----------------------------------------------------------------------------#
"""
import enum
import typing

class Tk(enum.Enum):
    """ Token type for an `Ast` node.
        To simplify parsing logic: there is no tokenizer step.
    """
    NOTHING = enum.auto()           # Empty node
    POSION = enum.auto()            # Error node, value is the error message
    SYNTAX = enum.auto()            # Root node
    USAGE = enum.auto()             # Usage line
    BRIEF = enum.auto()             # Brief description paragraph
    SECTION = enum.auto()           # Section with title
    TEXT_LINE = enum.auto()         # A line of text
    PARAGRAPH = enum.auto()         # One or more paragraphs of equally indented lines.
    SHELL_IDENT = enum.auto()       # Shell variable identifier
    SHORT_FLAG = enum.auto()        # Short flag, e.g. -f
    SHORT_FLAG_IDENT = enum.auto()  # Short flag identifier, e.g. f
    LONG_FLAG = enum.auto()         # Long flag, e.g. --force
    LONG_FLAG_IDENT = enum.auto()   # Long flag identifier, e.g. force
    OPTIONAL_ARG = enum.auto()      # Optional argument, e.g. [file]
    REQUIRED_ARG = enum.auto()      # Required argument, e.g. <file>
    ARGUMENT = enum.auto()          # An argument with flags and description
    ARGUMENT_LIST = enum.auto()     # A list of arguments

class Ast:
    """ Abstract syntax tree. """
    def __init__(self,
                             tk: Tk = Tk.NOTHING,
                             value: typing.Optional[str] = None,
                             line: int = 0,
                             col: int = 0,
                             end_line: int = 0,
                             end_col: int = 0,
                             branches: typing.Optional[typing.List['Ast']] = None
                             ) -> None:
        self.tk: Tk = tk
        self.value: typing.Optional[str] = value
        self.line: int = line
        self.col: int = col
        self.end_line: int = end_line
        self.end_col: int = end_col
        self.branches: typing.List[Ast] = branches if branches is not None else []

    def append(self, br: 'Ast') -> 'Ast':
        """ Append a branch to this AST node and return the appended branch. """
        self.branches.append(br)
        return self.branches[-1]

    def __repr__(self) -> str:
        return f'Ast({self.tk}, {self.value}, {self.branches})'

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Ast):
            return NotImplemented
        return (self.tk == other.tk and
                self.value == other.value and
                #self.line == other.line and
                #self.col == other.col and
                #self.end_line == other.end_line and
                #self.end_col == other.end_col and
                self.branches == other.branches)

# TODO: (pylint disable doesnt seem to work...?)
# pylint: disable=W0613
def print_ascii_tree(astnode: Ast, prefix: str = "", is_last: bool = True) -> None:
    # pylint: enable=W0613
    """Print the AST as a compact ASCII tree with boxes and connection lines"""
    content = astnode.tk.name + " : " + astnode.value if astnode.value is not None else astnode.tk.name
    lines = content.split('\n')
    max_width = max(len(line) for line in lines) if lines else 0

    box_lines = []
    box_lines.append("┌" + "─" * (max_width + 2) + "┐")
    for line in lines:
        box_lines.append("│ " + line.ljust(max_width) + " │")
    box_lines.append("└" + "─" * (max_width + 2) + "┘")

    for i, line in enumerate(box_lines):
        print(prefix + line)

    if astnode.branches:
        for i, child in enumerate(astnode.branches):
            is_last_child = (i == len(astnode.branches) - 1)

            # Print connection lines
            if is_last_child:
                print(prefix + "    │")
                print(prefix + "    └──────────┐")
            else:
                print(prefix + "    │")
                print(prefix + "    ├──────────┐")

            # Calculate child prefix
            child_prefix = prefix
            if is_last_child:
                child_prefix += "             "  # Align with the end of connection
            else:
                child_prefix += "    │         "  # Continue the vertical line

            # Recursive call to the function (not method)
            print_ascii_tree(child, child_prefix, is_last_child)

def print_ascii_tree_simple(astnode: Ast, indent: int = 0) -> None:
    """Simple recursive AST printer with ASCII art"""
    indent_str = "    " * indent
    connector = "└── " if indent > 0 else ""

    # Node content
    content = astnode.tk.name + ': ' + astnode.value if astnode.value is not None else astnode.tk.name
    print(f"{indent_str}{connector}{content}")

    # Print position info (optional)
    if astnode.line > 0:
        print(f"{indent_str}    \
            [L{astnode.line}:{astnode.col}-L{astnode.end_line}:{astnode.end_col}]")

    # Recursively print children
    for child in astnode.branches:
        print_ascii_tree_simple(child, indent + 1)

def print_ast_detailed(node, indent=0):
    """More detailed recursive AST printer"""
    if node is None:
        return

    indent_str = "  " * indent
    arrow = "├── " if indent > 0 else ""

    # Build node description
    parts = []
    parts.append(f"{node.type.name}")
    if node.value is not None:
        parts.append(f"value={repr(node.value)}")
    parts.append(f"pos=({node.line}:{node.col}-{node.end_line}:{node.end_col})")

    print(f"{indent_str}{arrow}{', '.join(parts)}")

    # Print branches
    for i, branch in enumerate(node.branches):
        if i == len(node.branches) - 1:
            # Last branch
            print_ast_detailed(branch, indent + 1)
        else:
            print_ast_detailed(branch, indent + 1)
