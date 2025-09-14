# Copyright(c) Anton Yashchenko 2025
# @created : 2025/09/13
# @project CMHN : Command Line Help Notation Parser
# @brief Grammar for parsing 'help' manuals displayed by command line applications.

import sys
from typing import List, Optional
from enum import Enum, auto

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

"""

###############################################################################
# Impl
# Models an LL Recursive parser directly from the raw input, no tokenizer.
###############################################################################
is_alnumus = lambda c: c.isalnum() or c == '_'
is_alpha = lambda c: c.isalpha() or c == '_'
is_numeric = lambda c: c.isdigit()
is_indent = lambda c: c in ("\n    " | "\n  " | "\n\t")
is_text = lambda c: c not in ('\n')
is_dash = lambda c: c == '-'
is_newline = lambda c: c == '\n'
is_whitespace = lambda c: c in (' ', '\t')

class eTk(Enum):
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
  def __init__(self,
               type: eTk = eTk.NOTHING,
               value: Optional[str] = None,
               line: int = 0,
               col: int = 0,
               end_line: int = 0,
               end_col: int = 0,
               branches: Optional[List['Ast']] = None
               ) -> None:
    self.type: eTk = type
    self.value: Optional[str] = value
    self.line: int = line
    self.col: int = col
    self.end_line: int = end_line
    self.end_col: int = end_col
    self.branches: List[Ast] = branches if branches is not None else []

  def append(self, br: 'Ast') -> None:
    self.branches.append(br)

  def __repr__(self) -> str:
    return f'Ast({self.type}, {self.value}, {self.branches})'

def verbose_print(msg: str) -> None:
  if verbose_mode:
    print(msg)

def debug_print(msg: str) -> None:
  if debug_mode:
    print(msg)

def print_help_text() -> None:
  print(CMNH_TITLE, CMNH_VERSION, CMNH_LICENSE, sep="\n")
  print(CMNH_HELP)
  sys.exit(0)

def print_ascii_tree(astnode : Ast, prefix: str = "", is_last: bool = True) -> None:
  """Print the AST as a compact ASCII tree with boxes and connection lines"""
  content = astnode.type
  if astnode.value is not None:
    content += f"\n{astnode.value}"

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

      if is_last_child:
        print(prefix + "    │   ")
        print(prefix + "    │   ")
        print(prefix + "    └───────┐")
      else:
        print(prefix + "    │   ")
        print(prefix + "    │   ")
        print(prefix + "    ├───────┐")

      # Calculate child prefix - align with the connection point
      child_prefix = prefix
      if is_last_child:
        child_prefix += "       "  # 7 spaces to align with the end of "└─ "
      else:
        child_prefix += "    │  "  # 6 spaces: 4 for indent + │ + 2 spaces

      if hasattr(child, 'print_ascii_tree'):
        child.print_ascii_tree(child_prefix, is_last_child)
      else:
        token_content = child.type
        if hasattr(child, 'value') and child.value is not None:
            token_content += f"\n{child.value}"

        token_lines = token_content.split('\n')
        token_max_width = max(len(line) for line in token_lines) if token_lines else 0

        token_box_lines = []
        token_box_lines.append("┌" + "─" * (token_max_width + 2) + "┐")
        for line in token_lines:
            token_box_lines.append("│ " + line.ljust(token_max_width) + " │")
        token_box_lines.append("└" + "─" * (token_max_width + 2) + "┘")

        for j, line in enumerate(token_box_lines):
            print(child_prefix + line)

class Parser:
  def __init__(self, input: str = "") -> None:
    self.input = input
    self.pos = 0
    self.output = []

  def curr(self):
    if self.pos < len(self.input):
      return self.input[self.pos]
    return None

  def advance(self, count : int = 1):
    self.pos += count

  def peek(self, offset: int = 1) -> int:
    if self.pos + offset < len(self.input):
      return self.input[self.pos + offset]
    return None

  def at_eof(self):
    return self.pos >= len(self.input)

  # Attempt to consume the next token if it matches one of the expected strings.
  # If successful, append the token to the provided Ast node , advance by string length,
  # and return True.
  # Otherwise, return False without modifying the Ast node.
  def eat(self, append_to : Ast,production : eTk ,expected_strings : List[str] = []):
    if self.at_eof():
      return False
    elif expected_strings:
      for expected_string in expected_strings:
        if self.input.startswith(expected_string, self.pos):
          append_to.append(Ast(production,expected_string))
          self.advance(len(expected_string))
          return True
    return False

  # pass count -1 to skip all consecutive chars, returns the number of chars skipped
  def skip(self, char: str, count: int = 1) -> int:
    skipped = 0
    while self.curr() and self.curr() == char and (count == -1 or skipped < count):
      self.advance()
      skipped += 1
    return skipped

  def skip_whitespace(self):
    while self.curr() and ( self.curr() == ' ' or self.curr() == "\n"):
      self.advance()

  def skip_empty_lines(self):
    while self.curr() and self.curr() == "\n":
      self.advance()

  def parse_syntax(self,input: str) -> Ast:
    # <cli_help> ::= "Usage: "? <text_line> "\n\n" <paragraph> <section>*
    root = Ast(eTk.SYNTAX)
    self.input = input
    self.pos = 0

    # Consume optional "usage:" prefix
    usage = None
    if self.eat(root,eTk.USAGE,"Usage","usage","USAGE","use","Use","USE"):
      usage = root.branches[0]
    else:
      usage = root.append(Ast(eTk.USAGE,""))
    self.skip_whitespace()
    self.skip(':',1)
    self.skip_whitespace()
    self.parse_text_line(usage)
    self.skip_empty_lines()

    # Consume optional brief description
    brief = None
    if self.eat(root,eTk.BRIEF,"brief","Brief","BRIEF"):
      brief = root.branches[1]
    else:
      brief = root.append(Ast(eTk.BRIEF,""))

    self.skip_whitespace()
    self.skip(':',1)
    self.skip_whitespace()
    self.parse_paragraph(brief)
    self.expect('\n')
    self.skip_whitespace()
    self.skip_empty_lines()

    # Parse all other sections
    while not self.at_eof():
      if self.curr() and is_alnumus(self.curr()):
        self.parse_section(root)
        while self.curr() and self.curr() == '\n':
          self.advance()
          self.skip_whitespace()
      else:
        self.advance()

    return root

  def expect(self, char: str) -> None:
    if self.curr() != char:
      raise Exception(f"Expected '{char}' at position {self.pos}, found '{self.curr()}'")
    self.advance()

  # All characters until newline
  def parse_text_line(self, append_to : Ast) -> None:
    text = ""
    while not self.at_eof() and is_text(self.curr()):
      text += self.curr()
      self.advance()
    if self.curr() == '\n' : self.advance()
    append_to.append(Ast(eTk.TEXT_LINE,text))

  # A paragraph is one or more lines of text separated by newlines
  def parse_paragraph(self, append_to : Ast) -> None:
    paragraph = Ast(eTk.PARAGRAPH)
    while not self.at_eof() and is_text(self.curr()):
      self.parse_text_line(paragraph)
    append_to.append(paragraph)

  # A section starts with a title (shell ident) followed by indented lines
  def parse_section(self, append_to : Ast) -> None:
    section = Ast(eTk.SECTION)
    title = ""
    while not self.at_eof() and is_alnumus(self.curr()):
      title += self.curr()
      self.advance()
    section.append(Ast(eTk.SHELL_IDENT,title))
    self.skip_whitespace()
    indent = ""
    while not self.at_eof() and is_indent(self.curr()):
      indent += self.curr()
      self.advance()
    section.append(Ast(eTk.INDENTED_LINE,indent))
    self.skip_whitespace()
    # Determine if next is argument list or paragraph
    if self.curr() and (self.curr() == '-' or self.curr() == '--'):
      self.parse_argument_list(section)
    else:
      self.parse_paragraph(section)
    append_to.append(section)

  # An argument list is one or more arguments
  def parse_argument_list(self, append_to : Ast) -> None:
    arg_list = Ast(eTk.ARGUMENT_LIST)
    while not self.at_eof() and (self.curr() == '-' or self.curr() == '--'):
      self.parse_argument(arg_list)
      self.skip_whitespace()
    append_to.append(arg_list)

  # An argument consists of optional short flag, one or more long flags,
  # optional or required argument, indented line, colon, text line
  def parse_argument(self, append_to : Ast) -> None:
    argument = Ast(eTk.ARGUMENT)
    self.skip_whitespace()
    if self.curr() == '-':
      self.parse_short_flag(argument)
      self.skip_whitespace()
    while self.curr() == '-':
      self.parse_long_flag(argument)
      self.skip_whitespace()
    if self.curr() == '[':
      self.parse_optional_arg(argument)
      self.skip_whitespace()
    elif self.curr() == '<':
      self.parse_required_arg(argument)
      self.skip_whitespace()
    indent = ""
    while not self.at_eof() and is_indent(self.curr()):
      indent += self.curr()
      self.advance()
    argument.append(Ast(eTk.INDENTED_LINE,indent))
    self.skip_whitespace()
    self.expect(':')
    self.skip_whitespace()
    self.parse_text_line(argument)
    append_to.append(argument)
  # Short cli flag identifier, single character.
  # <short_flag_ident> ::= ( [a-z] | [A-Z] )
  def parse_short_flag_ident(self, append_to : Ast) -> None:
    if not self.curr() or not is_alpha(self.curr()):
      raise Exception(f"Expected short flag identifier at position {self.pos}, found '{self.curr()}'")
    ident = self.curr()
    self.advance()
    append_to.append(Ast(eTk.SHORT_FLAG_IDENT,ident))

  # Short cli flag, starts with single dash
  # <short_flag> ::= "-" ( [a-z] | [A-Z] )
  def parse_short_flag(self, append_to : Ast) -> None:
    short_flag = Ast(eTk.SHORT_FLAG)
    self.expect('-')
    self.parse_short_flag_ident(short_flag)
    append_to.append(short_flag)

  # Long cli flag identifier, multiple characters.
  # <long_flag_ident> ::= ( [a-z] | [A-Z] |
  #     "-" | "_" | [0-9] )+
  def parse_long_flag_ident(self, append_to : Ast) -> None:
    ident = ""
    while not self.at_eof() and (is_alnumus(self.curr()) or self.curr() == '-'):
      ident += self.curr()
      self.advance()
    if not ident:
      raise Exception(f"Expected long flag identifier at position {self.pos}, found '{self.curr()}'")
    append_to.append(Ast(eTk.LONG_FLAG_IDENT,ident))

  # Long cli flag, starts with double dash
  # <long_flag> ::= "--" <long_flag_ident>
  def parse_long_flag(self, append_to : Ast) -> None:
    long_flag = Ast(eTk.LONG_FLAG)
    self.expect('-')
    self.expect('-')
    self.parse_long_flag_ident(long_flag)
    append_to.append(long_flag)

  # Optional argument, enclosed in square brackets
  # <optional_arg> ::= "[" <shell_ident> "]"
  def parse_optional_arg(self, append_to : Ast) -> None:
    optional_arg = Ast(eTk.OPTIONAL_ARG)
    self.expect('[')
    self.parse_shell_ident(optional_arg)
    self.expect(']')
    append_to.append(optional_arg)

  # Required argument, enclosed in angle brackets
  # <required_arg> ::= "<" <shell_ident> ">"
  def parse_required_arg(self, append_to : Ast) -> None:
    required_arg = Ast(eTk.REQUIRED_ARG)
    self.expect('<')
    self.parse_shell_ident(required_arg)
    self.expect('>')
    append_to.append(required_arg)

  # Shell identifier, alphanumeric and underscores
  # <shell_ident> ::= ( [a-z] | [A-Z] | [
  #     "_" | [0-9] )+
  def parse_shell_ident(self, append_to : Ast) -> None:
    ident = ""
    while not self.at_eof() and is_alnumus(self.curr()):
      ident += self.curr()
      self.advance()
    if not ident:
      raise Exception(f"Expected shell identifier at position {self.pos}, found '{self.curr()}'")
    append_to.append(Ast(eTk.SHELL_IDENT,ident))

###############################################################################
# Unit Test Utils
###############################################################################

def test_parser_func(func,test_name,parser_input,expected_output):
  try:
      result = func(parser_input)
      assert result == expected_output, \
        f"Test {test_name} failed: expected {expected_output}, got {result}"
      print(f"Test {test_name} passed.")
  except Exception as e:
      print(f"Test {test_name} raised an exception: {e}")

def test_parser(test_name, parser_input, expected_output):
  try:
      parser = Parser()
      ast = parser.parse_syntax(parser_input)
      assert ast == expected_output, \
        f"Test {test_name} failed: expected {expected_output}, got {ast}"
      print(f"Test {test_name} passed.")
  except Exception as e:
      print(f"Test {test_name} raised an exception: {e}")


###############################################################################
# Unit Tests
###############################################################################

# Help text's running shell variable identifier format.
#   - Begin with alpha or underscore.
#   - May contain alpha, numeric or underscore.
# <shell_ident> ::= ( [a-z] | [A-Z] ) ( [a-z] | [A-Z] | [0-9] )+ ( [a-z] | [A-Z] )
def ut_parser_shell_ident():
  test_parser_func(
    func=lambda inp: Parser().parse_shell_ident(inp),
    test_name="ut_parser_shell_ident",
    parser_input="TitleForASection_CanHaveAlphaOrNumerics123\n",
    expected_output=Ast(eTk.SHELL_IDENT,'TitleForASection_CanHaveAlphaOrNumerics123')
  )

# Long cli argument flag format.*/
#   - Begin with alpha.*/
#   - May contain alpha, numeric or dash.*/
#   - End with alpha or numeric.*/
# <long_flag_ident> ::= ( [a-z] | [A-Z] )+ ( [a-z] | [A-Z] | "-" )+ ( [a-z] | [A-Z] | [0-9] )
def ut_parser_long_flag_ident():
  test_parser_func(
    func=lambda inp: Parser().parse_long_flag_ident(inp),
    test_name="ut_parser_long_flag_ident",
    parser_input="long-flag-ident123\n",
    expected_output=Ast(eTk.LONG_FLAG_IDENT,'long-flag-ident123')
  )

# Short cli flag identifier, single character.
# <short_flag_ident> ::= ( [a-z] | [A-Z] )
def ut_parser_short_flag_ident():
  test_parser_func(
    func=lambda inp: Parser().parse_short_flag_ident(inp),
    test_name="ut_parser_short_flag_ident",
    parser_input="f\n",
    expected_output=Ast(eTk.SHORT_FLAG_IDENT,'f')
  )

# A line of text which ends on a newline.*/
# <text_line> ::= ( " " | "!" | "\"" | "#" | "$" | "%" | "&" | "'" | "(" | ")" | "*" | "+" | "," | "-" | "." | "/" |
# "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" | ":" | ";" | "<" | "=" | ">" | "?" |
# "@" | "A" | "B" | "C" | "D" | "E" | "F" | "G" | "H" | "I" | "J" | "K" | "L" | "M" | "N" | "O" |
# "P" | "Q" | "R" | "S" | "T" | "U" | "V" | "W" | "X" | "Y" | "Z" | "[" | "\\" | "]" | "^" | "_" |
# "`" | "a" | "b" | "c" | "d" | "e" | "f" | "g" | "h" | "i" | "j" | "k" | "l" | "m" | "n" | "o" |
# "p" | "q" | "r" | "s" | "t" | "u" | "v" | "w" | "x" | "y" | "z" | "{" | "|" | "}" | "~" )*
def ut_parser_text_line():
  test_parser_func(
    func=lambda inp: Parser().parse_long_flag_ident(inp),
    test_name="ut_parser_text_line",
    parser_input="""Hello World! This is a line of text !@#$%^&*()_+1234567890-=;'[]/.,<>?":\} {
