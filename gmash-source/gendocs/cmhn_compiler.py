"""
Copyright(c) Anton Yashchenko 2025
@created : 2025/09/13
@project CMHN : Command Line Help Notation Parser
@brief Grammar for parsing 'help' manuals displayed by command line applications.
"""

import sys
from typing import List, Optional
from enum import Enum, auto

def is_alnumus(c: str) -> bool:
    return c.isalnum() or c == '_'

def is_alpha(c: str) -> bool:
    return c.isalpha() or c == '_'

def is_numeric(c: str) -> bool:
    return c.isdigit()

def is_indent(c: str) -> bool:
    return c in ("\n    " or "\n  " or "\n\t")

def is_text(c: str) -> bool:
    return c not in ('\n')

def is_dash(c: str) -> bool:
    return c == '-'

def is_newline(c: str) -> bool:
    return c == '\n'

def is_whitespace(c: str) -> bool:
    return c in (' ', '\t')

class Tk(Enum):
    """ Grammar rule types for CMHN ast. """
    NOTHING = auto()    # Empty node
    POSION = auto()     # Error node, value is the error message
    SYNTAX = auto()   # Root node
    USAGE = auto()      # Usage line
    BRIEF = auto()      # Brief description paragraph
    SECTION = auto()    # Section with title
    TEXT_LINE = auto()  # A line of text
    PARAGRAPH = auto()
    SHELL_IDENT = auto() # Shell variable identifier
    SHORT_FLAG = auto()  # Short flag, e.g. -f
    SHORT_FLAG_IDENT = auto() # Short flag identifier, e.g. f
    LONG_FLAG = auto()   # Long flag, e.g. --force
    LONG_FLAG_IDENT = auto() # Long flag identifier, e.g. force
    OPTIONAL_ARG = auto() # Optional argument, e.g. [file]
    REQUIRED_ARG = auto() # Required argument, e.g. <file>
    ARGUMENT = auto()    # An argument with flags and description
    ARGUMENT_LIST = auto() # A list of arguments

class Ast:
    """ Abstract Syntax Tree node for CMHN parser. """
    def __init__(self,
                             tk: Tk = Tk.NOTHING,
                             value: Optional[str] = None,
                             line: int = 0,
                             col: int = 0,
                             end_line: int = 0,
                             end_col: int = 0,
                             branches: Optional[List['Ast']] = None
                             ) -> None:
        self.tk: Tk = tk
        self.value: Optional[str] = value
        self.line: int = line
        self.col: int = col
        self.end_line: int = end_line
        self.end_col: int = end_col
        self.branches: List[Ast] = branches if branches is not None else []

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
                self.line == other.line and
                self.col == other.col and
                self.end_line == other.end_line and
                self.end_col == other.end_col and
                self.branches == other.branches)

def verbose_print(msg: str) -> None:
    """ Print message if verbose_mode is true."""
    if verbose_mode:
        print(msg)

def print_action(msg: str,indent_level = 0) -> None:
    print("    " * indent_level + "└────" * (indent_level != 0) + "\033[92m" + msg +"\033[0m")

def print_error(msg: str,indent_level = 0) -> None:
    print("    " * indent_level + "└────" * (indent_level != 1) + "\033[91m" + msg +"\033[0m")

def debug_print(msg: str) -> None:
    """ Print message if debug_mode is true."""
    if debug_mode:
        print(msg)

def print_help_text() -> None:
    """ Print help text and exit. """
    print(CMNH_TITLE, CMNH_VERSION, CMNH_LICENSE, sep="\n")
    print(CMNH_HELP)
    sys.exit(0)

def print_ascii_tree(astnode: Ast, prefix: str = "", is_last: bool = True) -> None:
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

###############################################################################
# Parser
# Models an LL Recursive parser directly from the raw input string, no tokenizer.
###############################################################################

# Utils

def skip_chars(s: str, pos: int, char: str, count: int = 1) -> int:
    """ Skip the specified character from the given position in the string.
        - Pass count -1 to skip all consecutive chars.
        - Returns the number of characters skipped.
    """
    beg = pos
    curr = pos
    while curr < len(s) and s[curr] == char and (count == -1 or (curr - pos) < count):
        curr += 1
    return curr - beg

