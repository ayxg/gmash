"""
Copyright(c) Anton Yashchenko 2025
@created : 2025/09/13
@project CMHN : Command Line Help Notation Parser
@brief Grammar for parsing 'help' manuals displayed by command line applications.
"""
import sys
from typing import List, Optional, Union
from enum import Enum, auto

def is_alnumus(c: str) -> bool:
    """ Is alpha, numeric or underscore."""
    return c.isalnum() or c == '_'

def is_alnumdash(c: str) -> bool:
    """ Is alpha, numeric or underscore."""
    return c.isalnum() or c == '_' or c == '-'

def is_alpha(c: str) -> bool:
    """ Is alpha or underscore."""
    return c.isalpha() or c == '_'

def is_numeric(c: str) -> bool:
    """ Is numeric."""
    return c.isdigit()

def is_indent(c: str) -> bool:
    """ Is indent character (4 spaces or a tab)."""
    return c in ("\n    " or "\n  " or "\n\t")

def is_text(c: str) -> bool:
    """ Is any character except newline."""
    return c not in ('\n')

def is_dash(c: str) -> bool:
    """ Is dash character."""
    return c == '-'

def is_newline(c: str) -> bool:
    """ Is newline character."""
    return c == '\n'

def is_whitespace(c: str) -> bool:
    """ Is whitespace character (space or tab)."""
    return c in (' ', '\t')

def is_usage_keyword(s: str) -> bool:
    """ Check if a line starts with 'Usage', 'USAGE' or 'usage'. """
    return s.startswith("Usage") or s.startswith("usage") or s.startswith("USAGE")

def is_indented_line(s: str, indent_level: int = 1) -> bool:
    """ Check if a line starts with the specified indent level (spaces or tabs). """
    if indent_level < 1:
        # make sure the line has no leading spaces or tabs
        if s.startswith(' ') or s.startswith('\t'):
            return False
        else :
            return True
    space_indent = ' ' * (4 * indent_level)
    tab_indent = '\t' * indent_level
    return s.startswith(space_indent) or s.startswith(tab_indent)

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
    """ Print an action message in green color.
        - indent_level : number of indents to add before the message.
    """
    print("    " * indent_level + "└────" * (indent_level != 0) + "\033[92m" + msg +"\033[0m")

def print_error(msg: str,indent_level = 0) -> None:
    """ Print an error message in red color.
        - indent_level : number of indents to add before the message.
    """
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

class ParseResult:
    """ Result of a parse operation. """
    def __init__(self, res: Union[tuple[Ast,int,int],str]) -> None:
        if isinstance(res, tuple):
            self.ast = res[0]
            self.end_line = res[1]
            self.end_col = res[2]
            self.error = None
        else:
            self.ast = None
            self.end_line = 0
            self.end_col = 0
            self.error = res

    def is_error(self) -> bool:
        """ Check if the parse result is an error. """
        return self.error is not None

    def get_ast(self) -> Optional[Ast]:
        """ Get the AST if parse was successful, else None. """
        return self.ast if not self.is_error() else None

    def get_error(self) -> Optional[str]:
        """ Get the error message if parse failed, else None. """
        return self.error if self.is_error() else None

    def get_line(self) -> int:
        """ Get the line number where the parse ended. """
        return self.end_line

    def get_col(self) -> int:
        """ Get the column number where the parse ended. """
        return self.end_col

def split_lines(s: str) -> List[str]:
    """ Split the input string into lines, keeping line endings. """
    return s.splitlines()

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

def line_startswith(s: str, prefix: str, pos : int = 0) -> bool:
    """ Check if line starts with a given prefix, ignoring leading whitespace."""
    return s.startswith(prefix,pos + skip_whitespace(s,pos))

# Parsing automatons

def parse_long_flag(inp : List[str], line: int, pos: int) -> ParseResult:
    """ A long flag starts with two dashes followed by an identifier.
        - Returns a tuple of (Ast, end_line, end_col) on success, or an error message string on failure.
    """
    if line >= len(inp):
        return ParseResult("Expected long flag but reached end of inp")
    line_str = inp[line]
    pos += skip_whitespace(line_str,pos)
    if not line_str.startswith('--',pos):
        return ParseResult(f"Expected long flag starting with '--' at line {line}")
    pos += 2
    flag_ident = ""
    while pos < len(line_str) and is_alnumdash(line_str[pos]):
        flag_ident += line_str[pos]
        pos += 1
    if len(flag_ident) < 2 or not is_alpha(flag_ident[0]) or not is_alnumus(flag_ident[-1]):
        return ParseResult(f"Expected long flag identifier at line {line}")
    long_flag_ast = Ast(Tk.LONG_FLAG,None,branches = [Ast(Tk.LONG_FLAG_IDENT,flag_ident)])
    return ParseResult((long_flag_ast,line,pos))