""",
    expected_output=Ast(eTk.TEXT_LINE,"""Hello World! This is a line of text !@#$%^&*()_+1234567890-=;'[]/.,<>?":\} {""")
  )

# <short_flag> ::= "-" ( [a-z] | [A-Z] )
def ut_parser_short_flag():
  test_parser_func(
    func=lambda inp: Parser().parse_short_flag(inp),
    test_name="ut_parser_short_flag",
    parser_input="-f \n",
    expected_output=Ast(eTk.SHORT_FLAG, None ,[Ast(eTk.SHORT_FLAG_IDENT,'f')])
  )

# <long_flag> ::= "--" <long_flag_ident>
def ut_parser_long_flag():
  test_parser_func(
    func=lambda inp: Parser().parse_long_flag(inp),
    test_name="ut_parser_long_flag",
    parser_input="--long-flag-ident123 \n",
    expected_output=Ast(eTk.LONG_FLAG,None,[Ast(eTk.LONG_FLAG_IDENT,'long-flag-ident123')])
  )

# <optional_arg> ::= "[" <shell_ident> "]"
def ut_parser_optional_arg():
  test_parser_func(
    func=lambda inp: Parser().parse_optional_arg(inp),
    test_name="ut_parser_optional_arg",
    parser_input="[optional_arg123] \n",
    expected_output=Ast(eTk.OPTIONAL_ARG,None,[Ast(eTk.SHELL_IDENT,'optional_arg123')])
  )

