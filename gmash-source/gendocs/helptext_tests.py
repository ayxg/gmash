from helptext_common import print_error,print_action
from helptext_ast import Ast,Tk
from helptext_parser import Parser,split_lines
from helptext_parser import                                     \
    parse_long_flag,parse_short_flag,parse_argument,            \
    parse_optional_arg,parse_required_arg,parse_argument_list,  \
    parse_section,parse_usage_section,parse_help_text
###############################################################################
# Unit Test Utils
###############################################################################

def print_ast_diff(input_ast, expected_ast, indent: int = 0, path: tuple = ()) -> None:
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
        print_ast_diff(child, expected_ast, indent + 1, path + (i,))

def print_expected_ast_diff(expected_ast, input_ast, indent: int = 0, path: tuple = ()) -> None:
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
        print_expected_ast_diff(child, input_ast, indent + 1, path + (i,))

def compare_asts(input_ast, expected_ast):
    """Main function to compare two ASTs"""
    print("Input AST (differences in red):")
    print_ast_diff(input_ast, expected_ast)

    print("\nExpected AST (differences in green):")
    print_expected_ast_diff(expected_ast, input_ast)

def test_parser(test_name, parser_input, expected_output):
    """ Run a parser test and compare the output AST to the expected AST."""
    prs = Parser()
    ast = prs.parse(parser_input)
    if ast.is_error():
        print_error(f"Test {test_name} failed with error:\n\t{ast.get_error()}",1)
    else:
        did_test_pass = ast.get_ast() == expected_output
        if not did_test_pass:
            print_error(f"Test {test_name} failed.",1)
            compare_asts(ast.get_ast(), expected_output)
        else:
            print_action(f"Test {test_name} passed.",1)

def test_parser_function(funct,test_name,parser_input,expected_output):
    """ Run a specific parser function test and compare the output AST to the expected AST."""
    result = funct(split_lines(parser_input),0,0)
    if result.is_error():
        print_error(f"Test {test_name} failed with error:\n\t{result.error}",1)
        return
    ast = result.get_ast()
    did_test_pass = ast == expected_output
    if not did_test_pass:
        print_error(f"Test {test_name} failed.",1)
        compare_asts(ast, expected_output)
    else:
        print_action(f"Test {test_name} passed.",1)

# ###############################################################################
# # Unit Tests
# ###############################################################################

def ut_parsefunc_long_flag():
    """ Long flag parse function """
    test_parser_function(parse_long_flag,
        "ut_parsefunc_long_flag",
        parser_input="--long-flag-ident123",
        expected_output=Ast(Tk.LONG_FLAG,None,branches = [Ast(Tk.LONG_FLAG_IDENT,'long-flag-ident123')])
    )

def ut_parsefunc_short_flag():
    """ Short flag parse function """
    test_parser_function(parse_short_flag,
        "ut_parsefunc_short_flag",
        parser_input="-f\n",
        expected_output=Ast(Tk.SHORT_FLAG,None,branches = [Ast(Tk.SHORT_FLAG_IDENT,'f')])
    )

def ut_parsefunc_long_and_short_flag():
    """ Long and short flag parse function """
    test_parser_function(parse_argument,
        "ut_parsefunc_long_and_short_flag",
        parser_input="-f --long-flag-ident123 This is the argument documentation.\n",
        expected_output=Ast(Tk.ARGUMENT,None,branches = [
            Ast(Tk.SHORT_FLAG,None,branches = [Ast(Tk.SHORT_FLAG_IDENT,'f')]),
            Ast(Tk.LONG_FLAG,None,branches = [Ast(Tk.LONG_FLAG_IDENT,'long-flag-ident123')]),
            Ast(Tk.TEXT_LINE,"This is the argument documentation.")
        ])
    )

def ut_parsefunc_optional_arg():
    """ Optional arg parse function """
    test_parser_function(parse_optional_arg,
        "ut_parsefunc_optional_arg",
        parser_input="[optional_arg123]",
        expected_output=Ast(Tk.OPTIONAL_ARG,None,branches = [Ast(Tk.SHELL_IDENT,'optional_arg123')])
    )

