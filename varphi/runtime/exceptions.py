"""varphi/runtime/exceptions.py"""


class VarphiNoTallyException(Exception):
    """An exception raised when a tally is not found on the initial tape."""


class VarphiInvalidTapeCharacterException(Exception):
    """An exception raised when an invalid character is written to a tape."""


class VarphiTuringMachineHaltedException(Exception):
    """An exception raised when a Turing machine halts."""


class VarphiDomainError(Exception):
    """An exception raised when an input outside the domain of a Turing machine is encountered."""
