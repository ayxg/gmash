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
    """ Is alpha, numeric , underscore or dash."""
    return c.isalnum() or c == '_' or c == '-'

def is_alpha(c: str) -> bool:
    """ Is alpha or underscore."""
    return c.isalpha() or c == '_'

def is_usage_keyword(s: str) -> bool:
    """ Check if a line starts with 'Usage', 'USAGE' or 'usage'. """
    is_usage = False
    if s.startswith("Usage"):
        is_usage = True
    elif s.startswith("usage"):
        is_usage = True
    elif s.startswith("USAGE"):
        is_usage = True
    return is_usage

def is_indented_line(s: str, indent_level: int = 1) -> bool:
    """ Check if a line starts with the specified indent level (4 spaces or a tab). """
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
    def __init__(self, res: Union[tuple[Ast,int,int],tuple[str,int,int,List[str]]]) -> None:
        if isinstance(res, tuple):
            self.ast = res[0]
            self.end_line = res[1]
            self.end_col = res[2]
            self.error = None
        else:
            self.ast = None
            self.error = res[0]
            self.end_line = res[1]
            self.end_col = res[2]
            self.source = res[3] if len(res) > 3 else None

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
    """ Count the number of concecutive whitespaces(or tabs) in a `str`, starting from `pos`.
    """
    beg = pos
    while beg < len(s) and (s[beg] in (' ', '\t')):
        beg += 1
    return beg - pos

def line_startswith(s: str, prefix: str, pos : int = 0) -> bool:
    """ Check if line starts with a given prefix, ignoring leading whitespace."""
    return s.startswith(prefix,pos + skip_whitespace(s,pos))

###############################################################################
# Parsing Automatons
# - Each parse function approximatley models a grammar rule from the CMNH EBNF.
# - Success -> tuple[Ast,int,int] -> (ast, end_line, end_col)
# - Failure -> tuple[str,int,int,List[str]]] -> (error message, line, col, input)
###############################################################################

def parse_long_flag(inp : List[str], line: int, pos: int) -> ParseResult:
    """
    EBNF:
        `<long_flag_ident> ::= ( [a-z] | [A-Z] )+ ( [a-z] | [A-Z] | "-" )+ ( [a-z] | [A-Z] | [0-9] )`
        `<long_flag> ::= "--" <long_flag_ident>`

    Long cli argument flag format:
        - Begins with alpha.
        - May contain alpha, numeric or dash.
        - Ends with alpha or numeric.
    """
    if line >= len(inp):
        return ParseResult(("Expected long flag but reached end of input.",line,pos,inp))
    inp[line] = inp[line]
    pos += skip_whitespace(inp[line],pos)
    if not inp[line].startswith('--',pos):
        return ParseResult(("Expected long flag starting with a '--'.",line,pos,inp))
    pos += 2
    flag_ident = ""
    while pos < len(inp[line]) and is_alnumdash(inp[line][pos]):
        flag_ident += inp[line][pos]
        pos += 1
    if len(flag_ident) < 2 or not is_alpha(flag_ident[0]) or not is_alnumus(flag_ident[-1]):
        return ParseResult(("Invalid long flag identifier.",line,pos,inp))
    return ParseResult((Ast(Tk.LONG_FLAG,None,branches = [Ast(Tk.LONG_FLAG_IDENT,flag_ident)]),line,pos))

def parse_short_flag(inp : List[str], line: int, pos: int) -> ParseResult:
    """
    EBNF:
        `<short_flag> ::= "-" ( [a-z] | [A-Z] )`
    """
    if line >= len(inp):
        return ParseResult(("Expected short flag but reached end of inp.",line,pos,inp))
    inp[line] = inp[line]
    if not inp[line].startswith('-',pos) or inp[line].startswith('--',pos):
        return ParseResult(("Expected short flag starting with a '-'.",line,pos,inp))
    pos += 1
    if pos >= len(inp[line]) or not is_alpha(inp[line][pos]):
        return ParseResult(("Invalid short flag identifier.",line,pos,inp))
    flag_ident = inp[line][pos]
    pos += 1
    return ParseResult((Ast(Tk.SHORT_FLAG,None,branches = [Ast(Tk.SHORT_FLAG_IDENT,flag_ident)]),line,pos))