def skip_whitespace(s: str, pos: int = 0) -> int:
    """ Skip whitespace characters from the given position in the string.
        - Returns the number of characters skipped.
    """
    beg = pos
    while beg < len(s) and is_whitespace(s[beg]):
        beg += 1
    return beg - pos

class ParserError(Exception):
    """ Exception raised for parser errors.
        - Pass the parser instance to `prs` arg to print context.
    """
    def __init__(self, message: str, line: int = 0, col: int = 0,prs = None) -> None:
        super().__init__(f"ParserError at line {line}, col {col}: {message}")
        self.line = line
        self.col = col
        if prs is not None:
            # Print the current line with a marker at the error position.
            curr_line = prs.curr_line()
            print_error(curr_line)
            print_action(" " * (prs.pos) + "^")

class Parser:
    """ LL Recursive descent parser for CMHN grammar.
        - Initialize `Parser` with an input string, or pass the input to `parse_syntax` method.
        - Call `parse_syntax` method to parse.
        - Parse result will be the stored in `output` attribute as an `Ast` class.
    """
    def __init__(self, inp: str = "") -> None:
        self.inp = inp
        self.inp_lines = []
        self.pos = 0
        self.line = 0
        self.output = []

    def advance(self, count : int = 1):
        """ Advance current position by count. """
        self.pos += count

    def curr_line(self) -> str:
        """ Return the current line from inp_lines or empty string if out of range. """
        if 0 <= self.line < len(self.inp_lines):
            return self.inp_lines[self.line]
        return ""

    def parse_syntax(self,inp: str) -> Ast:
        """
        Grammar Rule:
        ```
        <cli_help> ::= \"Usage: \"? <text_line> \"\\n\\n\" <paragraph> <section>*
        ```
        """
        self.output = Ast(Tk.SYNTAX)
        self.inp = inp
        self.pos = 0

        # Split input into lines for easier processing
        self.inp_lines = inp.splitlines(keepends=True)
        self.line = 0

        while self.line < len(self.inp_lines):
            self.pos = 0
            # Strip a single following newline to normalize line endings.
            self.inp_lines[self.line] = self.inp_lines[self.line].rstrip('\n')

            if self.inp_lines[self.line] == "":
                self.line += 1
                continue

            is_usage = False
            is_section = False
            sect_title = self.inp_lines[self.line]

            # Check for special case usage section which does not require a following indent.
            is_usage = False
            if sect_title.startswith("Usage") or sect_title.startswith("usage") or sect_title.startswith("USAGE"):
                is_usage = True
                self.pos = len("Usage")
                self.pos += skip_whitespace(sect_title,self.pos)
                self.pos += skip_chars(sect_title,self.pos,':',1)
                self.pos += skip_whitespace(sect_title,self.pos)
                # The rest of the line is the usage text
                # If the rest of the line is empty look for indented text on the next line.
                usage_text = sect_title[self.pos:].strip()
                if usage_text == "":
                    self.line += 1
                    if self.line < len(self.inp_lines) and (self.inp_lines[self.line].startswith("    ") or self.inp_lines[self.line].startswith("\t")):
                        usage_text = self.inp_lines[self.line].strip()
                    else:
                        raise Exception(f"Expected indented usage text after 'Usage:' at line {self.line}")
                self.output.append(Ast(Tk.USAGE,usage_text))
                self.line += 1
                continue

            # If not usage, parse regular section or paragraph
            if not is_usage:
                section_begin = self.inp_lines[self.line + 1] if self.line + 1 < len(self.inp_lines) else ""
                if section_begin.startswith("    ") or section_begin.startswith("\t"):
                    is_section = True

                # Section
                if is_section:
                    self.output.append(Ast(Tk.SECTION,sect_title.strip()))
                    self.line += 1

                    # If a section begins with a - or --, parse as argument list.
                    if self.line < len(self.inp_lines) and (self.inp_lines[self.line].startswith("    -") or self.inp_lines[self.line].startswith("\t-")):
                        self.parse_argument_list(append_to = self.output.branches[-1])
                    else:
                        while self.line < len(self.inp_lines) and (self.inp_lines[self.line].startswith("    ") or self.inp_lines[self.line].startswith("\t")):
                            self.output.branches[-1].append(Ast(Tk.TEXT_LINE,self.inp_lines[self.line].strip()))
                            self.line += 1
                # Paragraph
                else:
                    paragraph = self.output.append(Ast(Tk.PARAGRAPH))
                    while self.line < len(self.inp_lines) and self.inp_lines[self.line].strip() != "":
                        paragraph.append(Ast(Tk.TEXT_LINE,self.inp_lines[self.line].strip()))
                        self.line += 1
                    self.line += 1 # skip empty line after paragraph

        return self.output

    def parse_argument_list(self, append_to : Ast) -> None:
        """ An argument list is one or more arguments """
        arg_list = Ast(Tk.ARGUMENT_LIST)
        # Skip any whitespace before an argument.
        flag_start = skip_whitespace(self.curr_line(),0)
        if not self.curr_line().startswith('-',flag_start):
            Exception(f"Expected argument list starting with '-' or '--' at line {self.line}")
        while self.line < len(self.inp_lines) and self.curr_line().startswith('-',flag_start):
            self.pos = flag_start
            self.parse_argument(arg_list)
            self.line += 1
        append_to.append(arg_list)

    def parse_argument(self, append_to : Ast) -> None:
        """
            # An argument consists of optional short flag, one or more long flags,
            # optional or required argument, indented line, colon, text line
        """
        argument = Ast(Tk.ARGUMENT)
        # Optional short flag.
        flag_start = self.pos
        has_short_flag = False
        if self.curr_line().startswith('-',flag_start) and \
                not self.curr_line().startswith('--',flag_start):
            has_short_flag = True
            self.advance()
            flag_ident : str = ""
            while(self.curr_line()[self.pos] != ' ' and self.curr_line()[self.pos]\
                    != '\t' and self.curr_line()[self.pos] != '\n'):
                self.pos += 1
                flag_ident += self.curr_line()[self.pos - 1]

            if len(flag_ident) != 1 or not is_alpha(flag_ident[0]):
                raise ParserError\
                    (f"Expected single character short flag identifier at line {self.line}")
            argument.append\
                (Ast(Tk.SHORT_FLAG,None,branches = [Ast(Tk.SHORT_FLAG_IDENT,flag_ident)]))
            self.pos += skip_whitespace(self.curr_line(),self.pos)
            flag_start = self.pos

        # One or more long flags, but only requried if there wasn't any previous short flag.
        if self.curr_line().startswith('--',flag_start):
            while self.curr_line().startswith('--',flag_start):
                self.advance(2)
                flag_ident : str = ""
                while(self.pos < len(self.curr_line()) and\
                        self.curr_line()[self.pos] not in (' ', '\t', '\n')):
                    self.pos += 1
                    flag_ident += self.curr_line()[self.pos - 1]
                if len(flag_ident) < 2 or not is_alpha(flag_ident[0])\
                        or not is_alnumus(flag_ident[-1]):
                    raise ParserError(f"Expected long flag identifier at line {self.line}")
                argument.append(Ast(Tk.LONG_FLAG,None,\
                        branches = [Ast(Tk.LONG_FLAG_IDENT,flag_ident)]))
                self.pos += skip_whitespace(self.curr_line(),self.pos)
                flag_start = self.pos
        else:
            if not has_short_flag:
                raise ParserError(f"Expected long flag starting with '--' at line {self.line}")

        # Optional or required argument
        if self.curr_line().startswith('[',flag_start):
            self.pos = flag_start
            self.advance()
            argument_ident : str = ""
            while self.pos < len(self.curr_line()) and is_alnumus(self.curr_line()[self.pos]):
                argument_ident += self.curr_line()[self.pos]
                self.pos += 1
            if argument_ident == "":
                raise ParserError(f"Expected optional argument identifier after '[' at line {self.line}")
            if self.pos >= len(self.curr_line()) or self.curr_line()[self.pos] != ']':
                raise ParserError(f"Expected closing ']' for optional argument at line {self.line}")
            self.advance() # skip closing ']'
            argument.append(Ast(Tk.OPTIONAL_ARG,None,branches = [Ast(Tk.SHELL_IDENT,argument_ident)]))
            self.pos += skip_whitespace(self.curr_line(),self.pos)
            flag_start = self.pos
        elif self.curr_line().startswith('<',flag_start):
            self.pos = flag_start
            self.advance()
            argument_ident : str = ""
            while self.pos < len(self.curr_line()) and is_alnumus(self.curr_line()[self.pos]):
                argument_ident += self.curr_line()[self.pos]
                self.pos += 1
            if argument_ident == "":
                raise ParserError(f"Expected required argument identifier after '<' at line {self.line}")
            if self.pos >= len(self.curr_line()) or self.curr_line()[self.pos] != '>':
                raise ParserError(f"Expected closing '>' for required argument at line {self.line}")
            self.advance() # skip closing '>'
            argument.append(Ast(Tk.REQUIRED_ARG,None,branches = [Ast(Tk.SHELL_IDENT,argument_ident)]))
            self.pos += skip_whitespace(self.curr_line(),self.pos)
            flag_start = self.pos
        # Indented line with colon and text
        if self.curr_line().startswith(':',flag_start):
            self.pos = flag_start + 1
            self.pos += skip_whitespace(self.curr_line(),self.pos)
            text = self.curr_line()[self.pos:].strip()
            if text == "":
                raise ParserError(f"Expected argument description text after ':' at line {self.line}")
            argument.append(Ast(Tk.TEXT_LINE,text))
            append_to.append(argument)
        else: # Else parse the rest of the line as the description
            text = self.curr_line()[flag_start:].strip()
            if text == "":
                # Check for indented following paragraph.
                next_line = self.line + 1
                if next_line < len(self.inp_lines) and (self.inp_lines[next_line].startswith("        ") or self.inp_lines[next_line].startswith("\t\t")):
                    # parse a paragraph.
                    self.line += 1
                    text = self.curr_line().strip()
                    self.line += 1
                    if text == "":
                        raise ParserError(f"Expected argument description text at line {self.line}",self.line,self.pos,self)
                    argument.append(Ast(Tk.TEXT_LINE,text))

                    while self.line < len(self.inp_lines) and (self.inp_lines[self.line].startswith("        ") or self.inp_lines[self.line].startswith("\t\t")):
                        text = self.curr_line().strip()
                        self.line += 1
                        argument.append(Ast(Tk.TEXT_LINE,text))
                else:
                    raise ParserError(f"Expected argument description text at line {self.line}",self.line,self.pos,self)
            else :
                argument.append(Ast(Tk.TEXT_LINE,text))
        append_to.append(argument)

