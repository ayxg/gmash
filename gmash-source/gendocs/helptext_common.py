""" `HelpText` Common
    - Global verbose/debug config,
    - Colorful print functions shared across all `helptext` submodules.
"""

_TITLE = "helptext"
_VERSION = "v0.0.0"
_LICENSE = "AGPL-3.0-or-later Copyright(c) 2025 Anton Yashchenko"
HELP_TEXT = """Usage: py helptext.py <helpTextToParse> [-o <outputFile>]
Usage: <pipedInput> | py helptext.py [-o <outputFile>]

Generate formatted markdown documentation from command line help text.
See "Command Line Help Notation" grammar for details on accepted help text formats.

Parameters:
    <helpTextToParse>           Help text to parse. If not provided, will check stdin for piped input.
    -o, --output <outputFile>   Target codegen output file. If not provided, output is piped to stdout.
Options:
    -h, --help                  Display this help message.
    -v, --version               Display version string.
    -V, --verbose               Enable verbose output.
    -r, --raw                   Print parsed nodes as a raw Python class (`__repr__`).
    -a, --ascii                 Print parsed nodes as a simple ASCII tree.
    -f, --fancy                 Print parsed nodes as a decorated ASCII tree.

Developer Arguments:
    -t, --test [[testNameOrPattern]...]
        Run all unit tests.
        If any test names/pattern are provided, run only matching tests.
    -d, --debug
        Enable developer debug output. Implicitly enables verbose output.
"""

_verbose_mode : bool = False   # [INTERNAL][GLOBAL] verbose flag for `helptext` module.
_debug_mode : bool = False     # [INTERNAL][GLOBAL] debug flag for `helptext` module.

def verbose_print(msg: str) -> None:
    """ Print message if `_verbose_mode` is on.
        The `CommandLineInterface` class will set global `_verbose_mode` after parsing.
        TODO: Refactoring to avoid global state ??? possible ???
    """
    if _verbose_mode:
        print(msg)

def print_action(msg: str,indent_level = 0,indent_type = False) -> None:
    """ Print an action message in green color.
        - indent_level : number of indents to add before the message.
        - indent_type  : set indentation string, False = '└────', True = '    '
    """
    indent_txt = "    " if indent_type else "└────"
    print("    " * indent_level + indent_txt * (indent_level != 0) + "\033[92m" + msg +"\033[0m")

def print_error(msg: str,indent_level = 0,indent_type = False) -> None:
    """ Print an error message in red color.
        - indent_level : number of indents to add before the message.
        - indent_type  : set indentation string, False = '└────', True = '    '
    """
    indent_txt = "    " if indent_type else "└────"
    print("    " * indent_level + indent_txt * (indent_level != 1) + "\033[91m" + msg +"\033[0m")

def debug_print(msg: str) -> None:
    """ Print message if debug_mode is true. This function may be "unused" in production.
        For temporary dev debug messages only.
    """
    if _debug_mode:
        print(msg)

def get_help_str() -> str:
    """ Get this scripts(`helptext.py`) help text as a string. """
    return _TITLE + " " + _VERSION + "\n" + _LICENSE + "\n" + HELP_TEXT

def get_version_str() -> str:
    """ Get this scripts(`helptext.py`) version as a string. """
    return _VERSION

def get_license_str() -> str:
    """ Get this scripts(`helptext.py`) license as a string. """
    return _LICENSE

def print_help_text() -> None:
    """ Print help text and exit. """
    print(get_help_str())