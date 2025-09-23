"""
#@doc-------------------------------------------------------------------------#
SPDX-License-Identifier: AGPL-3.0-or-later
Copyright(c) 2025 Anton Yashchenko
#-----------------------------------------------------------------------------#
@project: [gmash] Git Smash
@author(s): Anton Yashchenko
@website: https://www.acpp.dev
#-----------------------------------------------------------------------------#
@file `helptext_parser.py`
@created: 2025/09/13
@brief Command Line Help Notation parser.
    - Approximatley models a recursive descent LL parser directly from the
    input string, no tokenizer step.
    - Each parse function(automaton) models a grammar rule from the CMNH EBNF.
    - ParseResult class encapsulates the result of a parse operation.
    - `parse` function will split input lines and trim all extra whitespace.
#-----------------------------------------------------------------------------#
"""
from typing import List, Optional, Union
from helptext_ast import Ast, Tk

###############################################################################
# Parsing Utils
###############################################################################

def _is_alnumus(c: str) -> bool:
    """ Is alpha, numeric or underscore."""
    return c.isalnum() or c == '_'

def _is_alnumdash(c: str) -> bool:
    """ Is alpha, numeric , underscore or dash."""
    return c.isalnum() or c == '_' or c == '-'

def _is_alpha(c: str) -> bool:
    """ Is alpha or underscore."""
    return c.isalpha() or c == '_'

def _is_usage_keyword(s: str) -> bool:
    """ Check if a line starts with 'Usage', 'USAGE' or 'usage'. """
    is_usage = False
    if s.startswith("Usage"):
        is_usage = True
    elif s.startswith("usage"):
        is_usage = True
    elif s.startswith("USAGE"):
        is_usage = True
    return is_usage

def _is_command_keyword(s: str) -> int:
    """
    Check if a line starts with the command keyword.
    Returns the size of the keyword or 0 if not found.
    """
    if s.startswith("Command"):
        return len("Command")
    elif s.startswith("command"):
        return len("command")
    elif s.startswith("COMMAND"):
        return len("COMMAND")
    elif s.startswith("Commands"):
        return len("Commands")
    elif s.startswith("commands"):
        return len("commands")
    elif s.startswith("COMMANDS"):
        return len("COMMANDS")
    elif s.startswith("Subcommands"):
        return len("Subcommands")
    elif s.startswith("subcommands"):
        return len("subcommands")
    elif s.startswith("SUBCOMMANDS"):
        return len("SUBCOMMANDS")
    elif s.startswith("Subcommand"):
        return len("Subcommand")
    elif s.startswith("subcommand"):
        return len("subcommand")
    elif s.startswith("SUBCOMMAND"):
        return len("SUBCOMMAND")
    elif s.startswith("sub-command"):
        return len("sub-command")
    elif s.startswith("Sub-Command"):
        return len("Sub-Command")
    elif s.startswith("SUB-COMMAND"):
        return len("SUB-COMMAND")
    elif s.startswith("sub-commands"):
        return len("sub-commands")
    elif s.startswith("Sub-Commands"):
        return len("Sub-Commands")
    elif s.startswith("SUB-COMMANDS"):
        return len("SUB-COMMANDS")
    return 0

def _is_indented_line(s: str, indent_level: int = 1) -> bool:
    """ Check if a line starts with the specified indent level (4 spaces or a tab). """
    if not s.strip():
        return False

    if indent_level < 1:
        # make sure the line has no leading spaces or tabs
        if s.startswith(' ') or s.startswith('\t'):
            return False
        else :
            return True
    half_indent = ' ' * (2 * indent_level)
    space_indent = ' ' * (4 * indent_level)
    tab_indent = '\t' * indent_level
    return s.startswith(space_indent) or s.startswith(tab_indent) or s.startswith(half_indent)

def _is_whitespace(c: str) -> bool:
    """ Check if a character is a whitespace or tab. """
    return c == ' ' or c == '\t'

