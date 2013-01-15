import serial as s
import time as t
import re

# Use this one for Mac/Linux
DEFAULT_DEV = '/dev/tty.KeySerial1'

# Use this one for PC
DEFAULT_DEV_PC = 'COM#'
DEFAULT_BAUD_RATE = 19200

CR = '\r'
LF = '\n'

PURGE = 'PURGE'
ROBOFORTH = 'ROBOFORTH'
START = 'START'
CALIBRATE = 'CALIBRATE'
HOME = 'HOME'
CARTESIAN = 'CARTESIAN'
MOVETO = 'MOVETO'


class StArm():
    '''Class for controlling the 5-axis R17 arm from ST Robotics'''


    '''
    Description:
    Create a serial connection and open it.

    Inputs:
        dev_name: The name of the serial device. For Macs/Linux, use
        /dev/tty.somestringofcharsandnums and for PCs use COMX where
        X is the COM port number the serial connector for the arm is
        connected to.
    '''

    def __init__(self, dev=DEFAULT_DEV, baud=DEFAULT_BAUD_RATE):
        self.cxn = s.Serial(dev, baudrate=baud, timeout=3)
        # TODO 
        # Check and parse return values of all ROBOFORTH methods called. 
        self.wait_read()
        self.purge()
        self.roboforth()
        self.start()
        self.calibrate()
        self.home()
        self.cartesian()

    def purge(self):
        print('Purging...')
        self.cxn.write(PURGE + CR)
        self.check_result(PURGE)

    def roboforth(self):
        print('Starting RoboForth...')
        self.cxn.write(ROBOFORTH + CR)
        t.sleep(3)
        self.check_result(ROBOFORTH)

    def start(self):
        print('Starting...')
        self.cxn.write(START + CR)
        t.sleep(3)
        self.check_result(START)

    def calibrate(self):
        print('Calibrating...')
        self.cxn.write(CALIBRATE + CR)
        t.sleep(15)
        self.check_result(CALIBRATE)

    def home(self):
        print('Homing...')
        self.cxn.write(HOME + CR)
        t.sleep(5)
        self.check_result(HOME)

    def cartesian(self):
        print('Setting mode to Cartesian...')
        self.cxn.write(CARTESIAN + CR)
        t.sleep(2)
        self.check_result(CARTESIAN)

    def check_result(self, cmd):
        while(self.cxn.inWaiting() == 0):
            pass
        result = self.cxn.read(self.cxn.inWaiting())
        if result[-5:-3] == 'OK':
            print('Command ' + cmd + ' succeeded.')
            return True
        else:
            print result
            raise RuntimeError(cmd + ' command failed.')


    def wait_read(self):
        print(str(self.cxn.inWaiting()))
        while(self.cxn.inWaiting()):
            if self.cxn.inWaiting() == 1:
                print self.cxn.read()
                break
            print(self.cxn.readline())

    def get_status(self):
        if self.cxn.isOpen():
            self.cxn.write('' + CR)

    def move_to(self, x, y, z, pitch=None, roll=None):
        print('Moving to cartesian coords: (' + str(x) + ', ' + str(y) + ', ' + \
        str(z) + ')')
        self.cxn.write(str(x) + ' ' + str(y) + ' ' + str(z) + ' MOVETO' + CR)
        t.sleep(5)
        self.check_result(MOVETO)