def parse_short_flag(inp : List[str], line: int, pos: int) -> ParseResult:
    """ A short flag starts with a single dash followed by a single character identifier.
        - Returns a tuple of (Ast, end_line, end_col) on success, or an error message string on failure.
    """
    if line >= len(inp):
        return ParseResult("Expected short flag but reached end of inp")
    line_str = inp[line]
    if not line_str.startswith('-',pos) or line_str.startswith('--',pos):
        return ParseResult(f"Expected short flag starting with '-' at line {line}")
    pos += 1
    if pos >= len(line_str) or not is_alpha(line_str[pos]):
        return ParseResult(f"Expected single character short flag identifier at line {line}")
    flag_ident = line_str[pos]
    pos += 1
    short_flag_ast = Ast(Tk.SHORT_FLAG,None,branches = [Ast(Tk.SHORT_FLAG_IDENT,flag_ident)])
    return ParseResult((short_flag_ast,line,pos))

def parse_optional_arg(inp : List[str], line: int, pos: int) -> ParseResult:
    """ An optional argument is enclosed in square brackets.
        - Returns a tuple of (Ast, end_line, end_col) on success, or an error message string on failure.
    """
    curr_line = line
    curr_pos = pos
    if curr_line >= len(inp):
        return ParseResult("Expected optional argument but reached end of inp")
    line_str = inp[curr_line]
    curr_pos += skip_whitespace(line_str,curr_pos)
    if not line_str.startswith('[',curr_pos):
        return ParseResult(f"Expected optional argument starting with '[' at line {curr_line}")
    curr_pos += 1
    arg_ident = ""
    while curr_pos < len(line_str) and is_alnumus(line_str[curr_pos]):
        arg_ident += line_str[curr_pos]
        curr_pos += 1
    if len(arg_ident) < 1 or not is_alpha(arg_ident[0]) or not is_alnumus(arg_ident[-1]):
        return ParseResult(f"Expected optional argument identifier at line {curr_line}")
    curr_pos += skip_whitespace(line_str,curr_pos)
    if curr_pos >= len(line_str) or not line_str.startswith(']',curr_pos):
        return ParseResult(f"Expected closing ']' for optional argument at line {curr_line}")
    curr_pos += 1
    optional_arg_ast = Ast(Tk.OPTIONAL_ARG,None,branches = [Ast(Tk.SHELL_IDENT,arg_ident)])
    return ParseResult((optional_arg_ast,curr_line,curr_pos))

def parse_required_arg(inp : List[str], line: int, pos: int) -> ParseResult:
    """ A required argument is enclosed in angle brackets.
        - Returns a tuple of (Ast, end_line, end_col) on success, or an error message string on failure.
    """
    curr_line = line
    curr_pos = pos
    if curr_line >= len(inp):
        return ParseResult("Expected required argument but reached end of inp")
    line_str = inp[curr_line]
    curr_pos += skip_whitespace(line_str,curr_pos)
    if not line_str.startswith('<',curr_pos):
        return ParseResult(f"Expected required argument starting with '<' at line {curr_line}")
    curr_pos += 1
    arg_ident = ""
    while curr_pos < len(line_str) and is_alnumus(line_str[curr_pos]):
        arg_ident += line_str[curr_pos]
        curr_pos += 1
    if len(arg_ident) < 1 or not is_alpha(arg_ident[0]) or not is_alnumus(arg_ident[-1]):
        return ParseResult(f"Expected required argument identifier at line {curr_line}")
    curr_pos += skip_whitespace(line_str,curr_pos)
    if curr_pos >= len(line_str) or not line_str.startswith('>',curr_pos):
        return ParseResult(f"Expected closing '>' for required argument at line {curr_line}")
    curr_pos += 1
    required_arg_ast = Ast(Tk.REQUIRED_ARG,None,branches = [Ast(Tk.SHELL_IDENT,arg_ident)])
    return ParseResult((required_arg_ast,curr_line,curr_pos))

