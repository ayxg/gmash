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


    return GeneratorResult("\n".join(outp))