#!/usr/bin/python3
""" interface_to_wemo.py:
"""

# Import Required Libraries (Standard, Third Party, Local) ********************
import copy
import logging
import os
import sys
if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) 
from bob_auto_service.tools.device import search_device_list
from bob_auto_service.messages.get_device_state import GetDeviceStateMessage
from bob_auto_service.messages.get_device_state_ack import GetDeviceStateMessageACK
from bob_auto_service.messages.set_device_state import SetDeviceStateMessage
from bob_auto_service.messages.set_device_state_ack import SetDeviceStateMessageACK


# Authorship Info *************************************************************
__author__ = "Christopher Maue"
__copyright__ = "Copyright 2017, The RPi-Home Project"
__credits__ = ["Christopher Maue"]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Christopher Maue"
__email__ = "csmaue@gmail.com"
__status__ = "Development"


# Process get device state message ********************************************
def process_get_device_state_msg(logger, msg, service_addresses):
    """ Get Device Status
        When a mis-directed GDS message is received, this function will:
        1) Update destination addr and port values in the GDS message to the
           appropraite values for the wemo service
        2) Update the device address, status, and last_seen values to the most
           current values known
        3) Queue the message to be sent to the wemo service
    """
    # Configure logging for this function
    logger = logger or logging.getLogger(__name__)

    # Initialize result list
    out_msg_list = []

    # Map message into CCS message class
    message = GetDeviceStateMessage(logger=logger)
    message.complete = msg

    # Modify CCS message to forward to wemo service
    message.dest_addr = service_addresses['wemo_addr']
    message.dest_port = service_addresses['wemo_port']

    # Load message into output list
    logger.debug('Loading completed msg: [%s]', message.complete)
    out_msg_list.append(copy.copy(message.complete))

    # Return response message
    return out_msg_list


# Process get device state ACK message ****************************************
def process_get_device_state_msg_ack(logger, devices, msg):
    """ Get Device Status ACK
        When a GDS-ACK message is received, this function will:
        1) Search for the device in the active device table
        2) If found, update the status and last-seen values in the device
           table to the values encoded in the message.
    """
    # Configure logging for this function
    logger = logger or logging.getLogger(__name__)

    # Initialize result list
    out_msg_list = []

    # Map message into CCS message class
    message = GetDeviceStateMessageACK(logger=logger)
    message.complete = msg

    # Search device table to find device name
    logger.debug('Searching device table for [%s]', message.dev_name)
    dev_pointer = search_device_list(devices, message.dev_name, logger=logger)
    logger.debug('Match found at device table index: %s', dev_pointer)    

    # Update values based on message content
    if dev_pointer is not None:
        logger.debug('Updating device [%s] status to [%s] and last seen to [%s]',
                     message.dev_name,
                     message.dev_status,
                     message.dev_last_seen)
        devices[dev_pointer].dev_status = copy.copy(message.dev_status)
        devices[dev_pointer].dev_last_seen = copy.copy(message.dev_last_seen)
    else:
        logger.debug('Device [%s] not found in active device table. '
                     'No further action being taken', message.dev_name)

    # Return response message
    return out_msg_list


# Process set device state message ********************************************
def process_set_device_state_msg(logger, msg, service_addresses):
    """ Set Device Status
        When a mis-directed SDS message is received, this function will:
        1) Update destination addr and port values in the SDS message to the
           appropraite values for the wemo service
        2) Update the device address, status, and last_seen values to the most
           current values known
        3) Queue the message to be sent to the wemo service
    """
    # Configure logging for this function
    logger = logger or logging.getLogger(__name__)

    # Initialize result list
    out_msg_list = []

    # Map message into CCS message class
    message = SetDeviceStateMessage(logger=logger)
    message.complete = msg

    message.dest_addr=service_addresses['wemo_addr']
    message.dest_port=service_addresses['wemo_port']
        
    # Load message into output list
    logger.debug('Loading completed msg: [%s]', message.complete)
    out_msg_list.append(copy.copy(message.complete))

    # Return response message
    return out_msg_list


# Process get device state ACK message ****************************************
def process_set_device_state_msg_ack(logger, devices, msg):
    """ Set Device Status ACK
        When a SDS-ACK message is received, this function will:
        1) Search for the device in the active device table
        2) If found, update the status and last-seen values in the device
           table to the values encoded in the message.
    """
    # Configure logging for this function
    logger = logger or logging.getLogger(__name__)

    # Initialize result list
    out_msg_list = []

    # Map message into CCS message class
    message = SetDeviceStateMessageACK(logger=logger)
    message.complete = msg

    # Search device table to find device name
    logger.debug('Searching device table for [%s]', message.dev_name)
    dev_pointer = search_device_list(devices, message.dev_name, logger=logger)
    logger.debug('Match found at device table index: %s', dev_pointer)

    # Update values based on message content
    if dev_pointer is not None:
        logger.debug('Updating device [%s] status to [%s] and last seen to [%s]',
                     message.dev_name,
                     message.dev_status,
                     message.dev_last_seen)
        devices[dev_pointer].dev_status = copy.copy(message.dev_status)
        devices[dev_pointer].dev_last_seen = copy.copy(message.dev_last_seen)
    else:
        logger.debug('Device [%s] not found in active device table. '
                     'No further action being taken', message.dev_name)

    # Return response message
    return out_msg_list