def _skip_chars(s: str, pos: int, char: str, count: int = 1) -> int:
    """ Skip the specified character from the given position in the string.
        - Pass count -1 to skip all consecutive chars.
        - Returns the number of characters skipped.
    """
    beg = pos
    curr = pos
    while curr < len(s) and s[curr] == char and (count == -1 or (curr - pos) < count):
        curr += 1
    return curr - beg

def _skip_whitespace(s: str, pos: int = 0) -> int:
    """ Count the number of concecutive whitespaces(or tabs) in a `str`, starting from `pos`.
    """
    beg = pos
    while beg < len(s) and (s[beg] in (' ', '\t')):
        beg += 1
    return beg - pos

def _line_startswith(s: str, prefix: str, pos : int = 0) -> bool:
    """ Check if line starts with a given prefix, ignoring leading whitespace."""
    return s.startswith(prefix,pos + _skip_whitespace(s,pos))

def _in_line(pos: int, s: str) -> bool:
    """ Check if the position is within the line bounds. """
    return pos >= 0 and pos < len(s)

def _in_range(line: int, inp: List[str]) -> bool:
    """ Check if the line and column are within the input bounds. """
    return line >= 0 and line < len(inp)

###############################################################################
# Parsing Automatons
# - Each parse function approximatley models a grammar rule from the CMNH EBNF.
# - Success -> tuple[Ast,int,int] -> (ast, end_line, end_col)
# - Failure -> tuple[str,int,int,List[str]]] -> (error message, line, col, input)
###############################################################################

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

def parse_long_flag(inp : List[str], line: int, col: int) -> ParseResult:
    """
    EBNF:
        `<long_flag_ident> ::= ( [a-z] | [A-Z] )+ ( [a-z] | [A-Z] | "-" )+ ( [a-z] | [A-Z] | [0-9] )`
        `<long_flag> ::= "--" <long_flag_ident>`

    Long cli argument flag format:
        - Begins with alpha.
        - May contain alpha, numeric or dash.
        - Ends with alpha or numeric.
    """
    beg_line = line
    beg_col = col
    if not _in_line(col,inp[line]):
        return ParseResult(("Expected long flag but reached end of input.",line,col,inp))
    col += _skip_whitespace(inp[line],col)
    if not inp[line].startswith('--',col):
        return ParseResult(("Expected long flag starting with a '--'.",line,col,inp))
    col += 2
    flag_beg_line = line
    flag_beg_col = col
    flag_ident = ""
    while _in_line(col,inp[line]) and _is_alnumdash(inp[line][col]):
        flag_ident += inp[line][col]
        col += 1
    if len(flag_ident) < 2 or not _is_alpha(flag_ident[0]) or not _is_alnumus(flag_ident[-1]):
        return ParseResult(("Invalid long flag identifier.",line,col,inp))
    if _in_line(col,inp[line]) and not (_is_whitespace(inp[line][col]) or inp[line][col] == ','):
        return ParseResult(("Expected whitespace or comma after long flag.",line,col,inp))
    return ParseResult((Ast(Tk.LONG_FLAG,None,beg_line,beg_col,line,col,\
                            [Ast(Tk.LONG_FLAG_IDENT,flag_ident,flag_beg_line,flag_beg_col,line,col)]),
                        line,
                        col))

def parse_short_flag(inp : List[str], line: int, col: int) -> ParseResult:
    """
    EBNF:
        `<short_flag> ::= "-" ( [a-z] | [A-Z] )`
    """
    beg_line = line
    beg_col = col
    if not _in_line(col,inp[line]):
        return ParseResult(("Expected short flag but reached end of inp.",line,col,inp))
    if not inp[line].startswith('-',col) or inp[line].startswith('--',col):
        return ParseResult(("Expected short flag starting with a '-'.",line,col,inp))
    col += 1
    if not _in_line(col,inp[line]) or not _is_alpha(inp[line][col]):
        return ParseResult(("Invalid short flag identifier.",line,col,inp))
    flag_beg_line = line
    flag_beg_col = col
    flag_ident = inp[line][col]
    col += 1
    if _in_line(col,inp[line]) and not (_is_whitespace(inp[line][col]) or inp[line][col] == ','):
        return ParseResult(("Expected whitespace or comma after short flag.",line,col,inp))
    return ParseResult((Ast(Tk.SHORT_FLAG,None,beg_line,beg_col,line,col,\
                            [Ast(Tk.SHORT_FLAG_IDENT,flag_ident,flag_beg_line,flag_beg_col,line,col)])
                        ,line
                        ,col))

