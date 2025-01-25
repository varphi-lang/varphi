import sys
from io import StringIO

from varphi.compilation.varphi_translator import VarphiTranslatorCLITarget
from varphi.compilation.core import varphi_to_python

def test_add1():
    program = """
q0 1 q0 1 R
q0 0 qf 1 L
    """
    sys.stdin = StringIO("1\n")
    sys.stdout = captured_output = StringIO()
    exec(varphi_to_python(program, "from varphi.runtime.cli import main\n", VarphiTranslatorCLITarget), {"__name__": "__main__"})
    assert captured_output.getvalue().strip().strip('0') == "11"

    sys.stdin = StringIO("11\n")
    sys.stdout = captured_output = StringIO()
    exec(varphi_to_python(program, "from varphi.runtime.cli import main\n", VarphiTranslatorCLITarget), {"__name__": "__main__"})
    assert captured_output.getvalue().strip().strip('0') == "111"

    sys.stdin = StringIO("110\n")
    sys.stdout = captured_output = StringIO()
    exec(varphi_to_python(program, "from varphi.runtime.cli import main\n", VarphiTranslatorCLITarget), {"__name__": "__main__"})
    assert captured_output.getvalue().strip().strip('0') == "111"
    

def test_add():
    program = """
q0 0 qh 0 R // Nothing from first number remaining; halt
q0 1 q1 0 R // Change first tally (to the left) of the first number to a 0 (we'll "move" this to the end of the second number)
q1 1 q1 1 R // Skip the rest of the tallies of the first number
q1 0 q2 0 R // Found middle blank
q2 1 q2 1 R // Skip through the tallies of the second number
q2 0 q3 1 L // Found end of second number; add a tally here
q3 1 q3 1 L // Skip through tallies of second number (moving left)
q3 0 q4 0 L // Found middle blank
q4 1 q4 1 L // Skip through tallies of first number
q4 0 q0 0 R // Found end of first number (it will be 1 less than before now), switch to q0 and repeat the process
    """
    sys.stdin = StringIO("101\n")
    sys.stdout = captured_output = StringIO()
    exec(varphi_to_python(program, "from varphi.runtime.cli import main\n", VarphiTranslatorCLITarget), {"__name__": "__main__"})
    assert captured_output.getvalue().strip().strip('0') == "11"

    sys.stdin = StringIO("1101\n")
    sys.stdout = captured_output = StringIO()
    exec(varphi_to_python(program, "from varphi.runtime.cli import main\n", VarphiTranslatorCLITarget), {"__name__": "__main__"})
    assert captured_output.getvalue().strip().strip('0') == "111"

    sys.stdin = StringIO("1011\n")
    sys.stdout = captured_output = StringIO()
    exec(varphi_to_python(program, "from varphi.runtime.cli import main\n", VarphiTranslatorCLITarget), {"__name__": "__main__"})
    assert captured_output.getvalue().strip().strip('0') == "111"

    sys.stdin = StringIO("11011\n")
    sys.stdout = captured_output = StringIO()
    exec(varphi_to_python(program, "from varphi.runtime.cli import main\n", VarphiTranslatorCLITarget), {"__name__": "__main__"})
    assert captured_output.getvalue().strip().strip('0') == "1111"


