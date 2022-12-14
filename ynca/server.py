#!/usr/bin/env python3
from __future__ import annotations

"""
Simple socket server to test without a real YNCA device

Note that it just responds to commands and does not implement
special interactions like return @RESTRICTED when subunit is not available when turned off.

It is intended to be just enough to test without a real device
"""

import argparse
import logging
import re
import socketserver
from collections import namedtuple
from typing import Dict, Tuple

RESTRICTED = "@RESTRICTED"
UNDEFINED = "@UNDEFINED"
OK = "OK"

YncaCommand = namedtuple("YncaCommand", ["subunit", "function", "value"])


def line_to_command(line):
    match = re.search(r"@(?P<subunit>.+?):(?P<function>.+?)=(?P<value>.*)", line)
    if match is not None:
        subunit = match.group("subunit")
        function = match.group("function")
        value = match.group("value")
        return YncaCommand(subunit, function, value)
    return None


class YncaDataStore:
    def __init__(self) -> None:
        self._store: Dict[str, Dict[str, str]] = {}

    def fill_from_file(self, filename):
        print(f"--- Filling store with data from file: {filename}")
        command = None
        with open(filename) as file:
            for line in file:
                line = line.strip()
                line = line.rstrip(
                    '",'
                )  # Strip to be able to use diagnotics output directly

                # Error values are stored based on command sent on previous line
                if command and (RESTRICTED in line or UNDEFINED in line):
                    # Only set RESTRICTED or UNDEFINED for non existing entries
                    # Avoids "removal" of valid values that were already stored
                    if self.get_data(command.subunit, command.function) == UNDEFINED:
                        self.add_data(
                            command.subunit,
                            command.function,
                            RESTRICTED if RESTRICTED in line else UNDEFINED,
                        )
                else:
                    command = line_to_command(line)
                    if command is not None and command.value != "?":
                        self.add_data(command.subunit, command.function, command.value)

    def add_data(self, subunit, function, value):
        if subunit not in self._store:
            self._store[subunit] = {}
        self._store[subunit][function] = value

    def get_data(self, subunit, function):
        try:
            value = self._store[subunit][function]
        except KeyError:
            return UNDEFINED
        return value

    def put_data(self, subunit, function, new_value):
        """Write new value, returns tuple with result and if value changed in case of OK"""
        try:
            if subunit in self._store:
                old_value = self._store[subunit][function]
                if old_value is None or new_value not in [UNDEFINED, RESTRICTED]:
                    self._store[subunit][function] = new_value
                return (OK, old_value != new_value)
        except KeyError:
            return (UNDEFINED, False)
        return (RESTRICTED, False)


multiresponse_functions_table = {
    "BASIC": [
        "PWR",
        "SLEEP",
        "VOL",
        "MUTE",
        "INP",
        "STRAIGHT",
        "ENHANCER",
        "SOUNDPRG",
        "TONEBASS",
        "TONETREBLE",
        "3DCINEMA",
        "PUREDIRMODE",
        "SPBASS",
        "SPTREBLE",
        "EXBASS",
        "ADAPTIVEDRC",
        "DIALOGUELVL",
        "DTSDIALOGUECONTROL",
    ],
    "METAINFO": ["ARTIST", "ALBUM", "SONG", "CHNAME"],
    "RDSINFO": ["RDSPRGTYPE", "RDSPRGSERVICE", "RDSTXTA", "RDSTXTB", "RDSCLOCK"],
}


