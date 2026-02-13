"""
    sugarcube.py
    Simple API to access the PiSugar2 power platform for Raspbery Pi
    (https://docs.pisugar.com/docs/product-wiki/battery/pisugar2/pisugar-2)
    (




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


    def read(self,s): -> str
        if None is not self.connection:
            self.connection.send(str.encode(s))
            b = self.connection.recv(512)
            rv = b.decode("utf-8").strip()
            if 'I2C not connected' in rv:
                raise SugarDisconnected(rv)
            return rv

if "__main__" == __name__:

    try:
        conn = Connection()
        model = conn.read('get model')
        print(model)
        level = conn.read('get battery')
        print(level + '%')
        volts = conn.read('get battery_v')
        print(volts + ' volts')
        current = conn.read('get battery_i')
        print(current + ' amps')
        temp = conn.read('get temperature')
        print(temp)

        enabled = conn.read('get battery_output_enabled')
        print('battery output enabled: ' + str(enabled))

        version = conn.read('get firmware_version')
        print(version)
    except ConnectionRefusedError as ex:
        print('PiSugar server not found')
    except SugarDisconnected as ex:
        print('PiSugar disconnected (' + str(ex) + ')')

