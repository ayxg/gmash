"""
#@doc-------------------------------------------------------------------------#
SPDX-License-Identifier: AGPL-3.0-or-later
Copyright(c) 2025 Anton Yashchenko
#-----------------------------------------------------------------------------#
@project: [gmash] Git Smash
@author(s): Anton Yashchenko
@website: https://www.acpp.dev
#-----------------------------------------------------------------------------#
@file `helptext_md.py`
@created: 2025/09/13
@brief Use `generate_md` to generate markdown documentation from a command
# line
       help notation abstract syntax tree.
#-----------------------------------------------------------------------------#
"""

from typing import Union, List
from helptext_ast import Tk, Ast

class GeneratorResult:
    """GeneratorResult"""
    def __init__(self, res : Union[str,tuple[str,int,int]]) -> None:
        if isinstance(res, str):
            self.md = res
            self.error = None
            self.line = -1
            self.col = -1
        else:
            self.md = ""
            self.error = res[0]
            self.line = res[1]
            self.col = res[2]

    def is_error(self) -> bool:
        """ Check if the result is an error. """
        return self.error is not None

    def get_md(self) -> str:
        """ Get the generated markdown, or empty string if there was an error. """
        return self.md if self.md is not None else ""

    def get_error(self) -> tuple[str,int,int]:
        """ Get the error message, line and column, or `"No error"` if there was no error. """
        return self.error if self.error is not None else ("No error",0,0)


def generate_argument(arg : Ast) -> GeneratorResult:
    """ Generate markdown documentation for a single argument node.
    """
    if arg.tk != Tk.ARGUMENT:
        return GeneratorResult(("Expected argument node",arg.line,arg.col))
    if len(arg.branches) == 0:
        return GeneratorResult(("Invalid ARGUMENT node format.",arg.line,arg.col))

    outp : str = ""
    # Check for a short flag. Must be first if present.
    next_branch = 0
    if arg.branches[0].tk == Tk.SHORT_FLAG:
        outp += f"`-{arg.branches[next_branch].branches[next_branch].value}` "
        next_branch += 1

    # Check for a long flag and any optional/required args.
    has_long_flag : bool = False
    if next_branch < len(arg.branches) and arg.branches[next_branch].tk == Tk.LONG_FLAG:
        has_long_flag = True
        if len(outp) > 0:
            outp += " "
        # The last backtick is added later.
        outp += f"`--{arg.branches[next_branch].branches[0].value}"
        next_branch += 1

    has_positional : bool = False
    while next_branch < len(arg.branches) \
            and (arg.branches[next_branch].tk == Tk.OPTIONAL_ARG \
            or arg.branches[next_branch].tk == Tk.REQUIRED_ARG):
        has_positional = True
        if len(outp) > 0:
            outp += " "
        if arg.branches[next_branch].tk == Tk.OPTIONAL_ARG:
            outp += f" [{arg.branches[next_branch].branches[0].value}]` "
        else:
            outp += f" <{arg.branches[next_branch].branches[0].value}>` "
        next_branch += 1

    if not has_positional and has_long_flag:
        # Close the long flag backtick if no positional args were added.
        outp += "` "

    # Look for any text lines.
    if next_branch < len(arg.branches) and arg.branches[next_branch].tk != Tk.TEXT_LINE:
        return GeneratorResult(("Unexpected token in argument list:" \
            + arg.branches[next_branch].tk.name ,arg.line,arg.col))

    arg_brief : str = ""
    for text in arg.branches:
        if text.tk == Tk.TEXT_LINE:
            arg_brief += "\\\n&nbsp;&nbsp;&nbsp;&nbsp;" + text.value.strip()
    if arg_brief.strip() != "":
        outp += arg_brief

    return GeneratorResult(outp)

def generate_md(ast : Ast) -> GeneratorResult:
    """ Generate markdown documentation from the command line help notation
        abstract syntax tree.
    """
    outp : List[str] = []
    line = 0
    col = 0
    if ast.tk != Tk.SYNTAX:
        return GeneratorResult(("Expected root syntax node",line,col))

    # Find the all usage sections and place them at the top.
    for br in ast.branches:
        if br.tk == Tk.USAGE:
            # Extract the first line of usage up to the first occurrence of a flag
            # and set it as the title of the markdown page.
            if br.value is not None and br.value.strip() != "":
                first_line = br.value.split("\n")[0]
                title : str = ""
                for ch in first_line:
                    if ch.isspace():
                        title += " "
                    elif ch == "-" or ch == "[" or ch == "<":
                        break
                    else:
                        title += ch
                outp.append(f"# {title}\n")
            outp.append("### Usage")
            # If there are multiple usage lines, put each on its own line surrounded by backticks.
            for ln in br.value.split("\n"):
                if ln.strip() != "":
                    outp.append(f"`{ln.strip()}`\n")

    # Get the brief description if any.
    for br in ast.branches:
        if br.tk == Tk.BRIEF:
            for ln in br.branches[0].branches: # tk.PARAGRAPH
                outp.append(ln.value.strip())

    # If there is a paragraph at the root level, before any section, its a brief.
    no_preceding_section = True
    for br in ast.branches:
        if br.tk == Tk.PARAGRAPH:
            if no_preceding_section:
                outp.append("### Brief")
                for ln in br.branches:
                    outp.append(ln.value.strip())
                outp.append("")
        elif br.tk == Tk.SECTION:
            no_preceding_section = False

    for br in ast.branches:
        # -> Section
        if br.tk == Tk.SECTION:
            section = br
            if section.value is not None and section.value.strip() != "":
                outp.append(f"### {section.value.strip()}")
            # -> Section -> Paragraph
            if section.branches[0].tk == Tk.PARAGRAPH:
                for sec_br in section.branches:
                    if sec_br.tk == Tk.PARAGRAPH:
                        for ln in sec_br.branches:
                            outp.append("    " + ln.value.strip())
                outp.append("")
            # -> Section -> Argument_List
            elif section.branches[0].tk == Tk.ARGUMENT_LIST:
                arg_list = section.branches[0]
                if arg_list.value is not None and arg_list.value.strip() != "":
                    outp.append(f"### {arg_list.value.strip()}")
                # -> Section -> Argument_List -> Argument
                for arg in arg_list.branches:
                    arg_res = generate_argument(arg)
                    if arg_res.is_error():
                        return arg_res
                    outp.append(arg_res.get_md())
                    outp.append("")
    return GeneratorResult("\n".join(outp))