def parse_optional_arg(inp : List[str], line: int, col: int) -> ParseResult:
    """
    EBNF:
        `<shell_ident> ::= ( [a-z] | [A-Z] ) ( [a-z] | [A-Z] | [0-9] )+ ( [a-z] | [A-Z] )`
        `<optional_arg> ::= "[" <shell_ident> "]"`

    Help text's running shell variable identifier format.
        - Begin with alpha or underscore.
        - May contain alpha, numeric or underscore.
    """
    beg_line = line
    beg_col = col
    if not _in_range(line,inp):
        return ParseResult(("Expected optional argument but reached end of input.",line,col,inp))
    col += _skip_whitespace(inp[line],col)
    if not inp[line].startswith('[',col):
        return ParseResult(("Expected optional argument starting with a '['.",line,col,inp))
    col += 1
    ident_beg_line = line
    ident_beg_col = col
    arg_ident = ""
    while _in_line(col,inp[line]) and inp[line][col] != ']':
        arg_ident += inp[line][col]
        col += 1
    if len(arg_ident) < 1:
        return ParseResult(("Expected optional argument identifier.",line,col,inp))
    col += _skip_whitespace(inp[line],col)
    if not _in_line(col,inp[line]) or not inp[line].startswith(']',col):
        return ParseResult(("Expected closing ']' for optional argument.",line,col,inp))
    col += 1
    return ParseResult((Ast(Tk.OPTIONAL_ARG,None,beg_line,beg_col,line,col,\
                            [Ast(Tk.SHELL_IDENT,arg_ident,ident_beg_line,ident_beg_col,line,col)])
                        ,line
                        ,col))

def parse_required_arg(inp : List[str], line: int, col: int) -> ParseResult:
    """
    EBNF:
        `<shell_ident> ::= ( [a-z] | [A-Z] ) ( [a-z] | [A-Z] | [0-9] )+ ( [a-z] | [A-Z] )`
        `<required_arg> ::= "<" <shell_ident> ">"`
    """
    beg_line = line
    beg_col = col
    if not _in_range(line,inp):
        return ParseResult(("Expected required argument but reached end of input.",line,col,inp))
    col += _skip_whitespace(inp[line],col)
    if not inp[line].startswith('<',col):
        return ParseResult(("Expected required argument starting with a '<'.",line,col,inp[line]))
    col += 1
    ident_beg_line = line
    ident_beg_col = col
    arg_ident = ""
    while _in_line(col,inp[line]) and inp[line][col] != '>':
        arg_ident += inp[line][col]
        col += 1
    if len(arg_ident) < 1 or not _is_alpha(arg_ident[0]) or not _is_alnumus(arg_ident[-1]):
        return ParseResult(("Expected required argument identifier.",line,col,inp[line]))
    col += _skip_whitespace(inp[line],col)
    if not _in_line(col,inp[line]) or not inp[line].startswith('>',col):
        return ParseResult(("Expected closing '>' for required argument.",line,col,inp[line]))
    col += 1
    return ParseResult((Ast(Tk.REQUIRED_ARG,None,beg_line,beg_col,line,col,\
                            [Ast(Tk.SHELL_IDENT,arg_ident,ident_beg_line,ident_beg_col,line,col)])
                        ,line
                        ,col))