def parse_optional_arg(inp : List[str], line: int, pos: int) -> ParseResult:
    """
    EBNF:
        `<shell_ident> ::= ( [a-z] | [A-Z] ) ( [a-z] | [A-Z] | [0-9] )+ ( [a-z] | [A-Z] )`
        `<optional_arg> ::= "[" <shell_ident> "]"`

    Help text's running shell variable identifier format.
        - Begin with alpha or underscore.
        - May contain alpha, numeric or underscore.
    """
    if line >= len(inp):
        return ParseResult(("Expected optional argument but reached end of input.",line,pos,inp))
    inp[line] = inp[line]
    pos += skip_whitespace(inp[line],pos)
    if not inp[line].startswith('[',pos):
        return ParseResult(("Expected optional argument starting with a '['.",line,pos,inp))
    pos += 1
    arg_ident = ""
    while pos < len(inp[line]) and is_alnumus(inp[line][pos]):
        arg_ident += inp[line][pos]
        pos += 1
    if len(arg_ident) < 1 or not is_alpha(arg_ident[0]) or not is_alnumus(arg_ident[-1]):
        return ParseResult(("Expected optional argument identifier.",line,pos,inp))
    pos += skip_whitespace(inp[line],pos)
    if pos >= len(inp[line]) or not inp[line].startswith(']',pos):
        return ParseResult(("Expected closing ']' for optional argument.",line,pos,inp))
    pos += 1
    return ParseResult((Ast(Tk.OPTIONAL_ARG,None,branches = [Ast(Tk.SHELL_IDENT,arg_ident)]),line,pos))

def parse_required_arg(inp : List[str], line: int, pos: int) -> ParseResult:
    """
    EBNF:
        `<shell_ident> ::= ( [a-z] | [A-Z] ) ( [a-z] | [A-Z] | [0-9] )+ ( [a-z] | [A-Z] )`
        `<required_arg> ::= "<" <shell_ident> ">"`
    """
    if line >= len(inp):
        return ParseResult(("Expected required argument but reached end of input.",line,pos,inp))
    inp = inp[line]
    pos += skip_whitespace(inp,pos)
    if not inp.startswith('<',pos):
        return ParseResult(("Expected required argument starting with a '<'.",line,pos,inp))
    pos += 1
    arg_ident = ""
    while pos < len(inp) and is_alnumus(inp[pos]):
        arg_ident += inp[pos]
        pos += 1
    if len(arg_ident) < 1 or not is_alpha(arg_ident[0]) or not is_alnumus(arg_ident[-1]):
        return ParseResult(("Expected required argument identifier.",line,pos,inp))
    pos += skip_whitespace(inp,pos)
    if pos >= len(inp) or not inp.startswith('>',pos):
        return ParseResult(("Expected closing '>' for required argument.",line,pos,inp))
    pos += 1
    return ParseResult((Ast(Tk.REQUIRED_ARG,None,branches = [Ast(Tk.SHELL_IDENT,arg_ident)]),line,pos))

