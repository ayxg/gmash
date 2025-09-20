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
            outp.append("### Usage")
            outp.append(f"`{br.value.strip()}`\n")

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
                    arg_line = "    "
                    is_first_flag = True
                    for flag in arg.branches:
                        if flag.tk == Tk.SHORT_FLAG:
                            if not is_first_flag:
                                arg_line += " "
                            else:
                                is_first_flag = False
                            arg_line += f"**-{flag.branches[0].value}**"
                        elif flag.tk == Tk.LONG_FLAG:
                            if not is_first_flag:
                                arg_line += " "
                            else:
                                is_first_flag = False
                            arg_line += f"**--{flag.branches[0].value}**"
                        elif flag.tk == Tk.OPTIONAL_ARG:
                            if not is_first_flag:
                                arg_line += " "
                            else:
                                is_first_flag = False
                            arg_line += f"**[{flag.branches[0].value}]**"
                        elif flag.tk == Tk.REQUIRED_ARG:
                            if not is_first_flag:
                                arg_line += " "
                            else:
                                is_first_flag = False
                            arg_line += f"**<{flag.branches[0].value}>**"
                        elif flag.tk == Tk.TEXT_LINE:
                            pass # All text lines appended at end.
                        else:
                            return GeneratorResult(\
                                ("Unexpected token in argument list:" + flag.tk.name ,line,col))


                    arg_brief = ""
                    for text in arg.branches:
                        if text.tk == Tk.TEXT_LINE:
                            arg_brief += "\n        " + text.value.strip()
                    if arg_brief.strip() != "":
                        arg_line += arg_brief
                    outp.append(arg_line)
                    outp.append("")
    return GeneratorResult("\n".join(outp))
