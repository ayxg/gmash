"""
#@doc-------------------------------------------------------------------------#
SPDX-License-Identifier: AGPL-3.0-or-later
Copyright(c) 2025 Anton Yashchenko
#-----------------------------------------------------------------------------#
@project: [gmash] Git Smash
@author(s): Anton Yashchenko
@website: https://www.acpp.dev
#-----------------------------------------------------------------------------#
@file `helptext_tests.py`
@created: 2025/09/13
@brief Unit tests for `helptext` module.
#-----------------------------------------------------------------------------#
"""

from helptext_common import print_error,print_action
from helptext_ast import Ast,Tk
from helptext_parser import parse
from helptext_parser import                                     \
    parse_long_flag,parse_short_flag,parse_argument,            \
    parse_optional_arg,parse_required_arg,parse_argument_list,  \
    parse_section,parse_usage_section,parse_help_text
from helptext_md import generate_md
###############################################################################
# Unit Test Utils
###############################################################################

def _print_ast_diff(input_ast : Ast, expected_ast : Ast, indent: int = 0, path: tuple = ()) -> None:
    """Compare and print two ASTs with differences highlighted"""
    indent_str = "    " * indent
    connector = "└── " if indent > 0 else ""

    # Find corresponding node in expected AST
    expected_node = expected_ast
    for idx in path:
        if idx < len(expected_node.branches):
            expected_node = expected_node.branches[idx]
        else:
            expected_node = None
            break

    # Determine if nodes are different
    is_different = (
        expected_node is None or
        input_ast.tk.name != expected_node.tk.name or
        input_ast.value != expected_node.value
    )

    # Node content with color coding
    content = input_ast.tk.name + ': ' + input_ast.value if input_ast.value is not None else input_ast.tk.name

    if is_different:
        print(f"{indent_str}{connector}\033[91m{content}\033[0m")  # Red for differences
    else:
        print(f"{indent_str}{connector}{content}")  # Default color for matches

    # Print position info (optional)
    if input_ast.line > 0:
        pos_info = f"[L{input_ast.line}:{input_ast.col}-L{input_ast.end_line}:{input_ast.end_col}]"
        if is_different:
            print(f"{indent_str}    \033[91m{pos_info}\033[0m")
        else:
            print(f"{indent_str}    {pos_info}")

    # Recursively print children
    for i, child in enumerate(input_ast.branches):
        _print_ast_diff(child, expected_ast, indent + 1, path + (i,))

def _print_expected_ast_diff(expected_ast : Ast, input_ast : Ast, indent: int = 0, path: tuple = ()) -> None:
    """Print expected AST highlighting differences from input"""
    indent_str = "    " * indent
    connector = "└── " if indent > 0 else ""

    # Find corresponding node in input AST
    input_node = input_ast
    for idx in path:
        if idx < len(input_node.branches):
            input_node = input_node.branches[idx]
        else:
            input_node = None
            break

    # Determine if nodes are different
    is_different = (
        input_node is None or
        expected_ast.tk.name != input_node.tk.name or
        expected_ast.value != input_node.value
    )

    # Node content with color coding
    content = expected_ast.tk.name + ': ' + expected_ast.value if expected_ast.value is not None else expected_ast.tk.name

    if is_different:
        print(f"{indent_str}{connector}\033[92m{content}\033[0m")  # Green for differences
    else:
        print(f"{indent_str}{connector}{content}")  # Default color for matches

    # Print position info (optional)
    if expected_ast.line > 0:
        pos_info = f"[L{expected_ast.line}:{expected_ast.col}-L{expected_ast.end_line}:{expected_ast.end_col}]"
        if is_different:
            print(f"{indent_str}    \033[92m{pos_info}\033[0m")
        else:
            print(f"{indent_str}    {pos_info}")

    # Recursively print children
    for i, child in enumerate(expected_ast.branches):
        _print_expected_ast_diff(child, input_ast, indent + 1, path + (i,))

def _compare_asts(input_ast : Ast, expected_ast: Ast):
    """Main function to compare two ASTs"""
    print("Input AST (differences in red):")
    _print_ast_diff(input_ast, expected_ast)

    print("\nExpected AST (differences in green):")
    _print_expected_ast_diff(expected_ast, input_ast)

def _test_parser(test_name : str, parser_input : str, expected_output: Ast):
    """ Run a parser test and compare the output AST to the expected AST."""
    ast = parse(parser_input)
    if ast.is_error():
        print_error(f"[FAIL] {test_name}:\n\t{ast.get_error()}",1)
    else:
        did_test_pass = ast.get_ast() == expected_output
        if not did_test_pass:
            print_error(f"[FAIL] {test_name}. Expected ast does not match.",1)
            _compare_asts(ast.get_ast(), expected_output)
        else:
            print_action(f"[PASS] {test_name}.",1)

def _test_parser_function(funct,test_name : str ,parser_input : str,expected_output : Ast):
    """ Run a specific parser function test and compare the output AST to the expected AST."""
    result = funct(parser_input.splitlines(),0,0)
    if result.is_error():
        print_error(f"[FAIL] {test_name}:\n\t{result.error}",1)
        return
    ast = result.get_ast()
    did_test_pass = ast == expected_output
    if not did_test_pass:
        print_error(f"[FAIL] {test_name} failed. Expected ast does not match.",1)
        _compare_asts(ast, expected_output)
    else:
        print_action(f"[PASS] {test_name}.",1)

