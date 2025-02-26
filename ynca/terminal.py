#!/usr/bin/env python3
import re
import sys

from .connection import YncaConnection, YncaProtocolStatus

PROMPT = ">> "


def delete_prompt() -> None:
    print("\b" * len(PROMPT), end="")  # \b is backspace


def print_prompt() -> None:
    print(PROMPT, end="", flush=True)


def ynca_terminal(serial_url: str) -> None:
    """YNCA Terminal.

    With the YNCA terminal you can manually send YNCA commands to a receiver.
    This is useful to figure out what a command does.

    Note that a receiver only allows 1 YNCA connection at the time!
    When connection gets lost immediately after connecting that
    usually means something else already has a YNCA connection open.

    Type 'exit' or 'quit' to exit.


    Quick reference:

    Command format: @<subunit>:<function>=<value>
    Use ? as <value> to GET the value.

    Examples:
      @SYS:MODELNAME=?
      @MAIN:VOL=-24

    """

    def output_response(
        status: YncaProtocolStatus,
        subunit: str | None,
        function: str | None,
        value: str | None,
    ) -> None:
        delete_prompt()

        if status is YncaProtocolStatus.OK:
            print(f"Received: {status.name} @{subunit}:{function}={value}")
        else:
            print(f"Received: @{status.name}")

        print_prompt()

    def disconnected_callback() -> None:
        print("\n *** Connection lost, will attempt to reconnect on next command ***")
        print_prompt()

    print(ynca_terminal.__doc__)

    connection = YncaConnection(serial_url)
    connection.register_message_callback(output_response)
    connection.connect(disconnected_callback)

    quit_ = False
    while not quit_:
        command = input(PROMPT)

        if command.lower() in ["bye", "done", "exit", "q", "quit"]:
            quit_ = True
        elif command != "":
            match = re.match(
                r"@?(?P<subunit>.+?):(?P<function>.+?)=(?P<value>.+)", command
            )
            if match is not None:
                # Because the connection receives on another thread, there is no use in catching YNCA exceptions here
                # However exceptions will cause the connection to break, re-connect if needed
                if not connection.connected:
                    connection.connect(disconnected_callback)
                connection.put(
                    match.group("subunit"),
                    match.group("function"),
                    match.group("value"),
                )
            else:
                print("Invalid command format")

    connection.close()


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print("Must provide a serial_url parameter like:")
        print("  COM3")
        print("  /dev/ttyUSB0")
        print("  socket://192.168.178.21:50000")
        sys.exit(1)

    ynca_terminal(sys.argv[1])

    print("Done")
