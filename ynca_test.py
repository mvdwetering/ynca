import serial
import serial.threaded
import time
import traceback
import sys
import threading
import queue


class YncaProtocol(serial.threaded.LineReader):

    # YNCA spec defines a minumum timeinterval of 100 milliseconds between sending commands
    COMMAND_INTERVAL = 0.1

    # YNCA spec says standby timeout is 40 seconds, so use 30 seconds to be on the safe side
    KEEP_ALIVE_INTERVAL = 5


    def connection_made(self, transport):
        super(YncaProtocol, self).connection_made(transport)
        sys.stdout.write('port opened\n')

        self._send_queue = queue.Queue()
        self._send_thread = threading.Thread(target=self._send_handler)
        self._send_thread.start()

        # When the device is in low power mode the first command is to wake up 
        # So send a dummy keep-alive on connect
        self._send_keepalive()

    def connection_lost(self, exc):
        # There seems to be no way to clear the queue so just read all and  add the _EXIT command
        try:
            while self._send_queue.get(False):
                pass
        except queue.Empty:
            self._send_queue.put("_EXIT")

        if exc:
            sys.stdout.write(exc)
            #traceback.print_exc(exc)
        sys.stdout.write('port closed\n')

    def handle_line(self, line):
        sys.stdout.write(repr(line))

    def _send_keepalive(self):
        self.get('SYS','MODELNAME') # This message is suggested by YNCA spec for keep-alive

    def _send_handler(self):
        exit = False
        while not exit:
            try:
                message = self._send_queue.get(True, self.KEEP_ALIVE_INTERVAL)
            
                if message == "_EXIT":
                    exit = True
                else:
                   self.write_line(message)
                   time.sleep(self.COMMAND_INTERVAL) # Maintain required commandspacing
            except queue.Empty:
                # To avoid random message being eaten because device goes to sleep, keep it alive
                self._send_keepalive()

    def put(self, subunit, funcname, parameter):
        self._send_queue.put('@{subunit}:{funcname}={parameter}'.format(subunit=subunit, funcname=funcname, parameter=parameter))

    def get(self, subunit, funcname):
        self.put(subunit, funcname, '?')


ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)  # open serial port
print(ser.name)         # check which port was really used

with serial.threaded.ReaderThread(ser, YncaProtocol) as protocol:
    remaining = 10
    while remaining >= 0:
      print("Remaining: {}".format(remaining))
      #protocol.get('SYS','VERSION')
      time.sleep(1)
      remaining = remaining - 1

#line = ser.readline()   # read a line
#print(line)

#ser.close()             # close port


