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


DEFAULT_PORT = 8423

class SugarDisconnected(Exception):
    pass

class Connection(object):

    def __init__(self,port=DEFAULT_PORT):
        self.port = port
        self.connection = None
        self.connect()

    def connect(self):
        addr = ('127.0.0.1',self.port)
        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.connection = socket.create_connection(addr)

    def read(self,s) -> str:
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
        s = self.read('get battery_charging')
        parts = s.split(' ')
        rv = parts[-1]
        return bool(rv)

    def is_battery_output_enabled(self) -> bool:
        s = self.read('get battery_output_enabled')
        parts = s.split(' ')
        rv = parts[-1]
        return bool(rv)

    def get_model(self) -> str:
        s = self.read('get model')
        parts = s.split(':')
        rv = parts[1][1:]
        return rv 

    def get_battery_percentage(self) -> float:
        s = self.read('get battery')
        parts = s.split(' ')
        rv = parts[-1]
        return float(rv)

    def get_battery_voltage(self) -> float:
        s = self.read('get battery_v')
        parts = s.split(' ')
        rv = parts[-1]
        return float(rv)

    def get_battery_current(self) -> float:
        s = self.read('get battery_i')
        parts = s.split(' ')
        rv = parts[-1]
        return float(rv)

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

