"""
#@doc-------------------------------------------------------------------------#
SPDX-License-Identifier: AGPL-3.0-or-later
Copyright(c) 2025 Anton Yashchenko
#-----------------------------------------------------------------------------#
@project: [gmash] Git Smash
@author(s): Anton Yashchenko
@website: https://www.acpp.dev
#-----------------------------------------------------------------------------#
@file `helptext.py`
@created: 2025/09/13
@brief Command line help text to markdown documentation converter.
       See "Command Line Help Notation" grammar for details on accepted help\
       text formats.
#-----------------------------------------------------------------------------#
"""

import sys
from helptext_common import  print_error, print_action
from helptext_ast import Tk, Ast, print_ascii_tree, print_ascii_tree_simple
from helptext_parser import parse
from helptext_tests import run_unit_tests, CMNH_TEST_MAP
from helptext_md import generate_md

_TITLE = "\033[1mhelptext\033[0m"
_VERSION = "v0.0.0"
_LICENSE = "AGPL-3.0-or-later\nCopyright(c) 2025 Anton Yashchenko"
_HELP_TEXT = _TITLE + "\n" + _VERSION + "\n" + _LICENSE + "\n\n" \
    + """Usage:
    py helptext.py <helpTextToParse> [-o <outputFile>]

    <pipedInput> | py helptext.py [-o <outputFile>]

Generate formatted markdown documentation from command line help text.
Pass help text to parse. If not provided, will check stdin for piped input.
See "Command Line Help Notation" grammar for details on accepted help text formats.

Parameters:
    -o, --output <outputFile>   Target markdown output file. If not provided, output is piped to stdout.

Options:
    -s, --skip <lineCount>
        Skip the first <lineCount> lines of the provided help text.
        Useful for skipping license headers or other non-help text.
    -r, --raw                   Print parsed nodes as a raw Python class (`__repr__`).
    -a, --ascii                 Print parsed nodes as a simple ASCII tree.
    -f, --fancy                 Print parsed nodes as a decorated ASCII tree.

Display:
    -h, --help                  Display this help message.
    -v, --version               Display version string.

Developer Arguments:
    -t, --test [testNamesOrPatterns]
        Run all unit tests.
        If any test names/pattern are provided, run only matching tests.
"""

class HelpText():
    """ Command line help text to markdown documentation converter.
    """
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
            print(_HELP_TEXT)
            sys.exit(0)

        # Display version and exit
        if any(arg == '-v' or arg == '--version' for arg in sys.argv):
            print(_VERSION)
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

        # Skip first N lines of help text
        lines_to_skip = 0
        is_skipping = False
        skip_index = -1
        if '--skip' in sys.argv:
            skip_index = sys.argv.index('--skip')
            is_skipping = True
        else:
            skip_index = sys.argv.index('-s')
            is_skipping = True
        if is_skipping:
            if skip_index + 1 < len(sys.argv):
                try:
                    skip_count = int(sys.argv[skip_index + 1])
                    if skip_count < 0:
                        raise ValueError()
                except ValueError:
                    print_error("Invalid skip line count provided.",1)
                    sys.exit(1)
                # Remove the -s and the count from args
                sys.argv.pop(skip_index)  # -s | --skip
                sys.argv.pop(skip_index)  # count
                lines_to_skip = skip_count
            else:
                print_error("No skip line count provided.",1)
                sys.exit(1)

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

        # Skip first N lines if requested
        if lines_to_skip > 0:
            help_text_lines = help_text.splitlines()
            if lines_to_skip >= len(help_text_lines):
                print_error("Skip line count exceeds total help text line count.",1)
                sys.exit(1)
            help_text = "\n".join(help_text_lines[lines_to_skip:])

        # Parse
        parse_res = parse(help_text)
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

        gen_res = generate_md(parse_res.get_ast())
        if gen_res.is_error():
            print_error(gen_res.get_error(),1)
            sys.exit(1)
        else:
            print(gen_res.get_md())

    def parse(self, text: str) -> Ast:
        """Parse a help text into an intermediate abstract syntax tree.

        Args:
            text (str): Help text to parse.

        Returns:
            node(Ast): Produced ast. On error, returns a `Tk.POSION` `Ast` w/error as value.
        """
        parse_res = parse(text)
        if parse_res.is_error():
            return Ast(Tk.POSION, parse_res.error)
        return parse_res.get_ast()

    def gen(self, ast) -> tuple[bool,str]:
        """ Generate `Markdown` documentation from the provided `Ast`.
        On error, returns an empty string.
        Error messages are piped to stderr by default.


        Args:
            ast (Ast): Input ast. Should be produced by `HelpText.parse()`.

        Returns:
            tuple[bool,str]: Generated markdown docs or error message.
                - bool : True if generation was successful, False on error.
                - str  : Generated markdown docs if successful, error message otherwise.
        """
        gen_res = generate_md(ast)
        if gen_res.is_error():
            return (False,gen_res.get_error())
        return (True,gen_res.get_md())

if __name__ == "__main__":
    HelpText().run()
