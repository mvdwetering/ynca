import serial
import serial.threaded
import time
import traceback
import sys
import threading


class RepeatingTimer(threading.Timer):
    def run(self):
        while not self.finished.is_set():
            self.finished.wait(self.interval)
            self.function(*self.args, **self.kwargs)

        self.finished.set()


class YncaProtocol(serial.threaded.LineReader):

    # YNCA spec defines a minumum timeinterval of 100 milliseconds between sending commands
    COMMAND_INTERVAL = 0.1

    # YNCA spec says standby timeout is 40 seconds, so use 30 seconds to be on the safe side
    KEEP_ALIVE_INTERVAL = 5

    def __init__(self):
        super(YncaProtocol, self).__init__()

        def _send_keepaliveXYZ():
            sys.stdout.write("Keep the dream alive! ")
            self.get('SYS','MODELNAME')

        self._keepalive_timer = RepeatingTimer(self.KEEP_ALIVE_INTERVAL, _send_keepaliveXYZ())
       


    def connection_made(self, transport):
        super(YncaProtocol, self).connection_made(transport)
        sys.stdout.write('port opened\n')

        self._timestamp_last_command = 0

        self._keepalive_timer.start()

        # When the device is in low power mode the first command is to wake up 
        # So send a dummy keep-alive on connect (which also starts the keepalive sequence)
        #self._send_keepalive()

    def connection_lost(self, exc):
        #self._keepalive_timer.cancel()
        #self._keepalive_timer = None

        if exc:
            sys.stdout.write(exc)
            #traceback.print_exc(exc)
        sys.stdout.write('port closed\n')

    def handle_line(self, line):
        sys.stdout.write(repr(line))

    def _send_keepalive2(self):
        self.get('SYS','MODELNAME')

        # To avoid random message being eaten because device goes to sleep, keep it alive
        #if not self._keepalive_timer:
        #self._keepalive_timer = threading.Timer(self.KEEP_ALIVE_INTERVAL, self._send_keepalive())
        #self._keepalive_timer.start()
        

    def put(self, subunit, funcname, parameter):
        # Maintain required commandspacing (not nice that it blocks, but works for now FIXME)
        time_since_last_command = time.monotonic() - self._timestamp_last_command
        if time_since_last_command < self.COMMAND_INTERVAL:
            time.sleep(self.COMMAND_INTERVAL - time_since_last_command)

        self.write_line('@{subunit}:{funcname}={parameter}'.format(subunit=subunit, funcname=funcname, parameter=parameter))
        self._timestamp_last_command = time.monotonic()

    def get(self, subunit, funcname):
        self.put(subunit, funcname, '?')


ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)  # open serial port
print(ser.name)         # check which port was really used

with serial.threaded.ReaderThread(ser, YncaProtocol) as protocol:
    remaining = 10
    while remaining >= 0:
      print("Remaining: {}".format(remaining))
      protocol.get('SYS','VERSION')
      time.sleep(1)
      remaining = remaining - 1

#line = ser.readline()   # read a line
#print(line)

#ser.close()             # close port