###############################################################################
# Unit Test Utils
###############################################################################

def print_ast_diff(input_ast, expected_ast, indent: int = 0, path: tuple = ()) -> None:
    """Compare and print two ASTs with differences highlighted"""
    indent_str = "    " * indent
    connector = "└── " if indent > 0 else ""

    # Find corresponding node in expected AST
    expected_node = expected_ast
    for idx in path:
        if idx < len(expected_node.branches):
            expected_node = expected_node.branches[idx]
        else:
            expected_node = None
            break

    # Determine if nodes are different
    is_different = (
        expected_node is None or
        input_ast.tk.name != expected_node.tk.name or
        input_ast.value != expected_node.value
    )

    # Node content with color coding
    content = input_ast.tk.name + ': ' + input_ast.value if input_ast.value is not None else input_ast.tk.name

    if is_different:
        print(f"{indent_str}{connector}\033[91m{content}\033[0m")  # Red for differences
    else:
        print(f"{indent_str}{connector}{content}")  # Default color for matches

    # Print position info (optional)
    if input_ast.line > 0:
        pos_info = f"[L{input_ast.line}:{input_ast.col}-L{input_ast.end_line}:{input_ast.end_col}]"
        if is_different:
            print(f"{indent_str}    \033[91m{pos_info}\033[0m")
        else:
            print(f"{indent_str}    {pos_info}")

    # Recursively print children
    for i, child in enumerate(input_ast.branches):
        print_ast_diff(child, expected_ast, indent + 1, path + (i,))