class YncaCommandHandler(socketserver.StreamRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def __init__(self, request, client_address, server: YncaServer):
        self.store = server.store
        self.disconnect_after_receiving_num_commands = (
            server.disconnect_after_receiving_num_commands
        )
        self.disconnect_after_sending_num_commands = (
            server.disconnect_after_sending_num_commands
        )
        self._commands_sent = 0
        super().__init__(request, client_address, server)

    def write_line(self, line: str):
        print(f"Send - {line}")
        line += "\r\n"
        self.wfile.write(line.encode("utf-8"))
        self._commands_sent += 1

    def handle_get(self, subunit, function, skip_error_response=False):

        # Some GET commands result in multple reponses
        if subunit == "SYS" and function == "INPNAME":
            sys_values = self.store._store["SYS"]
            for key in sys_values.keys():
                if key.startswith("INPNAME") and key != "INPNAME":
                    self.handle_get(subunit, key)
            return
        elif response_functions := multiresponse_functions_table.get(function, None):
            before = self._commands_sent
            for response_function in response_functions:
                self.handle_get(subunit, response_function, skip_error_response=True)
            if self._commands_sent == before:
                # No responses so apparently not supported
                self.write_line(UNDEFINED)
            return
        elif function == "SCENENAME":
            response_sent = False
            subunit_values = self.store._store[subunit]
            for key in subunit_values.keys():
                if (
                    key.startswith("SCENE")
                    and key.endswith("NAME")
                    and key != "SCENENAME"
                ):
                    self.handle_get(subunit, key)
                    response_sent = True
            if not response_sent:
                self.write_line(UNDEFINED)
            return

        # Standard handling
        value = self.store.get_data(subunit, function)
        if value.startswith("@"):
            if not skip_error_response:
                self.write_line(value)
        else:
            self.write_line(f"@{subunit}:{function}={value}")

    def handle_put(self, subunit, function, value):
        if function == "VOL" and value.startswith("Up") or value.startswith("Down"):
            # Need to handle Up/Down as it would otherwise overwrite the VOL value wtih text Up/Down
            up = value.startswith("Up")

            parts = value.split(" ")
            amount = 0.5 if len(parts) == 1 else (int(parts[1]))

            value = float(self.store.get_data(subunit, function))
            value = str(value + (amount * (1 if up else -1)))
        result = self.store.put_data(subunit, function, value)
        if result[0].startswith("@"):
            self.write_line(result[0])
        elif result[1]:
            # Value change so send a report
            self.write_line(f"@{subunit}:{function}={value}")

    def handle(self):
        # self.rfile is a file-like object created by the handler;
        # we can now use e.g. readline() instead of raw recv() calls
        #
        # Note that the connection is closed when this handler returns!

        commands_received = 0

        print(f"--- Client connected from: {self.client_address[0]}")
        while True:
            bytes_line = self.rfile.readline()
            if bytes_line == b"":
                print("--- Client disconnected")
                print("--- Waiting for connections")
                return

            bytes_line = bytes_line.strip()
            line = bytes_line.decode(
                "utf-8"
            )  # Note that YNCA spec says in some places that text can be ASCII, Latin-1 or UTF-8 without a way to indicate what it is :/ UTF-8 seems to work fine for now
            print(f"Recv - {line}")

            command = line_to_command(line)
            if command is not None:
                if command.value == "?":
                    self.handle_get(command.subunit, command.function)
                else:
                    self.handle_put(command.subunit, command.function, command.value)

            commands_received += 1
            if (
                self.disconnect_after_receiving_num_commands is not None
                and commands_received >= self.disconnect_after_receiving_num_commands
            ):
                print(
                    f"--- Disconnecting because of `disconnect_after_receiving_num_commands` limit {self.disconnect_after_receiving_num_commands} reached"
                )
                return

            if (
                self.disconnect_after_sending_num_commands is not None
                and self._commands_sent >= self.disconnect_after_sending_num_commands
            ):
                print(
                    "--- Disconnecting because of `disconnect_after_sending_num_commands` {self.disconnect_after_sending_num_commands} limit reached"
                )
                return


class YncaServer(socketserver.TCPServer):
    def __init__(
        self,
        server_address: Tuple[str, int],
        initfile=None,
        disconnect_after_receiving_num_commands=None,
        disconnect_after_sending_num_commands=None,
    ) -> None:
        self.allow_reuse_address = True
        super().__init__(server_address, YncaCommandHandler)

        self.store = YncaDataStore()
        self.disconnect_after_receiving_num_commands = (
            disconnect_after_receiving_num_commands
        )
        self.disconnect_after_sending_num_commands = (
            disconnect_after_sending_num_commands
        )

        if disconnect_after_receiving_num_commands is not None:
            print(
                f"--- Each connection will be disconnected after receiving {disconnect_after_receiving_num_commands} commands!"
            )
        if disconnect_after_sending_num_commands is not None:
            print(
                f"--- Each connection will be disconnected after sending {disconnect_after_sending_num_commands} commands!"
            )

        if initfile:
            self.store.fill_from_file(initfile)
        else:
            # Minimum needed data to satisfy example.py script
            self.store.add_data("SYS", "MODELNAME", "ModelName")
            self.store.add_data("SYS", "VERSION", "Version")
            self.store.add_data("MAIN", "AVAIL", "Not ready")
            self.store.add_data("MAIN", "VOL", "0.0")
            self.store.add_data("MAIN", "ZONENAME", "MainZone")
            self.store.add_data("ZONE2", "AVAIL", "Not ready")
            self.store.add_data("ZONE2", "ZONENAME", "Zone2Name")


def main(args):
    print(__doc__)

    with YncaServer(
        (args.host, args.port),
        args.initfile,
        args.disconnect_after_receiving_num_commands,
        args.disconnect_after_sending_num_commands,
    ) as server:
        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C

        print("--- Waiting for connections")

        server.timeout = None
        server.serve_forever()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="YNCA server to emulate a device for testing."
    )

    parser.add_argument(
        "initfile",
        help="File to use to initialize the YncaDatastore. Needs to contain Ynca command logging in format `@SUBUNIT:FUNCTION=VALUE`. E.g. output of example script with loglevel DEBUG.",
    )

    parser.add_argument(
        "--host",
        help="Host interface to bind to, default is localhost",
        default="localhost",
    )
    parser.add_argument(
        "--port",
        help="Port to use, default is the standard port 50000",
        default=50000,
        type=int,
    )
    parser.add_argument(
        "--disconnect_after_receiving_num_commands",
        help="Disconnect after receiving this amount of commands, useful for testing disconnects",
        default=None,
        type=int,
    )
    parser.add_argument(
        "--disconnect_after_sending_num_commands",
        help="Disconnect after sending this amount of commands, useful for testing disconnects",
        default=None,
        type=int,
    )
    parser.add_argument(
        "--loglevel",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Define loglevel, default is INFO.",
    )

    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel)

    main(args)