# <required_arg> ::= "<" <shell_ident> ">"
def ut_parser_required_arg():
  test_parser_func(
    func=lambda inp: Parser().parse_required_arg(inp),
    test_name="ut_parser_required_arg",
    parser_input="<required_arg123> \n",
    expected_output=Ast(eTk.REQUIRED_ARG,None,[Ast(eTk.SHELL_IDENT,'required_arg123')])
  )

# <argument> ::= (( <short_flag> ) " ")? (( <long_flag> ) " " )+
#     ( <optional_arg> |  <required_arg> )? <indented_line> ": " <text_line>
def ut_parser_argument():
  test_parser_func(
    func=lambda inp: Parser().parse_argument(inp),
    test_name="ut_parser_argument",
    parser_input="-f --long-flag-ident123 [optional_arg123] \n    : This is a text line describing the argument.\n",
    expected_output=Ast(eTk.ARGUMENT,None,[
      Ast(eTk.SHORT_FLAG,None,[Ast(eTk.SHORT_FLAG_IDENT,'f')]),
      Ast(eTk.LONG_FLAG,None,[Ast(eTk.LONG_FLAG_IDENT,'long-flag-ident123')]),
      Ast(eTk.OPTIONAL_ARG,None,[Ast(eTk.SHELL_IDENT,'optional_arg123')]),
      Ast(eTk.TEXT_LINE,"This is a text line describing the argument.")
    ])
  )

