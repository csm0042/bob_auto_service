#!/usr/bin/python3
""" configure.py:
    Configuration process for the RPiHome application.
"""

# Import Required Libraries (Standard, Third Party, Local) ********************
import configparser
import datetime
import logging
import os
import sys
if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bob_auto_service.tools.device import Device


# Authorship Info *************************************************************
__author__ = "Christopher Maue"
__copyright__ = "Copyright 2017, The RPi-Home Project"
__credits__ = ["Christopher Maue"]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Christopher Maue"
__email__ = "csmaue@gmail.com"
__status__ = "Development"


class LogFilter(logging.Filter):

    def filter(self, record):

        record.ip = choice(ContextFilter.IPS)
        record.user = choice(ContextFilter.USERS)
        return True


# Config Function Def *********************************************************
class ConfigureService(object):
    def __init__(self, filename):
        self.filename = filename
        self.service_addresses = {}
        self.message_types = {}
        self.latitude = float()
        self.longitude = float()
        self.devices = []
        self.device_num = int()
        self.device_id = str()
        self.i = int()
        self.device = None
        self.func_names = {}
        self.handlers = []
        self.log_path = str()
        # Define connection to configuration file
        self.config_file = configparser.ConfigParser()
        # Configure logger
        self.log = self.get_logger()


    def get_logger(self):
        # Set up application logging
        self.config_file.read(self.filename)
        self.log_path = self.config_file['LOG FILES']['log_file_path']
        self.log = logging.getLogger('master')
        self.log.setLevel(logging.DEBUG)
        self.log.handlers = []
        os.makedirs(self.log_path, exist_ok=True)
        # Console handler
        self.handlers = []
        self.ch = logging.StreamHandler(sys.stdout)
        self.ch.setLevel(logging.INFO)
        self.cf = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.ch.setFormatter(self.cf)
        self.log.addHandler(self.ch)
        self.log.info('Console logger handler created and applied')
        # File handler
        self.fh = logging.handlers.TimedRotatingFileHandler(
            os.path.join(self.log_path, "Debug.log"),
            when='d',
            interval=1,
            backupCount=4
        )
        self.fh.setLevel(logging.DEBUG)
        self.ff = logging.Formatter(
            '%(asctime)-25s %(levelname)-10s '
            '%(funcName)-22s %(message)s'
        )
        self.fh.setFormatter(self.ff)
        self.log.addHandler(self.fh)
        # Return configured objects to main program
        return self.log


    def get_servers(self):
        # Create dict with all services defined in INI file
        self.config_file.read(self.filename)
        for option in self.config_file.options('SERVICES'):
            self.service_addresses[option] = self.config_file['SERVICES'][option]
        # Return dict of configured addresses and ports to main program
        return self.service_addresses


    def get_message_types(self):
        # Create dict with all services defined in INI file
        self.config_file.read(self.filename)
        for option in self.config_file.options('MESSAGE TYPES'):
            self.message_types[option] = self.config_file['MESSAGE TYPES'][option]
        # Return dict of configured addresses and ports to main program
        return self.message_types


    def get_location(self):
        self.config_file.read(self.filename)
        self.latitude = float(self.config_file['LOCATION']['latitude'])
        self.longitude = float(self.config_file['LOCATION']['longitude'])
        # Return configured objects to main program
        return self.latitude, self.longitude


    def get_devices(self):
        self.config_file.read(self.filename)
        # Create list of automation devices defined in config.ini file
        self.devices = []
        self.log.debug('Begining search for device configuration in config file')
        self.device_num = int(self.config_file['DEVICES']['device_num']) + 1
        self.log.debug('Importing configuration for %s devices', str(self.device_num))
        for self.i in range(1, self.device_num, 1):
            try:
                if len(str(self.i)) == 1:
                    self.log.debug('Single digit device ID number')
                    self.device_id = 'device0' + str(self.i)
                elif len(str(self.i)) == 2:
                    self.log.debug('Double digit device ID number')
                    self.device_id = 'device' + str(self.i)
                self.devices.append(
                    Device(
                        dev_name=self.config_file['DEVICES'][self.device_id + '_name'],
                        dev_type=self.config_file['DEVICES'][self.device_id + '_devtype'],
                        dev_addr=self.config_file['DEVICES'][self.device_id + '_address'],
                        dev_last_seen=datetime.datetime.now(),
                        dev_rule=self.config_file['DEVICES'][self.device_id + '_rule']))
                self.log.debug('Device %s added to automation device list',
                               self.config_file['DEVICES'][self.device_id + '_name'])
            except Exception:
                pass
        self.log.debug('Completed automation device list:')
        for self.device in self.devices:
            self.log.debug(
                '%s, %s, %s, %s, %s, %s, %s',
                self.device.dev_name, self.device.dev_type,
                self.device.dev_addr, self.device.dev_cmd,
                self.device.dev_status, self.device.dev_last_seen,
                self.device.dev_rule)
        # Return configured objects to main program
        return self.devices
