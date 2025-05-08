#!/usr/bin/env python3

import argparse
import logging
from pathlib import Path
import re
import sys
import threading
import time

from ynca import YncaConnection, YncaProtocolStatus

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Execute YNCA commands from a file.")

    parser.add_argument(
        "serial_url",
        help="Can be a devicename like /dev/ttyUSB0 or COM3 for serial or use socket://<ip-or-host>:50000 IP based connections.",
    )
    parser.add_argument(
        "commandfile",
        help="File with a command per line.",
    )
    parser.add_argument(
        "--outputfile",
        help="Optional name of output file.",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level="DEBUG", format="%(message)s", filename=args.outputfile, filemode="w"
    )

    print("Setup connection")

    sem = threading.Semaphore(0)

    def on_disconnect() -> None:
        sem.release()

    def message_received(
        _status: YncaProtocolStatus,
        _subunit: str | None,
        function_: str | None,
        _value: str | None,
    ) -> None:
        if function_ == "VERSION":
            sem.release()

    connection = YncaConnection.create_from_serial_url(args.serial_url)
    try:
        connection.connect(on_disconnect)
    except Exception as e:  # noqa: BLE001
        print(f"** Connection error: {e}")
        sys.exit(1)
    connection.register_message_callback(message_received)

    time.sleep(1)
    print()
    print("*" * 30)
    print("Submitting commands")
    print(
        "Note that there is 100ms inbetween commands, with lots of commands it can take a while"
    )
    print("*" * 30)
    print()
    time.sleep(1)

    commands_sent = 0
    with Path(args.commandfile).open() as commandfile:
        for line in commandfile:
            line = re.sub(r"#.*", "", line)  # noqa: PLW2901
            line = line.strip()  # noqa: PLW2901

            match = re.match(r"@(?P<subunit>.+?):(?P<function>.+?)=(?P<value>.*)", line)
            if match is not None:
                subunit = match.group("subunit")
                function = match.group("function")
                value = match.group("value")

                if function == "VERSION":
                    logging.info("Skipping VERSION command as it is used as end marker")
                    continue

                connection.raw(f"@{subunit}:{function}={value}")
                commands_sent += 1

    # Send command with guarenteed response as done indication
    connection.raw("@SYS:VERSION=?")
    sem.acquire()

    print("Done")
    connection.close()
