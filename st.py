import serial as s
import time as t

# Use this one for Mac/Linux
DEFAULT_DEV = '/dev/tty.somestuff'

# Use this one for PC
DEFAULT_DEV_PC = 'COM#'
DEFAULT_BAUD_RATE = 19200

CR = '\r'


class StArm():
    '''Class for controlling the 5-axis R12 arm from ST Robotics'''


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
        self.cxn = s.Serial(dev, baud_rate=baud)
        self.cxn.open()
        # TODO 
        # Check and parse return values of all ROBOFORTH methods called. 
        self.cxn.write('PURGE' + CR)
        t.sleep(3)
        self.cxn.write('ROBOFORTH' + CR)
        print('Energizing the arm...')
        self.cxn.write('START' + CR)
        t.sleep(3)
        self.cxn.write('CALIBRATE' + CR)
        print('Going to home position...')
        self.cxn.write('HOME' + CR



    def get_status()
        if self.cxn.isOpen():
            self.cxn.write('' + CR)

    def move_to(x, y, z, pitch=None, roll=None):
        self.cxn.write(str(x) + ' ' + str(y) + ' ' + str(z) + ' MOVETO' + CR)







