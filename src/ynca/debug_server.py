#!/usr/bin/env python3
from __future__ import annotations

import argparse
import logging
from pathlib import Path
import re
import socketserver
import threading
import time
from typing import NamedTuple

from .enums import Input
from .subunits.system import REMOTE_CODE_LENGTH

"""Simple socket server to test without a real YNCA device.

Note that it just responds to commands and does not implement
special interactions like return @RESTRICTED when subunit is not available when turned off.

It is intended to be just enough to test without a real device
"""

RESTRICTED = "@RESTRICTED"
UNDEFINED = "@UNDEFINED"
OK = "OK"


class YncaCommand(NamedTuple):
    subunit: str
    function: str
    value: str


ZONES = ["MAIN", "ZONE2", "ZONE3", "ZONE4"]


def line_to_command(line: str) -> YncaCommand | None:
    match = re.search(r"@(?P<subunit>.+?):(?P<function>.+?)=(?P<value>.*)", line)
    if match is not None:
        subunit = match.group("subunit")
        function = match.group("function")
        value = match.group("value")
        return YncaCommand(subunit, function, value)
    return None


class YncaDataStore:
    def __init__(self) -> None:
        self._store: dict[str, dict[str, str]] = {}
        self._lock = threading.Lock()

    def fill_from_file(self, filename: str) -> None:
        with self._lock:
            print(f"--- Filling store with data from file: {filename}")
            command = None
            with Path(filename).open() as file:
                for line in file:
                    line = line.strip()
                    line = line.rstrip(
                        '",'
                    )  # Strip to be able to use diagnostics output directly

                    # Error values are stored based on command sent on previous line
                    if command and (RESTRICTED in line or UNDEFINED in line):
                        # Only set RESTRICTED or UNDEFINED for non existing entries
                        # Avoids "removal" of valid values that were already stored
                        if (
                            self._get_data(command.subunit, command.function)
                            == UNDEFINED
                        ):
                            self._add_data(
                                command.subunit,
                                command.function,
                                RESTRICTED if RESTRICTED in line else UNDEFINED,
                            )
                    else:
                        command = line_to_command(line)
                        if command is not None and command.value != "?":
                            logging.debug("Adding from file: %s", command)
                            self._add_data(
                                command.subunit, command.function, command.value
                            )

    def _add_data(self, subunit, function, value) -> None:
        if subunit not in self._store:
            self._store[subunit] = {}
        self._store[subunit][function] = value

    def _get_data(self, subunit, function) -> str:
        try:
            return self._store[subunit][function]
        except KeyError:
            return UNDEFINED

    def add_data(self, subunit, function, value) -> None:
        with self._lock:
            return self._add_data(subunit, function, value)

    def get_data(self, subunit, function) -> str:
        with self._lock:
            return self._get_data(subunit, function)

    def get_subunit_functions(self, subunit) -> list[str] | None:
        with self._lock:
            try:
                functions = [f for f in self._store[subunit] if not f.startswith("@")]
            except KeyError:
                return None
            else:
                return functions

    def put_data(self, subunit, function, new_value) -> tuple[str, bool]:
        """Write new value, returns tuple with result and if value changed in case of OK."""
        with self._lock:
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
        "PWRB",
        "SLEEP",
        "VOL",
        "MUTE",
        "ZONEBAVAIL",
        "ZONEBVOL",
        "ZONEBMUTE",
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
        "SPEAKERA",
        "SPEAKERB",
        "DIRMODE",
    ],
    "METAINFO": ["ARTIST", "ALBUM", "SONG", "TRACK", "CHNAME"],
    "RDSINFO": ["RDSPRGTYPE", "RDSPRGSERVICE", "RDSTXTA", "RDSTXTB", "RDSCLOCK"],
}

# The following commands are related
# They report the related command status even when not changed
# The order is obtained from how it works on RX-A810
related_functions_table = {
    "INP": ["INP", "AUDSEL", "DECODERSEL", "ENHANCER", "STRAIGHT", "SOUNDPRG"],
    "SOUNDPRG": ["STRAIGHT", "SOUNDPRG"],
    "PUREDIRMODE": ["PUREDIRMODE", "STRAIGHT"],
    "STRAIGHT": ["STRAIGHT", "SOUNDPRG"],
    "DIRMODE": [
        "STRAIGHT"
    ],  # Note that DIRMODE does not report DIRMODE itself, this is how it behaves on RX-V473
}