def parse_argument(inp : List[str], line: int, pos: int) -> ParseResult:
    """
    EBNF:
        `<argument> ::= (( <short_flag> ) " ")? (( <long_flag> ) " " ) +
        ( <optional_arg> |  <required_arg> )? <indented_line> ": " <text_line>`
    """
    if not _in_range(line,inp):
        return ParseResult(("Expected argument but reached end of input.",line,pos,inp))
    node = Ast(Tk.ARGUMENT) # Argument root node
    has_short_flag = False          # Whether a short flag was parsed
    has_long_flag = False           # Whether a long flag was parsed

    # Parse optional short flag
    if _line_startswith(inp[line],"-") and not _line_startswith(inp[line],"--"):
        has_short_flag = True
        pos += _skip_whitespace(inp[line],pos)
        short_flag_result = parse_short_flag(inp,line,pos)
        if short_flag_result.is_error():
            return short_flag_result
        node.append(short_flag_result.get_ast())
        line = short_flag_result.get_line()
        pos = short_flag_result.get_col()
        pos += _skip_whitespace(inp[line],pos)
        if line < len(inp) and pos < len(inp[line]) and inp[line][pos] == ',':
            pos += 1
        pos += _skip_whitespace(inp[line],pos)

    # Parse one or more long flags
    while _line_startswith(inp[line],"--",pos):
        has_long_flag = True
        pos += _skip_whitespace(inp[line],pos)
        long_flag_result = parse_long_flag(inp,line,pos)
        if long_flag_result.is_error():
            return long_flag_result
        node.append(long_flag_result.get_ast())
        line = long_flag_result.get_line()
        pos = long_flag_result.get_col()
        pos += _skip_whitespace(inp[line],pos)
        if line < len(inp) and pos < len(inp[line]) and inp[line][pos] == ',':
            pos += 1
            pos += _skip_whitespace(inp[line],pos)

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
        pos += _skip_whitespace(inp[line],pos)
    elif inp[line].startswith('<',pos):
        required_arg_result = parse_required_arg(inp,line,pos)
        if required_arg_result.is_error():
            return required_arg_result
        node.append(required_arg_result.get_ast())
        line = required_arg_result.get_line()
        pos = required_arg_result.get_col()
        if line >= len(inp):
            return ParseResult(("Expected argument description but reached end of input.",line,pos,inp))

        pos += _skip_whitespace(inp[line],pos)

    # Description
    # Indented line with colon and text
    if inp[line].startswith(':',pos):
        pos += 1
        pos += _skip_whitespace(inp[line],pos)
        text = inp[line][pos:].strip()
        if text == "":
            return ParseResult(("Expected argument description text after ':'.",line,pos,inp))
        node.append(Ast(Tk.TEXT_LINE,text))
        return ParseResult((node,line,0))
    else:
        text = inp[line][pos:].strip()
        if text == "":
            # Check for indented following paragraph.
            next_line = line + 1
            if next_line < len(inp)\
                    and _is_indented_line(inp[next_line],2):
                # parse a paragraph.
                line += 1
                text = inp[line].strip()
                #line += 1

                if not text == "":
                    node.append(Ast(Tk.TEXT_LINE,text))
                    line += 1

                while line < len(inp)\
                        and (inp[line].startswith("        ") or inp[line].startswith("\t\t")):
                    text = inp[line].strip()
                    line += 1
                    node.append(Ast(Tk.TEXT_LINE,text))
            else:
                line += 1
                return ParseResult((node,line,pos)) # No desc, continue
        else :
            node.append(Ast(Tk.TEXT_LINE,text))
            line += 1

    return ParseResult((node,line,pos))

def parse_argument_list(inp : List[str], line: int, pos: int) -> ParseResult:
    """
    EBNF:
        `<argument_list> ::= ( <argument> "\\n" )+`
    """
    node = Ast(Tk.ARGUMENT_LIST)
    while _in_range(line,inp) and _line_startswith(inp[line],'-'):
        arg_result = parse_argument(inp,line,pos)
        if arg_result.is_error():
            return arg_result
        node.append(arg_result.get_ast())
        line = arg_result.get_line()
        pos = 0 # Reset the column position for the newline. Assuming each argument starts on a new line.
        # Skip any empty lines between arguments.
        while line < len(inp) and inp[line].strip() == "":
            line += 1

    # Programmer error, you should detect an argument dash before calling this function.
    if len(node.branches) == 0:
        return ParseResult(("Attempting to parse non-existing argument list.",line,pos,inp))
    return ParseResult((node,line,pos))