# <argument_list> ::= ( <argument> "\n" )+
def ut_parser_argument_list():
  test_parser_func(
    func=lambda inp: Parser().parse_argument_list(inp),
    test_name="ut_parser_argument_list",
    parser_input=(
      "-f --long-flag-ident123 [optional_arg123] \n"
      "    : This is a text line describing the argument.\n"
      "-g --another-flag <required_arg456> \n"
      "    : Another argument description line.\n"
    ),
    expected_output=Ast(eTk.ARGUMENT_LIST,None,[
      Ast(eTk.ARGUMENT,None,[
        Ast(eTk.SHORT_FLAG,None,[Ast(eTk.SHORT_FLAG_IDENT,'f')]),
        Ast(eTk.LONG_FLAG,None,[Ast(eTk.LONG_FLAG_IDENT,'long-flag-ident123')]),
        Ast(eTk.OPTIONAL_ARG,None,[Ast(eTk.SHELL_IDENT,'optional_arg123')]),
        Ast(eTk.TEXT_LINE,"This is a text line describing the argument.")
      ]),
      Ast(eTk.ARGUMENT,None,[
        Ast(eTk.SHORT_FLAG,None,[Ast(eTk.SHORT_FLAG_IDENT,'g')]),
        Ast(eTk.LONG_FLAG,None,[Ast(eTk.LONG_FLAG_IDENT,'another-flag')]),
        Ast(eTk.REQUIRED_ARG,None,[Ast(eTk.SHELL_IDENT,'required_arg456')]),
        Ast(eTk.TEXT_LINE,"Another argument description line.")
      ])
    ])
  )