def ut_parsefunc_required_arg():
    """ Required arg parse function """
    test_parser_function(parse_required_arg,
        "ut_parsefunc_required_arg",
        parser_input="<required_arg123>",
        expected_output=Ast(Tk.REQUIRED_ARG,None,branches = [Ast(Tk.SHELL_IDENT,'required_arg123')])
    )

def ut_parsefunc_argument_shortflag_only():
    """ Argument with short flag only parse function """
    test_parser_function(parse_argument,
        "ut_parsefunc_argument_shortflag_only",
        parser_input="-f\n",
        expected_output=Ast(Tk.ARGUMENT,None,branches = [
            Ast(Tk.SHORT_FLAG,None,branches = [Ast(Tk.SHORT_FLAG_IDENT,'f')])
        ])
    )

def ut_parsefunc_argument_longflag_only():
    """ Argument with long flag only parse function """
    test_parser_function(parse_argument,
        "ut_parsefunc_argument_longflag_only",
        parser_input="--long-flag-ident123\n",
        expected_output=Ast(Tk.ARGUMENT,None,branches = [
            Ast(Tk.LONG_FLAG,None,branches = [Ast(Tk.LONG_FLAG_IDENT,'long-flag-ident123')])
        ])
    )

def ut_parsefunc_argument_long_and_short_flag():
    """ Argument with long and short flag parse function """
    test_parser_function(parse_argument,
        "ut_parsefunc_argument_long_and_short_flag",
        parser_input="-f --long-flag-ident123",
        expected_output=Ast(Tk.ARGUMENT,None,branches = [
            Ast(Tk.SHORT_FLAG,None,branches = [Ast(Tk.SHORT_FLAG_IDENT,'f')]),
            Ast(Tk.LONG_FLAG,None,branches = [Ast(Tk.LONG_FLAG_IDENT,'long-flag-ident123')])
        ])
    )

def ut_parsefunc_argument_required_arg():
    """ Argument with required arg parse function """
    test_parser_function(parse_argument,
        "ut_parsefunc_argument_required_arg",
        parser_input="--long-flag-ident123 <required_arg123>",
        expected_output=Ast(Tk.ARGUMENT,None,branches = [
            Ast(Tk.LONG_FLAG,None,branches = [Ast(Tk.LONG_FLAG_IDENT,'long-flag-ident123')]),
            Ast(Tk.REQUIRED_ARG,None,branches = [Ast(Tk.SHELL_IDENT,'required_arg123')])
        ])
    )

def ut_parsefunc_argument_optional_arg():
    """ Argument with optional arg parse function """
    test_parser_function(parse_argument,
        "ut_parsefunc_argument_optional_arg",
        parser_input="--long-flag-ident123 [optional_arg123]",
        expected_output=Ast(Tk.ARGUMENT,None,branches = [
            Ast(Tk.LONG_FLAG,None,branches = [Ast(Tk.LONG_FLAG_IDENT,'long-flag-ident123')]),
            Ast(Tk.OPTIONAL_ARG,None,branches = [Ast(Tk.SHELL_IDENT,'optional_arg123')])
        ])
    )

def ut_parsefunc_argument_desc_same_line():
    """ Argument with description on the same line parse function """
    test_parser_function(parse_argument,
        "ut_parsefunc_argument_desc_same_line",
        parser_input="--long-flag-ident123 This is the argument documentation.\n",
        expected_output=Ast(Tk.ARGUMENT,None,branches = [
            Ast(Tk.LONG_FLAG,None,branches = [Ast(Tk.LONG_FLAG_IDENT,'long-flag-ident123')]),
            Ast(Tk.TEXT_LINE,"This is the argument documentation.")
        ])
    )

def ut_parsefunc_argument_indented_brief_following_arg():
    """ Argument with indented brief following parse function """
    test_parser_function(parse_argument,
        "ut_parsefunc_argument_indented_brief_following_arg",
        parser_input="--long-flag-ident123\n        This is the argument documentation.\n",
        expected_output=Ast(Tk.ARGUMENT,None,branches = [
            Ast(Tk.LONG_FLAG,None,branches = [Ast(Tk.LONG_FLAG_IDENT,'long-flag-ident123')]),
            Ast(Tk.TEXT_LINE,"This is the argument documentation.")
        ])
    )