def parse_argument(inp : List[str], line: int, pos: int) -> ParseResult:
    """ An argument consists of optional short flag, one or more long flags,
        optional or required argument, followed by a description text line.
        - Returns a tuple of (Ast, end_line, end_col) on success, or an error message string on failure.
    """
    if line >= len(inp):
        return ParseResult("Expected argument but reached end of inp")
    line_str = inp[line]            # Current line string
    argument_ast = Ast(Tk.ARGUMENT) # Argument root node
    has_short_flag = False          # Whether a short flag was parsed
    has_long_flag = False           # Whether a long flag was parsed

    # Parse optional short flag
    if line_startswith(line_str,"-") and not line_startswith(line_str,"--"):
        has_short_flag = True
        pos += skip_whitespace(line_str,pos)
        short_flag_result = parse_short_flag(inp,line,pos)
        if short_flag_result.is_error():
            return short_flag_result
        argument_ast.append(short_flag_result.get_ast())
        line = short_flag_result.get_line()
        pos = short_flag_result.get_col()
        pos += skip_whitespace(line_str,pos)
        if line < len(inp) and pos < len(inp[line]) and inp[line][pos] == ',':
            pos += 1
            pos += skip_whitespace(inp[line],pos)

    # Parse one or more long flags
    while line_startswith(line_str,"--",pos):
        has_long_flag = True
        pos += skip_whitespace(line_str,pos)
        long_flag_result = parse_long_flag(inp,line,pos)
        if long_flag_result.is_error():
            return ParseResult(f"Failed to parse long flag at line {line} with error:\n\t\t\"{long_flag_result.get_error()}\"")
        argument_ast.append(long_flag_result.get_ast())
        line = long_flag_result.get_line()
        pos = long_flag_result.get_col()
        pos += skip_whitespace(line_str,pos)
        if line < len(inp) and pos < len(inp[line]) and inp[line][pos] == ',':
            pos += 1
            pos += skip_whitespace(inp[line],pos)

    # Require atleast one flag
    if not has_long_flag and not has_short_flag:
        return ParseResult(f"Expected at least one long flag at line {line}")

    # Parse optional or required argument
    if line_str.startswith('[',pos):
        optional_arg_result = parse_optional_arg(inp,line,pos)
        if optional_arg_result.is_error():
            return ParseResult(f"Failed to parse optional argument at line {line}")
        argument_ast.append(optional_arg_result.get_ast())
        line = optional_arg_result.get_line()
        pos = optional_arg_result.get_col()
        if line >= len(inp):
            return ParseResult("Expected argument description but reached end of inp")
        line_str = inp[line]
        pos += skip_whitespace(line_str,pos)
    elif line_str.startswith('<',pos):
        required_arg_result = parse_required_arg(inp,line,pos)
        if required_arg_result.is_error():
            return ParseResult(f"Failed to parse required argument at line {line}")
        argument_ast.append(required_arg_result.get_ast())
        line = required_arg_result.get_line()
        pos = required_arg_result.get_col()
        if line >= len(inp):
            return ParseResult("Expected argument description but reached end of inp")
        line_str = inp[line]
        pos += skip_whitespace(line_str,pos)

    # Description
    # Indented line with colon and text
    if line_str.startswith(':',pos):
        pos += 1
        pos += skip_whitespace(line_str,pos)
        text = line_str[pos:].strip()
        if text == "":
            return ParseResult(f"Expected argument description text after ':' at line {line}")
        argument_ast.append(Ast(Tk.TEXT_LINE,text))
        return ParseResult((argument_ast,line + 1,0))
    else:
        text = line_str[pos:].strip()
        if text == "":
            # Check for indented following paragraph.
            next_line = line + 1
            if next_line < len(inp)\
                    and (inp[next_line].startswith("        ") or inp[next_line].startswith("\t\t")):
                # parse a paragraph.
                line += 1
                text = inp[line].strip()
                line += 1
                if text == "":
                    return ParseResult(f"Expected argument description text at line {line}")
                argument_ast.append(Ast(Tk.TEXT_LINE,text))

                while line < len(inp)\
                        and (inp[line].startswith("        ") or inp[line].startswith("\t\t")):
                    text = inp[line].strip()
                    line += 1
                    argument_ast.append(Ast(Tk.TEXT_LINE,text))
            else:
                return ParseResult((argument_ast,line,pos)) # No desc, continue
        else :
            argument_ast.append(Ast(Tk.TEXT_LINE,text))

    return ParseResult((argument_ast,line,pos))

def parse_argument_list(inp : List[str], line: int, pos: int) -> ParseResult:
    """ An argument list is one or more arguments """
    arg_list = Ast(Tk.ARGUMENT_LIST)
    while line < len(inp) and line_startswith(inp[line],'-'):
        arg_result = parse_argument(inp,line,pos)
        if arg_result.is_error():
            return ParseResult(f"Failed to parse argument at line {line} with error:\n\t\t\"{arg_result.get_error()}\"")
        arg_list.append(arg_result.get_ast())
        line = arg_result.get_line()
        pos = 0 # Reset the column position for the newline. Assuming each argument starts on a new line.
        line += 1 # Go to the next line.
        # Skip any empty lines between arguments.
        while line < len(inp) and inp[line].strip() == "":
            line += 1
    # Programmer error, you should detect an argument dash before calling this function.
    if len(arg_list.branches) == 0:
        return ParseResult(f"[EXCEPTION][parse_argument_list]\
            Attempting to parse non-existing argument list at line {line}, col {pos}.")
    return ParseResult((arg_list,line,pos))