def _test_generator(test_name : str, input_string : str, expected_md : str):
    """ Run a generator test and compare the output markdown to the expected markdown."""
    prs = parse(input_string)
    if prs.is_error():
        print_error(f"[FAIL] {test_name}:\n\t{prs.get_error()}",1)
        return
    gen_res = generate_md(prs.get_ast())
    if gen_res.is_error():
        print_error(f"[FAIL] {test_name}:\n\t{gen_res.get_error()}",1)
    else:
        md = gen_res.get_md()
        did_test_pass = md.strip() == expected_md.strip()
        if not did_test_pass:
            print_error(f"[FAIL] {test_name}. Expected markdown does not match.",1)
            # Print the differences
            print("Generated MD:")
            print(md)
            print("Expected MD:")
            print(expected_md)

            for i, (gen_line, exp_line) in enumerate(zip(md.splitlines(), expected_md.splitlines()), start=1):
                if gen_line != exp_line:
                    print_error(f"Line {i} differs:")
                    print(f"  Generated: '{gen_line}'")
                    print(f"  Expected : '{exp_line}'")
        else:
            print_action(f"[PASS] {test_name}.",1)

###############################################################################
# Bottom-Up Unit Tests
###############################################################################

def ut_parsefunc_long_flag():
    """ Test `parse_long_flag` function. """
    _test_parser_function(parse_long_flag,
        "ut_parsefunc_long_flag", "--long-flag-ident123",
        Ast(Tk.LONG_FLAG,None,branches = [Ast(Tk.LONG_FLAG_IDENT,'long-flag-ident123')])
    )

def ut_parsefunc_short_flag():
    """ Test `parse_short_flag` function. """
    _test_parser_function(parse_short_flag,
        "ut_parsefunc_short_flag",
        "-f\n",
        Ast(Tk.SHORT_FLAG,None,branches = [Ast(Tk.SHORT_FLAG_IDENT,'f')])
    )

def ut_parsefunc_long_and_short_flag():
    """ Test `parse_argument` with a long and short flag. """
    _test_parser_function(parse_argument,
        "ut_parsefunc_long_and_short_flag",
        "-f --long-flag-ident123 This is the argument documentation.\n",
        Ast(Tk.ARGUMENT,None,branches = [
            Ast(Tk.SHORT_FLAG,None,branches = [Ast(Tk.SHORT_FLAG_IDENT,'f')]),
            Ast(Tk.LONG_FLAG,None,branches = [Ast(Tk.LONG_FLAG_IDENT,'long-flag-ident123')]),
            Ast(Tk.TEXT_LINE,"This is the argument documentation.")
        ])
    )

def ut_parsefunc_optional_arg():
    """ Test `parse_optional_arg` function. """
    _test_parser_function(parse_optional_arg,
        "ut_parsefunc_optional_arg",
        "[optional_arg123]",
        Ast(Tk.OPTIONAL_ARG,None,branches = [Ast(Tk.SHELL_IDENT,'optional_arg123')])
    )

def ut_parsefunc_required_arg():
    """ Test `parse_required_arg` function. """
    _test_parser_function(parse_required_arg,
        "ut_parsefunc_required_arg",
        "<required_arg123>",
        Ast(Tk.REQUIRED_ARG,None,branches = [Ast(Tk.SHELL_IDENT,'required_arg123')])
    )

def ut_parsefunc_argument_shortflag_only():
    """ Test `parse_argument` with a short flag only. """
    _test_parser_function(parse_argument,
        "ut_parsefunc_argument_shortflag_only",
        "-f\n",
        Ast(Tk.ARGUMENT,None,branches = [
            Ast(Tk.SHORT_FLAG,None,branches = [Ast(Tk.SHORT_FLAG_IDENT,'f')])
        ])
    )

def ut_parsefunc_argument_longflag_only():
    """ Test `parse_argument` with a long flag only. """
    _test_parser_function(parse_argument,
        "ut_parsefunc_argument_longflag_only",
        "--long-flag-ident123\n",
        Ast(Tk.ARGUMENT,None,branches = [
            Ast(Tk.LONG_FLAG,None,branches = [Ast(Tk.LONG_FLAG_IDENT,'long-flag-ident123')])
        ])
    )

def ut_parsefunc_argument_long_and_short_flag():
    """ Test `parse_argument` with both long and short flags. No documentation. """
    _test_parser_function(parse_argument,
        "ut_parsefunc_argument_long_and_short_flag",
        "-f --long-flag-ident123",
        Ast(Tk.ARGUMENT,None,branches = [
            Ast(Tk.SHORT_FLAG,None,branches = [Ast(Tk.SHORT_FLAG_IDENT,'f')]),
            Ast(Tk.LONG_FLAG,None,branches = [Ast(Tk.LONG_FLAG_IDENT,'long-flag-ident123')])
        ])
    )

def ut_parsefunc_argument_required_arg():
    """ Test `parse_argument` with a required arg. """
    _test_parser_function(parse_argument,
        "ut_parsefunc_argument_required_arg",
        "--long-flag-ident123 <required_arg123>",
        Ast(Tk.ARGUMENT,None,branches = [
            Ast(Tk.LONG_FLAG,None,branches = [Ast(Tk.LONG_FLAG_IDENT,'long-flag-ident123')]),
            Ast(Tk.REQUIRED_ARG,None,branches = [Ast(Tk.SHELL_IDENT,'required_arg123')])
        ])
    )