# <paragraph> ::= ( <text_line> "\n"+ )+
def ut_parser_paragraph():
  test_parser_func(
    func=lambda inp: Parser().parse_paragraph(inp),
    test_name="ut_parser_paragraph",
    parser_input=(
      "This is the first line of a paragraph.\n"
      "This is the second line of the same paragraph.\n"
      "\n"
    ),
    expected_output=Ast(eTk.PARAGRAPH,None,[
      Ast(eTk.TEXT_LINE,"This is the first line of a paragraph."),
      Ast(eTk.TEXT_LINE,"This is the second line of the same paragraph."),
    ])
  )

#  Help Section */
# A regular help section starting with a title. May be a paragraph of text or a list of arguments.*/
# <section> ::= <shell_ident> <indented_line> ( <argument_list> | <paragraph> )
def ut_parser_section():
  test_parser_func(
    func=lambda inp: Parser().parse_section(inp),
    test_name="ut_parser_section",
    parser_input=(
      "Parameters\n"
      "    -f --force \n"
      "        : Force changes and overwrite.\n"
      "    -g --another-flag <required_arg456> \n"
      "        : Another argument description line.\n"
    ),
    expected_output=Ast(eTk.SECTION,None,[
      Ast(eTk.SHELL_IDENT,'Parameters'),
      Ast(eTk.INDENTED_LINE,'\n    '),
      Ast(eTk.ARGUMENT_LIST,None,[
        Ast(eTk.ARGUMENT,None,[
          Ast(eTk.SHORT_FLAG,None,[Ast(eTk.SHORT_FLAG_IDENT,'f')]),
          Ast(eTk.LONG_FLAG,None,[Ast(eTk.LONG_FLAG_IDENT,'force')]),
          Ast(eTk.TEXT_LINE,"Force changes and overwrite.")
        ]),
        Ast(eTk.ARGUMENT,None,[
          Ast(eTk.SHORT_FLAG,None,[Ast(eTk.SHORT_FLAG_IDENT,'g')]),
          Ast(eTk.LONG_FLAG,None,[Ast(eTk.LONG_FLAG_IDENT,'another-flag')]),
          Ast(eTk.REQUIRED_ARG,None,[Ast(eTk.SHELL_IDENT,'required_arg456')]),
          Ast(eTk.TEXT_LINE,"Another argument description line.")
        ])
      ])
    ])
  )

