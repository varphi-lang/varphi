"""varphi/command_line_executable.py"""

import sys

from .common import get_tape_from_stdin
from .types import NamedState, TuringMachine
from .exceptions import VarphiTuringMachineHaltedException, VarphiDomainError
from .common import debug_view_tape_head


def main(initial_state: NamedState | None):  # pylint: disable=R0801
    """Construct the Turing machine given an initial state and run it.
    
    Reads the input tape from standard input and runs the Turing machine until it halts.
    """
    number_of_steps = 0
    print("Input Tape: ", end="")
    sys.stdout.flush()
    tape = get_tape_from_stdin()
    if initial_state is None:
        raise VarphiDomainError("Error: Input provided to an empty Turing machine.")
    turing_machine = TuringMachine(tape, initial_state)
    while True:
        try:
            print("State: ", turing_machine.state.name)
            print("Tape: ", debug_view_tape_head(tape, turing_machine.head))
            print("Press ENTER to step...")
            sys.stdin.read(1)
            turing_machine.step()
            number_of_steps += 1
        except VarphiTuringMachineHaltedException:
            break
    print(f"Output Tape: {tape}")
    print(f"Number of Steps: {number_of_steps}")
    print(f"Number of Tape Cells Accessed: {len(str(tape))}")
