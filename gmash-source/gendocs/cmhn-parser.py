# Copyright(c) Anton Yashchenko 2025
# @created : 2025/09/13
# @project CMHN : Command Line Help Notation Parser
# @brief Grammar for parsing 'help' manuals displayed by command line applications.

from typing import List, Optional, Union
from enum import Enum, auto

###############################################################################
# Impl
# Models an LL Recursive parser directly from the raw input, no tokenizer.
###############################################################################

is_alpha = lambda c: c.isalpha() or c == '_'
is_numeric = lambda c: c.isdigit()
is_indent = lambda c: c in ("\n    " | "\n  " | "\n\t")
is_text = lambda c: c not in ('\n')
is_dash = lambda c: c == '-'
is_newline = lambda c: c == '\n'
is_whitespace = lambda c: c in (' ', '\t')

class eTk(Enum):
  USAGE = auto()
  TEXT = auto()
  NEWLINE = auto()
  SHELL_IDENT = auto()
  LONG_FLAG_IDENT = auto()
  SHORT_FLAG_IDENT = auto()
  INDENTED_LINE = auto()
  SHORT_FLAG = auto()
  LONG_FLAG = auto()
  OPTIONAL_ARG = auto()
  REQUIRED_ARG = auto()
  SPACE = auto()
  COLON = auto()
  TEXT_LINE = auto()
  ARGUMENT = auto()
  ARGUMENT_LIST = auto()
  PARAGRAPH = auto()
  SECTION = auto()