# Usage Line & Title */
# Usage title is expected at the start of the help text. All other sections with a title matching */
# this pattern are interpreted as paragraphs. */
# <usage_title> ::= ( ( "Usage" | "usage" | "USAGE" |  "use" | "Use" | "USE" )
#	    <ignored_whitespace> <optional_colon> <ignored_whitespace> ) | E
# <usage_line> ::= <usage_title> <text_line> "\n"+ | E
def ut_parser_usage_line():
  test_parser_func(
    func=lambda inp: Parser().parse_usage_line(inp),
    test_name="ut_parser_usage_line",
    parser_input=(
      "Usage: gmash dirs prefix --p <prefix> --P [fileOrFolder]\n\n"
    ),
    expected_output=Ast(eTk.USAGE_LINE,None,[
      Ast(eTk.USAGE,"gmash dirs prefix --p <prefix> --P [fileOrFolder]")
    ])
  )

# Brief Section
# Optional brief paragraph which does not require a title.
# Must be the first paragraph following the usage line.
def ut_parser_brief_section():
  test_parser_func(
    func=lambda inp: Parser().parse_brief_section(inp),
    test_name="ut_parser_brief_section",
    parser_input=(
      "Add a prefix to each top-level file in a directory.\n\n"
    ),
    expected_output=Ast(eTk.BRIEF_SECTION,None,[
      Ast(eTk.PARAGRAPH,None,[
        Ast(eTk.TEXT_LINE,"Add a prefix to each top-level file in a directory.")
      ])
    ])
  )