def parse_section(inp : List[str], line: int, pos: int) -> ParseResult:
    if line > len(inp): return ParseResult("Expected section but reached end of input")
    if is_indented_line(inp[line]): return ParseResult(f"Expected section title at line {line}, col {pos}")
    section_title = inp[line].strip()
    line += 1
    section = Ast(Tk.SECTION,section_title)
    if not line < len(inp) or not is_indented_line(inp[line]):
        return ParseResult(f"Expected indented text after section title at line {line}, col {pos}")

    section_start = skip_whitespace(inp[line])
    if inp[line].startswith('-',section_start):
        arg_list_result = parse_argument_list(inp,line,section_start)
        if arg_list_result.is_error():
            return ParseResult(f"Failed to parse argument list at line {line}")
        section.append(arg_list_result.get_ast())
        return ParseResult((section,arg_list_result.get_line(),arg_list_result.get_col()))
    else:
        while line < len(inp) and is_indented_line(inp[line]) or inp[line].strip() == "":
            section.append(Ast(Tk.TEXT_LINE,inp[line].strip()))
            line += 1
        return ParseResult((section,line,0))

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
        if 0 <= self.in_lines(self.line):
            return self.inp_lines[self.line]
        return ""

    def line_at(self, line: int) -> str:
        """ Return the line at the given index from inp_lines or empty string if out of range. """
        if self.in_lines(line):
            return self.inp_lines[line]
        return ""

    def in_lines(self, line: int) -> bool:
        """ Check if the given line index is in range of inp_lines. """
        return 0 <= line < len(self.inp_lines)

    def try_parse(self, parse_func, append_to ,from_line: int, from_pos: int) -> ParseResult:
        """ Try to parse using the given parse function from the specified line and position.
            - If parsing fails, restore the parser state to the original line and position.
        """
        orig_line = from_line
        orig_pos = from_pos
        result = parse_func(from_line, from_pos)
        if result.is_error():
            # Restore original state on failure
            self.line = orig_line
            self.pos = orig_pos
        else:
            append_to.append(result.ast)
            self.line = result.end_line
            self.pos = result.end_col
        return result

    def parse_syntax(self,inp: str = "") -> ParseResult:
        """
        Grammar Rule:
            ```
            <cli_help> ::= \"Usage: \"? <text_line> \"\\n\\n\" <paragraph> <section>*
            ```
        """
        # Configure parser state
        self.output = Ast(Tk.SYNTAX)
        if inp != "":
            self.inp = inp
        self.pos = 0
        self.line = 0

        # Split input into lines for easier processing
        self.inp_lines = inp.splitlines(keepends=True)

        if self.inp_lines == []:
            raise ParserError("Input is empty")

        while self.in_lines(self.line):
            self.pos = 0

            # Strip a single following newline to normalize line endings.
            self.inp_lines[self.line] = self.inp_lines[self.line].rstrip('\n')

            if self.inp_lines[self.line] == "": # Skip empty lines
                self.line += 1
                continue
            is_usage = False
            is_section = False
            sect_title = self.inp_lines[self.line]

            # Check for special case usage section which does not require a following indent.
            is_usage = False
            if is_usage_keyword(sect_title):
                is_usage = True
                if self.try_parse(self.parse_usage_section,self.output,self.line,self.pos).is_error():
                    raise ParserError("Failed to parse usage section",self.line,self.pos,self)
                continue

            # If not usage, parse regular section or paragraph
            if not is_usage:
                section_begin = self.inp_lines[self.line + 1] if self.line + 1 < len(self.inp_lines) else ""
                if is_indented_line(section_begin,1):
                    is_section = True
                if is_section:
                    if self.try_parse(self.parse_section,self.output,self.line,self.pos).is_error():
                        raise ParserError("Failed to parse section",self.line,self.pos,self)
                else:
                    if self.try_parse(self.parse_paragraph,self.output,self.line,self.pos).is_error():
                        raise ParserError("Failed to parse paragraph",self.line,self.pos,self)
        return self.output

    def parse_usage_section(self, from_line: int, from_pos: int) -> ParseResult:
        """ A usage section starts with 'Usage:' or 'usage:' or 'USAGE:' """
        if not self.in_lines(from_line):
            return ParseResult("Expected usage section but reached end of input")
        curr_line = from_line
        curr_pos = from_pos
        line = self.line_at(curr_line)
        if not is_usage_keyword(line):
            return ParseResult(f"Expected usage section starting with 'Usage:' at line {curr_line}")
        curr_pos += len("Usage")
        curr_pos += skip_whitespace(line,curr_pos)
        curr_pos += skip_chars(line,curr_pos,':',1)
        curr_pos += skip_whitespace(line,curr_pos)

        # The rest of the line is the usage text. If the rest of the line is empty
        # look for indented text on the next line.
        usage_text = line[curr_pos:].strip()
        if usage_text == "":
            curr_line += 1
            if self.in_lines(curr_line) and is_indented_line(self.line_at(curr_line),1):
                usage_text = self.line_at(curr_line).strip()
            else:
                return ParseResult(f"Expected indented usage\
                    text after usage keyword at line {curr_line}")
        usage_ast = Ast(Tk.USAGE,usage_text)
        return ParseResult((usage_ast,curr_line + 1,0))

    def parse_section(self, from_line: int, from_pos: int) -> ParseResult:
        """ A section starts with a title line followed by one or more indented text lines. """
        if not self.in_lines(from_line): return ParseResult("Expected section but reached end of input")
        if is_indented_line(self.line_at(from_line),1): return ParseResult(f"Expected section title at line {from_line}")
        section_title = self.line_at(from_line).strip()
        from_line += 1
        if not self.in_lines(from_line) or not is_indented_line(self.line_at(from_line),1):
            return ParseResult(f"Expected indented text after section title at line {from_line}")
        section_ast = Ast(Tk.SECTION,section_title)

        section_start = skip_whitespace(self.line_at(from_line),0)
        if self.line_at(from_line).startswith('-',section_start):
            arg_list_result = self.try_parse(self.parse_argument_list,section_ast,from_line,0)
            if arg_list_result.is_error():
                return ParseResult(f"Failed to parse argument list at line {from_line}")
            return ParseResult((section_ast,from_line,0))
        else:
            while self.in_lines(from_line) and is_indented_line(self.line_at(from_line),1):
                section_ast.append(Ast(Tk.TEXT_LINE,self.line_at(from_line).strip()))
                from_line += 1
            return ParseResult((section_ast,from_line,0))

    def parse_paragraph(self, from_line: int, from_pos: int) -> ParseResult:
        """ A paragraph is one or more text lines separated by empty lines. """
        if not self.in_lines(from_line):
            return ParseResult("Expected paragraph but reached end of input")
        curr_line = from_line
        curr_pos = from_pos
        paragraph_ast = Ast(Tk.PARAGRAPH)
        while self.in_lines(curr_line) and self.line_at(curr_line).strip() != "":
            paragraph_ast.append(Ast(Tk.TEXT_LINE,self.line_at(curr_line).strip()))
            curr_line += 1
        curr_line += 1 # skip empty line after paragraph
        return ParseResult((paragraph_ast,curr_line,0))

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
    """ Run a parser test and compare the output AST to the expected AST."""
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