def print_expected_ast_diff(expected_ast, input_ast, indent: int = 0, path: tuple = ()) -> None:
    """Print expected AST highlighting differences from input"""
    indent_str = "    " * indent
    connector = "└── " if indent > 0 else ""

    # Find corresponding node in input AST
    input_node = input_ast
    for idx in path:
        if idx < len(input_node.branches):
            input_node = input_node.branches[idx]
        else:
            input_node = None
            break

    # Determine if nodes are different
    is_different = (
        input_node is None or
        expected_ast.tk.name != input_node.tk.name or
        expected_ast.value != input_node.value
    )

    # Node content with color coding
    content = expected_ast.tk.name + ': ' + expected_ast.value if expected_ast.value is not None else expected_ast.tk.name

    if is_different:
        print(f"{indent_str}{connector}\033[92m{content}\033[0m")  # Green for differences
    else:
        print(f"{indent_str}{connector}{content}")  # Default color for matches

    # Print position info (optional)
    if expected_ast.line > 0:
        pos_info = f"[L{expected_ast.line}:{expected_ast.col}-L{expected_ast.end_line}:{expected_ast.end_col}]"
        if is_different:
            print(f"{indent_str}    \033[92m{pos_info}\033[0m")
        else:
            print(f"{indent_str}    {pos_info}")

    # Recursively print children
    for i, child in enumerate(expected_ast.branches):
        print_expected_ast_diff(child, input_ast, indent + 1, path + (i,))