# <cli_help> ::= <usage_line> <brief_section> <section>*
def ut_parser_basic():
  test_parser(test_name="ut_parser_basic",parser_input=""
    "Usage: gmash dirs prefix --p <prefix> --P [fileOrFolder]\n\n"
    "Add a prefix to each top-level file in a directory.\n\n"
    "Parameters\n"
    "   -f --force \n"
    "    : Force changes and overwrite.\n"
    "   -f --force \n"
    "    : Force changes and overwrite.\n\n"
    "Display\n"
    "  -h --help\n"
    "    : Display help.\n"
    "  -v -version\n"
    "    : Display version\n\n"
    "Details\n"
    "A paragraph of text, these are the details of a command.\n\n\n\n",
    expected_output=Ast(eTk.CLI_HELP,None,[
      Ast(eTk.USAGE_LINE,None,[
        Ast(eTk.USAGE,"gmash dirs prefix --p <prefix> --P [fileOrFolder]")
      ]),
      Ast(eTk.BRIEF_SECTION,None,[
        Ast(eTk.PARAGRAPH,None,[
          Ast(eTk.TEXT_LINE,"Add a prefix to each top-level file in a directory.")
        ])
      ]),
      Ast(eTk.SECTION,None,[
        Ast(eTk.SHELL_IDENT,'Parameters'),
        Ast(eTk.INDENTED_LINE,'\n    '),
        Ast(eTk.ARGUMENT_LIST,None,[
          Ast(eTk.ARGUMENT,None,[
            Ast(eTk.SHORT_FLAG,None,[Ast(eTk.SHORT_FLAG_IDENT,'f')]),
            Ast(eTk.LONG_FLAG,None,[Ast(eTk.LONG_FLAG_IDENT,'force')]),
            Ast(eTk.TEXT_LINE,"Force changes and overwrite.")
          ]),
          Ast(eTk.ARGUMENT,None,[
            Ast(eTk.SHORT_FLAG,None,[Ast(eTk.SHORT_FLAG_IDENT,'f')]),
            Ast(eTk.LONG_FLAG,None,[Ast(eTk.LONG_FLAG_IDENT,'force')]),
            Ast(eTk.TEXT_LINE,"Force changes and overwrite.")
          ])
        ])
      ]),
      Ast(eTk.SECTION,None,[
        Ast(eTk.SHELL_IDENT,'Display'),
        Ast(eTk.INDENTED_LINE,'\n  '),
        Ast(eTk.ARGUMENT_LIST,None,[
          Ast(eTk.ARGUMENT,None,[
            Ast(eTk.SHORT_FLAG,None,[Ast(eTk.SHORT_FLAG_IDENT,'h')]),
            Ast(eTk.LONG_FLAG,None,[Ast(eTk.LONG_FLAG_IDENT,'help')]),
            Ast(eTk.TEXT_LINE,"Display help.")
          ]),
          Ast(eTk.ARGUMENT,None,[
            Ast(eTk.SHORT_FLAG,None,[Ast(eTk.SHORT_FLAG_IDENT,'v')]),
            Ast(eTk.LONG_FLAG,None,[Ast(eTk.LONG_FLAG_IDENT,'version')]),
            Ast(eTk.TEXT_LINE,"Display version")
          ])
        ])
      ]),
      Ast(eTk.SECTION,None,[
        Ast(eTk.SHELL_IDENT,'Details'),
        Ast(eTk.INDENTED_LINE,'\n'),
        Ast(eTk.PARAGRAPH,None,[
          Ast(eTk.TEXT_LINE,"A paragraph of text, these are the details of a command.")
        ])
      ])
    ])
  )


###############################################################################
# Command Line Interface
###############################################################################
verbose_mode = False
debug_mode = False

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
    print("Running unit tests...")
    # ut_parser_shell_ident()
    # ut_parser_long_flag_ident()
    # ut_parser_short_flag_ident()
    # ut_parser_text_line()
    # ut_parser_short_flag()
    # ut_parser_long_flag()
    # ut_parser_optional_arg()
    # ut_parser_required_arg()
    # ut_parser_argument()
    # ut_parser_argument_list()
    # ut_parser_paragraph()
    # ut_parser_section()
    # ut_parser_usage_line()
    # ut_parser_brief_section()
    # ut_parser_basic()
    print("All unit tests completed.")
    sys.exit(0)

  # Enable debug mode
  verbose_mode = any(arg == '-V' or arg == '--verbose' for arg in sys.argv)
  debug_mode = any(arg == '-d' or arg == '--debug' for arg in sys.argv)
  if debug_mode : verbose_mode = True

  # Pop the script name
  sys.argv.pop(0)

  # Remove all flags from args
  sys.argv = [arg for arg in sys.argv if not arg.startswith('-')]

  # If no args left, show help and exit
  if len(sys.argv) < 1:
    print_help_text()

  help_text = sys.argv[0]

  verbose_print("\033[92mParing Input...\033[0m")
  verbose_print(help_text)

  parser = Parser()
  parser.parse_syntax(help_text)

  verbose_print("\033[92mDisplaying AST...\033[0m")
  if verbose_mode:
    print_ascii_tree(parser.output)