def ut_parsefunc_argument_optional_arg():
    """ Test `parse_argument` with an optional arg. """
    _test_parser_function(parse_argument,
        "ut_parsefunc_argument_optional_arg",
        "--long-flag-ident123 [optional_arg123]",
        Ast(Tk.ARGUMENT,None,branches = [
            Ast(Tk.LONG_FLAG,None,branches = [Ast(Tk.LONG_FLAG_IDENT,'long-flag-ident123')]),
            Ast(Tk.OPTIONAL_ARG,None,branches = [Ast(Tk.SHELL_IDENT,'optional_arg123')])
        ])
    )

def ut_parsefunc_argument_desc_same_line():
    """ Test `parse_argument` with description on the same line. """
    _test_parser_function(parse_argument,
        "ut_parsefunc_argument_desc_same_line",
        "--long-flag-ident123 This is the argument documentation.\n",
        Ast(Tk.ARGUMENT,None,branches = [
            Ast(Tk.LONG_FLAG,None,branches = [Ast(Tk.LONG_FLAG_IDENT,'long-flag-ident123')]),
            Ast(Tk.TEXT_LINE,"This is the argument documentation.")
        ])
    )

def ut_parsefunc_argument_indented_brief_following_arg():
    """ Test `parse_argument` with indented description following the arg. """
    _test_parser_function(parse_argument,
        "ut_parsefunc_argument_indented_brief_following_arg",
        "--long-flag-ident123\n        This is the argument documentation.\n",
        Ast(Tk.ARGUMENT,None,branches = [
            Ast(Tk.LONG_FLAG,None,branches = [Ast(Tk.LONG_FLAG_IDENT,'long-flag-ident123')]),
            Ast(Tk.TEXT_LINE,"This is the argument documentation.")
        ])
    )

def ut_parsefunc_argument_full():
    """ Test `parse_argument` with full features. """
    _test_parser_function(parse_argument,
        "ut_parsefunc_argument_full",
        "-f --long-flag-ident123 --second-flag-opt [optional_arg] This is the argument documentation.\n",
        Ast(Tk.ARGUMENT,None,branches = [
            Ast(Tk.SHORT_FLAG,None,branches = [Ast(Tk.SHORT_FLAG_IDENT,'f')]),
            Ast(Tk.LONG_FLAG,None,branches = [Ast(Tk.LONG_FLAG_IDENT,'long-flag-ident123')]),
            Ast(Tk.LONG_FLAG,None,branches = [Ast(Tk.LONG_FLAG_IDENT,'second-flag-opt')]),
            Ast(Tk.OPTIONAL_ARG,None,branches = [Ast(Tk.SHELL_IDENT,'optional_arg')]),
            Ast(Tk.TEXT_LINE,"This is the argument documentation.")
        ])
    )

def ut_parsefunc_argument_full_with_commas():
    """ Test `parse_argument` with full features and commas. """
    _test_parser_function(parse_argument,
        "ut_parsefunc_argument_full_with_commas",
        "-f, --long-flag-ident123, --second-flag-opt [optional_arg] This is the argument documentation.\n",
        Ast(Tk.ARGUMENT,None,branches = [
            Ast(Tk.SHORT_FLAG,None,branches = [Ast(Tk.SHORT_FLAG_IDENT,'f')]),
            Ast(Tk.LONG_FLAG,None,branches = [Ast(Tk.LONG_FLAG_IDENT,'long-flag-ident123')]),
            Ast(Tk.LONG_FLAG,None,branches = [Ast(Tk.LONG_FLAG_IDENT,'second-flag-opt')]),
            Ast(Tk.OPTIONAL_ARG,None,branches = [Ast(Tk.SHELL_IDENT,'optional_arg')]),
            Ast(Tk.TEXT_LINE,"This is the argument documentation.")
        ])
    )

def ut_parsefunc_argument_list():
    """ Test `parse_argument_list` function. """
    _test_parser_function(parse_argument_list,
        "ut_parsefunc_argument_list",
        "-f --long-flag-ident123 This is the argument documentation.\n"
                     "-g --another-flag [optional_arg] This is another argument.\n",
        Ast(Tk.ARGUMENT_LIST,None,branches = [
            Ast(Tk.ARGUMENT,None,branches = [
                Ast(Tk.SHORT_FLAG,None,branches = [Ast(Tk.SHORT_FLAG_IDENT,'f')]),
                Ast(Tk.LONG_FLAG,None,branches = [Ast(Tk.LONG_FLAG_IDENT,'long-flag-ident123')]),
                Ast(Tk.TEXT_LINE,"This is the argument documentation.")
            ]),
            Ast(Tk.ARGUMENT,None,branches = [
                Ast(Tk.SHORT_FLAG,None,branches = [Ast(Tk.SHORT_FLAG_IDENT,'g')]),
                Ast(Tk.LONG_FLAG,None,branches = [Ast(Tk.LONG_FLAG_IDENT,'another-flag')]),
                Ast(Tk.OPTIONAL_ARG,None,branches = [Ast(Tk.SHELL_IDENT,'optional_arg')]),
                Ast(Tk.TEXT_LINE,"This is another argument.")
            ])
        ])
    )

def ut_parsefunc_section_paragraph():
    """ Test `parse_section` with a paragraph inside. """
    _test_parser_function(parse_section,
        "ut_parsefunc_section_paragraph",
        "Details\n    This is a paragraph.\n    This is the second line.\n",
        Ast(Tk.SECTION,"Details",branches = [
            Ast(Tk.PARAGRAPH,None,branches = [
                Ast(Tk.TEXT_LINE,"This is a paragraph."),
                Ast(Tk.TEXT_LINE,"This is the second line.")
            ])
        ])
    )