def parse_section(inp : List[str], line: int, pos: int) -> ParseResult:
    """
    EBNF:
        `<section> ::= <text_line> "\\n" <indented_line> ( <argument_list> | <paragraph> )`
    """
    if line > len(inp):
        return ParseResult(("Expected section but reached end of input.",line,pos,inp))
    if _is_indented_line(inp[line]):
        return ParseResult(("Expected section title.",line,pos,inp))
    section_title = inp[line].strip()
    line += 1
    section = Ast(Tk.SECTION,section_title)
    if not line < len(inp) or not _is_indented_line(inp[line]):
        return ParseResult(("Expected indented text after section title.",line,pos,inp))

    section_start = _skip_whitespace(inp[line])
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
        # Skip any empty lines beforehand
    if inp[line].strip() == "":
        line += 1
    if line >= len(inp):
        return ParseResult(("Expected paragraph but reached end of input.",line,pos,inp))
    if not _is_indented_line(inp[line],indent_level):
        return ParseResult(("Expected indented paragraph.",line,pos,inp))
    para = Ast(Tk.PARAGRAPH)
    while line < len(inp) and                                                  \
        ( _is_indented_line(inp[line],indent_level) or inp[line].strip() == "" ):
        # When indent level is 0, disambiguate from a section title by looking
        # forward for an indented line.
        if indent_level == 0                                                   \
            and not _is_indented_line(inp[line],1) and inp[line].strip() != ""  \
            and line + 1 < len(inp) and _is_indented_line(inp[line + 1],1):
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
    if not _is_usage_keyword(inp[line]):
        return ParseResult(("Expected usage section starting with 'Usage:'.",line,pos,inp))
    pos += len("Usage")
    pos += _skip_whitespace(inp[line],pos)
    pos += _skip_chars(inp[line],pos,':',1)
    pos += _skip_whitespace(inp[line],pos)
    usage_text = inp[line][pos:].strip()
    # If the rest of the line is empty look for indented text on the next line.
    if usage_text == "":
        line += 1
        if line < len(inp) and _is_indented_line(inp[line],1):
            usage_text = inp[line].strip()
            line += 1
        else:
            return ParseResult(("Expected indented usage text after usage keyword.",line,pos,inp))

        while line < len(inp) and (_is_indented_line(inp[line],1) \
              or inp[line].strip() == ""):
            usage_text += "\n" + inp[line].strip()
            line += 1
        # Delete any following empty lines
        while usage_text[-1] == " " or usage_text[-1] == '\t' \
            or usage_text[-1] == '\n':
            usage_text = usage_text[0:len(usage_text)-1]
    else: # inline usage
        line += 1 # move past usage line
        # Delete any following empty lines
        while usage_text[-1] == " " or usage_text[-1] == '\t' \
            or usage_text[-1] == '\n':
            usage_text = usage_text[0:len(usage_text)-1]
        pos = 0  # reset pos for next line, always end at start of next line
    return ParseResult((Ast(Tk.USAGE,usage_text),line,pos))

