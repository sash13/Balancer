#!/usr/bin/env python
import logging
import itertools
import platform
import serial
import time
if platform.system() == 'Windows':
    import _winreg as winreg
else:
    import glob

logging.basicConfig(filename='main.log',level=logging.DEBUG)
log = logging.getLogger(__name__)

def parseStendData(in_data):
    out = {}
    infos = in_data.split('#')
    for info in infos:
        [type, data] = info.split(':')
        if type == 'DEL':
            out['delay'] = float(data)
        elif type == 'FIL':
            angles = []
            for d in data.split(','):
                angles.append(float(d))
            out['angles'] = angles
        elif type == 'PWM':
            pwm = []
            for d in data.split(','):
                pwm.append(int(d))
            out['pwm'] = pwm
    return out

def build_cmd_str(cmd, args=None):
    if args:
        args = '%'.join(map(str, args))
    else:
        args = ''
    return "{cmd}%{args}\n".format(cmd=cmd, args=args)

def enumerate_serial_ports():
    """
    Uses the Win32 registry to return a iterator of serial
        (COM) ports existing on this computer.
    """
    path = 'HARDWARE\\DEVICEMAP\\SERIALCOMM'
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
    except WindowsError:
        raise Exception
  
    for i in itertools.count():
        try:
            val = winreg.EnumValue(key, i)
            yield (str(val[1]))  # , str(val[0]))
        except EnvironmentError:
            break

def find_port(baud, timeout):
    """
    Find the first port that is connected to an servo
    """
    if platform.system() == 'Windows':
        ports = enumerate_serial_ports()
    else:
        ports = glob.glob("/dev/ttyUSB*") + glob.glob("/dev/ttyACM*")
    for p in ports:
        log.debug('Found {0}, testing...'.format(p))
        try:
            sr = serial.Serial(p, baud, timeout=timeout)
        except (serial.serialutil.SerialException, OSError) as e:
            log.debug(str(e))
            continue
        time.sleep(2)
        ping_get = ping(sr)
        print ping_get
        if ping_get != '1':
            log.debug('Bad version {0}. This is not a Servo!'.format(
                ping_get))
            #sr.close()
            continue
        log.info('Using port {0}.'.format(p))
        if sr:
            return sr
    return None

def ping(sr):
    try:
        sr.write('V')
        sr.flush()
    except Exception:
        return None
    return sr.read()

class Stend(object):
    def __init__(self, baud=19200, port=None, timeout=2, sr=None):
        if not sr:
            if not port:
                sr = find_port(baud, timeout)
                if not sr:
                    pass
                    #raise ValueError("Could not find port.")
            else:
                try:
                    sr = serial.Serial(port, baud, timeout=timeout)
                except:
                    pass
        try:
            sr.flush()
            self.sr = sr
        except:
            pass            

    def get_data(self):
        self.sr.write('I\n')
        self.sr.flush()
        rd = self.sr.readline().replace("\r\n", "")

        try:
            return parseStendData(rd)
        except:
            return 0

    def set_angle(self, a):
        cmd_str = build_cmd_str("A", (a,))
        try:
            self.sr.write(cmd_str)
            self.sr.flush()
        except:
            pass
        
    def set_throttle(self, t):
        cmd_str = build_cmd_str("T", (t,))
        try:
            self.sr.write(cmd_str)
            self.sr.flush()
        except:
            pass
        
    def set_pid(self, pid):
        cmd_str = build_cmd_str("R", pid)
        try:
            self.sr.write(cmd_str)
            self.sr.flush()
        except:
            pass
        
    def get_pid(self):
        self.sr.write('G\n')
        self.sr.flush()
        rd = self.sr.readline().replace("\r\n", "")
        try:
            print rd
            out =[]
            data = rd.split(',')
            for d in data:
                out.append(int(d)*1000)
            return out
        except:
            pass
        return 0

    def get_info(self):
        self.sr.write('I\n')
        self.sr.flush()
        rd = self.sr.readline().replace("\r\n", "")
        try:
            print rd
            out =[]
            data = rd.split(',')
            for d in data:
                out.append(int(d)*1000)
            return out
        except:
            pass
        return 0
'''ser = Stend(port = 'COM11')
while 1:
    print ser.get_data()
'''