def ut_parsefunc_section_arguments():
    """ Test `parse_section` with arguments inside. """
    _test_parser_function(parse_section,
        "ut_parsefunc_section_arguments",
        "Options\n    -f --long-flag-ident123 This is the argument documentation.\n    -g --another-flag [optional_arg] This is another argument.\n",
        Ast(Tk.SECTION,"Options",branches = [
            Ast(Tk.ARGUMENT_LIST,None,branches = [
                Ast(Tk.ARGUMENT,None,branches = [
                    Ast(Tk.SHORT_FLAG,None,branches = [Ast(Tk.SHORT_FLAG_IDENT,'f')]),
                    Ast(Tk.LONG_FLAG,None,branches = [Ast(Tk.LONG_FLAG_IDENT,'long-flag-ident123')]),
                    Ast(Tk.TEXT_LINE,"This is the argument documentation.")
                ]),
                Ast(Tk.ARGUMENT,None,branches = [
                    Ast(Tk.SHORT_FLAG,None,branches = [Ast(Tk.SHORT_FLAG_IDENT,'g')]),
                    Ast(Tk.LONG_FLAG,None,branches = [Ast(Tk.LONG_FLAG_IDENT,'another-flag')]),
                    Ast(Tk.OPTIONAL_ARG,None,branches = [Ast(Tk.SHELL_IDENT,'optional_arg')]),
                    Ast(Tk.TEXT_LINE,"This is another argument.")
                ])
            ])
        ])
    )

def ut_parsefunc_usage_section():
    """ Test `parse_usage_section` function. """
    _test_parser_function(parse_usage_section,
        "ut_parsefunc_usage_section",
        "Usage: myprogram [options] <input_file>\n",
        Ast(Tk.USAGE,"myprogram [options] <input_file>")
    )

def ut_parsefunc_help_text():
    """ Test `parse_help_text` function. (syntax root) """
    _test_parser_function(parse_help_text,
        "ut_parsefunc_help_text",
        "Usage: myprogram [options] <input_file>\n\nThis is a paragraph.\nThis is the second line.\n\nDetails\n    These are the details.\n\n",
        Ast(Tk.SYNTAX,None,branches = [
            Ast(Tk.USAGE,"myprogram [options] <input_file>"),
            Ast(Tk.PARAGRAPH,None,branches = [
                Ast(Tk.TEXT_LINE,"This is a paragraph."),
                Ast(Tk.TEXT_LINE,"This is the second line.")
            ]),
            Ast(Tk.SECTION,"Details",branches = [ Ast(Tk.PARAGRAPH,None,branches = [
                Ast(Tk.TEXT_LINE,"These are the details.")
            ])
        ])
    ])
    )

###############################################################################
# End-To-End Unit Tests
###############################################################################

def ut_parser_usage_line():
    """ Test parsing a usage line. """
    _test_parser("ut_parser_usage_line",
        "Usage: myprogram [options] <input_file>\n\n",
        Ast(Tk.SYNTAX,None,branches = [
            Ast(Tk.USAGE,"myprogram [options] <input_file>")
        ])
    )

def ut_parser_paragraph():
    """ Test parsing a paragraph. """
    _test_parser("ut_parser_paragraph",
        "This is a paragraph.\nThis is the second line.\n\n",
        Ast(Tk.SYNTAX,None,branches = [
            Ast(Tk.PARAGRAPH,None,branches = [
                Ast(Tk.TEXT_LINE,"This is a paragraph."),
                Ast(Tk.TEXT_LINE,"This is the second line.")
            ])
        ])
    )

def ut_parser_usage_and_paragraph():
    """Test parsing a usage line and paragraph."""
    _test_parser("ut_parser_usage_and_paragraph",
        "Usage: myprogram [options] <input_file>\n\nThis is a paragraph.\nThis is the second line.\n\n",
        Ast(Tk.SYNTAX,None,branches = [
            Ast(Tk.USAGE,"myprogram [options] <input_file>"),
            Ast(Tk.PARAGRAPH,None,branches = [
                Ast(Tk.TEXT_LINE,"This is a paragraph."),
                Ast(Tk.TEXT_LINE,"This is the second line.")
            ])
        ])
    )

def ut_parser_usage_paragraph_section():
    """Test parsing a usage line, paragraph and section."""
    _test_parser("ut_parser_usage_paragraph_section",
        "Usage: myprogram [options] <input_file>\n\nThis is a paragraph.\nThis is the second line.\n\nDetails\n    These are the details.\n\n",
        Ast(Tk.SYNTAX,None,branches = [
            Ast(Tk.USAGE,"myprogram [options] <input_file>"),
            Ast(Tk.PARAGRAPH,None,branches = [
                Ast(Tk.TEXT_LINE,"This is a paragraph."),
                Ast(Tk.TEXT_LINE,"This is the second line.")
            ]),
            Ast(Tk.SECTION,"Details",branches = [
                Ast(Tk.PARAGRAPH,None,branches = [
                    Ast(Tk.TEXT_LINE,"These are the details.")
                ])
            ])
        ])
    )

def ut_parser_arg_long_flag():
    """Test parsing a long cli argument flag."""
    _test_parser("ut_parser_arg_long_flag",
        "Options\n    --long-flag-ident123 This is the argument documentation.\n\n",
        Ast(Tk.SYNTAX,None,branches = [
            Ast(Tk.SECTION,"Options",branches = [
                Ast(Tk.ARGUMENT_LIST,None,branches = [
                    Ast(Tk.ARGUMENT,None,branches = [
                        Ast(Tk.LONG_FLAG,None,branches = [Ast(Tk.LONG_FLAG_IDENT,'long-flag-ident123')]),
                        Ast(Tk.TEXT_LINE,"This is the argument documentation.")
                    ])
                ])
            ])
        ])
    )