def compare_asts(input_ast, expected_ast):
    """Main function to compare two ASTs"""
    print("Input AST (differences in red):")
    print_ast_diff(input_ast, expected_ast)

    print("\nExpected AST (differences in green):")
    print_expected_ast_diff(expected_ast, input_ast)

def test_parser(test_name, parser_input, expected_output):
    try:
        prs = Parser()
        ast = prs.parse_syntax(parser_input)
        did_test_pass = ast == expected_output
        if not did_test_pass:
            print_error(f"Test {test_name} failed.",1)
            # print_action(f"Test {test_name} : Expected :")
            # print_ascii_tree_simple(expected_output)
            # print_action(f"Test {test_name} : Got :")
            # print_ascii_tree_simple(prs.output)
            compare_asts(prs.output, expected_output)
        else:
            print_action(f"Test {test_name} passed.",1)
    except ParserError as e:
        print_error(f"Test {test_name} raised an exception: {e}",1)

# ###############################################################################
# # Unit Tests
# ###############################################################################

def ut_parser_arg_long_flag():
    """Long cli argument flag"""
    test_parser("ut_parser_arg_long_flag",
        parser_input="Options\n    --long-flag-ident123 This is the argument documentation.\n\n",
        expected_output=Ast(Tk.SYNTAX,None,branches = [
            Ast(Tk.SECTION,"Options",branches = [
                Ast(Tk.ARGUMENT_LIST,None,branches = [
                    Ast(Tk.ARGUMENT,None,branches = [
                        Ast(Tk.LONG_FLAG,None,branches = [Ast(Tk.LONG_FLAG_IDENT,'long-flag-ident123')]),
                        Ast(Tk.TEXT_LINE,"This is the argument documentation.")
                    ])
                ])
            ])
        ])
    )

def ut_parser_arg_short_flag():
    """Short cli argument flag"""
    test_parser("ut_parser_arg_short_flag",
        parser_input="Options\n    -f This is the argument documentation.\n\n",
        expected_output=Ast(Tk.SYNTAX,None,branches = [
            Ast(Tk.SECTION,"Options",branches = [
                Ast(Tk.ARGUMENT_LIST,None,branches = [
                    Ast(Tk.ARGUMENT,None,branches = [
                        Ast(Tk.SHORT_FLAG,None,branches = [Ast(Tk.SHORT_FLAG_IDENT,'f')]),
                        Ast(Tk.TEXT_LINE,"This is the argument documentation.")
                    ])
                ])
            ])
        ])
    )

def ut_parser_arg_short_and_long_flag():
    """Short and long cli argument flags"""
    test_parser("ut_parser_arg_short_and_long_flag",
        parser_input="Options\n    -f --long-flag-ident123 This is the argument documentation.\n\n",
        expected_output=Ast(Tk.SYNTAX,None,branches = [
            Ast(Tk.SECTION,"Options",branches = [
                Ast(Tk.ARGUMENT_LIST,None,branches = [
                    Ast(Tk.ARGUMENT,None,branches = [
                        Ast(Tk.SHORT_FLAG,None,branches = [Ast(Tk.SHORT_FLAG_IDENT,'f')]),
                        Ast(Tk.LONG_FLAG,None,branches = [Ast(Tk.LONG_FLAG_IDENT,'long-flag-ident123')]),
                        Ast(Tk.TEXT_LINE,"This is the argument documentation.")
                    ])
                ])
            ])
        ])
    )