INPUT_SUBUNITLIST_MAPPING = [
    (Input.AIRPLAY, ["AIRPLAY"]),
    (Input.BLUETOOTH, ["BT"]),
    (Input.DEEZER, ["DEEZER"]),
    (Input.IPOD, ["IPOD"]),
    (Input.IPOD_USB, ["IPODUSB"]),
    (Input.MCLINK, ["MCLINK"]),
    (Input.NAPSTER, ["NAPSTER"]),
    (Input.NETRADIO, ["NETRADIO"]),
    (Input.PANDORA, ["PANDORA"]),
    (Input.PC, ["PC"]),
    (Input.RHAPSODY, ["RHAP"]),
    (Input.SERVER, ["SERVER"]),
    (Input.SIRIUS, ["SIRIUS"]),
    (Input.SIRIUS_IR, ["SIRIUSIR"]),
    (Input.SIRIUS_XM, ["SIRIUSXM"]),
    (Input.SPOTIFY, ["SPOTIFY"]),
    (Input.TIDAL, ["TIDAL"]),
    (Input.TUNER, ["TUN", "DAB"]),
    (Input.UAW, ["UAW"]),
    (Input.USB, ["USB"]),
]


class YncaCommandHandler(socketserver.StreamRequestHandler):
    """The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    timeout = 40  # Receiver disconnects after 40 seconds of no traffic

    def __init__(self, request, client_address, server: YncaServer) -> None:
        self.store = server.store
        self.disconnect_after_receiving_num_commands = (
            server.disconnect_after_receiving_num_commands
        )
        self.disconnect_after_sending_num_commands = (
            server.disconnect_after_sending_num_commands
        )
        self._commands_sent = 0
        self._elapsedtime_thread: threading.Thread | None = None
        self._elapsedtime_thread_stop = threading.Event()
        super().__init__(request, client_address, server)

    def _start_elapsedtime_thread(self) -> None:
        self._elapsedtime_thread_stop.clear()
        thread = threading.Thread(target=self._elapsedtime_worker)
        thread.daemon = True
        thread.start()
        self._elapsedtime_thread = thread

    def _stop_elapsedtime_thread(self) -> None:
        self._elapsedtime_thread_stop.set()
        if self._elapsedtime_thread:
            self._elapsedtime_thread.join(timeout=2)
        self._elapsedtime_thread = None

    def _elapsedtime_worker(self) -> None:
        while not self._elapsedtime_thread_stop.is_set():
            time.sleep(1)
            for zone in ZONES:
                input_subunit = self.get_active_input_subunit_for_zone(zone)
                if input_subunit:
                    elapsedtime = self.store.get_data(input_subunit, "ELAPSEDTIME")
                    playbackinfo = self.store.get_data(input_subunit, "PLAYBACKINFO")

                    # Only update if playing and elapsedtime is supported
                    if (
                        playbackinfo != "Play"
                        or elapsedtime == ""
                        or elapsedtime.startswith("@")
                    ):
                        continue

                    try:
                        mins, secs = map(int, elapsedtime.split(":"))
                        elapsed_seconds = mins * 60 + secs + 1
                    except ValueError:
                        logging.exception("Error parsing elapsedtime")
                        continue

                    totaltime = self.store.get_data(input_subunit, "TOTALTIME")
                    if totaltime and not totaltime.startswith("@"):
                        try:
                            mins, secs = map(int, totaltime.split(":"))
                            totaltime_seconds = mins * 60 + secs
                        except ValueError:
                            logging.exception("Error parsing totaltime")
                            totaltime_seconds = None
                    else:
                        totaltime_seconds = None

                    if (
                        totaltime_seconds is not None
                        and elapsed_seconds > totaltime_seconds
                    ):
                        elapsed_seconds = 0

                    elapsedtime = f"{elapsed_seconds // 60}:{elapsed_seconds % 60:02d}"

                    (_, changed) = self.store.put_data(
                        input_subunit, "ELAPSEDTIME", elapsedtime
                    )
                    if changed:
                        self._send_ynca_value(input_subunit, "ELAPSEDTIME", elapsedtime)

    def _write_line(self, line: str) -> None:
        print(f"Send - {line}")
        line += "\r\n"
        self.wfile.write(line.encode("utf-8"))
        self._commands_sent += 1

    def _send_stored_value_no_error(self, subunit, function) -> str | None:
        """Send the value that is stored, returns the value or None if it did not exist."""
        return self._send_stored_value_or_error(
            subunit, function, skip_error_response=True
        )

    def _send_stored_value_or_error(
        self, subunit, function, skip_error_response=False
    ) -> str | None:
        """Send the value that is stored, returns the value or None if it did not exist."""
        value = self.store.get_data(subunit, function)
        if value.startswith("@"):
            if not skip_error_response:
                self._send_ynca_error(value)
            return None
        self._send_ynca_value(subunit, function, value)
        return value

    def _send_ynca_value(self, subunit, function, value) -> None:
        """Just formats and send the value."""
        self._write_line(f"@{subunit}:{function}={value}")

    def _send_ynca_error(self, error) -> None:
        """Just formats and send the value."""
        self._write_line(error)

    def handle_get(self, subunit, function) -> None:
        """Handle (multi)response(s) for GET."""
        response_functions = multiresponse_functions_table.get(function)

        if response_functions is None:
            self._handle_get(subunit, function, suppress_error_response=False)
            return

        # Multiple responses
        before = self._commands_sent
        for response_function in response_functions:
            self._handle_get(subunit, response_function, suppress_error_response=True)
        if self._commands_sent == before:
            # No responses so apparently not supported
            self._send_ynca_error(UNDEFINED)

    def _handle_get(self, subunit, function, suppress_error_response=False) -> None:
        """Get one value and writes the response to the socket."""
        # SYS:INPNAME returns all inputnames
        if subunit == "SYS" and function == "INPNAME":
            sys_values = self.store._store["SYS"]
            for key in sys_values:
                if key.startswith("INPNAME") and key != "INPNAME":
                    self._send_stored_value_no_error(subunit, key)

            return
        # SCENENAME returns all scenenames
        if function == "SCENENAME":
            response_sent = False
            subunit_values = self.store._store[subunit]
            for key in subunit_values:
                if (
                    key.startswith("SCENE")
                    and key.endswith("NAME")
                    and key != "SCENENAME"
                ):
                    self._send_stored_value_no_error(subunit, key)
                    response_sent = True
            if not response_sent:
                self._send_ynca_error(UNDEFINED)
            return
        if function == "DIRMODE":
            # DIRMODE is special, it also returns STRAIGHT when it is On, but not when Off (at least on RX-V473)
            if value := self._send_stored_value_or_error(
                subunit, function, skip_error_response=suppress_error_response
            ):
                if value == "On":
                    # MUST use _handle_get since we need to send the overridden value instead of the real one
                    self._handle_get(
                        subunit,
                        "STRAIGHT",
                        suppress_error_response=suppress_error_response,
                    )
            return
        if function == "STRAIGHT":
            # STRAIGHT gets overridden to ON when (PURE)DIRMODE is ON
            # When (PURE)DIRMODE is disabled again the original value is valid again.
            if (
                self.store.get_data(subunit, "DIRMODE") == "On"
                or self.store.get_data(subunit, "PUREDIRMODE") == "On"
            ):
                self._send_ynca_value(subunit, function, "On")
                return

        # Default case for sending response
        self._send_stored_value_or_error(
            subunit, function, skip_error_response=suppress_error_response
        )

    def handle_put(self, subunit, function, value) -> None:

        model = self.store.get_data("SYS", "MODELNAME")

        # Just eat remote codes as they don't give responses
        # unless not supported, but can not really check
        if subunit == "SYS" and function == "REMOTECODE":
            if len(value) != REMOTE_CODE_LENGTH:
                self._send_ynca_error(UNDEFINED)
            return

        # MEM does not seem to generate a response
        # assume it was supported for the subunit, so no error message
        if function == "MEM":
            return

        # Assume ZONEBVOL is independant of VOL
        if (function in ("VOL", "ZONEBVOL")) and (value.startswith(("Up", "Down"))):
            # Need to handle Up/Down as it would otherwise overwrite the VOL value wtih text Up/Down
            up = value.startswith("Up")

            parts = value.split(" ")
            amount = 0.5 if len(parts) == 1 else (int(parts[1]))

            value = float(self.store.get_data(subunit, function))
            value = str(value + (amount * (1 if up else -1)))

        # CX-A5100 uses "One" instead of "Single"; others use "Single" instead of "One"
        if function == "REPEAT" and (
            (model == "CX-A5100" and value == "Single")
            or (model != "CX-A5100" and value == "One")
        ):
            self._send_ynca_error(UNDEFINED)
            return

        previous_input = None
        if function == "INP":
            previous_input = self.store.get_data(subunit, function)

        # Store new value, will handle errors for unsupported functions
        result = self.store.put_data(subunit, function, value)

        # Response for PLAYBACK is PLAYBACKINFO and other special handling
        if function == "PLAYBACK":
            function = "PLAYBACKINFO"

            # Not for Fwd or others as they are not a state
            if value not in ["Play", "Pause", "Stop"]:
                return

            # When received on a Zone the response is on INP subunit
            if subunit in ZONES:
                subunit = self.get_active_input_subunit_for_zone(subunit)

            result = self.store.put_data(subunit, function, value)

        # This does not seem to be true always, see later logs in the linked issue
        # if (function in ("SHUFFLE", "REPEAT")) and (subunit in ("TIDAL", "DEEZER")):
        #     # TIDAL and probably Deezer (on CX-A5100 at least) does not return response for Shuffle or Repeat changes
        #     # See logs in https://github.com/mvdwetering/yamaha_ynca/issues/441
        #     return

        if result[0].startswith("@"):
            self._send_ynca_error(result[0])
        elif result[1]:  # Value change so send a report

            # Send (possibly multiple) responses
            if response_functions := related_functions_table.get(function):
                for response_function in response_functions:
                    related_response_value = self.store.get_data(
                        subunit, response_function
                    )
                    if related_response_value is not UNDEFINED:
                        self._send_ynca_value(
                            subunit, response_function, related_response_value
                        )
            else:
                self._send_ynca_value(subunit, function, value)

            # Special handling for PWR
            if function in ("PWR", "PWRB"):
                self._handle_power_change(subunit, function, value)

            # When changing inputs send updates for new input
            if function == "INP":
                self._handle_input_change(subunit, value, previous_input)

            if function == "PLAYBACKINFO":
                self._handle_playbackinfo_change(subunit, value)

    def _handle_playbackinfo_change(self, subunit, new_playbackinfo_value) -> None:
        # Make sure there is reasonable metadata when changing playback state
        if subunit in ZONES:
            subunit = self.get_active_input_subunit_for_zone(subunit)

        def update_function(function, fallback_value) -> None:
            value = self.store.get_data(subunit, function)
            if value != UNDEFINED:
                value = (
                    "" if new_playbackinfo_value == "Stop" else value or fallback_value
                )
                (_, changed) = self.store.put_data(subunit, function, value)
                if changed:
                    self._send_ynca_value(subunit, function, value)

        update_function("ALBUM", "Album Title")
        update_function("ARTIST", "Artist Name")
        update_function("SONG", "Song Title")
        update_function("TRACK", "Track Title")
        update_function("ELAPSEDTIME", "0:00")
        update_function("TOTALTIME", "1:23")

    def _handle_input_change(
        self, zone_subunit, new_input_value, previous_input_value
    ) -> None:
        if zone_subunit not in ZONES:
            return

        new_input_used_on_other_zone = False
        previous_input_used_on_other_zone = False
        for zone in ZONES:
            if (
                zone != zone_subunit
                and self.store.get_data(zone, "INP") == new_input_value
                and self.store.get_data(zone, "PWR") == "On"
            ):
                new_input_used_on_other_zone = True
            if (
                self.store.get_data(zone, "INP") == previous_input_value
                and self.store.get_data(zone, "PWR") == "On"
            ):
                previous_input_used_on_other_zone = True

        logging.debug(
            "Input changed on %s changed to %s, new value active on other zone %s, previous value active on other zone %s",
            zone_subunit,
            new_input_value,
            new_input_used_on_other_zone,
            previous_input_used_on_other_zone,
        )

        # Real receiver only sends update when input is not active at all
        # So it is not really when input changes but when subunit becomes active
        if not previous_input_used_on_other_zone:
            if previous_input_subunit := self.get_subunit_for_input(
                previous_input_value
            ):
                logging.debug(
                    "Input changed, previous_input_subunit %s is not active anymore",
                    previous_input_subunit,
                )
                self.store.put_data(previous_input_subunit, "AVAIL", "Not Ready")
                self._send_ynca_value(previous_input_subunit, "AVAIL", "Not Ready")

        if not new_input_used_on_other_zone:
            new_input_subunit = self.get_active_input_subunit_for_zone(zone_subunit)
            logging.debug(
                "Input changed, new_input_subunit is now: %s", new_input_subunit
            )
            self.store.put_data(new_input_subunit, "AVAIL", "Ready")

            if subunit_functions := self.store.get_subunit_functions(new_input_subunit):
                logging.debug(
                    "Input changed, send update for subunit functions: %s",
                    subunit_functions,
                )
                for subunit_function in subunit_functions:
                    subunit_function_value = self.store.get_data(
                        new_input_subunit, subunit_function
                    )
                    if not subunit_function_value.startswith(
                        "@"
                    ):  # Errors start with @
                        self._send_ynca_value(
                            new_input_subunit, subunit_function, subunit_function_value
                        )

    def _handle_power_change(self, subunit, function, value) -> None:
        if subunit == "SYS":
            # Setting PWR on SYS impacts Zone PWR
            for zone in ZONES:
                result = self.store.put_data(zone, function, value)
                if result[1]:
                    self._send_ynca_value(zone, function, value)
            result = self.store.put_data("MAIN", "PWRB", value)
            if result[1]:
                self._send_ynca_value("MAIN", "PWRB", value)
        elif subunit in ZONES:
            # Setting PWR on a ZONE can influence SYS overall PWR
            sys_is_on = False
            for zone in ZONES:
                zone_is_on = self.store.get_data(zone, function)
                if zone_is_on != UNDEFINED:
                    sys_is_on |= zone_is_on == "On"

            zoneb_is_on = self.store.get_data("MAIN", function)
            if zoneb_is_on != UNDEFINED:
                sys_is_on |= zoneb_is_on == "On"

            sys_on_value = "On" if sys_is_on else "Standby"
            result = self.store.put_data("SYS", function, sys_on_value)
            if result[1]:
                self._send_ynca_value("SYS", function, sys_on_value)

    def get_active_input_subunit_for_zone(self, zone_subunit) -> str | None:
        try:
            return next(
                m[1][0]
                for m in INPUT_SUBUNITLIST_MAPPING
                if m[0].value == self.store.get_data(zone_subunit, "INP")
            )
        except StopIteration:
            return None

    def get_subunit_for_input(self, input_) -> str | None:
        for m in INPUT_SUBUNITLIST_MAPPING:
            (subunit_input, zone_subunitlist) = m
            if subunit_input == input_:
                for zone_subunit in zone_subunitlist:
                    if self.store.get_data(zone_subunit, "AVAIL") is not UNDEFINED:
                        return zone_subunit
        return None

    def handle(self) -> None:
        self._start_elapsedtime_thread()
        # self.rfile is a file-like object created by the handler;
        # we can now use e.g. readline() instead of raw recv() calls
        #
        # Note that the connection is closed when this handler returns!

        commands_received = 0

        print(f"--- Client connected from: {self.client_address[0]}")
        try:
            while True:
                try:
                    bytes_line = self.rfile.readline()
                    if bytes_line == b"":
                        print("--- Client disconnected")
                        return
                except TimeoutError:
                    print("--- Disconnecting client because of timeout")
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
                        self.handle_put(
                            command.subunit, command.function, command.value
                        )

                commands_received += 1
                if (
                    self.disconnect_after_receiving_num_commands is not None
                    and commands_received
                    >= self.disconnect_after_receiving_num_commands
                ):
                    print(
                        f"--- Disconnecting because of `disconnect_after_receiving_num_commands` limit {self.disconnect_after_receiving_num_commands} reached"
                    )
                    return

                if (
                    self.disconnect_after_sending_num_commands is not None
                    and self._commands_sent
                    >= self.disconnect_after_sending_num_commands
                ):
                    print(
                        "--- Disconnecting because of `disconnect_after_sending_num_commands` {self.disconnect_after_sending_num_commands} limit reached"
                    )
                    return
        finally:
            self._stop_elapsedtime_thread()
            # While not technically already waiting for connections
            # it is nice to have a print indicating the server is ready
            print("--- Waiting for connections")


class YncaServer(socketserver.TCPServer):
    def __init__(
        self,
        server_address: tuple[str, int],
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


def main(args) -> None:
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
        help="Host interface to bind to, default is 0.0.0.0 for all interfaces",
        default="0.0.0.0",  # noqa: S104
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