def ut_parser_arg_short_flag():
    """Test parsing a short cli argument flag."""
    _test_parser("ut_parser_arg_short_flag",
        "Options\n    -f This is the argument documentation.\n\n",
        Ast(Tk.SYNTAX,None,branches = [
            Ast(Tk.SECTION,"Options",branches = [
                Ast(Tk.ARGUMENT_LIST,None,branches = [
                    Ast(Tk.ARGUMENT,None,branches = [
                        Ast(Tk.SHORT_FLAG,None,branches = [Ast(Tk.SHORT_FLAG_IDENT,'f')]),
                        Ast(Tk.TEXT_LINE,"This is the argument documentation.")
                    ])
                ])
            ])
        ])
    )

def ut_parser_arg_short_and_long_flag():
    """Test parsing a short and long cli argument flags."""
    _test_parser("ut_parser_arg_short_and_long_flag",
        "Options\n    -f --long-flag-ident123 This is the argument documentation.\n\n",
        Ast(Tk.SYNTAX,None,branches = [
            Ast(Tk.SECTION,"Options",branches = [
                Ast(Tk.ARGUMENT_LIST,None,branches = [
                    Ast(Tk.ARGUMENT,None,branches = [
                        Ast(Tk.SHORT_FLAG,None,branches = [Ast(Tk.SHORT_FLAG_IDENT,'f')]),
                        Ast(Tk.LONG_FLAG,None,branches = [Ast(Tk.LONG_FLAG_IDENT,'long-flag-ident123')]),
                        Ast(Tk.TEXT_LINE,"This is the argument documentation.")
                    ])
                ])
            ])
        ])
    )

def ut_parser_arg_optional_arg():
    """Test parsing an optional cli argument."""
    _test_parser("ut_parser_arg_optional_arg",
        "Options\n    --long-flag-ident123 [optional_arg123] This is the argument documentation.\n\n",
        Ast(Tk.SYNTAX,None,branches = [
            Ast(Tk.SECTION,"Options",branches = [
                Ast(Tk.ARGUMENT_LIST,None,branches = [
                    Ast(Tk.ARGUMENT,None,branches = [
                        Ast(Tk.LONG_FLAG,None,branches = [Ast(Tk.LONG_FLAG_IDENT,'long-flag-ident123')]),
                        Ast(Tk.OPTIONAL_ARG,None,branches = [Ast(Tk.SHELL_IDENT,'optional_arg123')]),
                        Ast(Tk.TEXT_LINE,"This is the argument documentation.")
                    ])
                ])
            ])
        ])
    )

def ut_parser_arg_required_arg():
    """Test parsing a required cli argument."""
    _test_parser("ut_parser_arg_required_arg",
        "Options\n    --long-flag-ident123 <required_arg123> This is the argument documentation.\n\n",
        Ast(Tk.SYNTAX,None,branches = [
            Ast(Tk.SECTION,"Options",branches = [
                Ast(Tk.ARGUMENT_LIST,None,branches = [
                    Ast(Tk.ARGUMENT,None,branches = [
                        Ast(Tk.LONG_FLAG,None,branches = [Ast(Tk.LONG_FLAG_IDENT,'long-flag-ident123')]),
                        Ast(Tk.REQUIRED_ARG,None,branches = [Ast(Tk.SHELL_IDENT,'required_arg123')]),
                        Ast(Tk.TEXT_LINE,"This is the argument documentation.")
                    ])
                ])
            ])
        ])
    )

def ut_parser_arg_indented_brief_following_arg():
    """Test parsing an argument with indented brief following."""
    _test_parser("ut_parser_arg_indented_brief_following_arg",
        "Options\n    --long-flag-ident123 <required_arg123>\n        This is the argument documentation.\n\n",
        Ast(Tk.SYNTAX,None,branches = [
            Ast(Tk.SECTION,"Options",branches = [
                Ast(Tk.ARGUMENT_LIST,None,branches = [
                    Ast(Tk.ARGUMENT,None,branches = [
                        Ast(Tk.LONG_FLAG,None,branches = [Ast(Tk.LONG_FLAG_IDENT,'long-flag-ident123')]),
                        Ast(Tk.REQUIRED_ARG,None,branches = [Ast(Tk.SHELL_IDENT,'required_arg123')]),
                        Ast(Tk.TEXT_LINE,"This is the argument documentation.")
                    ])
                ])
            ])
        ])
    )

def ut_parser_arg_indented_multiline_brief_following_arg():
    """Test parsing an argument with a multiline indented brief following."""
    _test_parser("ut_parser_arg_indented_multiline_brief_following_arg",
        "Options\n    --long-flag-ident123 <required_arg123>\n        This is the argument documentation.\n        This is the second line.\n\n",
        Ast(Tk.SYNTAX,None,branches = [
            Ast(Tk.SECTION,"Options",branches = [
                Ast(Tk.ARGUMENT_LIST,None,branches = [
                    Ast(Tk.ARGUMENT,None,branches = [
                        Ast(Tk.LONG_FLAG,None,branches = [Ast(Tk.LONG_FLAG_IDENT,'long-flag-ident123')]),
                        Ast(Tk.REQUIRED_ARG,None,branches = [Ast(Tk.SHELL_IDENT,'required_arg123')]),
                        Ast(Tk.TEXT_LINE,"This is the argument documentation.")
                        ,Ast(Tk.TEXT_LINE,"This is the second line.")
                    ])
                ])
            ])
        ])
    )

