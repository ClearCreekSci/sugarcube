"""
    sugarcube.py
    Simple API to access the PiSugar2 power platform for Raspbery Pi
    (https://docs.pisugar.com/docs/product-wiki/battery/pisugar2/pisugar-2)
    (https://github.com/PiSugar/PiSugar/wiki/PiSugar-Power-Manager-(Software))


    Copyright (C) 2026 Clear Creek Scientific

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
import argparse
import socket
import datetime
import subprocess
import time

DEFAULT_PORT = 8423

RTC_TIME_PREFIX = 'rtc_time: '

class SugarDisconnected(Exception):
    pass

# FIXME: Remove this for release
def logmsg(msg):
    with open('/opt/ccs/DataLogger/sugarcube.log','a') as fd:
            ts = datetime.datetime.now(datetime.UTC)
            s = ts.strftime('%Y-%m-%d %I:%M:%S ') + msg + '\n'
            fd.write(s)

class Connection(object):

    def __init__(self,port=DEFAULT_PORT):
        self.port = port
        self.connection = None
        self.connect()

    def connect(self):
        addr = ('127.0.0.1',self.port)
        self.connection = socket.create_connection(addr)

    def send(self,s) -> str:
        if None is not self.connection:
            self.connection.send(str.encode(s))
            b = self.connection.recv(512)
            rv = b.decode('utf-8').strip()
            if 'I2C not connected' in rv:
                raise SugarDisconnected(rv)
            return rv

    def is_connected(self) -> bool:
        return self.connection is not None

    def is_battery_charging(self) -> bool:
        s = self.send('get battery_charging')
        parts = s.split(' ')
        rv = parts[-1]
        return bool(rv)

    def is_battery_output_enabled(self) -> bool:
        s = self.send('get battery_output_enabled')
        parts = s.split(' ')
        rv = parts[-1]
        return bool(rv)

    def get_model(self) -> str:
        s = self.send('get model')
        parts = s.split(':')
        rv = parts[1][1:]
        return rv 

    def get_battery_percentage(self) -> float:
        s = self.send('get battery')
        parts = s.split(' ')
        rv = parts[-1]
        return float(rv)

    def get_battery_voltage(self) -> float:
        s = self.send('get battery_v')
        parts = s.split(' ')
        rv = parts[-1]
        return float(rv)

    def get_battery_current(self) -> float:
        s = self.send('get battery_i')
        parts = s.split(' ')
        rv = parts[-1]
        return float(rv)

    # sleep for "v" minutes and then wakeup
    def sleep(self,v) -> bool:
        rv = False
        # Force the pi to use our clock
        chk = self.send('rtc_rtc2pi')
        if 'done' in chk:
            chk = self.send('get rtc_time')
            if chk.startswith(RTC_TIME_PREFIX):
                chk = chk[len(RTC_TIME_PREFIX):]
            else:
                return rv 
            now = datetime.datetime.fromisoformat(chk)
            logmsg('now: ' + now.isoformat(timespec='seconds'))
            wake = now + datetime.timedelta(minutes=v)
            logmsg('wake: ' + wake.isoformat(timespec='seconds'))
            s = wake.isoformat(timespec='seconds')
            s = 'rtc_alarm_set ' + s + ' 7' 
            # Include the the repeat value to '7' so that it happens every day?
            logmsg('sending: ' + s)
            chk = self.send(s)
            logmsg('rtc_alarm_set returned: ' + chk)
            subprocess.run(['pisugar-poweroff','-m','PiSugar 2 (2-LEDs)'])
        else:
            logmsg('rtc_rtc2pi returned: ' + chk)

if "__main__" == __name__:

    try:
        conn = Connection()
        model = conn.get_model()
        print(model)
        level = conn.get_battery_percentage()
        print(str(level) + '%')
        volts = conn.get_battery_voltage()
        print(str(volts) + ' volts')
        current = conn.get_battery_current()
        print(str(current) + ' amps')

        enabled = conn.is_battery_output_enabled()
        print('battery output enabled: ' + str(enabled))

    except ConnectionRefusedError as ex:
        print('PiSugar server not found')
    except SugarDisconnected as ex:
        print('PiSugar disconnected (' + str(ex) + ')')