def test_mult2():
    program = """
q0 1 q1 0 R // "Mark" the current tally from the first number by changing it to 0
q0 0 qmerge 0 R // No more tallies from the first number, "merge" the two halves of the doubled number
q1 1 q1 1 R // Skip over the rest of the tallies from the first number
q1 0 q2 0 R // We've reached the middle blank
q2 1 q2 1 R // Skip over the tallies from the second number
q2 0 q3 1 L // We've reached the end of the first number, place a tally here
q3 1 q3 1 L // Skip over the tallies from the second number (moving left now)
q3 0 q4 0 L // We've reached the middle blank
q4 1 q4 1 L // Skip over the tallies from the first number (moving left now)
q4 0 q0 1 R // We've reached the beginning of the first number. Return the tally that we replaced with a blank, and point the head to the next tally of the first number and restart

qmerge 1 qmerge1 1 L // When we hit qmerge, the head will be pointed at the first tally from the second half. Shift to the left to go to the middle blank
qmerge1 0 qmerge2 1 R // Change the middle blank to a tally
qmerge2 1 qmerge2 1 R // Skip over the tallies of the second half
qmerge2 0 qmerge3 0 L // We've reached the end of the second half, but there's one more tally at the far right of the second half. Remove it
qmerge3 1 qh 0 R // Replace the last tally of the second half with a blank
    """
    sys.stdin = StringIO("1\n")
    sys.stdout = captured_output = StringIO()
    exec(varphi_to_python(program, "from varphi.runtime.cli import main\n", VarphiTranslatorCLITarget), {"__name__": "__main__"})
    assert captured_output.getvalue().strip().strip('0') == "11"

    sys.stdin = StringIO("11\n")
    sys.stdout = captured_output = StringIO()
    exec(varphi_to_python(program, "from varphi.runtime.cli import main\n", VarphiTranslatorCLITarget), {"__name__": "__main__"})
    assert captured_output.getvalue().strip().strip('0') == "1111"

def test_nonnegative_subtraction():
    program = """
q0 1 q0 1 R // Keep scanning through tallies of the first number until you see the middle blank
q0 0 q1 0 R // Middle blank found
q1 1 q1 1 R // Go through all the tallies of the second number
q1 0 q2 0 L // Found end of second number
q2 0 qh 0 R // If the end of the last number is a blank, there's nothing left from the second number
q2 1 q3 0 L // If the end of the last number is a tally, take out the last tally and replace with a blank
q3 1 q3 1 L // Go through the remaining tallies of the second number until you see the middle blank
q3 0 q4 0 L // Middle blank found
q4 1 q4 1 L // Go through the tallies of the first number
q4 0 q5 0 R // Found end of the first number (to the left)
q5 1 q0 0 R // Take out first tally of the first number to the left (this subtracts 1); switch to q0 and repeat the process
    """
    sys.stdin = StringIO("11101\n")
    sys.stdout = captured_output = StringIO()
    exec(varphi_to_python(program, "from varphi.runtime.cli import main\n", VarphiTranslatorCLITarget), {"__name__": "__main__"})
    assert captured_output.getvalue().strip().strip('0') == "11"

    sys.stdin = StringIO("1101\n")
    sys.stdout = captured_output = StringIO()
    exec(varphi_to_python(program, "from varphi.runtime.cli import main\n", VarphiTranslatorCLITarget), {"__name__": "__main__"})
    assert captured_output.getvalue().strip().strip('0') == "1"


