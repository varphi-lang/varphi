"""varphi/types/varphi_types.py"""

from __future__ import annotations
import random
from dataclasses import dataclass
from enum import Enum, auto
from typing import List
from collections import defaultdict
from .exceptions import VarphiTuringMachineHaltedException


class TapeCharacter(Enum):
    """Enumeration representing the possible characters on the tape."""

    BLANK = auto()
    TALLY = auto()


class HeadDirection(Enum):
    """Enumeration representing the possible directions for the head to move."""

    LEFT = auto()
    RIGHT = auto()


@dataclass(frozen=True)
class Instruction:
    """Represents an instruction for a Turing machine, detailing the next state,
    character to place, and the direction to move the head.
    """

    next_state: State
    character_to_place: TapeCharacter
    direction_to_move: HeadDirection


@dataclass(frozen=True)
class LineNumberedInstruction(Instruction):
    """Represents an instruction for a Turing machine, detailing the next state,
    character to place, and the direction to move the head.

    This instruction is aware of its line number in the Varphi source.
    """

    line_number: int


class State:
    """Represents a state in the Turing machine. This includes instructions for
    both when the tape head is on a blank or tally.

    Note that a state can have multiple instructions for the same character,
    in the case of a non-deterministic machine.
    """

    on_tally_instructions: List[Instruction]
    on_blank_instructions: List[Instruction]

    def __init__(self) -> None:
        """Initializes a State object."""
        self.on_tally_instructions = []
        self.on_blank_instructions = []

    def add_on_tally_instruction(self, instruction: Instruction) -> None:
        """Adds an instruction for when the tape head is on a tally."""
        if instruction in self.on_tally_instructions:
            return
        self.on_tally_instructions.append(instruction)

    def add_on_blank_instruction(self, instruction: Instruction) -> None:
        """Adds an instruction for when the tape head is on a blank."""
        if instruction in self.on_blank_instructions:
            return
        self.on_blank_instructions.append(instruction)


@dataclass
class NamedState(State):
    """Represents a state in the Turing machine. This includes instructions for
    both when the tape head is on a blank or tally.

    Note that a state can have multiple instructions for the same character,
    in the case of a non-deterministic machine.

    This state is aware of its name.
    """

    name: str

    def __init__(self, name: str) -> None:
        """Initializes a State object."""
        self.name = name
        super().__init__()


class Tape:
    """A class representing the tape of a Turing machine."""

    _tape: defaultdict[int, TapeCharacter]
    _maximum_accessed_index: int
    _minimum_accessed_index: int

    def __init__(self, initial_values: list[TapeCharacter]) -> None:
        self._tape = defaultdict(lambda: TapeCharacter.BLANK)
        self._maximum_accessed_index = 0
        self._minimum_accessed_index = 0

        i = 0
        for initial_value in initial_values:
            self[i] = initial_value
            i += 1

    def _update_maximum_and_minimum_indices_accessed(self, index: int) -> None:
        self._maximum_accessed_index = max(self._maximum_accessed_index, index)
        self._minimum_accessed_index = min(self._minimum_accessed_index, index)

    def __getitem__(self, index: int) -> TapeCharacter:
        self._update_maximum_and_minimum_indices_accessed(index)
        return self._tape[index]

    def __setitem__(self, index: int, value: TapeCharacter) -> None:
        self._update_maximum_and_minimum_indices_accessed(index)
        self._tape[index] = value

    def __repr__(self) -> str:
        representation = ""
        for i in range(self._minimum_accessed_index, self._maximum_accessed_index + 1):
            representation += "1" if self._tape[i] == TapeCharacter.TALLY else "0"
        return representation


class Head:
    """A class representing the head of a Turing machine."""

    _tape: Tape
    _current_tape_cell_index: int

    def __init__(self, tape: Tape) -> None:
        self._tape = tape
        self._current_tape_cell_index = 0

    def right(self) -> None:
        """Move the head one cell to the right."""
        self._current_tape_cell_index += 1

    def left(self) -> None:
        """Move the head one cell to the left."""
        self._current_tape_cell_index -= 1

    def read(self) -> TapeCharacter:
        """Read the value of the current cell."""
        return self._tape[self._current_tape_cell_index]

    def write(self, value: TapeCharacter) -> None:
        """Write a value to the current cell."""
        self._tape[self._current_tape_cell_index] = value

    def __repr__(self) -> str:
        return str(self._current_tape_cell_index)


class TuringMachine:  # pylint: disable=R0903
    """A class representing a Turing machine."""

    tape: Tape
    head: Head
    state: State

    def __init__(self, tape: Tape, initial_state: State) -> None:
        self.tape = tape
        self.head = Head(tape)
        self.state = initial_state

    def step(self):
        """Execute one step of the Turing machine and return the instruction that was executed.

        Raises `VarphiTuringMachineHaltedException` if the machine halts.
        """
        tape_character = self.head.read()
        if tape_character == TapeCharacter.TALLY:
            possible_instructions_to_follow = self.state.on_tally_instructions
        else:
            possible_instructions_to_follow = self.state.on_blank_instructions
        if len(possible_instructions_to_follow) == 0:
            raise VarphiTuringMachineHaltedException()
        next_instruction = random.choice(possible_instructions_to_follow)
        self.state = next_instruction.next_state
        self.head.write(next_instruction.character_to_place)
        if next_instruction.direction_to_move == HeadDirection.LEFT:
            self.head.left()
        else:
            self.head.right()


class DebugAdapterTuringMachine(TuringMachine):  # pylint: disable=R0903
    """A class representing a Turing machine."""

    tape: Tape
    head: Head
    state: NamedState
    _next_instruction: LineNumberedInstruction | None
    _armed: bool

    def __init__(self, tape: Tape, initial_state: NamedState) -> None:
        super().__init__(tape, initial_state)
        self._next_instruction = None
        self._armed = False

    def determine_next_instruction(self) -> LineNumberedInstruction:
        """Determine the next instruction to be executed by this Turing machine."""
        if self._armed:
            raise Exception(  # pylint: disable=W0719
                "Attempted to determine next instruction when an instruction is already armed."
            )
        tape_character = self.head.read()
        if tape_character == TapeCharacter.TALLY:
            possible_instructions_to_follow = self.state.on_tally_instructions
        else:
            possible_instructions_to_follow = self.state.on_blank_instructions
        if len(possible_instructions_to_follow) == 0:
            raise VarphiTuringMachineHaltedException()
        self._next_instruction = random.choice(possible_instructions_to_follow)
        self._armed = True
        return self._next_instruction

    def execute_next_instruction(self):
        """Execute one step of the Turing machine and return the instruction that was executed.

        Raises `VarphiTuringMachineHaltedException` if the machine halts.
        """
        if not self._armed:
            raise Exception(  # pylint: disable=W0719
                "Attempted to execute next instruction when no instruction armed."
            )
        self.state = self._next_instruction.next_state
        self.head.write(self._next_instruction.character_to_place)
        if self._next_instruction.direction_to_move == HeadDirection.LEFT:
            self.head.left()
        else:
            self.head.right()
        self._armed = False