def ut_parser_arg_optional_arg():
    """Optional cli argument"""
    test_parser("ut_parser_arg_optional_arg",
        parser_input="Options\n    --long-flag-ident123 [optional_arg123] This is the argument documentation.\n\n",
        expected_output=Ast(Tk.SYNTAX,None,branches = [
            Ast(Tk.SECTION,"Options",branches = [
                Ast(Tk.ARGUMENT_LIST,None,branches = [
                    Ast(Tk.ARGUMENT,None,branches = [
                        Ast(Tk.LONG_FLAG,None,branches = [Ast(Tk.LONG_FLAG_IDENT,'long-flag-ident123')]),
                        Ast(Tk.OPTIONAL_ARG,None,branches = [Ast(Tk.SHELL_IDENT,'optional_arg123')]),
                        Ast(Tk.TEXT_LINE,"This is the argument documentation.")
                    ])
                ])
            ])
        ])
    )

def ut_parser_arg_required_arg():
    """Required cli argument"""
    test_parser("ut_parser_arg_required_arg",
        parser_input="Options\n    --long-flag-ident123 <required_arg123> This is the argument documentation.\n\n",
        expected_output=Ast(Tk.SYNTAX,None,branches = [
            Ast(Tk.SECTION,"Options",branches = [
                Ast(Tk.ARGUMENT_LIST,None,branches = [
                    Ast(Tk.ARGUMENT,None,branches = [
                        Ast(Tk.LONG_FLAG,None,branches = [Ast(Tk.LONG_FLAG_IDENT,'long-flag-ident123')]),
                        Ast(Tk.REQUIRED_ARG,None,branches = [Ast(Tk.SHELL_IDENT,'required_arg123')]),
                        Ast(Tk.TEXT_LINE,"This is the argument documentation.")
                    ])
                ])
            ])
        ])
    )

def ut_parser_arg_indented_brief_following_arg():
    """Argument with indented brief following"""
    test_parser("ut_parser_arg_indented_brief_following_arg",
        parser_input="Options\n    --long-flag-ident123 <required_arg123>\n        This is the argument documentation.\n\n",
        expected_output=Ast(Tk.SYNTAX,None,branches = [
            Ast(Tk.SECTION,"Options",branches = [
                Ast(Tk.ARGUMENT_LIST,None,branches = [
                    Ast(Tk.ARGUMENT,None,branches = [
                        Ast(Tk.LONG_FLAG,None,branches = [Ast(Tk.LONG_FLAG_IDENT,'long-flag-ident123')]),
                        Ast(Tk.REQUIRED_ARG,None,branches = [Ast(Tk.SHELL_IDENT,'required_arg123')]),
                        Ast(Tk.TEXT_LINE,"This is the argument documentation.")
                    ])
                ])
            ])
        ])
    )

def ut_parser_arg_indented_multiline_brief_following_arg():
    """Argument with indented brief following"""
    test_parser("ut_parser_arg_indented_multiline_brief_following_arg",
        parser_input="Options\n    --long-flag-ident123 <required_arg123>\n        This is the argument documentation.\n        This is the second line.\n\n",
        expected_output=Ast(Tk.SYNTAX,None,branches = [
            Ast(Tk.SECTION,"Options",branches = [
                Ast(Tk.ARGUMENT_LIST,None,branches = [
                    Ast(Tk.ARGUMENT,None,branches = [
                        Ast(Tk.LONG_FLAG,None,branches = [Ast(Tk.LONG_FLAG_IDENT,'long-flag-ident123')]),
                        Ast(Tk.REQUIRED_ARG,None,branches = [Ast(Tk.SHELL_IDENT,'required_arg123')]),
                        Ast(Tk.TEXT_LINE,"This is the argument documentation.")
                        ,Ast(Tk.TEXT_LINE,"This is the second line.")
                    ])
                ])
            ])
        ])
    )

def ut_parser_usage_line():
    """Usage line"""
    test_parser("ut_parser_usage_line",
        parser_input="Usage: myprogram [options] <input_file>\n\n",
        expected_output=Ast(Tk.SYNTAX,None,branches = [
            Ast(Tk.USAGE,"myprogram [options] <input_file>")
        ])
    )