def test_rock_paper_scissors():
    program = """
qUnknown 1 qRock 0 R
qRock 1 qPaper 0 R
qPaper 1 qScissors 0 R

qRock 0 qRockUnknown 0 R
qPaper 0 qPaperUnknown 0 R
qScissors 0 qScissorsUnknown 0 R

qRockUnknown 1 qRockRock 0 R
qPaperUnknown 1 qPaperRock 0 R
qScissorsUnknown 1 qScissorsRock 0 R

qRockRock 1 qRockPaper 0 R
qRockPaper 1 qRockScissors 0 R

qPaperRock 1 qPaperPaper 0 R
qPaperPaper 1 qPaperScissors 0 R

qScissorsRock 1 qScissorsPaper 0 R
qScissorsPaper 1 qScissorsScissors 0 R

qRockRock 0 qTie 0 R
qRockPaper 0 qPlayer2Won 0 R
qRockScissors 0 qPlayer1Won 0 R
qPaperRock 0 qPlayer1Won 0 R
qPaperPaper 0 qTie 0 R
qPaperScissors 0 qPlayer2Won 0 R
qScissorsRock 0 qPlayer2Won 0 R
qScissorsPaper 0 qPlayer1Won 0 R
qScissorsScissors 0 qTie 0 R

qTie 0 qWrite1 0 R
qPlayer1Won 0 qWrite2 0 R
qPlayer2Won 0 qWrite3 0 R

qWrite1 0 qHalt 1 R
qWrite2 0 qWrite1 1 R
qWrite3 0 qWrite2 1 R
    """
    sys.stdin = StringIO("101\n")  # Rock v Rock
    sys.stdout = captured_output = StringIO()
    exec(varphi_to_python(program, "from varphi.runtime.cli import main\n", VarphiTranslatorCLITarget), {"__name__": "__main__"})
    assert captured_output.getvalue().strip().strip('0') == "1"  # Tie

    sys.stdin = StringIO("1011\n")  # Rock v Paper
    sys.stdout = captured_output = StringIO()
    exec(varphi_to_python(program, "from varphi.runtime.cli import main\n", VarphiTranslatorCLITarget), {"__name__": "__main__"})
    assert captured_output.getvalue().strip().strip('0') == "111"  # Player 2 won

    sys.stdin = StringIO("10111\n")  # Rock v Scissors
    sys.stdout = captured_output = StringIO()
    exec(varphi_to_python(program, "from varphi.runtime.cli import main\n", VarphiTranslatorCLITarget), {"__name__": "__main__"})
    assert captured_output.getvalue().strip().strip('0') == "11"  # Player 1 won

    sys.stdin = StringIO("1101\n")
    sys.stdout = captured_output = StringIO()
    exec(varphi_to_python(program, "from varphi.runtime.cli import main\n", VarphiTranslatorCLITarget), {"__name__": "__main__"})
    assert captured_output.getvalue().strip().strip('0') == "11"  # Player 1 won

    sys.stdin = StringIO("11011\n")
    sys.stdout = captured_output = StringIO()
    exec(varphi_to_python(program, "from varphi.runtime.cli import main\n", VarphiTranslatorCLITarget), {"__name__": "__main__"})
    assert captured_output.getvalue().strip().strip('0') == "1"  # Tie

    sys.stdin = StringIO("110111\n")
    sys.stdout = captured_output = StringIO()
    exec(varphi_to_python(program, "from varphi.runtime.cli import main\n", VarphiTranslatorCLITarget), {"__name__": "__main__"})
    assert captured_output.getvalue().strip().strip('0') == "111"  # Player 2 won

    sys.stdin = StringIO("11101\n")
    sys.stdout = captured_output = StringIO()
    exec(varphi_to_python(program, "from varphi.runtime.cli import main\n", VarphiTranslatorCLITarget), {"__name__": "__main__"})
    assert captured_output.getvalue().strip().strip('0') == "111"  # Player 2 won

    sys.stdin = StringIO("111011\n")
    sys.stdout = captured_output = StringIO()
    exec(varphi_to_python(program, "from varphi.runtime.cli import main\n", VarphiTranslatorCLITarget), {"__name__": "__main__"})
    assert captured_output.getvalue().strip().strip('0') == "11"  # Player 1 won

    sys.stdin = StringIO("1110111\n")
    sys.stdout = captured_output = StringIO()
    exec(varphi_to_python(program, "from varphi.runtime.cli import main\n", VarphiTranslatorCLITarget), {"__name__": "__main__"})
    assert captured_output.getvalue().strip().strip('0') == "1"  # Tie

def test_coin_flip():
    program = """
qStart 1 qHeads 0 R
qStart 1 qTails 0 R

qHeads 0 qWrite1 0 R
qTails 0 qWrite2 0 R

qWrite1 0 qHalt 1 R
qWrite2 0 qWrite1 1 R
    """
    sys.stdin = StringIO("1\n")  # Heads
    sys.stdout = captured_output = StringIO()
    exec(varphi_to_python(program, "from varphi.runtime.cli import main\n", VarphiTranslatorCLITarget), {"__name__": "__main__"})
    assert captured_output.getvalue().strip().strip('0') in {"1", "11"}