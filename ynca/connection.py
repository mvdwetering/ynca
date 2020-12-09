#!/usr/bin/env python3

import queue
import re
import sys
import threading
import time
import logging
from enum import Enum

import serial
import serial.threaded


logger = logging.getLogger(__name__)


class YncaProtocolStatus(Enum):
    OK = 0
    UNDEFINED = 1
    RESTRICTED = 2


class YncaProtocol(serial.threaded.LineReader):
    # YNCA spec specifies that there should be at least 100 milliseconds between commands
    COMMAND_SPACING = 0.1

    # YNCA spec says standby timeout is 40 seconds, so use a shorter period to be on the safe side
    KEEP_ALIVE_INTERVAL = 30

    def __init__(self):
        super(YncaProtocol, self).__init__()
        self.callback = None
        self._send_queue = None
        self._send_thread = None
        self._last_sent_command = None
        self.connected = False;
        self._keep_alive_pending = False

    def connection_made(self, transport):
        super(YncaProtocol, self).connection_made(transport)

        logger.info("Connected")

        self._send_queue = queue.Queue()
        self._send_thread = threading.Thread(target=self._send_handler)
        self._send_thread.start()

        self.connected = True
        self._keep_alive_pending = False

        # When the device is in low power mode the first command is to wake up and gets lost
        # So send a dummy keep-alive on connect and a real one to make sure keep-alive administration is up-to-date
        self._send_keepalive()
        self._send_keepalive()

    def connection_lost(self, exc):
        self.connected = False;

        logger.info("Connection lost")

        # There seems to be no way to clear a queue so just read all and add the _EXIT command
        try:
            while self._send_queue.get(False):
                pass
        except queue.Empty:
            self._send_queue.put("_EXIT")

        if exc:
            sys.stdout.write(repr(exc))

    def handle_line(self, line):
        ignore = False
        status = YncaProtocolStatus.OK
        subunit = None
        function = None
        value = line  # For the case where the command is invalid so there is some info to debug with

        logger.debug("< {}".format(line))

        if line == "@UNDEFINED":
            status = YncaProtocolStatus.UNDEFINED
            line = self._last_sent_command
        elif line == "@RESTRICTED":
            status = YncaProtocolStatus.RESTRICTED
            line = self._last_sent_command

        match = re.match(r"@(?P<subunit>.+?):(?P<function>.+?)=(?P<value>.*)", line)
        if match is not None:
            subunit = match.group("subunit")
            function = match.group("function")
            value = match.group("value")

            if self._keep_alive_pending and subunit == "SYS" and function == "MODELNAME":
                ignore = True

        self._keep_alive_pending = False

        if not ignore and self.callback is not None:
            self.callback(status, subunit, function, value)

    def _send_keepalive(self):
        self._send_queue.put("_KEEP_ALIVE")

    def _send_handler(self):
        stop = False
        while not stop:
            try:
                message = self._send_queue.get(True, self.KEEP_ALIVE_INTERVAL)

                if message == "_EXIT":
                    stop = True
                elif message == "_KEEP_ALIVE":
                    message = "@SYS:MODELNAME=?"  # This message is suggested by YNCA spec for keep-alive
                    self._keep_alive_pending = True

                if not stop:
                    logger.debug("> {}".format(message))

                    self._last_sent_command = message
                    self.write_line(message)
                    time.sleep(self.COMMAND_SPACING)  # Maintain required command spacing
            except queue.Empty:
                # To avoid random message being eaten because device goes to sleep, keep it alive
                self._send_keepalive()

    def put(self, subunit, funcname, parameter):
        self._send_queue.put(
            '@{subunit}:{funcname}={parameter}'.format(subunit=subunit, funcname=funcname, parameter=parameter))

    def get(self, subunit, funcname):
        self.put(subunit, funcname, '?')


class YncaConnection:
    def __init__(self, serial_url, callback=None):
        """Instantiate a YncaConnection

        serial_url -- Can be a devicename (e.g. /dev/ttyUSB0 or COM3),
                      but also any of supported url handlers by pyserial
                      https://pyserial.readthedocs.io/en/latest/url_handlers.html
                      This allows to setup IP connections with socket://ip:50000
                      or select a specific usb-2-serial with hwgrep:// which is
                      useful when the links to ttyUSB# change randomly.

        callback -- Callback to be called when changes happen. Should be defined as
                    `def my_callback(status, subunit, function, value):`

        """
        self._port = serial_url
        self.callback = callback
        self._serial = None
        self._readerthread = None
        self._protocol = None

    def connect(self):
        if not self._serial:
            self._serial = serial.serial_for_url(self._port)
        self._readerthread = serial.threaded.ReaderThread(self._serial, YncaProtocol)
        self._readerthread.start()
        dummy, self._protocol = self._readerthread.connect()
        self._protocol.callback = self.callback

    def disconnect(self):
        self._readerthread.close()

    def put(self, subunit, funcname, parameter):
        self._protocol.put(subunit, funcname, parameter)

    def get(self, subunit, funcname):
        self._protocol.get(subunit, funcname)

    @property
    def connected(self):
        return self._protocol.connected


def ynca_console(serial_port):
    """
    With the YNCA console you can manually send YNCA commands to a receiver.
    This is useful to figure out what a command does.

    Use ? as <value> to GET the value.
    Type 'quit' to exit.

    Command format: @<subunit>:<function>=<value>
    Example: @SYS:MODELNAME=?
    """

    def output_response(status, subunit, function, value):
        print("Response: {3} {0}:{1}={2}".format(subunit, function, value, status.name))

    print(ynca_console.__doc__)

    connection = YncaConnection(serial_port, output_response)
    connection.connect()
    quit_ = False
    while not quit_:
        command = input('>> ')

        if command == "quit":
            quit_ = True
        elif command != "":
            match = re.match(r"@?(?P<subunit>.+?):(?P<function>.+?)=(?P<value>.+)", command)
            if match is not None:
                # Because the connection receives on another thread, there is no use in catching YNCA exceptions here
                # However exceptions will cause the connection to break, re-connect if needed
                if not connection.connected:
                    connection.connect()
                connection.put(match.group("subunit"), match.group("function"), match.group("value"))
            else:
                print("Invalid command format")

    connection.disconnect()


if __name__ == "__main__":

    port = "/dev/ttyUSB0"
    if len(sys.argv) > 1:
        port = sys.argv[1]

    ynca_console(port)

    print("Done")