def parse_command_section(inp : List[str], line: int, pos: int) -> ParseResult:
    if line >= len(inp):
        return ParseResult("Expected usage section but reached end of inp")
    is_command_section = _is_command_keyword(inp[line])
    if is_command_section == 0:
        return ParseResult(("Expected command section starting with command keyword.",line,pos,inp))
    pos += is_command_section
    pos += _skip_whitespace(inp[line],pos)
    pos += _skip_chars(inp[line],pos,':',1)
    pos += _skip_whitespace(inp[line],pos)
    # Must be followed by indented list of commands
    if line + 1 >= len(inp) or not _is_indented_line(inp[line + 1],1):
        return ParseResult(("Expected indented command list after command keyword.",line,pos,inp))
    line += 1
    pos = 0
    cmd_section = Ast(Tk.COMMAND_SECTION)
    while line < len(inp) and _is_indented_line(inp[line],1):
        # parse a command
        cmd_line = inp[line].strip()
        if cmd_line == "":
            line += 1
            continue
        cmd_parts = cmd_line.split(' ',1)
        cmd_name = cmd_parts[0]
        cmd_desc = cmd_parts[1].strip() if len(cmd_parts) > 1 else ""
        if cmd_name == "":
            return ParseResult(("Expected command name.",line,pos,inp))
        cmd_node = Ast(Tk.COMMAND,cmd_name)
        if cmd_desc != "":
            cmd_node.append(Ast(Tk.TEXT_LINE,cmd_desc))
        line += 1
        pos = 0
        # skip any empty lines after command
        while line < len(inp) and inp[line].strip() == "":
            line += 1

        # Check for a following indented line, indicating a sub-command.
        while line < len(inp) and _is_indented_line(inp[line],2):
            sub_cmd_line = inp[line].strip()
            if sub_cmd_line == "":
                line += 1
                continue
            sub_cmd_parts = sub_cmd_line.split(' ',1)
            sub_cmd_name = sub_cmd_parts[0]
            sub_cmd_desc = sub_cmd_parts[1].strip() if len(sub_cmd_parts) > 1 else ""
            if sub_cmd_name == "":
                return ParseResult(("Expected sub-command name.",line,pos,inp))
            sub_cmd_node = Ast(Tk.COMMAND,sub_cmd_name)
            if sub_cmd_desc != "":
                sub_cmd_node.append(Ast(Tk.TEXT_LINE,sub_cmd_desc))
            cmd_node.append(sub_cmd_node)
            line += 1
            pos = 0
            # skip any empty lines after sub-command
            while line < len(inp) and inp[line].strip() == "":
                line += 1

        cmd_section.append(cmd_node)

    if len(cmd_section.branches) == 0:
        return ParseResult(("Expected at least one command in command section.",line,pos,inp))
    return ParseResult((cmd_section,line,pos))

def parse_help_text(inp : List[str], line: int, pos: int) -> ParseResult:
    """
    Grammar Rule:
        `<cli_help> ::= <usage_section>? ( <section> | <paragraph> )*`
    """
    # TODO: <prelude> grammar rule for app title/license
    # Configure parser state
    output = Ast(Tk.SYNTAX)
    pos = 0
    line = 0

    if inp == []:
        return ParseResult(("Input is empty",line,pos,inp))

    while line < len(inp):
        pos = 0

        if inp[line].strip() == "": # Skip empty lines
            line += 1
            continue
        is_usage = False
        is_section = False
        sect_title = inp[line]

        # Check for special case usage section which does not require a following indent.
        is_usage = False
        if _is_usage_keyword(sect_title):
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

        # Check for special case command section. Requires a following indent.
        is_command = _is_command_keyword(sect_title)
        if is_command != 0:
            is_command = True
            command_result = parse_command_section(inp,line,pos)
            if command_result.is_error():
                return command_result
            output.append(command_result.get_ast())
            line = command_result.get_line()
            pos = command_result.get_col()
            # skip any empty lines after command section
            while line < len(inp) and inp[line].strip() == "":
                line += 1
            continue

        # If not usage, parse regular section or paragraph
        if not is_usage:
            section_begin = inp[line + 1] if line + 1 < len(inp) else ""
            if _is_indented_line(section_begin,1):
                if section_begin.strip() != "": # next line is empty, paragraph
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

###############################################################################
# Parser
# Models an LL Recursive parser directly from the raw input string, no tokenizer.
###############################################################################
def parse(inp: str) -> ParseResult:
    """ Parse the input string and return the AST. """
    inp_lines : List[str] = inp.splitlines()
    return parse_help_text(inp_lines,0,0)
