#!/usr/bin/env python3
import logging
import re
import sys

from .connection import YncaConnection


def terminal(serial_url: str):
    """
    With the YNCA terminal you can manually send YNCA commands to a receiver.
    This is useful to figure out what a command does.

    Use ? as <value> to GET the value.
    Type 'exit' to exit.

    Command format: @<subunit>:<function>=<value>
    Examples:
      @SYS:MODELNAME=?
      @MAIN:VOL=-24
    """

    def output_response(status, subunit, function, value):
        print(f"Response: {status.name} @{subunit}:{function}={value}")

    def disconnected_callback():
        print("\n *** Connection lost, will attempt to reconnect on next command ***")

    print(terminal.__doc__)

    connection = YncaConnection(serial_url)
    connection.register_message_callback(output_response)
    connection.connect(disconnected_callback)
    quit_ = False
    while not quit_:
        command = input(">> ")

        if command == "exit":
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

    port = "/dev/ttyUSB0"
    if len(sys.argv) > 1:
        port = sys.argv[1]

    terminal(port)

    print("Done")