def parse_argument(inp : List[str], line: int, pos: int) -> ParseResult:
    """
    EBNF:
        `<argument> ::= (( <short_flag> ) " ")? (( <long_flag> ) " " ) +
        ( <optional_arg> |  <required_arg> )? <indented_line> ": " <text_line>`
    """
    if line >= len(inp):
        return ParseResult(("Expected argument but reached end of input.",line,pos,inp))
    inp[line] = inp[line]            # Current line string
    node = Ast(Tk.ARGUMENT) # Argument root node
    has_short_flag = False          # Whether a short flag was parsed
    has_long_flag = False           # Whether a long flag was parsed

    # Parse optional short flag
    if line_startswith(inp[line],"-") and not line_startswith(inp[line],"--"):
        has_short_flag = True
        pos += skip_whitespace(inp[line],pos)
        short_flag_result = parse_short_flag(inp,line,pos)
        if short_flag_result.is_error():
            return short_flag_result
        node.append(short_flag_result.get_ast())
        line = short_flag_result.get_line()
        pos = short_flag_result.get_col()
        pos += skip_whitespace(inp[line],pos)
        if line < len(inp) and pos < len(inp[line]) and inp[line][pos] == ',':
            pos += 1
            pos += skip_whitespace(inp[line],pos)

    # Parse one or more long flags
    while line_startswith(inp[line],"--",pos):
        has_long_flag = True
        pos += skip_whitespace(inp[line],pos)
        long_flag_result = parse_long_flag(inp,line,pos)
        if long_flag_result.is_error():
            return long_flag_result
        node.append(long_flag_result.get_ast())
        line = long_flag_result.get_line()
        pos = long_flag_result.get_col()
        pos += skip_whitespace(inp[line],pos)
        if line < len(inp) and pos < len(inp[line]) and inp[line][pos] == ',':
            pos += 1
            pos += skip_whitespace(inp[line],pos)

    # Require atleast one flag
    if not has_long_flag and not has_short_flag:
        return ParseResult(f"Expected at least one long flag at line {line}")

    # Parse optional or required argument
    if inp[line].startswith('[',pos):
        optional_arg_result = parse_optional_arg(inp,line,pos)
        if optional_arg_result.is_error():
            return optional_arg_result
        node.append(optional_arg_result.get_ast())
        line = optional_arg_result.get_line()
        pos = optional_arg_result.get_col()
        if line >= len(inp):
            return ParseResult(("Expected argument description but reached end of input.",line,pos,inp))
        inp[line] = inp[line]
        pos += skip_whitespace(inp[line],pos)
    elif inp[line].startswith('<',pos):
        required_arg_result = parse_required_arg(inp,line,pos)
        if required_arg_result.is_error():
            return required_arg_result
        node.append(required_arg_result.get_ast())
        line = required_arg_result.get_line()
        pos = required_arg_result.get_col()
        if line >= len(inp):
            return ParseResult(("Expected argument description but reached end of input.",line,pos,inp))
        inp[line] = inp[line]
        pos += skip_whitespace(inp[line],pos)

    # Description
    # Indented line with colon and text
    if inp[line].startswith(':',pos):
        pos += 1
        pos += skip_whitespace(inp[line],pos)
        text = inp[line][pos:].strip()
        if text == "":
            return ParseResult(("Expected argument description text after ':'.",line,pos,inp))
        node.append(Ast(Tk.TEXT_LINE,text))
        return ParseResult((node,line + 1,0))
    else:
        text = inp[line][pos:].strip()
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
                    return ParseResult(("Expected argument description text.",line,pos,inp))
                node.append(Ast(Tk.TEXT_LINE,text))

                while line < len(inp)\
                        and (inp[line].startswith("        ") or inp[line].startswith("\t\t")):
                    text = inp[line].strip()
                    line += 1
                    node.append(Ast(Tk.TEXT_LINE,text))
            else:
                return ParseResult((node,line,pos)) # No desc, continue
        else :
            node.append(Ast(Tk.TEXT_LINE,text))

    return ParseResult((node,line,pos))

def parse_argument_list(inp : List[str], line: int, pos: int) -> ParseResult:
    """
    EBNF:
        `<argument_list> ::= ( <argument> "\\n" )+`
    """
    node = Ast(Tk.ARGUMENT_LIST)
    while line < len(inp) and line_startswith(inp[line],'-'):
        arg_result = parse_argument(inp,line,pos)
        if arg_result.is_error():
            return arg_result
        node.append(arg_result.get_ast())
        line = arg_result.get_line()
        pos = 0 # Reset the column position for the newline. Assuming each argument starts on a new line.
        line += 1 # Go to the next line.
        # Skip any empty lines between arguments.
        while line < len(inp) and inp[line].strip() == "":
            line += 1
    # Programmer error, you should detect an argument dash before calling this function.
    if len(node.branches) == 0:
        return ParseResult(("Attempting to parse non-existing argument list.",line,pos,inp))
    return ParseResult((node,line,pos))

def parse_section(inp : List[str], line: int, pos: int) -> ParseResult:
    if line > len(inp):
        return ParseResult(("Expected section but reached end of input.",line,pos,inp))
    if is_indented_line(inp[line]):
        return ParseResult(("Expected section title.",line,pos,inp))
    section_title = inp[line].strip()
    line += 1
    section = Ast(Tk.SECTION,section_title)
    if not line < len(inp) or not is_indented_line(inp[line]):
        return ParseResult(("Expected indented text after section title.",line,pos,inp))

    section_start = skip_whitespace(inp[line])
    if inp[line].startswith('-',section_start):
        arg_list_result = parse_argument_list(inp,line,section_start)
        if arg_list_result.is_error():
            return ParseResult(("Failed to parse argument list.",line,pos,inp))
        section.append(arg_list_result.get_ast())
        return ParseResult((section,arg_list_result.get_line(),arg_list_result.get_col()))
    else:
        para_result = parse_paragraph(inp,line,0,1)
        if para_result.is_error():
            return ParseResult(("Failed to parse paragraph.",line,pos,inp))
        section.append(para_result.get_ast())
        line = para_result.get_line()
        pos = para_result.get_col()
        return ParseResult((section,line,pos))