class Ast:
  def __init__(self, type: eTk, value: Optional[str] = None,
               line: int = 0, col: int = 0, end_line: int = 0, end_col: int = 0,
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

class Parser:
  def __init__(self, tokens):
    self.tokens = tokens
    self.pos = 0
    self.output = []

  def curr(self):
    if self.pos < len(self.tokens):
      return self.tokens[self.pos]
    return None

  def advance(self, count : int = 1):
    self.pos += count

  def peek(self, offset: int = 1) -> Optional[Tk]:
    if self.pos + offset < len(self.tokens):
      return self.tokens[self.pos + offset]
    return None

  def at_eof(self):
    return self.pos >= len(self.tokens)

  def eat(self, expected_type: eTk) -> Tk:
    token = self.curr()
    if token is None:
      raise Exception(f"Unexpected end of input, expected {expected_type.name}")
    if token.type != expected_type:
      raise Exception(f"Unexpected token {token.type.name} at line {token.line}, col {token.col}, expected {expected_type.name}")
    self.advance()
    return token

  def skip_whitespace(self):
    while self.curr() and ( self.curr().type == eTk.SPACE or self.curr().type == eTk.NEWLINE):
      self.advance()

  def parse_syntax(self,input):
    # <cli_help> ::= "Usage: "? <text_line> "\n\n" <paragraph> <section>*
    # Consume optional "usage:" prefix
    if input.startswith("Usage") or input.startswith("usage")     \
        or input.startswith("USAGE"):
          self.advance(len("usage"))
    self.skip_whitespace()
    if self.curr() and self.curr() == ':':
      self.advance()
      self.skip_whitespace()
    # Get usage line
    self.parse_paragraph()
    self.eat(eTk.NEWLINE)
    # Get brief description paragraph
    self.parse_paragraph()
    self.eat(eTk.NEWLINE)
    # Look for any identified sections
    while self.curr():
      if self.curr().type == eTk.SHELL_IDENT:
        self.parse_section()
      else:


            if self.curr().type == eTk.SPACE:
                self.advance()

    root = Ast('CLI_HELP')
    self.eat(eTk.USAGE)  # "Usage: "
    root.append(self.parse_text_line())
    self.eat(eTk.NEWLINE)
    self.eat(eTk.NEWLINE)
    root.append(self.parse_paragraph())

    while self.curr() and self.curr().type == eTk.SHELL_IDENT:
      root.append(self.parse_section())
    return root

  def parse_text_line(self):
    # <text_line>
    node = Ast('TEXT_LINE')
    node.append(self.eat(eTk.TEXT))
    return node

  def parse_paragraph(self):
    # <paragraph> ::= ( <text_line> "\n" )+
    node = Ast('PARAGRAPH')
    while self.curr() and self.curr().type == eTk.TEXT \
        and (self.curr().type != eTk.NEWLINE and self.peek().type != eTk.NEWLINE):
      node.append(self.parse_text_line())
      self.eat(eTk.NEWLINE)
      self.eat(eTk.NEWLINE)
    return node

  def parse_section(self):
    # <section> ::= <shell_ident> <indented_line> ( <argument_list> | <paragraph> )
    node = Ast('SECTION')
    node.append(self.eat(eTk.SHELL_IDENT))
    node.append(self.eat(eTk.INDENTED_LINE))
    if self.curr() and self.curr().type in (eTk.SHORT_FLAG, eTk.LONG_FLAG):
      node.append(self.parse_argument_list())
    else:
      node.append(self.parse_paragraph())
    return node

  def parse_argument_list(self):
    # <argument_list> ::= ( <argument> "\n" )+
    node = Ast('ARGUMENT_LIST')
    while self.curr() and self.curr().type in (eTk.SHORT_FLAG, eTk.LONG_FLAG):
      node.append(self.parse_argument())
      self.eat(eTk.NEWLINE)
    return node

  def parse_argument(self):
    # <argument> ::= (( <short_flag> ) " ")? (( <long_flag> ) " " )+ ( <optional_arg> |  <required_arg> )? <indented_line> ": " <text_line>
    node = Ast('ARGUMENT')
    if self.curr().type == eTk.SHORT_FLAG:
      node.append(self.eat(eTk.SHORT_FLAG))
      self.eat(eTk.SPACE)
    while self.curr().type == eTk.LONG_FLAG:
      node.append(self.eat(eTk.LONG_FLAG))
      self.eat(eTk.SPACE)
    if self.curr().type == eTk.OPTIONAL_ARG:
      node.append(self.eat(eTk.OPTIONAL_ARG))
    elif self.curr().type == eTk.REQUIRED_ARG:
      node.append(self.eat(eTk.REQUIRED_ARG))
    node.append(self.eat(eTk.INDENTED_LINE))
    self.eat(eTk.COLON)
    self.eat(eTk.SPACE)
    node.append(self.parse_text_line())
    return node


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
# Dev debugging stuff
###############################################################################

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

def run_test_parse():
  test_input = (
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
    "A paragraph of text, these are the details of a command.\n\n\n\n"
  )

  # Tokenize the input
  tokenizer = Lexer(test_input)
  tokens = tokenizer.tokenize()

  print("DEBUG - First 20 tokens:")
  for i, token in enumerate(tokens[:20]):
      print(f"{i}: {token}")
  print("...")

  # Parse the tokens
  parser = Parser(tokens)
  try:
      ast = parser.parse_syntax()
      print("Parsing successful!")
      print("AST Tree:")
      ast.print_ascii_tree()
      # Basic assertions
      assert ast.type == 'CLI_HELP'
      assert len(ast.children) >= 2  # At least usage and description
      print("Unit test passed!")
  except Exception as e:
      print(f"Parsing failed: {e}")
      raise


###############################################################################
# Command Line Interface
###############################################################################

if __name__ == "__main__":
  # if --test argument is postional argument 1, run unit tests
  import sys
  if '--test' == sys.argv[1]:
    ut_parser_shell_ident()
    ut_parser_long_flag_ident()
    ut_parser_short_flag_ident()
    ut_parser_text_line()
    ut_parser_short_flag()
    ut_parser_long_flag()
    ut_parser_optional_arg()
    ut_parser_required_arg()
    ut_parser_argument()
    ut_parser_argument_list()
    ut_parser_paragraph()
    ut_parser_section()
    ut_parser_usage_line()
    ut_parser_brief_section()
    ut_parser_basic()
  else:
  # else the entire argument is treated as a help text to parse
    if len(sys.argv) < 2:
      print("Usage: python gen-docs.py '<help text to parse>'")
      sys.exit(1)
    help_text = sys.argv[1]
    parser = Parser()
    try:
        ast = parser.parse_syntax(help_text)
        ast.print_ascii_tree()
    except Exception as e:
        print(f"Parsing failed: {e}")
        raise
