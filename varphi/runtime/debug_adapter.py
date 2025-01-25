"""varphi/runtime/debug_adapter.py"""
import sys
import json

from .types import Tape, TapeCharacter, State, DebugAdapterTuringMachine
from .exceptions import (
    VarphiInvalidTapeCharacterException,
    VarphiNoTallyException,
    VarphiTuringMachineHaltedException,
)
from .common import debug_view_tape_head


def get_tape_from_string(string: str) -> Tape:
    """Given a string with 1s and 0s, construct and return a tape."""
    # First strip all '0's
    string = string.strip("0")
    if len(string) == 0 or string[0] != "1":
        raise VarphiNoTallyException(
            "Error: Input tape must contain at least one tally (1)."
        )
    initial_characters = []
    for input_character in string:
        if input_character == "0":
            initial_characters.append(TapeCharacter.BLANK)
        elif input_character == "1":
            initial_characters.append(TapeCharacter.TALLY)
        else:
            raise VarphiInvalidTapeCharacterException(
                f"Error: Invalid tape character (ASCII #{ord(input_character)})."
            )
    return Tape(initial_characters)


class VarphiDebugAdapter:
    """A class representing a debug adapter for the Varphi programming language."""
    initial_state: State
    turing_machine: DebugAdapterTuringMachine | None
    no_debug: bool | None
    breakpoints: set[int]
    source_path: str | None
    current_line_number: int

    def __init__(self, initial_state: State):
        self.initial_state = initial_state
        self.breakpoints = set()
        self.current_line_number = -1

    def loop(self):
        """The debug adapter loop."""
        try:
            while True:
                sys.stdin.buffer.read(16)  # Skip "Content-Length: "
                content_length_string = ""
                character = sys.stdin.buffer.read(1)
                while character != b"\r":
                    content_length_string += chr(character[0])
                    character = sys.stdin.buffer.read(1)
                # Skip the remaining \n\r\n
                sys.stdin.buffer.read(3)
                content_length = int(content_length_string)
                content_part = sys.stdin.buffer.read(content_length).decode()
                self.parse_input(content_part)
        except Exception:  # pylint: disable=W0718
            import traceback  # pylint: disable=C0415

            exited_event = {}
            exited_event["exitCode"] = 0
            self.send_event("exited", exited_event)
            output_event = {}
            output_event["category"] = "stderr"
            output_event["output"] = str(traceback.format_exc())
            self.send_event("output", output_event)
            terminated_event = {}
            self.send_event("terminated", terminated_event)
            sys.exit(-1)

    def send_body_part(self, body_part: dict) -> None:
        """Send a message to the debug adapter client.."""
        body_part_string = json.dumps(body_part)
        content_length = str(len(body_part_string))
        sys.stdout.buffer.write(b"Content-Length: ")
        sys.stdout.buffer.write(content_length.encode("utf-8"))
        sys.stdout.buffer.write(b"\r\n\r\n")
        sys.stdout.buffer.write(body_part_string.encode("utf-8"))
        sys.stdout.flush()

    def send_response(  # pylint: disable=R0913 R0917
        self,
        request_seq: int,
        success: bool,
        command: str,
        message: str | None = None,
        body: dict | None = None,
    ) -> None:
        """Send a response to the debug adapter client."""
        body_part = {}
        body_part["type"] = "response"
        body_part["request_seq"] = request_seq
        body_part["success"] = success
        body_part["command"] = command
        if message is not None:
            body_part["message"] = message
        if body is not None:
            body_part["body"] = body
        self.send_body_part(body_part)

    def send_event(self, event: str, body: dict | None = None) -> None:
        """Send an event to the debug adapter client."""
        body_part = {}
        body_part["type"] = "event"
        body_part["event"] = event
        if body is not None:
            body_part["body"] = body
        self.send_body_part(body_part)

    def parse_input(self, input_json_string: str):
        """Parse and handle a message from the debug adapter client."""
        json_input = json.loads(input_json_string)
        if json_input["type"] == "request":
            self.handle_request(json_input)

    def handle_request(self, json_input):  # pylint: disable=R0912
        """Handle a general request from the debug adapter client."""
        command = json_input["command"]
        if command == "initialize":
            self.handle_initialize_request(json_input)
        if command == "launch":
            self.handle_launch_request(json_input)
        if command == "setBreakpoints":
            self.handle_set_breakpoints_request(json_input)
        if command == "configurationDone":
            self.handle_configuration_done_request(json_input)
        if command == "threads":
            self.handle_threads_request(json_input)
        if command == "stackTrace":
            self.handle_stack_trace_request(json_input)
        if command == "scopes":
            self.handle_scopes_request(json_input)
        if command == "variables":
            self.handle_variables_request(json_input)
        if command == "continue":
            self.handle_continue_request(json_input)
        if command == "next":
            self.handle_next_request(json_input)
        if command == "stepIn":
            self.handle_step_in_request(json_input)
        if command == "stepOut":
            self.handle_step_out_request(json_input)
        if command == "disconnect":
            self.handle_disconnect_request(json_input)

    def handle_initialize_request(self, json_input):
        """Handle an initialize request from the debug adapter client."""
        response_body = {
            "supportsConfigurationDoneRequest": True,
            "supportsSingleThreadExecutionRequests": True,
        }
        self.send_response(json_input["seq"], True, "initialize", None, response_body)
        self.send_event("initialized")

    def handle_set_breakpoints_request(self, json_input):
        """Handle a set breakpoints request from the debug adapter client."""
        response_body = {}
        response_body["breakpoints"] = []
        arguments = json_input["arguments"]
        if "breakpoints" in arguments:
            breakpoints = arguments["breakpoints"]
            for bp in breakpoints:
                breakpoint_line_number = bp["line"]
                self.breakpoints.add(breakpoint_line_number)
                breakpoint_response = {"verified": True}
                response_body["breakpoints"].append(breakpoint_response)

        if "sourceModified" in arguments and arguments["sourceModified"]:
            raise Exception(  # pylint: disable=W0719
                "Error: Source code change detected. Please kindly restart the debugging process."
            )
        self.send_response(
            json_input["seq"], True, "setBreakpoints", None, response_body
        )
        if self.no_debug:
            self.breakpoints = set()

    def handle_launch_request(self, json_input):
        """Handle a launch request from the debug adapter client."""
        arguments = json_input["arguments"]
        if "noDebug" not in arguments:
            raise Exception('Error: Missing argument "noDebug" for Debug Adapter.')  # pylint: disable=W0719
        if "sourcePath" not in arguments:
            raise Exception('Error: Missing argument "sourcePath" for Debug Adapter.')  # pylint: disable=W0719
        if "tape" not in arguments:
            raise Exception('Error: Missing argument "tape" for Debug Adapter.')  # pylint: disable=W0719
        self.no_debug = arguments["noDebug"]
        self.source_path = arguments["sourcePath"]
        input_tape = arguments["tape"]
        self.turing_machine = DebugAdapterTuringMachine(
            get_tape_from_string(input_tape), self.initial_state
        )
        self.send_response(json_input["seq"], True, "launch")

    def handle_configuration_done_request(self, json_input):  # pylint: disable=R0915
        """Handle a configuration done request from the debug adapter client."""
        self.send_response(json_input["seq"], True, "configurationDone")
        if self.no_debug:
            while True:
                try:
                    self.turing_machine.step()
                except VarphiTuringMachineHaltedException:
                    exited_event = {}
                    exited_event["exitCode"] = 0
                    self.send_event("exited", exited_event)
                    output_event = {}
                    output_event["category"] = "console"
                    output_event["output"] = str(self.turing_machine.tape)
                    self.send_event("output", output_event)
                    terminated_event = {}
                    self.send_event("terminated", terminated_event)
                    break
        else:
            if len(self.breakpoints) == 0:
                try:
                    self.current_line_number = (
                        self.turing_machine.determine_next_instruction().line_number
                    )
                    stopped_event = {}
                    stopped_event["reason"] = "step"
                    stopped_event["threadId"] = 1
                    stopped_event["allThreadsStopped"] = True
                    self.send_event("stopped", stopped_event)
                except VarphiTuringMachineHaltedException:
                    exited_event = {}
                    exited_event["exitCode"] = 0
                    self.send_event("exited", exited_event)
                    output_event = {}
                    output_event["category"] = "console"
                    output_event["output"] = str(self.turing_machine.tape)
                    self.send_event("output", output_event)
                    terminated_event = {}
                    self.send_event("terminated", terminated_event)
                    return

            else:
                while True:
                    try:
                        self.current_line_number = (
                            self.turing_machine.determine_next_instruction().line_number
                        )
                        if self.current_line_number in self.breakpoints:
                            stopped_event = {}
                            stopped_event["reason"] = "breakpoint"
                            stopped_event["threadId"] = 1
                            stopped_event["allThreadsStopped"] = True
                            self.send_event("stopped", stopped_event)
                            break
                        self.turing_machine.execute_next_instruction()
                    except VarphiTuringMachineHaltedException:
                        exited_event = {}
                        exited_event["exitCode"] = 0
                        self.send_event("exited", exited_event)
                        output_event = {}
                        output_event["category"] = "console"
                        output_event["output"] = str(self.turing_machine.tape)
                        self.send_event("output", output_event)
                        terminated_event = {}
                        self.send_event("terminated", terminated_event)
                        break

    def handle_threads_request(self, json_input):
        """Handle a threads request from the debug adapter client."""
        response_body = {}
        response_body["threads"] = [{"id": 1, "name": "thread1"}]
        self.send_response(json_input["seq"], True, "threads", None, response_body)

    def handle_stack_trace_request(self, json_input):
        """Handle a stack trace request from the debug adapter client."""
        response_body = {}
        stack_frame = {}
        stack_frame["id"] = 0
        stack_frame["name"] = "source"
        source = {}
        source["name"] = "Varphi Program"
        source["path"] = self.source_path
        stack_frame["source"] = source

        stack_frame["line"] = self.current_line_number
        stack_frame["column"] = 0
        response_body["stackFrames"] = [stack_frame]
        response_body["totalFrames"] = 1
        self.send_response(json_input["seq"], True, "stackTrace", None, response_body)

    def handle_scopes_request(self, json_input):
        """Handle a scopes request from the debug adapter client."""
        scope = {}
        scope["name"] = "Machine Variables"
        scope["variablesReference"] = (
            1  # The tape, the index of the head, the index of zero (first head location), state
        )

        response_body = {}
        response_body["scopes"] = [scope]
        self.send_response(json_input["seq"], True, "scopes", None, response_body)

    def handle_variables_request(self, json_input):
        """Handle a variables request from the debug adapter client."""
        tape_variable = {}
        tape_variable["name"] = "Tape"
        tape_variable["value"] = debug_view_tape_head(
            self.turing_machine.tape, self.turing_machine.head
        )
        tape_variable["variablesReference"] = 0

        head_variable = {}
        head_variable["name"] = "Head"
        head_variable["value"] = str(self.turing_machine.head)
        head_variable["variablesReference"] = 0

        zero_variable = {}
        zero_variable["name"] = "Tape Zero"
        zero_variable["value"] = str(-self.turing_machine.tape._minimum_accessed_index)  # pylint: disable=W0212
        zero_variable["variablesReference"] = 0

        state_variable = {}
        state_variable["name"] = "State"
        state_variable["value"] = str(self.turing_machine.state.name)
        state_variable["variablesReference"] = 0

        response_body = {}
        response_body["variables"] = [
            tape_variable,
            state_variable,
            head_variable,
            zero_variable,
        ]
        self.send_response(json_input["seq"], True, "variables", None, response_body)

    def handle_next_request(self, json_input):
        """Handle a next request from the debug adapter client."""
        try:
            self.turing_machine.execute_next_instruction()
            self.current_line_number = (
                self.turing_machine.determine_next_instruction().line_number
            )
            response_body = {}
            response_body["allThreadsContinued"] = True
            self.send_response(json_input["seq"], True, "next", None, response_body)

            stopped_event = {}
            stopped_event["reason"] = "step"
            stopped_event["threadId"] = 1
            stopped_event["allThreadsStopped"] = True
            self.send_event("stopped", stopped_event)

        except VarphiTuringMachineHaltedException:
            exited_event = {}
            exited_event["exitCode"] = 0
            self.send_event("exited", exited_event)
            output_event = {}
            output_event["category"] = "console"
            output_event["output"] = str(self.turing_machine.tape)
            self.send_event("output", output_event)
            terminated_event = {}
            self.send_event("terminated", terminated_event)

    def handle_step_in_request(self, json_input):
        """Handle a step in request from the debug adapter client."""
        try:
            self.turing_machine.execute_next_instruction()
            self.current_line_number = (
                self.turing_machine.determine_next_instruction().line_number
            )
            response_body = {}
            response_body["allThreadsContinued"] = True
            self.send_response(json_input["seq"], True, "stepIn", None, response_body)

            stopped_event = {}
            stopped_event["reason"] = "step"
            stopped_event["threadId"] = 1
            stopped_event["allThreadsStopped"] = True
            self.send_event("stopped", stopped_event)

        except VarphiTuringMachineHaltedException:
            exited_event = {}
            exited_event["exitCode"] = 0
            self.send_event("exited", exited_event)
            output_event = {}
            output_event["category"] = "console"
            output_event["output"] = str(self.turing_machine.tape)
            self.send_event("output", output_event)
            terminated_event = {}
            self.send_event("terminated", terminated_event)

    def handle_step_out_request(self, json_input):
        """Handle a step out request from the debug adapter client."""
        try:
            self.turing_machine.execute_next_instruction()
            self.current_line_number = (
                self.turing_machine.determine_next_instruction().line_number
            )
            response_body = {}
            response_body["allThreadsContinued"] = True
            self.send_response(json_input["seq"], True, "stepOut", None, response_body)

            stopped_event = {}
            stopped_event["reason"] = "step"
            stopped_event["threadId"] = 1
            stopped_event["allThreadsStopped"] = True
            self.send_event("stopped", stopped_event)

        except VarphiTuringMachineHaltedException:
            exited_event = {}
            exited_event["exitCode"] = 0
            self.send_event("exited", exited_event)
            output_event = {}
            output_event["category"] = "console"
            output_event["output"] = str(self.turing_machine.tape)
            self.send_event("output", output_event)
            terminated_event = {}
            self.send_event("terminated", terminated_event)

    def handle_continue_request(self, json_input):
        """Handle a continue request from the debug adapter client."""
        while True:
            try:
                self.turing_machine.execute_next_instruction()
                self.current_line_number = (
                    self.turing_machine.determine_next_instruction().line_number
                )
                if self.current_line_number in self.breakpoints:
                    response_body = {}
                    response_body["allThreadsContinued"] = True
                    self.send_response(
                        json_input["seq"], True, "continue", None, response_body
                    )
                    stopped_event = {}
                    stopped_event["reason"] = "breakpoint"
                    stopped_event["threadId"] = 1
                    stopped_event["allThreadsStopped"] = True
                    self.send_event("stopped", stopped_event)
                    return
            except VarphiTuringMachineHaltedException:
                exited_event = {}
                exited_event["exitCode"] = 0
                self.send_event("exited", exited_event)
                output_event = {}
                output_event["category"] = "console"
                output_event["output"] = str(self.turing_machine.tape)
                self.send_event("output", output_event)
                terminated_event = {}
                self.send_event("terminated", terminated_event)
                return

    def handle_disconnect_request(self, json_input):
        """Handle a disconnect request from the debug adapter client."""
        self.send_response(json_input["seq"], True, "terminate")


def main(initial_state: State | None):
    """Construct the Turing machine given an initial state and run it.

    Communicates with a debug adapter client.
    """
    VarphiDebugAdapter(initial_state).loop()
