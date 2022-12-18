#!/usr/bin/env python3
import logging
import re
import sys

from .connection import YncaConnection, YncaProtocolStatus

PROMPT = ">> "


def delete_prompt():
    print("\b" * len(PROMPT), end="")  # \b is backspace


def print_prompt():
    print(PROMPT, end="", flush=True)


def YncaTerminal(serial_url: str):
    """
    With the YNCA terminal you can manually send YNCA commands to a receiver.
    This is useful to figure out what a command does.

    Use ? as <value> to GET the value.
    Type 'exit' or 'quit' to exit.

    Command format: @<subunit>:<function>=<value>
    Examples:
      @SYS:MODELNAME=?
      @MAIN:VOL=-24
    """

    def output_response(status, subunit, function, value):
        delete_prompt()

        if status is YncaProtocolStatus.OK:
            print(f"Received: {status.name} @{subunit}:{function}={value}")
        else:
            print(f"Received: @{status.name}")

        print_prompt()

    def disconnected_callback():
        print("\n *** Connection lost, will attempt to reconnect on next command ***")
        print_prompt()

    print(YncaTerminal.__doc__)

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
        exit(1)

    YncaTerminal(sys.argv[1])

    print("Done")
