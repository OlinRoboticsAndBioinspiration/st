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
            self.cxn.flushInput()
            self.purge()
            t.sleep(1)
            self.check_result(PURGE)
            self.roboforth()
            t.sleep(3)
            self.check_result(ROBOFORTH)
            self.joint()
            t.sleep(1)
            self.check_result(JOINT)
            self.start()
            t.sleep(3)
            self.check_result(START)
            self.calibrate()
            t.sleep(20)
            self.check_result(CALIBRATE)
            self.home()
            t.sleep(5)
            self.check_result(HOME)
            self.cxn.flushInput()
            self.cartesian()
            t.sleep(3)
            self.check_result(CARTESIAN)

#        try:
#            (cp, pp) = self.where()
#            self.curr_pos = StPosCart(cp)
#            self.prev_pos = StPosCart(pp)
#        except:
#            self.curr_pos = StPosCart()
#            self.prev_pos = StPosCart()
#            print('Unable to get current arm coordinates.')

    def send(self, cmd, args=None):
        self.cxn.flushInput()
        print('Executing ' + cmd)
        if args is not None:
            str_args = ' '.join(map(str, args))
            cmd_str = str_args + ' ' + cmd + CR
        else:
            cmd_str = cmd + CR

    def purge(self):
        print('Purging...')
        self.cxn.write(PURGE + CR)

    def roboforth(self):
        print('Starting RoboForth...')
        self.cxn.write(ROBOFORTH + CR)

    def decimal(self):
		print('Setting decimal mode...')
		self.cxn.write(DECIMAL + CR)

    def start(self):
        print('Starting...')
        self.cxn.write(START + CR)

    def joint(self):
		print('Setting Joint mode...')
		self.cxn.write(JOINT + CR)

    def calibrate(self):
        print('Calibrating...')
        self.cxn.write(CALIBRATE + CR)

    def home(self):
        print('Homing...')
        self.cxn.write(HOME + CR)

    def cartesian(self):
        print('Setting mode to Cartesian...')
        self.cxn.write(CARTESIAN + CR)

    def hand(self):
		print('Controlling hand...')
		self.cxn.write(HAND + CR)

    def check_result(self, cmd):
        result = self.cxn.read(self.cxn.inWaiting())
        if result[-5:-3] == 'OK':
            print('Command ' + cmd + ' succeeded.')
            return True
        else:
            print("Received this erronenous result: " + result)
            #raise RuntimeError(cmd + ' command failed.')
            return False

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
        t.sleep(1.5)
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
        t.sleep(1.5)
        if self.get_accel() == accel:
            print('Acceleration successfully set to %d' % accel)
        else:
            print('Failed to set acceleration!')

    def move_to(self, x, y, z):
        print('Moving to cartesian coords: (' + str(x) + ', ' + str(y) + ', ' + \
              str(z) + ')')
        self.cxn.write(str(x) + ' ' + str(y) + ' ' + str(z) + ' MOVETO' + CR)

    def rotate_wrist(self, roll):
        print('Rotating wrist to %s' % roll)
        self.cxn.write(TELL + ' ' + WRIST + ' ' + str(roll) + ' ' + MOVETO + CR)

    def rotate_wrist_rel(self, roll_inc):
        print('Rotating wrist by %s.' % roll_inc)
        self.cxn.write(TELL + ' ' + WRIST + ' ' + str(roll_inc) + ' ' + MOVE + CR)

    def rotate_hand(self, pitch):
        print('Rotating hand to %s.' %pitch)
        self.cxn.write(TELL + ' ' + HAND + ' ' + str(pitch) + ' ' + MOVETO + CR)

    def rotate_hand_rel(self, pitch_inc):
        print('Rotating hand by %s' % pitch_inc)
        self.cxn.write(TELL + ' ' + HAND + ' ' + str(pitch_inc) + ' ' + MOVE + CR)

    def move_hand(self, roll):
		self.rotate_hand(roll)

    def energize(self):
        print('Powering motors...')
        self.cxn.write(ENERGIZE + CR)
        self.check_result(ENERGIZE)

    def de_energize(self):
        print('Powering down motors...')
        self.cxn.write(DE_ENERGIZE + CR)

    def where(self):
        self.cxn.flushInput()
        print('Obtaining robot coordinates...')
        self.cxn.write(WHERE + CR)
        res = self.cxn.readlines()
        cp = [int(10*float(x)) for x in shlex.split(res[2])]
        pp = [int(10*float(x)) for x in shlex.split(res[3])[1:]]

        self.curr_pos.set(cp)
        self.prev_pos.set(pp)
        print(self.curr_pos)
        print(self.prev_pos)
        return (cp, pp)