def ut_parser_simple():
    """ Test a simple complete example """
    _test_parser("ut_parser_simple",
        "USAGE:\n"
            +"    py cmhn_compiler.py [ [ -v | --verbose ] | [ -d | --debug ] ] <helpTextInput>"
            +"\n"
            +"BRIEF:\n"
            +"    This is a brief.\n"
            +"\n"
            +"\n"
            +"\n"
            +"This is a paragraph.\n"
            +"This is the second line.\n"
            +"\n"
            +"\n"
            +"PARAMS:\n"
            +"    -f This is an argument.\n"
            +"\n"
            +"\n"
        ,
        Ast(Tk.SYNTAX,None,branches = [
            Ast(Tk.USAGE,"py cmhn_compiler.py [ [ -v | --verbose ] | [ -d | --debug ] ] <helpTextInput>"),
            Ast(Tk.SECTION,"BRIEF:",branches = [
                Ast(Tk.PARAGRAPH,None,branches = [Ast(Tk.TEXT_LINE,"This is a brief.")
                ])
            ]),
            Ast(Tk.PARAGRAPH,None,branches = [
                Ast(Tk.TEXT_LINE,"This is a paragraph."),
                Ast(Tk.TEXT_LINE,"This is the second line.")
            ]),
            Ast(Tk.SECTION,"PARAMS:",branches = [
                Ast(Tk.ARGUMENT_LIST,None,branches = [
                    Ast(Tk.ARGUMENT,None,branches = [
                        Ast(Tk.SHORT_FLAG,None,branches = [Ast(Tk.SHORT_FLAG_IDENT,'f')]),
                        Ast(Tk.TEXT_LINE,"This is an argument.")
                    ])
                ])
            ])
        ])
    )

def ut_parser_full():
    """Test a full featured example."""
    _test_parser("ut_parser_full",""
        "Usage: gmash dirs prefix --p <prefix> --P [fileOrFolder]\n\n"
        "Add a prefix to each top-level file in a directory.\n\n"
        "Parameters\n"
        "    -f --force \n"
        "        Force changes and overwrite.\n"
        "    -h --husky \n"
        "        Use secret husky superpowers.\n\n"
        "Display\n"
        "    -h --help\n"
        "        Display help.\n"
        "    -v --version\n"
        "        Display version\n\n"
        "Details\n"
        "    A paragraph of text, these are the details of a command.\n\n\n\n",
        Ast(Tk.SYNTAX,None,branches = [
            Ast(Tk.USAGE,"gmash dirs prefix --p <prefix> --P [fileOrFolder]"),
            Ast(Tk.PARAGRAPH,None,branches = [
                Ast(Tk.TEXT_LINE,"Add a prefix to each top-level file in a directory.")
            ]),
            Ast(Tk.SECTION,"Parameters",branches = [
                Ast(Tk.ARGUMENT_LIST,None,branches = [
                    Ast(Tk.ARGUMENT,None,branches = [
                        Ast(Tk.SHORT_FLAG,None,branches = [Ast(Tk.SHORT_FLAG_IDENT,'f')]),
                        Ast(Tk.LONG_FLAG,None,branches = [Ast(Tk.LONG_FLAG_IDENT,'force')]),
                        Ast(Tk.TEXT_LINE,"Force changes and overwrite.")
                    ]),
                    Ast(Tk.ARGUMENT,None,branches = [
                        Ast(Tk.SHORT_FLAG,None,branches = [Ast(Tk.SHORT_FLAG_IDENT,'h')]),
                        Ast(Tk.LONG_FLAG,None,branches = [Ast(Tk.LONG_FLAG_IDENT,'husky')]),
                        Ast(Tk.TEXT_LINE,"Use secret husky superpowers.")
                    ])
                ])
            ]),
            Ast(Tk.SECTION,"Display",branches = [
                Ast(Tk.ARGUMENT_LIST,None,branches = [
                    Ast(Tk.ARGUMENT,None,branches = [
                        Ast(Tk.SHORT_FLAG,None,branches = [Ast(Tk.SHORT_FLAG_IDENT,'h')]),
                        Ast(Tk.LONG_FLAG,None,branches = [Ast(Tk.LONG_FLAG_IDENT,'help')]),
                        Ast(Tk.TEXT_LINE,"Display help.")
                    ]),
                    Ast(Tk.ARGUMENT,None,branches = [
                        Ast(Tk.SHORT_FLAG,None,branches = [Ast(Tk.SHORT_FLAG_IDENT,'v')]),
                        Ast(Tk.LONG_FLAG,None,branches = [Ast(Tk.LONG_FLAG_IDENT,'version')]),
                        Ast(Tk.TEXT_LINE,"Display version")
                    ])
                ])
            ]),
            Ast(Tk.SECTION,"Details",branches = [
                Ast(Tk.PARAGRAPH,None,branches = [
                    Ast(Tk.TEXT_LINE,"A paragraph of text, these are the details of a command.")
                ])
            ])
        ])
    )

def ut_parser_usage_with_multiline():
    """Test parsing a usage section with multiple usage lines."""
    _test_parser("ut_parser_usage_with_multiline",
        "Usage:\n    myprogram [options] <input_file>\n    second line of usage text\n\n",
        Ast(Tk.SYNTAX,None,branches = [
            Ast(Tk.USAGE,"myprogram [options] <input_file>\nsecond line of usage text")
        ])
    )

