# Copyright(c) Anton Yashchenko 2025
# @created : 2025/09/13
# @project CMHN : Command Line Help Notation Parser
# @brief Generates markdown doc pages from command line help output.
#        Help text format must be follow the CMHN(Command Line Help Notation) grammar.
from helptext_ast import Tk, Ast
from typing import Union, List, Optional


class GeneratorResult:
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
        return self.error is not None


    def get_md(self) -> str:
        return self.md if self.md is not None else ""

    def get_error(self) -> tuple[str,int,int]:
        return self.error if self.error is not None else ("No error",0,0)

def generate_md(ast : Ast) -> GeneratorResult:
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
                    for flag in arg.branches:
                        if flag.tk == Tk.SHORT_FLAG:
                            arg_line += f"**-{flag.branches[0].value}** "
                        elif flag.tk == Tk.LONG_FLAG:
                            arg_line += f"**--{flag.branches[0].value}** "
                        elif flag.tk == Tk.OPTIONAL_ARG:
                            arg_line += f"*<{flag.branches[0].value}>* "
                        elif flag.tk == Tk.REQUIRED_ARG:
                            arg_line += f"**<{flag.branches[0].value}>** "
                        elif flag.tk == Tk.TEXT_LINE:
                            pass
                        else:
                            return GeneratorResult(("Unexpected token in argument list:" + flag.tk.name ,line,col))


                    arg_brief = ""
                    for text in arg.branches:
                        if text.tk == Tk.TEXT_LINE:
                            arg_brief += "\n        " + text.value.strip()
                    if arg_brief.strip() != "":
                        arg_line += arg_brief
                    outp.append(arg_line)
                    outp.append("")

        # Process arguments
        #elif br.tk == Tk.ARG:
    return GeneratorResult("\n".join(outp))