def test_parser_function(funct,test_name,parser_input,expected_output):
    """ Run a specific parser function test and compare the output AST to the expected AST."""
    try:
        result = funct(split_lines(parser_input),0,0)
        if result.is_error():
            print_error(f"Test {test_name} failed with error:\n\t{result.error}",1)
            return
        ast = result.ast
        did_test_pass = ast == expected_output
        if not did_test_pass:
            print_error(f"Test {test_name} failed.",1)
            compare_asts(ast, expected_output)
        else:
            print_action(f"Test {test_name} passed.",1)
    except ParserError as e:
        print_error(f"Test {test_name} raised an exception: {e}",1)

# ###############################################################################
# # Unit Tests
# ###############################################################################

def ut_parser_usage_line():
    """Usage line"""
    test_parser("ut_parser_usage_line",
        parser_input="Usage: myprogram [options] <input_file>\n\n",
        expected_output=Ast(Tk.SYNTAX,None,branches = [
            Ast(Tk.USAGE,"myprogram [options] <input_file>")
        ])
    )

def ut_parser_paragraph():
    """Paragraph"""
    test_parser("ut_parser_paragraph",
        parser_input="This is a paragraph.\nThis is the second line.\n\n",
        expected_output=Ast(Tk.SYNTAX,None,branches = [
            Ast(Tk.PARAGRAPH,None,branches = [
                Ast(Tk.TEXT_LINE,"This is a paragraph."),
                Ast(Tk.TEXT_LINE,"This is the second line.")
            ])
        ])
    )

def ut_parser_usage_and_paragraph():
    """Usage line and paragraph"""
    test_parser("ut_parser_usage_and_paragraph",
        parser_input="Usage: myprogram [options] <input_file>\n\nThis is a paragraph.\nThis is the second line.\n\n",
        expected_output=Ast(Tk.SYNTAX,None,branches = [
            Ast(Tk.USAGE,"myprogram [options] <input_file>"),
            Ast(Tk.PARAGRAPH,None,branches = [
                Ast(Tk.TEXT_LINE,"This is a paragraph."),
                Ast(Tk.TEXT_LINE,"This is the second line.")
            ])
        ])
    )

def ut_parser_usage_paragraph_section():
    """Usage line, paragraph and section"""
    test_parser("ut_parser_usage_paragraph_section",
        parser_input="Usage: myprogram [options] <input_file>\n\nThis is a paragraph.\nThis is the second line.\n\nDetails\n    These are the details.\n\n",
        expected_output=Ast(Tk.SYNTAX,None,branches = [
            Ast(Tk.USAGE,"myprogram [options] <input_file>"),
            Ast(Tk.PARAGRAPH,None,branches = [
                Ast(Tk.TEXT_LINE,"This is a paragraph."),
                Ast(Tk.TEXT_LINE,"This is the second line.")
            ]),
            Ast(Tk.SECTION,"Details",branches = [
                Ast(Tk.TEXT_LINE,"These are the details.")
            ])
        ])
    )

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

def ut_parser_simple():
    """Simple complete example"""
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

def ut_parser_basic():
    """Basic complete example"""
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

def ut_parsefunc_long_flag():
    """ Long flag parse function """
    test_parser_function(parse_long_flag,
        "ut_parsefunc_long_flag",
        parser_input="--long-flag-ident123",
        expected_output=Ast(Tk.LONG_FLAG,None,branches = [Ast(Tk.LONG_FLAG_IDENT,'long-flag-ident123')])
    )

def ut_parsefunc_short_flag():
    """ Short flag parse function """
    test_parser_function(parse_short_flag,
        "ut_parsefunc_short_flag",
        parser_input="-f\n",
        expected_output=Ast(Tk.SHORT_FLAG,None,branches = [Ast(Tk.SHORT_FLAG_IDENT,'f')])
    )

