""" `HelpText` Common Utils & Constants
    - Colorful print functions shared across all `helptext` modules.
"""
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