def ut_parser_simple():
    test_parser("ut_parser_simple",parser_input=""
                """USAGE:
    py cmhn_compiler.py [ [ -v | --verbose ] | [ -d | --debug ] ] <helpTextInput>


BRIEF:
    This is a brief.



This is a paragraph.
This is the second line.


PARAMS:
    -f This is an argument.

""",
    expected_output=Ast(Tk.SYNTAX,None,branches = [
        Ast(Tk.USAGE,"py cmhn_compiler.py [ [ -v | --verbose ] | [ -d | --debug ] ] <helpTextInput>"),
        Ast(Tk.SECTION,"BRIEF:",branches = [
            Ast(Tk.TEXT_LINE,"This is a brief.")
        ]),
        Ast(Tk.PARAGRAPH,None,branches = [
            Ast(Tk.TEXT_LINE,"This is a paragraph."),
            Ast(Tk.TEXT_LINE,"This is the second line.")
        ]),
        Ast(Tk.SECTION,"PARAMS:",branches = [
            Ast(Tk.ARGUMENT_LIST,None,branches = [
                Ast(Tk.ARGUMENT,None,branches = [
                    Ast(Tk.SHORT_FLAG,None,branches = [Ast(Tk.SHORT_FLAG_IDENT,'f')]),
                    Ast(Tk.TEXT_LINE,"This is an argument.")
                ])
            ])
        ])
    ])
    )

# <cli_help> ::= <usage_line> <brief_section> <section>*
def ut_parser_basic():
    test_parser("ut_parser_basic",parser_input=""
        "Usage: gmash dirs prefix --p <prefix> --P [fileOrFolder]\n\n"
        "Add a prefix to each top-level file in a directory.\n\n"
        "Parameters\n"
        "    -f --force \n"
        "        Force changes and overwrite.\n"
        "    -h --husky \n"
        "        Use secret husky superpowers.\n\n"
        "Display\n"
        "   -h --help\n"
        "        Display help.\n"
        "   -v -version\n"
        "        Display version\n\n"
        "Details\n"
        "    A paragraph of text, these are the details of a command.\n\n\n\n",
        expected_output=Ast(Tk.SYNTAX,None,branches = [
            Ast(Tk.USAGE,"gmash dirs prefix --p <prefix> --P [fileOrFolder]"),
            Ast(Tk.PARAGRAPH,None,branches = [
                Ast(Tk.TEXT_LINE,"Add a prefix to each top-level file in a directory.")
            ]),
            Ast(Tk.SECTION,"Parameters",branches = [
                Ast(Tk.ARGUMENT_LIST,None,branches = [
                    Ast(Tk.ARGUMENT,None,branches = [
                        Ast(Tk.SHORT_FLAG,None,branches = [Ast(Tk.SHORT_FLAG_IDENT,'f')]),
                        Ast(Tk.LONG_FLAG,None,branches = [Ast(Tk.LONG_FLAG_IDENT,'force')]),
                        Ast(Tk.TEXT_LINE,"Force changes and overwrite.")
                    ]),
                    Ast(Tk.ARGUMENT,None,branches = [
                        Ast(Tk.SHORT_FLAG,None,branches = [Ast(Tk.SHORT_FLAG_IDENT,'h')]),
                        Ast(Tk.LONG_FLAG,None,branches = [Ast(Tk.LONG_FLAG_IDENT,'husky')]),
                        Ast(Tk.TEXT_LINE,"Use secret husky superpowers.")
                    ])
                ])
            ]),
            Ast(Tk.SECTION,"Display",branches = [
                Ast(Tk.ARGUMENT_LIST,None,branches = [
                    Ast(Tk.ARGUMENT,None,branches = [
                        Ast(Tk.SHORT_FLAG,None,branches = [Ast(Tk.SHORT_FLAG_IDENT,'h')]),
                        Ast(Tk.LONG_FLAG,None,branches = [Ast(Tk.LONG_FLAG_IDENT,'help')]),
                        Ast(Tk.TEXT_LINE,"Display help.")
                    ]),
                    Ast(Tk.ARGUMENT,None,branches = [
                        Ast(Tk.SHORT_FLAG,None,branches = [Ast(Tk.SHORT_FLAG_IDENT,'v')]),
                        Ast(Tk.LONG_FLAG,None,branches = [Ast(Tk.LONG_FLAG_IDENT,'version')]),
                        Ast(Tk.TEXT_LINE,"Display version")
                    ])
                ])
            ]),
            Ast(Tk.SECTION,"Details",branches = [
                Ast(Tk.PARAGRAPH,None,branches = [
                    Ast(Tk.TEXT_LINE,"A paragraph of text, these are the details of a command.")
                ])
            ])
        ])
    )


