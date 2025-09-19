import sys
from helptext_common import  print_error, print_action
from helptext_ast import Tk, Ast, print_ascii_tree, print_ascii_tree_simple
from helptext_parser import Parser
from helptext_tests import run_unit_tests, CMNH_TEST_MAP
import helptext_md

_TITLE = "helptext"
_VERSION = "v0.0.0"
_LICENSE = "AGPL-3.0-or-later Copyright(c) 2025 Anton Yashchenko"
_HELP_TEXT = _TITLE + " " + _VERSION + "\n" + _LICENSE + "\n" \
    + """Usage:
    py helptext.py <helpTextToParse> [-o <outputFile>]

    <pipedInput> | py helptext.py [-o <outputFile>]

Generate formatted markdown documentation from command line help text.
See "Command Line Help Notation" grammar for details on accepted help text formats.

Parameters:
    <helpTextToParse>           Help text to parse. If not provided, will check stdin for piped input.
    -o, --output <outputFile>   Target codegen output file. If not provided, output is piped to stdout.

Options:
    -h, --help                  Display this help message.
    -v, --version               Display version string.
    -r, --raw                   Print parsed nodes as a raw Python class (`__repr__`).
    -a, --ascii                 Print parsed nodes as a simple ASCII tree.
    -f, --fancy                 Print parsed nodes as a decorated ASCII tree.

Developer Arguments:
    -t, --test [[testNameOrPattern]...]
        Run all unit tests.
        If any test names/pattern are provided, run only matching tests.
"""

# _verbose_mode : bool = False   # [INTERNAL][GLOBAL] verbose flag for `helptext` module.
# _debug_mode : bool = False     # [INTERNAL][GLOBAL] debug flag for `helptext` module.

# def _verbose_print(msg: str) -> None:
#     """ Print message if `_verbose_mode` is on.
#         The `HelpText` class will set global `_verbose_mode` after parsing.
#         TODO: Refactoring to avoid global state ??? possible ???
#     """
#     if _verbose_mode:
#         print(msg)

# def _debug_print(msg: str) -> None:
#     """ Print message if debug_mode is true. This function may be "unused" in production.
#         For temporary dev debug messages only.
#     """
#     if _debug_mode:
#         print(msg)

class HelpText():
    def run(self) -> None:
        """ Parses current command line args from `sys.argv`, and handles them.

            This SHOULD ONLY be called from the `__main__` function.
        """
        _print_ast_raw = False
        _print_ast_tree = False
        _print_ast_fancy = False

        # No args,no piped input, show help and exit.
        if len(sys.argv) < 2:
            if sys.stdin.isatty():
                print(_HELP_TEXT)
                sys.exit(0)

        # Display help and exit
        if any(arg == '-h' or arg == '--help' for arg in sys.argv):
            print_help_text()
            sys.exit(0)

        # Display version and exit
        if any(arg == '-v' or arg == '--version' for arg in sys.argv):
            print(get_version_str())
            sys.exit(0)

        # Run unit tests and exit
        if any(arg == '-t' or arg == '--test' for arg in sys.argv):
            # Get all args not starting with '-' after the '-t'. If any match, run
            # only those tests.
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

        # Enbale printing Ast repr
        if any(arg == '-r' or arg == '--raw' for arg in sys.argv):
            _print_ast_raw = True
        if any(arg == '-a' or arg == '--ascii' for arg in sys.argv):
            _print_ast_tree = True
        if any(arg == '-f' or arg == '--fancy' for arg in sys.argv):
            _print_ast_fancy = True

        # Enable debug mode
        # !! Warning : `_verbose_mode` and `_debug_mode` are globals from `helptext_common`
        _verbose_mode = any(arg == '-V' or arg == '--verbose' for arg in sys.argv)
        _debug_mode = any(arg == '-d' or arg == '--debug' for arg in sys.argv)
        if _debug_mode :
            _verbose_mode = True

        # Pop the script name & remove flags
        sys.argv.pop(0)
        sys.argv = [arg for arg in sys.argv if not arg.startswith('-')]

        # If no args left, check stdin for piped input
        if len(sys.argv) < 1:
            if not sys.stdin.isatty():
                help_text = sys.stdin.read()
                if help_text.strip() == "":
                    print(_HELP_TEXT)
                sys.argv.append(help_text)
        else:
            help_text = sys.argv[0]
        if help_text.strip() == "":
            sys.exit(0)

        # Parse
        parser = Parser()
        parse_res = parser.parse(help_text)
        if parse_res.is_error():
            print_error(parse_res.get_error(),1)
            sys.exit(1)
        # Print ast if requested.
        if _print_ast_raw:
            print_action("Displaying raw AST.")
            print(parse_res.get_ast())
        if _print_ast_tree:
            print_action("Displaying ascii AST.")
            print_ascii_tree_simple(parse_res.get_ast())
        if _print_ast_fancy:
            print_action("Displaying fancy AST.")
            print_ascii_tree(parse_res.get_ast())

        gen_res = helptext_md.generate_md(parse_res.get_ast())
        if gen_res.is_error():
            print_error(gen_res.get_error(),1)
            sys.exit(1)
        else:
            print(gen_res.get_md())

    def parse(self, text: str):
        """Parse a help text into an intermediate abstract syntax tree.

        Args:
            text (str): Help text to parse.

        Returns:
            node(Ast): Produced ast. On error, returns a `Tk.POSION` `Ast` w/error as value.
        """
        parse_res = Parser().parse(text)
        if parse_res.is_error():
            return Ast(Tk.POSION, parse_res.error)
        return parse_res.get_ast()

    def gen(self, ast):
        """ Generate `Markdown` documentation from the provided `Ast`.
        On error, returns an empty string.
        Error messages are piped to stderr by default.


        Args:
            ast (Ast): Input ast. Should be produced by `HelpText.parse()`.

        Returns:
            md_docs(str): Generated markdown docs as a `str`. On error, returns an empty string.
                        Error messages are piped to stderr.
        """
        gen_res = MdGenerator().generate(ast)
        if gen_res.is_error():
            return ""
        return gen_res.get()

if __name__ == "__main__":
    HelpText().run()
