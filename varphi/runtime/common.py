# pylint: disable=R0801
"""varphi/runtime/common.py"""

import sys

from .types import TapeCharacter, Tape, Head
from .exceptions import VarphiNoTallyException, VarphiInvalidTapeCharacterException


def debug_view_tape_head(tape: Tape, head: Head) -> str:
    """Return a string representation of the tape with the head position marked."""
    tape_as_string = ""
    for i in range(
        tape._minimum_accessed_index,  # pylint: disable=W0212
        max(
            tape._maximum_accessed_index,  # pylint: disable=W0212
            head._current_tape_cell_index,  # pylint: disable=W0212
        )
        + 1,
    ):
        character = (
            "1"
            if tape._tape[i] == TapeCharacter.TALLY  # pylint: disable=W0212
            else "0"
        )
        if i == 0:
            character = "{" + character + "}"
        if i == head._current_tape_cell_index:  # pylint: disable=W0212
            character = "[" + character + "]"
        tape_as_string += character
    return tape_as_string


def get_tape_from_stdin() -> Tape:
    """Reads the input tape from standard input and returns it as a Tape object."""
    # Ignore all leading blanks (0s)
    found_tally = False
    while not found_tally:
        input_character = sys.stdin.read(1)
        if input_character == "1":
            found_tally = True
        elif input_character in {"\n", "\r"}:
            raise VarphiNoTallyException(
                "Error: Input tape must contain at least one tally (1)."
            )
        elif input_character != "0":
            raise VarphiInvalidTapeCharacterException(
                f"Error: Invalid tape character (ASCII {ord(input_character)})."
            )

    # Since the above loop exited, a tally must have been found.
    initial_characters = [TapeCharacter.TALLY]
    while (input_character := sys.stdin.read(1)) not in {"\n", "\r"}:
        if input_character == "0":
            initial_characters.append(TapeCharacter.BLANK)
        elif input_character == "1":
            initial_characters.append(TapeCharacter.TALLY)
        else:
            raise VarphiInvalidTapeCharacterException(
                f"Error: Invalid tape character (ASCII {ord(input_character)})."
            )
    return Tape(initial_characters)