def ut_parser_gmash_dirs_same():
    """Test parsing a real world example from gmash."""
    _test_parser("ut_parser_gmash_dirs_same",
        """Usage: gmash dirs same -p <srcPath> -P <tgtPath>

Get a diff of 2 directories.

Parameters:
  -p,     --path <srcPath>              Source path.
  -P,     --tgt-path <tgtPath>          Target path.

Display:
  -h,     --help                        Display gmash, command or subcommand help. Use -h or --help.
  -v,     --version                     [v0-0-0] Display command group version.

        """,
        Ast(Tk.SYNTAX,None,branches = [
            Ast(Tk.USAGE,"gmash dirs same -p <srcPath> -P <tgtPath>"),
            Ast(Tk.PARAGRAPH,None,branches = [
                Ast(Tk.TEXT_LINE,"Get a diff of 2 directories.")
            ]),
            Ast(Tk.SECTION,"Parameters:",branches = [
                Ast(Tk.ARGUMENT_LIST,None,branches = [
                    Ast(Tk.ARGUMENT,None,branches = [
                        Ast(Tk.SHORT_FLAG,None,branches = [Ast(Tk.SHORT_FLAG_IDENT,'p')]),
                        Ast(Tk.LONG_FLAG,None,branches = [Ast(Tk.LONG_FLAG_IDENT,'path')]),
                        Ast(Tk.REQUIRED_ARG,None,branches = [Ast(Tk.SHELL_IDENT,'srcPath')]),
                        Ast(Tk.TEXT_LINE,"Source path.")
                    ]),
                    Ast(Tk.ARGUMENT,None,branches = [
                        Ast(Tk.SHORT_FLAG,None,branches = [Ast(Tk.SHORT_FLAG_IDENT,'P')]),
                        Ast(Tk.LONG_FLAG,None,branches = [Ast(Tk.LONG_FLAG_IDENT,'tgt-path')]),
                        Ast(Tk.REQUIRED_ARG,None,branches = [Ast(Tk.SHELL_IDENT,'tgtPath')]),
                        Ast(Tk.TEXT_LINE,"Target path.")
                    ])
                ])
            ]),
            Ast(Tk.SECTION,"Display:",branches = [
                Ast(Tk.ARGUMENT_LIST,None,branches = [
                    Ast(Tk.ARGUMENT,None,branches = [
                        Ast(Tk.SHORT_FLAG,None,branches = [Ast(Tk.SHORT_FLAG_IDENT,'h')]),
                        Ast(Tk.LONG_FLAG,None,branches = [Ast(Tk.LONG_FLAG_IDENT,'help')]),
                        Ast(Tk.TEXT_LINE,"Display gmash, command or subcommand help. Use -h or --help.")
                    ]),
                    Ast(Tk.ARGUMENT,None,branches = [
                        Ast(Tk.SHORT_FLAG,None,branches = [Ast(Tk.SHORT_FLAG_IDENT,'v')]),
                        Ast(Tk.LONG_FLAG,None,branches = [Ast(Tk.LONG_FLAG_IDENT,'version')]),
                        Ast(Tk.OPTIONAL_ARG,None,branches = [Ast(Tk.SHELL_IDENT,'v0-0-0')]),
                        Ast(Tk.TEXT_LINE,"Display command group version.")
                    ])
                ])
            ])
        ])
    )

###############################################################################
# Validation Unit Tests
###############################################################################

def ut_generator_basic():
    """ Hello world generator test """
    _test_generator("ut_generator_hello_world",
        input_string="""
Usage: hello-world

Says hello to the world.

Parameters:
    -l --loud         Be very loud and scream instead.

Details:
    The world needs a friend, so im saying hello to it.
        """,
        expected_md=
"""# hello-world

### Usage
`hello-world`

### Brief
Says hello to the world.

### Parameters:
`-l`  `--loud` \\
&nbsp;&nbsp;&nbsp;&nbsp;Be very loud and scream instead.

### Details:
The world needs a friend, so im saying hello to it.

"""
    )

def ut_generator_self():
    """ Test the generator with its own help text. Skip the first 5 lines (license header)."""
    _test_generator("ut_generator_self",
        input_string="""Usage:
    helptext <helpTextToParse> [-o <outputFile>]

    <pipedInput> | helptext [-o <outputFile>]

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
""",
        expected_md="""# helptext

### Usage
`helptext <helpTextToParse> [-o <outputFile>]`

`<pipedInput> | helptext [-o <outputFile>]`

### Brief
Generate formatted markdown documentation from command line help text.
Pass help text to parse. If not provided, will check stdin for piped input.
See "Command Line Help Notation" grammar for details on accepted help text formats.

### Parameters:
`-o`  `--output  <outputFile>` \\
&nbsp;&nbsp;&nbsp;&nbsp;Target markdown output file. If not provided, output is piped to stdout.

### Options:
`-s`  `--skip  <lineCount>` \\
&nbsp;&nbsp;&nbsp;&nbsp;Skip the first <lineCount> lines of the provided help text.\\
&nbsp;&nbsp;&nbsp;&nbsp;Useful for skipping license headers or other non-help text.

`-r`  `--raw` \\
&nbsp;&nbsp;&nbsp;&nbsp;Print parsed nodes as a raw Python class (`__repr__`).

`-a`  `--ascii` \\
&nbsp;&nbsp;&nbsp;&nbsp;Print parsed nodes as a simple ASCII tree.

`-f`  `--fancy` \\
&nbsp;&nbsp;&nbsp;&nbsp;Print parsed nodes as a decorated ASCII tree.

### Display:
`-h`  `--help` \\
&nbsp;&nbsp;&nbsp;&nbsp;Display this help message.

`-v`  `--version` \\
&nbsp;&nbsp;&nbsp;&nbsp;Display version string.

### Developer Arguments:
`-t`  `--test  [testNamesOrPatterns]` \\
&nbsp;&nbsp;&nbsp;&nbsp;Run all unit tests.\\
&nbsp;&nbsp;&nbsp;&nbsp;If any test names/pattern are provided, run only matching tests.

"""
        )