def ut_parsefunc_long_and_short_flag():
    """ Long and short flag parse function """
    test_parser_function(parse_argument,
        "ut_parsefunc_long_and_short_flag",
        parser_input="-f --long-flag-ident123 This is the argument documentation.\n",
        expected_output=Ast(Tk.ARGUMENT,None,branches = [
            Ast(Tk.SHORT_FLAG,None,branches = [Ast(Tk.SHORT_FLAG_IDENT,'f')]),
            Ast(Tk.LONG_FLAG,None,branches = [Ast(Tk.LONG_FLAG_IDENT,'long-flag-ident123')]),
            Ast(Tk.TEXT_LINE,"This is the argument documentation.")
        ])
    )

def ut_parsefunc_optional_arg():
    """ Optional arg parse function """
    test_parser_function(parse_optional_arg,
        "ut_parsefunc_optional_arg",
        parser_input="[optional_arg123]",
        expected_output=Ast(Tk.OPTIONAL_ARG,None,branches = [Ast(Tk.SHELL_IDENT,'optional_arg123')])
    )

def ut_parsefunc_required_arg():
    """ Required arg parse function """
    test_parser_function(parse_required_arg,
        "ut_parsefunc_required_arg",
        parser_input="<required_arg123>",
        expected_output=Ast(Tk.REQUIRED_ARG,None,branches = [Ast(Tk.SHELL_IDENT,'required_arg123')])
    )

def ut_parsefunc_argument_shortflag_only():
    """ Argument with short flag only parse function """
    test_parser_function(parse_argument,
        "ut_parsefunc_argument_shortflag_only",
        parser_input="-f\n",
        expected_output=Ast(Tk.ARGUMENT,None,branches = [
            Ast(Tk.SHORT_FLAG,None,branches = [Ast(Tk.SHORT_FLAG_IDENT,'f')])
        ])
    )

def ut_parsefunc_argument_longflag_only():
    """ Argument with long flag only parse function """
    test_parser_function(parse_argument,
        "ut_parsefunc_argument_longflag_only",
        parser_input="--long-flag-ident123\n",
        expected_output=Ast(Tk.ARGUMENT,None,branches = [
            Ast(Tk.LONG_FLAG,None,branches = [Ast(Tk.LONG_FLAG_IDENT,'long-flag-ident123')])
        ])
    )

def ut_parsefunc_argument_long_and_short_flag():
    """ Argument with long and short flag parse function """
    test_parser_function(parse_argument,
        "ut_parsefunc_argument_long_and_short_flag",
        parser_input="-f --long-flag-ident123",
        expected_output=Ast(Tk.ARGUMENT,None,branches = [
            Ast(Tk.SHORT_FLAG,None,branches = [Ast(Tk.SHORT_FLAG_IDENT,'f')]),
            Ast(Tk.LONG_FLAG,None,branches = [Ast(Tk.LONG_FLAG_IDENT,'long-flag-ident123')])
        ])
    )

def ut_parsefunc_argument_required_arg():
    """ Argument with required arg parse function """
    test_parser_function(parse_argument,
        "ut_parsefunc_argument_required_arg",
        parser_input="--long-flag-ident123 <required_arg123>",
        expected_output=Ast(Tk.ARGUMENT,None,branches = [
            Ast(Tk.LONG_FLAG,None,branches = [Ast(Tk.LONG_FLAG_IDENT,'long-flag-ident123')]),
            Ast(Tk.REQUIRED_ARG,None,branches = [Ast(Tk.SHELL_IDENT,'required_arg123')])
        ])
    )

def ut_parsefunc_argument_optional_arg():
    """ Argument with optional arg parse function """
    test_parser_function(parse_argument,
        "ut_parsefunc_argument_optional_arg",
        parser_input="--long-flag-ident123 [optional_arg123]",
        expected_output=Ast(Tk.ARGUMENT,None,branches = [
            Ast(Tk.LONG_FLAG,None,branches = [Ast(Tk.LONG_FLAG_IDENT,'long-flag-ident123')]),
            Ast(Tk.OPTIONAL_ARG,None,branches = [Ast(Tk.SHELL_IDENT,'optional_arg123')])
        ])
    )

def ut_parsefunc_argument_desc_same_line():
    """ Argument with description on the same line parse function """
    test_parser_function(parse_argument,
        "ut_parsefunc_argument_desc_same_line",
        parser_input="--long-flag-ident123 This is the argument documentation.\n",
        expected_output=Ast(Tk.ARGUMENT,None,branches = [
            Ast(Tk.LONG_FLAG,None,branches = [Ast(Tk.LONG_FLAG_IDENT,'long-flag-ident123')]),
            Ast(Tk.TEXT_LINE,"This is the argument documentation.")
        ])
    )

def ut_parsefunc_argument_indented_brief_following_arg():
    """ Argument with indented brief following parse function """
    test_parser_function(parse_argument,
        "ut_parsefunc_argument_indented_brief_following_arg",
        parser_input="--long-flag-ident123\n        This is the argument documentation.\n",
        expected_output=Ast(Tk.ARGUMENT,None,branches = [
            Ast(Tk.LONG_FLAG,None,branches = [Ast(Tk.LONG_FLAG_IDENT,'long-flag-ident123')]),
            Ast(Tk.TEXT_LINE,"This is the argument documentation.")
        ])
    )

