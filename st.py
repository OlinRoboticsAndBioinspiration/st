import serial as s
import time as t
import re
import shlex
import re

# Use this one for Mac/Linux
DEFAULT_DEV = '/dev/tty.KeySerial1'

# Use this one for PC
DEFAULT_DEV = 'COM7'
DEFAULT_BAUD_RATE = 19200
DEFAULT_TIMEOUT = 0.05

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

OK = 'OK'

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

    def __init__(self, dev=DEFAULT_DEV, baud=DEFAULT_BAUD_RATE, init=True, to=DEFAULT_TIMEOUT):
        self.cxn = s.Serial(dev, baudrate=baud, timeout=to)
        # TODO 
        # Check and parse return values of all ROBOFORTH methods called. 
        if init:
            self.cxn.flushInput()
            self.purge()
            self.roboforth()
            self.joint()
            self.start()
            self.calibrate()
            self.home()
            self.cartesian()

        self.curr_pos = StPosCart()
        self.prev_pos = StPosCart()
        self.where()

    def purge(self):
        cmd = PURGE
        print('Purging...')
        self.cxn.flushInput()
        self.cxn.write(cmd + CR)
        self.block_on_result(cmd)

    def roboforth(self):
        cmd = ROBOFORTH
        print('Starting RoboForth...')
        self.cxn.flushInput()
        self.cxn.write(cmd + CR)
        self.block_on_result(cmd)

    def decimal(self):
        print('Setting decimal mode...')
        self.cxn.flushInput()
        self.cxn.write(DECIMAL + CR)

    def start(self):
        cmd = START
        print('Starting...')
        self.cxn.flushInput()
        self.cxn.write(cmd + CR)
        self.block_on_result(cmd)

    def joint(self):
        cmd = JOINT
        print('Setting Joint mode...')
        self.cxn.flushInput()
        self.cxn.write(cmd + CR)
        self.block_on_result(cmd)

    def calibrate(self):
        cmd = CALIBRATE
        print('Calibrating...')
        self.cxn.flushInput()
        self.cxn.write(cmd + CR)
        self.block_on_result(cmd)

    def home(self):
        cmd = HOME
        print('Homing...')
        self.cxn.flushInput()
        self.cxn.write(cmd + CR)
        self.block_on_result(cmd)

    def cartesian(self):
        cmd = CARTESIAN
        print('Setting mode to Cartesian...')
        self.cxn.flushInput()
        self.cxn.write(cmd + CR)
        self.block_on_result(cmd)

    # def hand(self):
    #     print('Controlling hand...')
    #     self.cxn.flushInput()
    #     self.cxn.write(HAND + CR)

    def block_on_result(self, cmd, debug=False):
        try:
            s = self.cxn.read(self.cxn.inWaiting())
            res = re.search(OK,s).group(0)
        except AttributeError:
            res = ''

        while res != OK:
            s += self.cxn.read(self.cxn.inWaiting())
            try:
                res = re.search('>',s).group(0)
                res = re.search(OK,s).group(0)
                if res == '>':
                    print('Command ' + cmd + ' completed without verification of success.')
                    return
            except AttributeError:
                res = ''

        if debug:
            print('Command ' + cmd + ' completed successfully.')
        return res

    def get_status(self):
        if self.cxn.isOpen():
            self.cxn.write('' + CR)

    def get_speed(self):
        cmd = SPEED + QUERY
        print('Getting current speed setting...')
        self.cxn.flushInput()
        self.cxn.write(cmd + CR)
        result = self.block_on_result(cmd)
        return int(result.split(' ')[-2])

    def set_speed(self, speed):
        print('Setting speed to %d' % speed)
        cmd = str(speed) + ' ' + SPEED + IMPERATIVE
        self.cxn.flushInput()
        self.cxn.write(cmd + CR)
        self.block_on_result(cmd)

    def get_accel(self):
        cmd = ACCEL + QUERY
        print('Getting current acceleration setting...')
        self.cxn.flushInput()
        self.cxn.write(cmd + CR)
        result = self.block_on_result(cmd)
        return int(result.split(' ')[-2])

    def set_accel(self, accel):
        cmd = str(accel) + ' ' + ACCEL + IMPERATIVE 
        print('Setting acceleration to %d' % accel)
        self.cxn.flushInput()
        self.cxn.write(cmd + CR)
        self.block_on_result(cmd)

    def move_to(self, x, y, z, debug=False, block=True):
        cmd = str(x) + ' ' + str(y) + ' ' + str(z) + ' MOVETO'
        if debug:
            print('Moving to cartesian coords: (' + str(x) + ', ' + str(y) + ', ' + \
                str(z) + ')')
        self.cxn.flushInput()
        self.cxn.write(str(x) + ' ' + str(y) + ' ' + str(z) + ' MOVETO' + CR)
        if block:
            self.block_on_result(cmd)
            self.where()

    def rotate_wrist(self, roll):
        cmd = TELL + ' ' + WRIST + ' ' + str(roll) + ' ' + MOVETO
        print('Rotating wrist to %s' % roll)
        self.cxn.flushInput()
        self.cxn.write(cmd + CR)
        self.block_on_result(cmd)

    def rotate_wrist_rel(self, roll_inc):
        cmd = TELL + ' ' + WRIST + ' ' + str(roll_inc) + ' ' + MOVE
        print('Rotating wrist by %s.' % roll_inc)
        self.cxn.flushInput()
        self.cxn.write(cmd + CR)
        self.block_on_result(cmd)
        self.cartesian()
        self.where()

    def rotate_hand(self, pitch):
        cmd = TELL + ' ' + HAND + ' ' + str(pitch) + ' ' + MOVETO
        print('Rotating hand to %s.' %pitch)
        self.cxn.flushInput()
        self.cxn.write(cmd + CR)
        self.block_on_result(cmd)
        self.where()

    def rotate_hand_rel(self, pitch_inc):
        cmd = TELL + ' ' + HAND + ' ' + str(pitch_inc) + ' ' + MOVE
        print('Rotating hand by %s' % pitch_inc)
        self.cxn.flushInput()
        self.cxn.write(cmd + CR)
        self.block_on_result(cmd)
        self.cartesian()
        self.where()

    def move_hand(self, roll):
        self.rotate_hand(roll)

    def energize(self):
        cmd = ENERGIZE
        print('Powering motors...')
        self.cxn.flushInput()
        self.cxn.write(cmd + CR)
        self.block_on_result(cmd)

    def de_energize(self):
        cmd = DE_ENERGIZE
        print('Powering down motors...')
        self.cxn.write(cmd + CR)
        self.block_on_result(cmd)

    def where(self):
        self.cxn.flushInput()
        self.cxn.write(WHERE + CR)
        res = self.cxn.readline()
        try:
            while res[-2:] != 'OK':
                res += self.cxn.readline()
                if res != '':
                    if res[-3] == '>':
                        print('WHERE command completed without verification of success.')
                        break

            
            lines = res.split('\r\n')
            #TODO: Need to account for possibility that arm is in decimal mode
            cp = [int(x.strip()) for x in shlex.split(lines[2])]
            pp = [int(x.strip()) for x in shlex.split(lines[3])]

            self.curr_pos.set(cp)
            self.prev_pos.set(pp)
        except RuntimeError, e:
            print('Exception in where.')
            print(e)
            self.curr_pos.set([0,0,0,0,0])
            self.prev_pos.set([0,0,0,0,0])


        return (self.curr_pos, self.prev_pos)
