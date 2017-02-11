import queue
import re
import sys
import threading
import time

import serial
import serial.threaded


class YncaProtocol(serial.threaded.LineReader):
    # YNCA spec defines a minimum timeinterval of 100 milliseconds between sending commands
    COMMAND_INTERVAL = 0.1

    # YNCA spec says standby timeout is 40 seconds, so use 30 seconds to be on the safe side
    KEEP_ALIVE_INTERVAL = 30

    def __init__(self):
        super(YncaProtocol, self).__init__()
        self._callback = None
        self._send_queue = None
        self._send_thread = None

    def connection_made(self, transport):
        super(YncaProtocol, self).connection_made(transport)
        sys.stdout.write('port opened\n')

        self._send_queue = queue.Queue()
        self._send_thread = threading.Thread(target=self._send_handler)
        self._send_thread.start()

        # When the device is in low power mode the first command is to wake up and gets lost
        # So send a dummy keep-alive on connect
        self._send_keepalive()

    def connection_lost(self, exc):
        # There seems to be no way to clear the queue so just read all and add the _EXIT command
        try:
            while self._send_queue.get(False):
                pass
        except queue.Empty:
            self._send_queue.put("_EXIT")

        if exc:
            sys.stdout.write(repr(exc))
        sys.stdout.write('port closed\n')

    def handle_line(self, line):
        # sys.stdout.write(repr(line))
        # Match lines formatted like @SUBUNIT:FUNCTION=PARAMETER
        match = re.match(r"@(?P<subunit>.*?):(?P<function>.*?)=(?P<value>.*)", line)
        if match is not None:
            if self._callback is not None:
                self._callback(match.group("subunit"), match.group("function"), match.group("value"))
        elif line == "@UNDEFINED":
            raise Exception("Undefined command")
        elif line == "@RESTRICTED":
            raise Exception("Restricted command")

    def _send_keepalive(self):
        self.get('SYS', 'MODELNAME')  # This message is suggested by YNCA spec for keep-alive

    def _send_handler(self):
        stop = False
        while not stop:
            try:
                message = self._send_queue.get(True, self.KEEP_ALIVE_INTERVAL)

                if message == "_EXIT":
                    stop = True
                else:
                    self.write_line(message)
                    time.sleep(self.COMMAND_INTERVAL)  # Maintain required commandspacing
            except queue.Empty:
                # To avoid random message being eaten because device goes to sleep, keep it alive
                self._send_keepalive()

    def put(self, subunit, funcname, parameter):
        self._send_queue.put(
            '@{subunit}:{funcname}={parameter}'.format(subunit=subunit, funcname=funcname, parameter=parameter))

    def get(self, subunit, funcname):
        self.put(subunit, funcname, '?')


class Ynca:
    def __init__(self, port=None, callback=None):
        self._port = port
        self._callback = callback
        self._serial = None
        self._readerthread = None
        self._protocol = None

    def connect(self):
        self._serial = serial.Serial(self._port, 9600)
        self._readerthread = serial.threaded.ReaderThread(self._serial, YncaProtocol)
        self._readerthread.start()
        dummy, self._protocol = self._readerthread.connect()
        self._protocol._callback = self._callback

    def disconnect(self):
        self._readerthread.close()

    def put(self, subunit, funcname, parameter):
        self._protocol.put(subunit, funcname, parameter)

    def get(self, subunit, funcname):
        self._protocol.get(subunit, funcname)


if __name__ == "__main__":

    def print_it(a, b, c):
        print("Subunit:{0}, Function:{1}, Value:{2}".format(a, b, c))


    port = "/dev/ttyUSB0"
    if len(sys.argv) > 1:
        port = sys.argv[1]

    ynca = Ynca(port, print_it)
    ynca.connect()
    ynca.get("SYS", "VERSION")

    remaining = 10
    while remaining >= 0:
        print("Remaining: {}".format(remaining))
        ynca.get("SYS", "PWR")
        time.sleep(1)
        remaining -= 1

    ynca.disconnect()
