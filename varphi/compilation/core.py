# pylint: disable=R0801
"""varphi/compilation/common.py"""

import os
import sys
from typing import Type

from antlr4 import InputStream, CommonTokenStream, ParseTreeWalker
from .varphi_translator import VarphiTranslator
from ..parsing import VarphiLexer, VarphiParser


def get_translator_from_program(
    program: str, translator_type: Type[VarphiTranslator]
) -> VarphiTranslator:
    """Parses a Varphi program string and returns a VarphiTranslatorCLITarget object."""
    # Create a lexer and parser for the input program
    input_stream = InputStream(program)
    lexer = VarphiLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = VarphiParser(token_stream)

    # Parse the input and get the parse tree
    parse_tree = parser.program()

    # Instantiate the custom listener
    translator = translator_type()

    # Walk the parse tree with the listener
    walker = ParseTreeWalker()
    walker.walk(translator, parse_tree)

    return translator


def varphi_to_python(
    program: str, main_import_statement: str, translator_type: Type[VarphiTranslator]
) -> str:
    """Compiles a Varphi program string to a Python program string."""
    translated_program = main_import_statement
    translated_program += get_translator_from_program(
        program, translator_type
    ).translated_program
    translated_program += "    main(initial_state)"
    return translated_program


def varphi_file_to_python(
    file_path: str, main_import_statement: str, translator_type: Type[VarphiTranslator]
) -> str:
    """Compiles a Varphi program file to a Python program string."""
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        sys.exit(1)
    with open(file_path, "r", encoding="utf-8") as f:
        translated_code = varphi_to_python(
            f.read(), main_import_statement, translator_type
        )
    return translated_code