def parse_paragraph(inp : List[str], line: int, pos: int,indent_level = 0) -> ParseResult:
    """ A paragraph is one or more indented text lines. """
    if line >= len(inp):
        return ParseResult(("Expected paragraph but reached end of input.",line,pos,inp))
    if not is_indented_line(inp[line],indent_level):
        return ParseResult(("Expected indented paragraph.",line,pos,inp))
    para = Ast(Tk.PARAGRAPH)
    while line < len(inp) and ( is_indented_line(inp[line],indent_level) or inp[line].strip() == "" ):
        # When indent level is 0, disambiguate from a section title by looking forward for an indented line.
        if indent_level == 0 and not is_indented_line(inp[line],1) and inp[line].strip() != ""\
                and line + 1 < len(inp) and is_indented_line(inp[line + 1],1):
            break
        para.append(Ast(Tk.TEXT_LINE,inp[line].strip()))
        line += 1

    # while the last line is empty, move back to the last non-empty line
    while len(para.branches) > 0 and para.branches[-1].value == "":
        para.branches.pop()

    return ParseResult((para,line,0))

def parse_usage_section(inp : List[str], line: int, pos: int) -> ParseResult:
    """ A usage section starts with 'Usage:' or 'usage:' or 'USAGE:' """
    if line >= len(inp):
        return ParseResult("Expected usage section but reached end of inp")
    if not is_usage_keyword(inp[line]):
        return ParseResult(("Expected usage section starting with 'Usage:'.",line,pos,inp))
    pos += len("Usage")
    pos += skip_whitespace(inp[line],pos)
    pos += skip_chars(inp[line],pos,':',1)
    pos += skip_whitespace(inp[line],pos)
    usage_text = inp[line][pos:].strip()
    # If the rest of the line is empty look for indented text on the next line.
    if usage_text == "":
        line += 1
        if line < len(inp) and is_indented_line(inp[line],1):
            usage_text = inp[line].strip()
            line += 1
        else:
            return ParseResult(("Expected indented usage text after usage keyword.",line,pos,inp))
    else: # inline usage
        line += 1 # move past usage line

    pos = 0  # reset pos for next line, always end at start of next line
    return ParseResult((Ast(Tk.USAGE,usage_text),line,pos))

def parse_help_text(inp : List[str], line: int, pos: int) -> ParseResult:
    """
    Grammar Rule:
        `<cli_help> ::= <usage_section>? ( <section> | <paragraph> )*`
    """
    # Configure parser state
    output = Ast(Tk.SYNTAX)
    pos = 0
    line = 0

    if inp == []:
        return ParseResult(("Input is empty",line,pos,inp))

    while line < len(inp):
        pos = 0

        if inp[line] == "": # Skip empty lines
            line += 1
            continue
        is_usage = False
        is_section = False
        sect_title = inp[line]

        # Check for special case usage section which does not require a following indent.
        is_usage = False
        if is_usage_keyword(sect_title):
            is_usage = True
            usage_result = parse_usage_section(inp,line,pos)
            if usage_result.is_error():
                return usage_result
            output.append(usage_result.get_ast())
            line = usage_result.get_line()
            pos = usage_result.get_col()
            # skip any empty lines after usage
            while line < len(inp) and inp[line].strip() == "":
                line += 1
            continue

        # If not usage, parse regular section or paragraph
        if not is_usage:
            section_begin = inp[line + 1] if line + 1 < len(inp) else ""
            if is_indented_line(section_begin,1):
                is_section = True

        if is_section:
            section_result = parse_section(inp,line,pos)
            if section_result.is_error():
                return section_result
            output.append(section_result.get_ast())
            line = section_result.get_line()
            pos = section_result.get_col()
            while line < len(inp) and inp[line].strip() == "":
                line += 1
        else:
            para_result = parse_paragraph(inp,line,pos)
            if para_result.is_error():
                return para_result
            output.append(para_result.get_ast())
            line = para_result.get_line()
            pos = para_result.get_col()
            while line < len(inp) and inp[line].strip() == "":
                line += 1
    return ParseResult((output,line,pos))

class CommandLineHelpText:
    """ Command line help text intermediate representation"""

    def __init__(self) -> None:
        self.ir : Ast = Ast(Tk.NOTHING)

    def parse(self, inp: str) -> ParseResult:
        """ Parse the input string and return the AST. """
        inp_lines = split_lines(inp)
        result = parse_help_text(inp_lines,0,0)
        if result.is_error():
            return result
        self.ir = result.get_ast()
        return result

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
    prs = CommandLineHelpText()
    ast = prs.parse(parser_input)
    if ast.is_error():
        print_error(f"Test {test_name} failed with error:\n\t{ast.get_error()}",1)
    else:
        did_test_pass = ast.get_ast() == expected_output
        if not did_test_pass:
            print_error(f"Test {test_name} failed.",1)
            compare_asts(ast.get_ast(), expected_output)
        else:
            print_action(f"Test {test_name} passed.",1)

