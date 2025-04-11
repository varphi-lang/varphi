# pylint: disable=duplicate-code
"""varphi/runtime/cli_with_prompts.py"""

import sys
from .common import get_tape_from_stdin
from .types import State, TuringMachine
from .exceptions import VarphiTuringMachineHaltedException, VarphiDomainError


def main(initial_state: State | None):  # pylint: disable=R0801
    """Construct the Turing machine given an initial state and run it.

    Reads the input tape from standard input and runs the Turing machine until it halts.
    """
    print("Input Tape: ", end="")
    sys.stdout.flush()
    tape = get_tape_from_stdin()
    if initial_state is None:
        raise VarphiDomainError("Error: Input provided to an empty Turing machine.")
    turing_machine = TuringMachine(tape, initial_state)
    while True:
        try:
            turing_machine.step()
        except VarphiTuringMachineHaltedException:
            break
    print(f"Output Tape: {tape}")
