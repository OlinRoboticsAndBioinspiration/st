import serial as s
import time as t
import re

# Use this one for Mac/Linux
DEFAULT_DEV = '/dev/tty.KeySerial1'

# Use this one for PC
DEFAULT_DEV_PC = 'COM3'
DEFAULT_BAUD_RATE = 19200

# Roboforth Strings
CR = '\r'
LF = '\n'

PURGE = 'PURGE'
ROBOFORTH = 'ROBOFORTH'
DECIMAL = 'DECIMAL'
START = 'START'
JOINT = 'JOINT'
CALIBRATE = 'CALIBRATE'
HOME = 'HOME'
WHERE = 'WHERE'
CARTESIAN = 'CARTESIAN'
MOVETO = 'MOVETO'
HAND = 'HAND'

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

    def __init__(self, dev=DEFAULT_DEV_PC, baud=DEFAULT_BAUD_RATE):
        self.cxn = s.Serial(dev, baudrate=baud, timeout=3)
        # TODO 
        # Check and parse return values of all ROBOFORTH methods called. 
        self.wait_read()
        self.purge()
        self.roboforth()
        self.decimal()
        self.joint()
        self.start()
        self.calibrate()
        self.home()
        self.cartesian()

    def purge(self):
        print('Purging...')
        self.cxn.write(PURGE + CR)
        t.sleep(3)
        self.check_result(PURGE)

    def roboforth(self):
        print('Starting RoboForth...')
        self.cxn.write(ROBOFORTH + CR)
        t.sleep(2)
        self.check_result(ROBOFORTH)

    def decimal(self):
		print('Setting decimal mode...')
		self.cxn.write(DECIMAL + CR)
		t.sleep(2)
		self.check_result(DECIMAL)
	
    def start(self):
        print('Starting...')
        self.cxn.write(START + CR)
        t.sleep(3)
        self.check_result(START)

    def joint(self):
		print('Setting Joint mode...')
		self.cxn.write(JOINT + CR)
		t.sleep(2)
		self.check_result(JOINT)

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
        
    def hand(self):
		print('Controlling hand...')
		self.cxn.write(HAND + CR)
		t.sleep(2)
		self.check_result(HAND)

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
        
    def move_hand(self, roll):
		self.joint()
		self.hand()
		print('Moving hand to ' + str(roll) + '...')
		self.cxn.write(str(roll) + ' MOVETO' + CR)
		t.sleep(5)
		self.check_result(MOVETO)
		self.cartesian()

    def where(self):
		print('Obtaining robot coordinates...')
		self.cxn.write(WHERE + CR)
		t.sleep(2)
		print (self.cxn.read(self.cxn.inWaiting()))
		self.check_result(WHERE)