def run_unit_tests():
    print_action("Running unit tests...")
    ut_parser_arg_long_flag()
    ut_parser_arg_short_flag()
    ut_parser_arg_short_and_long_flag()
    ut_parser_arg_optional_arg()
    ut_parser_arg_required_arg()
    ut_parser_arg_indented_brief_following_arg()
    ut_parser_arg_indented_multiline_brief_following_arg()
    ut_parser_usage_line()
    ut_parser_simple()

    ut_parser_basic()
    print_action("All unit tests completed.")

###############################################################################
# Command Line Interface
###############################################################################
verbose_mode = False
debug_mode = False
print_raw_repr = False
print_tree = False
print_fancy_tree = False
CMNH_TITLE = "CMHN - Command Line Help Notation Parser"
CMNH_VERSION = "v0.0.0"
CMNH_LICENSE = "AGPL-3.0-or-later Copyright(c) 2025 Anton Yashchenko"
CMNH_HELP = """Usage: python gen-docs.py '<help text to parse>'

Parse the provided help text into a Command Line Help Notation (CMHN) object.

Options:
    -t, --test            Run unit tests and exit.
    -v, --version         Show version information and exit.
    -h, --help            Show this help message and exit.
    -d, --debug           Enable debug mode for detailed output.
    -V, --verbose         Enable verbose output for more detailed information.
    -r, --raw             Print the raw Python object representation of the AST.
    -a, --ascii           Print the AST as a simple ASCII tree.
    -f, --fancy           Print the AST as a fancy ASCII tree with boxes and connection lines.
"""

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_help_text()

    # Display help and exit
    if any(arg == '-h' or arg == '--help' for arg in sys.argv):
        print_help_text()

    # Display version and exit
    if any(arg == '-v' or arg == '--version' for arg in sys.argv):
        print(CMNH_VERSION)
        sys.exit(0)

    # Run unit tests and exit
    if any(arg == '-t' or arg == '--test' for arg in sys.argv):
        run_unit_tests()
        sys.exit(0)

    # Print raw python object representation of the AST
    if any(arg == '-r' or arg == '--raw' for arg in sys.argv):
        print_raw_repr = True

    # Print the AST as a simple ASCII tree
    if any(arg == '-a' or arg == '--ascii' for arg in sys.argv):
        print_tree = True

    # Print the AST as a fancy ASCII tree with boxes and connection lines
    if any(arg == '-f' or arg == '--fancy' for arg in sys.argv):
        print_fancy_tree = True

    # Enable debug mode
    verbose_mode = any(arg == '-V' or arg == '--verbose' for arg in sys.argv)
    debug_mode = any(arg == '-d' or arg == '--debug' for arg in sys.argv)
    if debug_mode : verbose_mode = True

    # Pop the script name
    sys.argv.pop(0)

    # Remove all flags from args
    sys.argv = [arg for arg in sys.argv if not arg.startswith('-')]

    # If no args left,
    # check the standard input for piped input and read it as the help text
    if len(sys.argv) < 1:
        if not sys.stdin.isatty():
            help_text = sys.stdin.read()
            if help_text.strip() == "":
                print_help_text()
            sys.argv.append(help_text)

    help_text = sys.argv[0]

    print_action("Parsing input.")
    verbose_print(help_text)

    parser = Parser()
    parser.parse_syntax(help_text)


    if print_raw_repr:
        print_action("Displaying raw AST.")
        print(parser.output)
    if print_tree:
        print_action("Displaying ascii AST.")
        print_ascii_tree_simple(parser.output)
    if print_fancy_tree:
        print_action("Displaying fancy AST.")
        print_ascii_tree(parser.output)
