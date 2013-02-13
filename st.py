import serial as s
import time as t
import re
import shlex

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
SPEED = 'SPEED'
ACCEL = 'ACCEL'
MOVETO = 'MOVETO'
HAND = 'HAND'
WRIST = 'WRIST'
ENERGIZE = 'ENERGIZE'
DE_ENERGIZE = 'DE-ENERGIZE'
QUERY = ' ?'
IMPERATIVE = ' !'
TELL = 'TELL'
MOVE = 'MOVE'

class StPosCart():
    def __init__(self, pos=[0,0,0,0,0]):
        self.set(pos)

    def set(self, pos):
        self.x = pos[0]
        self.y = pos[1]
        self.z = pos[2]
        self.pitch = pos[3]
        self.roll = pos[4]

    def __repr__(self):
        return '(x=%s, y=%s, z=%s, pitch=%s roll=%s)' % (self.x, self.y, self.z, self.pitch, self.roll)


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

    def __init__(self, dev=DEFAULT_DEV_PC, baud=DEFAULT_BAUD_RATE, init=True):
        self.cxn = s.Serial(dev, baudrate=baud, timeout=3)
        # TODO 
        # Check and parse return values of all ROBOFORTH methods called. 
        if init:
            self.wait_read()
            self.purge()
            self.roboforth()
            self.joint()
            self.start()
            self.calibrate()
            self.home()
            self.cartesian()
        
        try:
            (cp, pp) = self.where()
            self.curr_pos = StPosCart(cp)
            self.prev_pos = StPosCart(pp)
        except:
            print('Unable to get current arm coordinates.')

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

    def home(self, check_result):
        print('Homing...')
        self.cxn.write(HOME + CR)
        if check_result:
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
        while not self.cxn.inWaiting():
            pass
        result = self.cxn.read(self.cxn.inWaiting())
        if result[-5:-3] == 'OK':
            print('Command ' + cmd + ' succeeded.')
            return True
        else:
            print result
            raise RuntimeError(cmd + ' command failed.')
            return False

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

    def get_speed(self):
        print('Getting current speed setting...')
        self.cxn.write(SPEED + QUERY + CR)
        t.sleep(1)
        return int(self.cxn.read(self.cxn.inWaiting()).split(' ')[-2])

    def set_speed(self, speed):
        print('Setting speed to %d' % speed)
        self.cxn.write(str(speed) + ' ' + SPEED + IMPERATIVE + CR)
        t.sleep(1)
        if self.get_speed() == speed:
            print('Speed successfully set to %d' % speed)
        else:
            print('Failed to set speed!')

    def get_accel(self):
        print('Getting current acceleration setting...')
        self.cxn.write(ACCEL + QUERY + CR)
        t.sleep(1)
        return int(self.cxn.read(self.cxn.inWaiting()).split(' ')[-2])

    def set_accel(self, accel):
        print('Setting acceleration to %d' % accel)
        self.cxn.write(str(accel) + ' ' +ACCEL + IMPERATIVE + CR)
        t.sleep(1)
        if self.get_accel() == accel:
            print('Acceleration successfully set to %d' % accel)
        else:
            print('Failed to set acceleration!')        

    def move_to(self, x, y, z, check_result=False, pitch=None, roll=None):
        print('Moving to cartesian coords: (' + str(x) + ', ' + str(y) + ', ' + \
        str(z) + ')')
        self.cxn.write(str(x) + ' ' + str(y) + ' ' + str(z) + ' MOVETO' + CR)
        if(check_result):
            t.sleep(5)
            self.check_result(MOVETO)
    
    def rotate_wrist(self, roll):
        print('Rotating wrist to %s' % roll)
        self.cxn.write(TELL + ' ' + WRIST + ' ' + str(roll) + ' ' + MOVETO + CR)
        self.check_result(MOVETO)

    def rotate_wrist_rel(self, roll_inc):
        print('Rotating wrist by %s.' % roll_inc)
        self.cxn.write(TELL + ' ' + WRIST + ' ' + str(roll_inc) + ' ' + MOVE + CR)
        self.check_result(MOVE)

    def rotate_hand(self, pitch):
        print('Rotating hand to %s.' %pitch)
        self.cxn.write(TELL + ' ' + HAND + ' ' + str(pitch) + ' ' + MOVETO + CR)
        self.check_result(MOVETO)

    def rotate_hand_rel(self, pitch_inc):
        print('Rotating hand by %s' % pitch_inc)
        self.cxn.write(TELL + ' ' + HAND + ' ' + str(pitch_inc) + ' ' + MOVE + CR)
        self.check_result(MOVE)

    def move_hand(self, roll):
		self.rotate_hand(roll)

    def energize(self):
        print('Powering motors...')
        self.cxn.write(ENERGIZE + CR)
        t.sleep(2)
        self.check_result(ENERGIZE)

    def de_energize(self):
        print('Powering down motors...')
        self.cxn.write(DE_ENERGIZE + CR)
        t.sleep(2)
        self.check_result(DE_ENERGIZE)

    def where(self):
        self.cxn.flushInput()
        print('Obtaining robot coordinates...')
        self.cartesian()
        self.cxn.write(WHERE + CR)
        res = self.cxn.readlines()
        print(res)
        cp = [int(10*float(x)) for x in shlex.split(res[2])]
        pp = [int(10*float(x)) for x in shlex.split(res[3])[1:]]
		
        return (cp, pp)