def ut_parsefunc_argument_full():
    """ Full argument parse function """
    test_parser_function(parse_argument,
        "ut_parsefunc_argument_full",
        parser_input="-f --long-flag-ident123 --second-flag-opt [optional_arg] This is the argument documentation.\n",
        expected_output=Ast(Tk.ARGUMENT,None,branches = [
            Ast(Tk.SHORT_FLAG,None,branches = [Ast(Tk.SHORT_FLAG_IDENT,'f')]),
            Ast(Tk.LONG_FLAG,None,branches = [Ast(Tk.LONG_FLAG_IDENT,'long-flag-ident123')]),
            Ast(Tk.LONG_FLAG,None,branches = [Ast(Tk.LONG_FLAG_IDENT,'second-flag-opt')]),
            Ast(Tk.OPTIONAL_ARG,None,branches = [Ast(Tk.SHELL_IDENT,'optional_arg')]),
            Ast(Tk.TEXT_LINE,"This is the argument documentation.")
        ])
    )

def ut_parsefunc_argument_full_with_commas():
    """ Full argument with commas parse function """
    test_parser_function(parse_argument,
        "ut_parsefunc_argument_full_with_commas",
        parser_input="-f, --long-flag-ident123, --second-flag-opt [optional_arg] This is the argument documentation.\n",
        expected_output=Ast(Tk.ARGUMENT,None,branches = [
            Ast(Tk.SHORT_FLAG,None,branches = [Ast(Tk.SHORT_FLAG_IDENT,'f')]),
            Ast(Tk.LONG_FLAG,None,branches = [Ast(Tk.LONG_FLAG_IDENT,'long-flag-ident123')]),
            Ast(Tk.LONG_FLAG,None,branches = [Ast(Tk.LONG_FLAG_IDENT,'second-flag-opt')]),
            Ast(Tk.OPTIONAL_ARG,None,branches = [Ast(Tk.SHELL_IDENT,'optional_arg')]),
            Ast(Tk.TEXT_LINE,"This is the argument documentation.")
        ])
    )

def ut_parsefunc_argument_list():
    """ Argument list parse function """
    test_parser_function(parse_argument_list,
        "ut_parsefunc_argument_list",
        parser_input="-f --long-flag-ident123 This is the argument documentation.\n"
                     "-g --another-flag [optional_arg] This is another argument.\n",
        expected_output=Ast(Tk.ARGUMENT_LIST,None,branches = [
            Ast(Tk.ARGUMENT,None,branches = [
                Ast(Tk.SHORT_FLAG,None,branches = [Ast(Tk.SHORT_FLAG_IDENT,'f')]),
                Ast(Tk.LONG_FLAG,None,branches = [Ast(Tk.LONG_FLAG_IDENT,'long-flag-ident123')]),
                Ast(Tk.TEXT_LINE,"This is the argument documentation.")
            ]),
            Ast(Tk.ARGUMENT,None,branches = [
                Ast(Tk.SHORT_FLAG,None,branches = [Ast(Tk.SHORT_FLAG_IDENT,'g')]),
                Ast(Tk.LONG_FLAG,None,branches = [Ast(Tk.LONG_FLAG_IDENT,'another-flag')]),
                Ast(Tk.OPTIONAL_ARG,None,branches = [Ast(Tk.SHELL_IDENT,'optional_arg')]),
                Ast(Tk.TEXT_LINE,"This is another argument.")
            ])
        ])
    )

def ut_parsefunc_section_paragraph():
    """ Section with paragraph parse function """
    test_parser_function(parse_section,
        "ut_parsefunc_section_paragraph",
        parser_input="Details\n    This is a paragraph.\n    This is the second line.\n",
        expected_output=Ast(Tk.SECTION,"Details",branches = [
            Ast(Tk.TEXT_LINE,"This is a paragraph."),
            Ast(Tk.TEXT_LINE,"This is the second line.")
        ])
    )

def ut_parsefunc_section_arguments():
    """ Section with argument list parse function """
    test_parser_function(parse_section,
        "ut_parsefunc_section_arguments",
        parser_input="Options\n    -f --long-flag-ident123 This is the argument documentation.\n    -g --another-flag [optional_arg] This is another argument.\n",
        expected_output=Ast(Tk.SECTION,"Options",branches = [
            Ast(Tk.ARGUMENT_LIST,None,branches = [
                Ast(Tk.ARGUMENT,None,branches = [
                    Ast(Tk.SHORT_FLAG,None,branches = [Ast(Tk.SHORT_FLAG_IDENT,'f')]),
                    Ast(Tk.LONG_FLAG,None,branches = [Ast(Tk.LONG_FLAG_IDENT,'long-flag-ident123')]),
                    Ast(Tk.TEXT_LINE,"This is the argument documentation.")
                ]),
                Ast(Tk.ARGUMENT,None,branches = [
                    Ast(Tk.SHORT_FLAG,None,branches = [Ast(Tk.SHORT_FLAG_IDENT,'g')]),
                    Ast(Tk.LONG_FLAG,None,branches = [Ast(Tk.LONG_FLAG_IDENT,'another-flag')]),
                    Ast(Tk.OPTIONAL_ARG,None,branches = [Ast(Tk.SHELL_IDENT,'optional_arg')]),
                    Ast(Tk.TEXT_LINE,"This is another argument.")
                ])
            ])
        ])
    )

