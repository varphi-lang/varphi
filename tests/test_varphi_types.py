"""tests/test_varphi_types.py"""
import pytest
from varphi.runtime.types import State, Instruction, TapeCharacter, HeadDirection

@pytest.fixture
def state():
    """Fixture to create a new state for each test."""
    return State()


def test_create_state(state):
    """Test the creation of a state and ensure its instruction lists are empty initially."""
    assert state.on_tally_instructions == []
    assert state.on_blank_instructions == []


def test_add_on_tally_instruction(state):
    """Test adding a valid instruction for the tally character."""
    instruction = Instruction(next_state=state,
                              character_to_place=TapeCharacter.TALLY,
                              direction_to_move=HeadDirection.RIGHT)
    state.add_on_tally_instruction(instruction)
    assert instruction in state.on_tally_instructions
    assert len(state.on_tally_instructions) == 1


def test_add_on_blank_instruction(state):
    """Test adding a valid instruction for the blank character."""
    instruction = Instruction(next_state=state,
                              character_to_place=TapeCharacter.BLANK,
                              direction_to_move=HeadDirection.LEFT)
    state.add_on_blank_instruction(instruction)
    assert instruction in state.on_blank_instructions
    assert len(state.on_blank_instructions) == 1


def test_duplicate_on_tally_instruction(state):
    """Test adding duplicate instructions to the tally list."""
    instruction = Instruction(next_state=state,
                              character_to_place=TapeCharacter.TALLY,
                              direction_to_move=HeadDirection.RIGHT)
    state.add_on_tally_instruction(instruction)
    state.add_on_tally_instruction(instruction)  # Adding the same instruction again
    assert len(state.on_tally_instructions) == 1  # It should not be duplicated


def test_duplicate_on_blank_instruction(state):
    """Test adding duplicate instructions to the blank list."""
    instruction = Instruction(next_state=state,
                              character_to_place=TapeCharacter.BLANK,
                              direction_to_move=HeadDirection.LEFT)
    state.add_on_blank_instruction(instruction)
    state.add_on_blank_instruction(instruction)  # Adding the same instruction again
    assert len(state.on_blank_instructions) == 1  # It should not be duplicated


def test_non_deterministic_state(state):
    """Test that a state can handle multiple instructions for the
    same character (non-determinism).
    """
    state_1 = State()
    state_2 = State()

    instruction_1 = Instruction(next_state=state_1,
                                character_to_place=TapeCharacter.TALLY,
                                direction_to_move=HeadDirection.RIGHT)
    instruction_2 = Instruction(next_state=state_2,\
                                character_to_place=TapeCharacter.TALLY,
                                direction_to_move=HeadDirection.LEFT)

    state.add_on_tally_instruction(instruction_1)
    state.add_on_tally_instruction(instruction_2)

    assert instruction_1 in state.on_tally_instructions
    assert instruction_2 in state.on_tally_instructions
    assert len(state.on_tally_instructions) == 2