def test_parser_function(funct,test_name,parser_input,expected_output):
    """ Run a specific parser function test and compare the output AST to the expected AST."""
    result = funct(split_lines(parser_input),0,0)
    if result.is_error():
        print_error(f"Test {test_name} failed with error:\n\t{result.error}",1)
        return
    ast = result.get_ast()
    did_test_pass = ast == expected_output
    if not did_test_pass:
        print_error(f"Test {test_name} failed.",1)
        compare_asts(ast, expected_output)
    else:
        print_action(f"Test {test_name} passed.",1)

# ###############################################################################
# # Unit Tests
# ###############################################################################

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
            Ast(Tk.PARAGRAPH,None,branches = [
                Ast(Tk.TEXT_LINE,"This is a paragraph."),
                Ast(Tk.TEXT_LINE,"This is the second line.")
            ])
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

def ut_parsefunc_usage_section():
    """ Usage section parse function """
    test_parser_function(parse_usage_section,
        "ut_parsefunc_usage_section",
        parser_input="Usage: myprogram [options] <input_file>\n",
        expected_output=Ast(Tk.USAGE,"myprogram [options] <input_file>")
    )

def ut_parsefunc_help_text():
    """ Full help text parse function """
    test_parser_function(parse_help_text,
        "ut_parsefunc_help_text",
        parser_input="Usage: myprogram [options] <input_file>\n\nThis is a paragraph.\nThis is the second line.\n\nDetails\n    These are the details.\n\n",
        expected_output=Ast(Tk.SYNTAX,None,branches = [
            Ast(Tk.USAGE,"myprogram [options] <input_file>"),
            Ast(Tk.PARAGRAPH,None,branches = [
                Ast(Tk.TEXT_LINE,"This is a paragraph."),
                Ast(Tk.TEXT_LINE,"This is the second line.")
            ]),
            Ast(Tk.SECTION,"Details",branches = [ Ast(Tk.PARAGRAPH,None,branches = [
                Ast(Tk.TEXT_LINE,"These are the details.")
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
                Ast(Tk.PARAGRAPH,None,branches = [
                    Ast(Tk.TEXT_LINE,"These are the details.")
                ])
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
    test_parser("ut_parser_simple",
        parser_input="USAGE:\n"
            +"    py cmhn_compiler.py [ [ -v | --verbose ] | [ -d | --debug ] ] <helpTextInput>\n"
            +"\n"
            +"\n"
            +"BRIEF:\n"
            +"    This is a brief.\n"
            +"\n"
            +"\n"
            +"\n"
            +"This is a paragraph.\n"
            +"This is the second line.\n"
            +"\n"
            +"\n"
            +"PARAMS:\n"
            +"    -f This is an argument.\n"
            +"\n"
            +"\n"
        ,
        expected_output=Ast(Tk.SYNTAX,None,branches = [
            Ast(Tk.USAGE,"py cmhn_compiler.py [ [ -v | --verbose ] | [ -d | --debug ] ] <helpTextInput>"),
            Ast(Tk.SECTION,"BRIEF:",branches = [
                Ast(Tk.PARAGRAPH,None,branches = [Ast(Tk.TEXT_LINE,"This is a brief.")
                ])
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

def ut_parser_full():
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

def run_unit_tests():
    """ Run all unit tests. """
    print_action("Running unit tests...")

    print_action("Testing parser bottom-up:")
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
    ut_parsefunc_usage_section()
    ut_parsefunc_help_text()

    print_action("Testing parser end-to-end:")
    ut_parser_usage_line()
    ut_parser_paragraph()
    ut_parser_usage_and_paragraph()
    ut_parser_usage_paragraph_section()
    ut_parser_arg_long_flag()
    ut_parser_arg_short_flag()
    ut_parser_arg_short_and_long_flag()
    ut_parser_arg_optional_arg()
    ut_parser_arg_required_arg()
    ut_parser_arg_indented_brief_following_arg()
    ut_parser_arg_indented_multiline_brief_following_arg()
    ut_parser_simple()
    #ut_parser_full()

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

    parser = CommandLineHelpText()
    parser.parse(help_text)


    if print_raw_repr:
        print_action("Displaying raw AST.")
        print(parser.output)
    if print_tree:
        print_action("Displaying ascii AST.")
        print_ascii_tree_simple(parser.output)
    if print_fancy_tree:
        print_action("Displaying fancy AST.")
        print_ascii_tree(parser.output)