def run_unit_tests():
    """ Run all unit tests. """
    print_action("Running unit tests...")

    print_action("      Testing parser functions:")
    ut_parsefunc_long_flag()
    ut_parsefunc_short_flag()
    ut_parsefunc_optional_arg()
    ut_parsefunc_required_arg()
    ut_parsefunc_argument_shortflag_only()
    ut_parsefunc_argument_longflag_only()
    ut_parsefunc_argument_long_and_short_flag()
    ut_parsefunc_argument_required_arg()
    ut_parsefunc_argument_optional_arg()
    ut_parsefunc_argument_desc_same_line()
    ut_parsefunc_argument_indented_brief_following_arg()
    ut_parsefunc_argument_full()
    ut_parsefunc_argument_full_with_commas()
    ut_parsefunc_argument_list()
    ut_parsefunc_section_paragraph()
    ut_parsefunc_section_arguments()

    # print_action("      Testing parser end-to-end:")
    # ut_parser_usage_line()
    # ut_parser_paragraph()
    # ut_parser_usage_and_paragraph()
    # ut_parser_usage_paragraph_section()
    # ut_parser_arg_long_flag()
    # ut_parser_arg_short_flag()
    # ut_parser_arg_short_and_long_flag()
    # ut_parser_arg_optional_arg()
    # ut_parser_arg_required_arg()
    # ut_parser_arg_indented_brief_following_arg()
    # ut_parser_arg_indented_multiline_brief_following_arg()
    # ut_parser_simple()
    # ut_parser_basic()

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

CMNH_TEST_MAP : dict = {
    # Bottom up tests
    "ut_parsefunc_long_flag": ut_parsefunc_long_flag
    ,"ut_parsefunc_short_flag": ut_parsefunc_short_flag
    ,"ut_parsefunc_optional_arg": ut_parsefunc_optional_arg
    ,"ut_parsefunc_required_arg": ut_parsefunc_required_arg
    ,"ut_parsefunc_argument_shortflag_only": ut_parsefunc_argument_shortflag_only
    ,"ut_parsefunc_argument_longflag_only": ut_parsefunc_argument_longflag_only
    ,"ut_parsefunc_argument_long_and_short_flag": ut_parsefunc_argument_long_and_short_flag
    ,"ut_parsefunc_argument_required_arg": ut_parsefunc_argument_required_arg
    ,"ut_parsefunc_argument_optional_arg": ut_parsefunc_argument_optional_arg
    ,"ut_parsefunc_argument_desc_same_line": ut_parsefunc_argument_desc_same_line
    , "ut_parsefunc_argument_indented_brief_following_arg": ut_parsefunc_argument_indented_brief_following_arg
    , "ut_parsefunc_argument_full" : ut_parsefunc_argument_full
    , "ut_parsefunc_argument_full_with_commas" : ut_parsefunc_argument_full_with_commas
    ,"ut_parsefunc_argument_list": ut_parsefunc_argument_list

    # Top down tests
    ,"ut_parser_usage_line": ut_parser_usage_line
    ,"ut_parser_paragraph": ut_parser_paragraph
    ,"ut_parser_usage_and_paragraph": ut_parser_usage_and_paragraph
    ,"ut_parser_usage_paragraph_section": ut_parser_usage_paragraph_section
    ,"ut_parser_arg_long_flag": ut_parser_arg_long_flag
    ,"ut_parser_arg_short_flag": ut_parser_arg_short_flag
    ,"ut_parser_arg_short_and_long_flag": ut_parser_arg_short_and_long_flag
    ,"ut_parser_arg_optional_arg": ut_parser_arg_optional_arg
    ,"ut_parser_arg_required_arg": ut_parser_arg_required_arg
    ,"ut_parser_arg_indented_brief_following_arg": ut_parser_arg_indented_brief_following_arg
    ,"ut_parser_arg_indented_multiline_brief_following_arg": ut_parser_arg_indented_multiline_brief_following_arg

    # "ut_parser_simple": ut_parser_simple,
    # "ut_parser_basic": ut_parser_basic
}

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
        # Get all args not starting with '-' after the '-t'. If any
        # run ony those tests.
        test_args = [arg for arg in sys.argv[1:] if not arg.startswith('-')]
        if len(test_args) > 0:
            for test_name in test_args:
                if test_name in CMNH_TEST_MAP:
                    CMNH_TEST_MAP[test_name]()
                else:
                    # Try finding the first match containing the passed pattern.
                    matched_tests = [name for name in CMNH_TEST_MAP if test_name in name]
                    if len(matched_tests) > 0:
                        for match in matched_tests:
                            CMNH_TEST_MAP[match]()
                    else:
                        print_error(f"Unknown unit test: {test_name}",1)
        else:
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