###############################################################################
# Test Driver
# You may selectivley comment out tests in the run_unit_tests function
# to debug during development. That's why I'm keeping the duplicate code in a
# map and function.
###############################################################################

def run_unit_tests():
    """ Run all unit tests. """
    print_action("[helptext] Unit Tests")

    print_action("Running bottom-up tests:")
    ut_parsefunc_long_flag()
    ut_parsefunc_short_flag()
    ut_parsefunc_optional_arg()
    ut_parsefunc_required_arg()
    ut_parsefunc_argument_shortflag_only()
    ut_parsefunc_argument_longflag_only()
    ut_parsefunc_argument_long_and_short_flag()
    ut_parsefunc_argument_required_arg()
    ut_parsefunc_argument_optional_arg()
    ut_parsefunc_argument_desc_same_line()
    ut_parsefunc_argument_indented_brief_following_arg()
    ut_parsefunc_argument_full()
    ut_parsefunc_argument_full_with_commas()
    ut_parsefunc_argument_list()
    ut_parsefunc_section_paragraph()
    ut_parsefunc_section_arguments()
    ut_parsefunc_usage_section()
    ut_parsefunc_help_text()

    print_action("Running end-to-end tests:")
    ut_parser_usage_line()
    ut_parser_paragraph()
    ut_parser_usage_and_paragraph()
    ut_parser_usage_paragraph_section()
    ut_parser_arg_long_flag()
    ut_parser_arg_short_flag()
    ut_parser_arg_short_and_long_flag()
    ut_parser_arg_optional_arg()
    ut_parser_arg_required_arg()
    ut_parser_arg_indented_brief_following_arg()
    ut_parser_arg_indented_multiline_brief_following_arg()
    ut_parser_simple()
    ut_parser_full()
    ut_parser_usage_with_multiline()
    ut_parser_gmash_dirs_same()

    # Generator tests
    print_action("Running Validation tests:")
    ut_generator_basic()
    ut_generator_self()

CMNH_TEST_MAP : dict = {
    # Bottom up tests
    "ut_parsefunc_long_flag": ut_parsefunc_long_flag
    ,"ut_parsefunc_short_flag": ut_parsefunc_short_flag
    ,"ut_parsefunc_optional_arg": ut_parsefunc_optional_arg
    ,"ut_parsefunc_required_arg": ut_parsefunc_required_arg
    ,"ut_parsefunc_argument_shortflag_only": ut_parsefunc_argument_shortflag_only
    ,"ut_parsefunc_argument_longflag_only": ut_parsefunc_argument_longflag_only
    ,"ut_parsefunc_argument_long_and_short_flag": ut_parsefunc_argument_long_and_short_flag
    ,"ut_parsefunc_argument_required_arg": ut_parsefunc_argument_required_arg
    ,"ut_parsefunc_argument_optional_arg": ut_parsefunc_argument_optional_arg
    ,"ut_parsefunc_argument_desc_same_line": ut_parsefunc_argument_desc_same_line
    , "ut_parsefunc_argument_indented_brief_following_arg": ut_parsefunc_argument_indented_brief_following_arg
    , "ut_parsefunc_argument_full" : ut_parsefunc_argument_full
    , "ut_parsefunc_argument_full_with_commas" : ut_parsefunc_argument_full_with_commas
    ,"ut_parsefunc_argument_list": ut_parsefunc_argument_list
    ,"ut_parsefunc_section_paragraph": ut_parsefunc_section_paragraph
    ,"ut_parsefunc_section_arguments": ut_parsefunc_section_arguments
    ,"ut_parsefunc_usage_section": ut_parsefunc_usage_section
    ,"ut_parsefunc_help_text": ut_parsefunc_help_text

    # Top down tests
    ,"ut_parser_usage_line": ut_parser_usage_line
    ,"ut_parser_paragraph": ut_parser_paragraph
    ,"ut_parser_usage_and_paragraph": ut_parser_usage_and_paragraph
    ,"ut_parser_usage_paragraph_section": ut_parser_usage_paragraph_section
    ,"ut_parser_arg_long_flag": ut_parser_arg_long_flag
    ,"ut_parser_arg_short_flag": ut_parser_arg_short_flag
    ,"ut_parser_arg_short_and_long_flag": ut_parser_arg_short_and_long_flag
    ,"ut_parser_arg_optional_arg": ut_parser_arg_optional_arg
    ,"ut_parser_arg_required_arg": ut_parser_arg_required_arg
    ,"ut_parser_arg_indented_brief_following_arg": ut_parser_arg_indented_brief_following_arg
    ,"ut_parser_arg_indented_multiline_brief_following_arg": ut_parser_arg_indented_multiline_brief_following_arg
    ,"ut_parser_simple" : ut_parser_simple
    ,"ut_parser_full": ut_parser_full
    ,"ut_parser_usage_with_multiline": ut_parser_usage_with_multiline
    ,"ut_parser_gmash_dirs_same": ut_parser_gmash_dirs_same

    # Generator tests
    ,"ut_generator_basic": ut_generator_basic
    , "ut_generator_self" : ut_generator_self

}