def ut_parsefunc_argument_full():
    """ Full argument parse function """
    test_parser_function(parse_argument,
        "ut_parsefunc_argument_full",
        parser_input="-f --long-flag-ident123 --second-flag-opt [optional_arg] This is the argument documentation.\n",
        expected_output=Ast(Tk.ARGUMENT,None,branches = [
            Ast(Tk.SHORT_FLAG,None,branches = [Ast(Tk.SHORT_FLAG_IDENT,'f')]),
            Ast(Tk.LONG_FLAG,None,branches = [Ast(Tk.LONG_FLAG_IDENT,'long-flag-ident123')]),
            Ast(Tk.LONG_FLAG,None,branches = [Ast(Tk.LONG_FLAG_IDENT,'second-flag-opt')]),
            Ast(Tk.OPTIONAL_ARG,None,branches = [Ast(Tk.SHELL_IDENT,'optional_arg')]),
            Ast(Tk.TEXT_LINE,"This is the argument documentation.")
        ])
    )

def ut_parsefunc_argument_full_with_commas():
    """ Full argument with commas parse function """
    test_parser_function(parse_argument,
        "ut_parsefunc_argument_full_with_commas",
        parser_input="-f, --long-flag-ident123, --second-flag-opt [optional_arg] This is the argument documentation.\n",
        expected_output=Ast(Tk.ARGUMENT,None,branches = [
            Ast(Tk.SHORT_FLAG,None,branches = [Ast(Tk.SHORT_FLAG_IDENT,'f')]),
            Ast(Tk.LONG_FLAG,None,branches = [Ast(Tk.LONG_FLAG_IDENT,'long-flag-ident123')]),
            Ast(Tk.LONG_FLAG,None,branches = [Ast(Tk.LONG_FLAG_IDENT,'second-flag-opt')]),
            Ast(Tk.OPTIONAL_ARG,None,branches = [Ast(Tk.SHELL_IDENT,'optional_arg')]),
            Ast(Tk.TEXT_LINE,"This is the argument documentation.")
        ])
    )

