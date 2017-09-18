#!/usr/bin/python3
""" message_rc_ack.py:
"""

# Import Required Libraries (Standard, Third Party, Local) ********************
import logging
import os
import sys
if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))   
from bob_auto_service.tools.ipv4_help import check_ipv4
from bob_auto_service.tools.field_checkers import in_int_range
from bob_auto_service.tools.field_checkers import is_valid_datetime


# Authorship Info *************************************************************
__author__ = "Christopher Maue"
__copyright__ = "Copyright 2017, The RPi-Home Project"
__credits__ = ["Christopher Maue"]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Christopher Maue"
__email__ = "csmaue@gmail.com"
__status__ = "Development"


# Message Class Definition ****************************************************
class ReturnCommandMessageACK(object):
    """ Return Command ACK message class and methods """
    def __init__(self, logger=None, **kwargs):
        # Configure loggers
        self.logger = logger or logging.getLogger(__name__)
        
        self._ref = str()
        self._dest_addr = str()
        self._dest_port = str()
        self._source_addr = str()
        self._source_port = str()
        self._msg_type = str()
        self._dev_id = str()
        self._dev_name = str()
        self._dev_cmd = str()
        self._dev_timestamp = str()
        self._dev_processed = str()
        self.temp_list = []
        
        # Process input variables if present
        if kwargs is not None:
            for key, value in kwargs.items():
                if key == "ref":
                    self.ref = value
                    self.logger.debug('Ref Number value set during '
                                      '__init__ to: %s', self.ref)
                if key == "dest_addr":
                    self.dest_addr = value
                    self.logger.debug('Destination address value set during __init__ '
                                      'to: %s', self.dest_addr)
                if key == "dest_port":
                    self.dest_port = value
                    self.logger.debug('Destination port value set during __init__ '
                                      'to: %s', self.dest_port)
                if key == "source_addr":
                    self.source_addr = value
                    self.logger.debug('Source address value set during __init__ '
                                      'to: %s', self.source_addr)
                if key == "source_port":
                    self.source_port = value
                    self.logger.debug('Source port value set during __init__ to: '
                                      '%s', self.source_port)
                if key == "msg_type":
                    self.msg_type = value
                    self.logger.debug('Message type value set during __init__ to: '
                                      '%s', self.msg_type)
                if key == "dev_id":
                    self.dev_id = value
                    self.logger.debug('Device cmd ID value set during '
                                      '__init__ to: %s', self.dev_id)                                   
                if key == "dev_name":
                    self.dev_name = value
                    self.logger.debug('Device name value set during __init__ to: '
                                      '%s', self.dev_name)
                if key == "dev_cmd":
                    self.dev_cmd = value
                    self.logger.debug('Device cmd value set during '
                                      '__init__ to: %s', self.dev_cmd)
                if key == "dev_timestamp":
                    self.dev_timestamp = value
                    self.logger.debug('Device cmd timestamp value set during '
                                      '__init__ to: %s', self.dev_timestamp) 
                if key == "dev_processed":
                    self.dev_processed = value
                    self.logger.debug('Device cmd processed value set during '
                                      '__init__ to: %s', self.dev_processed)                                                                                                      


    # ref number field ********************************************************
    @property
    def ref(self):
        self.logger.debug('Returning current value of ref number: %s', self._ref)
        return self._ref

    @ref.setter
    def ref(self, value):
        if in_int_range(value, 100, 999, logger=self.logger) is True:
            self._ref = str(value)
            self.logger.debug('Ref number updated to: %s', self._ref)
        else:
            self.logger.debug('Ref number update failed with input value: '
                              '%s', value)

    # destination address *****************************************************
    @property
    def dest_addr(self):
        self.logger.debug('Returning current value of destination address: '
                          '%s', self._dest_addr)
        return self._dest_addr

    @dest_addr.setter
    def dest_addr(self, value):
        if check_ipv4(value, logger=self.logger) is True:
            self._dest_addr = str(value)
            self.logger.debug('Destination address updated to: '
                              '%s', self._dest_addr)
        else:
            self.logger.warning('Destination address update failed with input value: '
                                '%s', value)

    # destination port ********************************************************
    @property
    def dest_port(self):
        self.logger.debug('Returning current value of destination port: '
                          '%s', self._dest_port)
        return self._dest_port

    @dest_port.setter
    def dest_port(self, value):
        if in_int_range(value, 10000, 60000, logger=self.logger) is True:
            self._dest_port = str(value)
            self.logger.debug('Destination port updated to: %s', self._dest_port)
        else:
            self.logger.debug('Destination port update failed with input value: '
                              '%s', value)

    # source address field ****************************************************
    @property
    def source_addr(self):
        self.logger.debug('Returning current value of source address: '
                          '%s', self._source_addr)
        return self._source_addr

    @source_addr.setter
    def source_addr(self, value):
        if check_ipv4(value, logger=self.logger) is True:
            self._source_addr = value
            self.logger.debug('source address updated to: '
                              '%s', self._source_addr)
        else:
            self.logger.warning('Source address update failed with input value: '
                                '%s', value)

    # source port field *******************************************************
    @property
    def source_port(self):
        self.logger.debug('Returning current value of source port: '
                          '%s', self._source_port)
        return self._source_port

    @source_port.setter
    def source_port(self, value):
        if in_int_range(value, 10000, 60000, logger=self.logger) is True:
            self._source_port = str(value)
            self.logger.debug('Source port updated to: %s', self._source_port)
        else:
            self.logger.debug('Source port update failed with input value: '
                              '%s', value)

    # message type field ******************************************************
    @property
    def msg_type(self):
        self.logger.debug('Returning current value of message type: '
                          '%s', self._msg_type)
        return self._msg_type

    @msg_type.setter
    def msg_type(self, value):
        if in_int_range(value, 100, 999, logger=self.logger) is True:
            self._msg_type = str(value)
            self.logger.debug('Message type updated to: %s', self._msg_type)
        else:
            self.logger.debug('Message type update failed with input value: '
                              '%s', value)

    # device ID field *********************************************************
    @property
    def dev_id(self):
        self.logger.debug('Returning current value of device ID: '
                          '%s', self._dev_id)
        return self._dev_id

    @dev_id.setter
    def dev_id(self, value):
        if in_int_range(self.logger, value, 1, 99999999) is True:
            self._dev_id = str(value)
            self.logger.debug('Device ID updated to: %s', self._dev_id)
        else:
            self.logger.debug('Device ID update failed with input value: '
                              '%s', value)

    # device name field *******************************************************
    @property
    def dev_name(self):
        self.logger.debug('Returning current value of device name: '
                          '%s', self._dev_name)
        return self._dev_name

    @dev_name.setter
    def dev_name(self, value):
        if isinstance(value, str):
            self._dev_name = value
        else:
            self._dev_name = str(value)
        self.logger.debug('Device name value updated to: '
                          '%s', self._dev_name)

    # device cmd field ********************************************************
    @property
    def dev_cmd(self):
        self.logger.debug('Returning current value of device cmd: '
                          '%s', self._dev_cmd)
        return self._dev_cmd

    @dev_cmd.setter
    def dev_cmd(self, value):
        if isinstance(value, str):
            self._dev_cmd = value
        else:
            self._dev_cmd = str(value)
        self.logger.debug('Device cmd value updated to: '
                          '%s', self._dev_cmd)

    # device timestamp field **************************************************
    @property
    def dev_timestamp(self):
        self.logger.debug('Returning current value of device cmd timestamp: '
                          '%s', self._dev_timestamp)
        return self._dev_timestamp

    @dev_timestamp.setter
    def dev_timestamp(self, value):
        self._dev_timestamp = is_valid_datetime(
            value,
            self._dev_timestamp,
            logger=self.logger)
        self.logger.debug('Device timestamp updated to: %s', self._dev_timestamp)

    # device last seen field **************************************************
    @property
    def dev_processed(self):
        self.logger.debug('Returning current value of device cmd processed: '
                          '%s', self._dev_processed)
        return self._dev_processed

    @dev_processed.setter
    def dev_processed(self, value):
        self._dev_processed = is_valid_datetime(
            value,
            self._dev_processed,
            logger=self.logger)
        self.logger.debug('Device processed updated to: %s', self._dev_processed)                      

    # complete message encode/decode methods **********************************
    @property
    def complete(self):
        self.logger.debug('Returning current value of complete message: '
                          '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s',
                          self._ref, self._dest_addr, self._dest_port,
                          self._source_addr, self._source_port,
                          self._msg_type,
                          self._dev_id, self._dev_name, self._dev_cmd,
                          self._dev_timestamp, self._dev_processed)
        return '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s' % (
            self._ref, self._dest_addr, self._dest_port,
            self._source_addr, self._source_port,
            self._msg_type, self._dev_id, self._dev_name, self._dev_cmd,
            self._dev_timestamp, self._dev_processed)

    @complete.setter
    def complete(self, value):
        self.logger.debug('Loading raw rc-ack message into data structure: %s', value)
        if isinstance(value, str):
            self.temp_list = value.split(',')
            if len(self.temp_list) >= 11:
                self.logger.debug('Message was properly formatted for decoding')
                self.ref = self.temp_list[0]
                self.dest_addr = self.temp_list[1]
                self.dest_port = self.temp_list[2]
                self.source_addr = self.temp_list[3]
                self.source_port = self.temp_list[4]
                self.msg_type = self.temp_list[5]
                self.dev_id = self.temp_list[6]
                self.dev_name = self.temp_list[7]
                self.dev_cmd = self.temp_list[8]
                self.dev_timestamp = self.temp_list[9]
                self.dev_processed = self.temp_list[10]
