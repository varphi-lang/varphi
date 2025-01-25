from antlr4 import InputStream, CommonTokenStream

from varphi.parsing import *
from varphi.compilation.varphi_compilation_errors import *

def lexer_error_occurred(input_text: str) -> bool:
    input_stream = InputStream(input_text)
    lexer = VarphiLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    error_listener = VarphiSyntaxErrorListener(input_text)
    lexer.removeErrorListeners()
    lexer.addErrorListener(error_listener)

    try:
        token_stream.fill()
        return False
    except VarphiSyntaxError:
        return True

def parser_error_occurred(input_text: str):
    input_stream = InputStream(input_text)
    lexer = VarphiLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = VarphiParser(token_stream)
    error_listener = VarphiSyntaxErrorListener(input_text)
    lexer.removeErrorListeners()
    parser.removeErrorListeners()
    lexer.addErrorListener(error_listener)
    parser.addErrorListener(error_listener)
    
    try:
        # Parse the program
        parser.program()
        return False
    except VarphiSyntaxError:
        return True

def test_empty_program():
    program = ""
    expect_lexer_error = False
    expect_parser_error = False
    assert lexer_error_occurred(program) == expect_lexer_error
    assert parser_error_occurred(program) == expect_parser_error

def test_invalid_token():
    program = "a"
    expect_lexer_error = True
    expect_parser_error = True
    assert lexer_error_occurred(program) == expect_lexer_error
    assert parser_error_occurred(program) == expect_parser_error

def test_invalid_line_ordering():
    program = "L q0 q1 1 0"
    expect_lexer_error = False
    expect_parser_error = True
    assert lexer_error_occurred(program) == expect_lexer_error
    assert parser_error_occurred(program) == expect_parser_error

def test_valid_line_ordering():
    program = "q0 1 q1 0 R"
    expect_lexer_error = False
    expect_parser_error = False
    assert lexer_error_occurred(program) == expect_lexer_error
    assert parser_error_occurred(program) == expect_parser_error

def test_multiple_valid_lines():
    program = "q0 1 q1 0 R\nq1 0 q2 1 R"
    expect_lexer_error = False
    expect_parser_error = False
    assert lexer_error_occurred(program) == expect_lexer_error
    assert parser_error_occurred(program) == expect_parser_error

def test_multiple_valid_lines_with_single_line_comment():
    program = "q0 1 q1 0 R // Comment 1\nq1 0 q2 1 R // Comment 2"
    expect_lexer_error = False
    expect_parser_error = False
    assert lexer_error_occurred(program) == expect_lexer_error
    assert parser_error_occurred(program) == expect_parser_error

def test_multiple_valid_lines_with_multi_line_comment():
    program = "/*This is a multiline comment\n This is the second line of a multiline comment!*/q0 1 q1 0 R // Comment 1\nq1 0 q2 1 R // Comment 2"
    expect_lexer_error = False
    expect_parser_error = False
    assert lexer_error_occurred(program) == expect_lexer_error
    assert parser_error_occurred(program) == expect_parser_error
