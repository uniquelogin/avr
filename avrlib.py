#!/usr/bin/python -u
import sys
import serial
import time

class TAvrDisplay(object):
    def __init__(self, devicename = '/dev/tty.usbmodemfd1311'):
        self.prev_percent = 0
        try:
            self.ser = serial.Serial(devicename, 19200, timeout=1, dsrdtr=True, rtscts=True)
            time.sleep(2)
            self.ser.write("\x00\x00\x00\x00\x00\x00\x00\x00")
            time.sleep(.1)
        except Exception, e:
            print repr(e)
            self.ser = None
            #raise

    def close(self):
        if self.ser is not None:
            self.ser.close()

    def set_percentage(self, percent):
        if self.ser is None:
            return
        if (percent == self.prev_percent):
            return
        self.prev_percent = percent
        value = (percent * 255) / 100;
        if value < 0:
            value = 1
        elif value > 255:
            value = 255
        packet = "\x00\x03\x01%c" % chr(value)
        self.ser.write(packet)
        time.sleep(.1)

    def set_message(self, msg, wrap = True, smoothclear = True):
        if self.ser is None:
            return
        lines = []
        line = ''
        for c in msg:
            if c == '\n':
                lines.append(line)
                line = ''
            else:
                if (len(line) == 20):
                    if wrap:
                        lines.append(line)
                        line = ''
                    else:
                        continue
                line += c
        if line:
            lines.append(line)

        phys_rows = [1, 3, 2, 4]
        for i in range(4):
            if i >= len(lines):
                if not smoothclear:
                    break
                line = ''
            else:
                line = lines[i]
            packet = "\x02%c%c%s" % (chr(len(line) + 1), chr(phys_rows[i]), line)
            self.ser.write(packet)
        time.sleep(.1)
        packet = "\x04"
        self.ser.write(packet)