def ut_parsefunc_argument_list():
    """ Argument list parse function """
    test_parser_function(parse_argument_list,
        "ut_parsefunc_argument_list",
        parser_input="-f --long-flag-ident123 This is the argument documentation.\n"
                     "-g --another-flag [optional_arg] This is another argument.\n",
        expected_output=Ast(Tk.ARGUMENT_LIST,None,branches = [
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
    """ Section with paragraph parse function """
    test_parser_function(parse_section,
        "ut_parsefunc_section_paragraph",
        parser_input="Details\n    This is a paragraph.\n    This is the second line.\n",
        expected_output=Ast(Tk.SECTION,"Details",branches = [
            Ast(Tk.PARAGRAPH,None,branches = [
                Ast(Tk.TEXT_LINE,"This is a paragraph."),
                Ast(Tk.TEXT_LINE,"This is the second line.")
            ])
        ])
    )

def ut_parsefunc_section_arguments():
    """ Section with argument list parse function """
    test_parser_function(parse_section,
        "ut_parsefunc_section_arguments",
        parser_input="Options\n    -f --long-flag-ident123 This is the argument documentation.\n    -g --another-flag [optional_arg] This is another argument.\n",
        expected_output=Ast(Tk.SECTION,"Options",branches = [
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
    """ Usage section parse function """
    test_parser_function(parse_usage_section,
        "ut_parsefunc_usage_section",
        parser_input="Usage: myprogram [options] <input_file>\n",
        expected_output=Ast(Tk.USAGE,"myprogram [options] <input_file>")
    )

def ut_parsefunc_help_text():
    """ Full help text parse function """
    test_parser_function(parse_help_text,
        "ut_parsefunc_help_text",
        parser_input="Usage: myprogram [options] <input_file>\n\nThis is a paragraph.\nThis is the second line.\n\nDetails\n    These are the details.\n\n",
        expected_output=Ast(Tk.SYNTAX,None,branches = [
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

def ut_parser_usage_line():
    """Usage line"""
    test_parser("ut_parser_usage_line",
        parser_input="Usage: myprogram [options] <input_file>\n\n",
        expected_output=Ast(Tk.SYNTAX,None,branches = [
            Ast(Tk.USAGE,"myprogram [options] <input_file>")
        ])
    )

def ut_parser_paragraph():
    """Paragraph"""
    test_parser("ut_parser_paragraph",
        parser_input="This is a paragraph.\nThis is the second line.\n\n",
        expected_output=Ast(Tk.SYNTAX,None,branches = [
            Ast(Tk.PARAGRAPH,None,branches = [
                Ast(Tk.TEXT_LINE,"This is a paragraph."),
                Ast(Tk.TEXT_LINE,"This is the second line.")
            ])
        ])
    )

def ut_parser_usage_and_paragraph():
    """Usage line and paragraph"""
    test_parser("ut_parser_usage_and_paragraph",
        parser_input="Usage: myprogram [options] <input_file>\n\nThis is a paragraph.\nThis is the second line.\n\n",
        expected_output=Ast(Tk.SYNTAX,None,branches = [
            Ast(Tk.USAGE,"myprogram [options] <input_file>"),
            Ast(Tk.PARAGRAPH,None,branches = [
                Ast(Tk.TEXT_LINE,"This is a paragraph."),
                Ast(Tk.TEXT_LINE,"This is the second line.")
            ])
        ])
    )

def ut_parser_usage_paragraph_section():
    """Usage line, paragraph and section"""
    test_parser("ut_parser_usage_paragraph_section",
        parser_input="Usage: myprogram [options] <input_file>\n\nThis is a paragraph.\nThis is the second line.\n\nDetails\n    These are the details.\n\n",
        expected_output=Ast(Tk.SYNTAX,None,branches = [
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
    """Long cli argument flag"""
    test_parser("ut_parser_arg_long_flag",
        parser_input="Options\n    --long-flag-ident123 This is the argument documentation.\n\n",
        expected_output=Ast(Tk.SYNTAX,None,branches = [
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
    """Short cli argument flag"""
    test_parser("ut_parser_arg_short_flag",
        parser_input="Options\n    -f This is the argument documentation.\n\n",
        expected_output=Ast(Tk.SYNTAX,None,branches = [
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
    """Short and long cli argument flags"""
    test_parser("ut_parser_arg_short_and_long_flag",
        parser_input="Options\n    -f --long-flag-ident123 This is the argument documentation.\n\n",
        expected_output=Ast(Tk.SYNTAX,None,branches = [
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
    """Optional cli argument"""
    test_parser("ut_parser_arg_optional_arg",
        parser_input="Options\n    --long-flag-ident123 [optional_arg123] This is the argument documentation.\n\n",
        expected_output=Ast(Tk.SYNTAX,None,branches = [
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
    """Required cli argument"""
    test_parser("ut_parser_arg_required_arg",
        parser_input="Options\n    --long-flag-ident123 <required_arg123> This is the argument documentation.\n\n",
        expected_output=Ast(Tk.SYNTAX,None,branches = [
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
    """Argument with indented brief following"""
    test_parser("ut_parser_arg_indented_brief_following_arg",
        parser_input="Options\n    --long-flag-ident123 <required_arg123>\n        This is the argument documentation.\n\n",
        expected_output=Ast(Tk.SYNTAX,None,branches = [
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
    """Argument with indented brief following"""
    test_parser("ut_parser_arg_indented_multiline_brief_following_arg",
        parser_input="Options\n    --long-flag-ident123 <required_arg123>\n        This is the argument documentation.\n        This is the second line.\n\n",
        expected_output=Ast(Tk.SYNTAX,None,branches = [
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
    test_parser("ut_parser_simple",
        parser_input="USAGE:\n"
            +"    py cmhn_compiler.py [ [ -v | --verbose ] | [ -d | --debug ] ] <helpTextInput>\n"
            +"\n"
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
        expected_output=Ast(Tk.SYNTAX,None,branches = [
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
    """Basic complete example"""
    test_parser("ut_parser_full",parser_input=""
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
        expected_output=Ast(Tk.SYNTAX,None,branches = [
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

def run_unit_tests():
    """ Run all unit tests. """
    print_action("Running unit tests...")

    print_action("Testing parser bottom-up:")
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

    print_action("Testing parser end-to-end:")
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

    print_action("All unit tests completed.")

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

}
