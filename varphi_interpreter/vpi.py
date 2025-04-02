# pylint: disable=R0801
"""varphi_interpreter/v2p.py"""

import argparse

from varphi.compilation import varphi_file_to_python
from varphi.compilation.varphi_translator import (
    VarphiTranslatorCLITarget,
    VarphiTranslatorCLIDebuggerTarget,
    VarphiTranslatorCLIDebugAdapterTarget,
)
import varphi.runtime.cli
import varphi.runtime.cli_debugger
import varphi.runtime.debug_adapter
import varphi.runtime.cli_with_complexity
import varphi.runtime.cli_with_prompts


VPI_VERSION = "1.1.0"

def main():
    """The main function for the vpi command line interface."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "program", type=str, help="The path to the Varphi source file to be translated."
    )

    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="Compile the program in debug mode.",
    )

    parser.add_argument(
        "-a",
        "--debug-adapter",
        action="store_true",
        help="Compile the program to a debug adapter target.",
    )

    parser.add_argument(
        "-c",
        "--complexity",
        action="store_true",
        help="Enable prompting and print the number of steps taken by the machine and the number of tape cells accessed.",
    )

    parser.add_argument(
        "-p",
        "--enable-prompts",
        action="store_true",
        help="Prompt explicitly for the input tape and explicitly specify the output tape.",
    )

    parser.add_argument(
        "-v",
        "--version",
        action="store_true",
        help="Display the vpi version.",
    )

    args = parser.parse_args()
    if args.debug:
        exec(  # pylint: disable=W0122
            varphi_file_to_python(
                args.program,
                "from varphi.runtime.cli_debugger import main\n",
                translator_type=VarphiTranslatorCLIDebuggerTarget,
            ),
            {"__name__": "__main__"},
        )
    elif args.debug_adapter:
        exec(  # pylint: disable=W0122
            varphi_file_to_python(
                args.program,
                "from varphi.runtime.debug_adapter import main\n",
                translator_type=VarphiTranslatorCLIDebugAdapterTarget,
            ),
            {"__name__": "__main__"},
        )
    elif args.complexity:
        exec(  # pylint: disable=W0122
            varphi_file_to_python(
                args.program,
                "from varphi.runtime.cli_with_complexity import main\n",
                translator_type=VarphiTranslatorCLITarget,
            ),
            {"__name__": "__main__"},
        )
    elif args.enable_prompts:
        exec(  # pylint: disable=W0122
            varphi_file_to_python(
                args.program,
                "from varphi.runtime.cli_with_prompts import main\n",
                translator_type=VarphiTranslatorCLITarget,
            ),
            {"__name__": "__main__"},
        )
    else:
        exec(  # pylint: disable=W0122
            varphi_file_to_python(
                args.program,
                "from varphi.runtime.cli import main\n",
                translator_type=VarphiTranslatorCLITarget,
            ),
            {"__name__": "__main__"},
        )

if __name__ == "__main__":
    main()
