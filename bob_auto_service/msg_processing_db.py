#!/usr/bin/python3
""" interface_to_db.py:
"""

# Import Required Libraries (Standard, Third Party, Local) ********************
import copy
import datetime
import logging
import os
import sys
if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bob_auto_service.tools.device import search_device_list
from bob_auto_service.messages.heartbeat import HeartbeatMessage
from bob_auto_service.messages.heartbeat_ack import HeartbeatMessageACK
from bob_auto_service.messages.log_status_update import LogStatusUpdateMessage
from bob_auto_service.messages.log_status_update_ack import LogStatusUpdateMessageACK
from bob_auto_service.messages.return_command import ReturnCommandMessage
from bob_auto_service.messages.return_command_ack import ReturnCommandMessageACK
from bob_auto_service.messages.set_device_state import SetDeviceStateMessage
from bob_auto_service.messages.update_command import UpdateCommandMessage
from bob_auto_service.messages.update_command_ack import UpdateCommandMessageACK


# Authorship Info *************************************************************
__author__ = "Christopher Maue"
__copyright__ = "Copyright 2017, The RPi-Home Project"
__credits__ = ["Christopher Maue"]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Christopher Maue"
__email__ = "csmaue@gmail.com"
__status__ = "Development"


# Process log status update messages ******************************************
def process_log_status_update_msg(logger, msg, service_addresses):
    """ If a mis-directed LSU message is received, this function will
        re-direct the message to the database service
    """
    # Configure logging for this function
    logger = logger or logging.getLogger(__name__)

    # Initialize result list
    out_msg_list = []

    # Map message into LSU message class
    message = LogStatusUpdateMessage(logger)
    message.complete = msg

    # Update destination address and port to forward to db service
    logger.debug('Revising LSU message to to forward to DB service')
    message.dest_addr = service_addresses['database_addr']
    message.dest_port = service_addresses['database_port']

    # Load revised message into output list
    logger.debug('Loading completed msg: %s', message.complete)
    out_msg_list.append(copy.copy(message.complete))

    # Return response messages
    return out_msg_list


# Process log status update ACK messages **************************************
def process_log_status_update_msg_ack(logger, msg):
    """ When a LSU-ACK message is received, this function will
        log it then exit
    """
    # Configure logging for this function
    logger = logger or logging.getLogger(__name__)

    # Initialize result list
    out_msg_list = []

    # Map message into LSU message class
    message = LogStatusUpdateMessageACK(logger)
    message.complete = msg

    # Log receipt of ACK for debug purposes
    logger.debug('Log Status Update Ack message received: %s', message.complete)

    # Return response messages
    return out_msg_list


# Process return command messages *********************************************
def process_return_command_msg(logger, msg, service_addresses):
    """ If a mis-directed RC message is received, this function will
        re-direct that message to database service
    """
    # Configure logging for this function
    logger = logger or logging.getLogger(__name__)

    # Initialize result list
    out_msg_list = []

    # Map message into LSU message class
    message = ReturnCommandMessage(logger)
    message.complete = msg

    # Update destination address and port to forward to db service
    logger.debug('Revising RC message to to forward to DB service')
    message.dest_addr = service_addresses['database_addr']
    message.dest_port = service_addresses['database_port']    
    
    # Load message into output list
    logger.debug('Loading completed msg: %s', message.complete)
    out_msg_list.append(copy.copy(message.complete))

    # Return response message
    return out_msg_list


# Process return command ACK messages *****************************************
def process_return_command_msg_ack(logger, ref_num, devices, msg, service_addresses, message_types):
    """ When a RC-ACK message is received, this function will:
        1) Generate and queue a UC message to mark the command as processed
        2) Generate and queue a SDS message to the appropriate device gateway
           to forward to the field device for action
    """
    # Configure logging for this function
    logger = logger or logging.getLogger(__name__)

    # Initialize result list
    out_msg_list = []

    # Map message into LSU message class
    message = ReturnCommandMessageACK(logger)
    message.complete = msg

    # Search device table to find device name
    logger.debug('Searching device table for [%s]', message.dev_name)
    dev_pointer = search_device_list(devices, message.dev_name, logger=logger)
    logger.debug('Match found at device table index: %s', dev_pointer)

    # Send UC message to acknowledge received command and mark as processed
    logger.debug('Generating UC message to mark device cmd as processed')
    out_msg = UpdateCommandMessage(
        logger=logger,
        ref=ref_num.new(),
        dest_addr=service_addresses['database_addr'],
        dest_port=service_addresses['database_port'],
        source_addr=service_addresses['automation_addr'],
        source_port=service_addresses['automation_port'],
        msg_type=message_types['update_command'],
        dev_id=message.dev_id,
        dev_processed=datetime.datetime.now())

    # Load message into output list
    logger.debug('Loading completed msg: %s', out_msg.complete)
    out_msg_list.append(copy.copy(out_msg.complete))

    # Create message to wemo service to issue command to device
    if dev_pointer is not None:
        # Wemo switch commands get sent to the wemo service for handling
        if devices[dev_pointer].dev_type == 'wemo_switch':
            # Determine what command to issue
            out_msg = SetDeviceStateMessage(
                logger=logger,
                ref=ref_num.new(),
                dest_addr=service_addresses['wemo_addr'],
                dest_port=service_addresses['wemo_port'],
                source_addr=service_addresses['automation_addr'],
                source_port=service_addresses['automation_port'],
                msg_type=message_types['set_device_state'],
                dev_name=message.dev_name,
                dev_addr=devices[dev_pointer].dev_addr,
                dev_cmd=message.dev_cmd,
                dev_status=devices[dev_pointer].dev_status,
                dev_last_seen=devices[dev_pointer].dev_last_seen)
            # Load message into output list
            logger.debug('Loading completed msg: %s', out_msg.complete)
            out_msg_list.append(copy.copy(out_msg.complete))
    else:
        logger.debug('Device name not found in known device table')

    # Return response message
    return out_msg_list


# Process update command messages *********************************************
def process_update_command_msg(logger, msg, service_addresses):
    """ If a mis-directed UC message is received, this function will
        re-direct that message to the database service
    """
    # Configure logging for this function
    logger = logger or logging.getLogger(__name__)

    # Initialize result list
    out_msg_list = []

    # Map message into LSU message class
    message = UpdateCommandMessage(logger)
    message.complete = msg

    # Update destination address and port to forward to db service
    logger.debug('Revising UC message to to forward to DB service')
    message.dest_addr = service_addresses['database_addr']
    message.dest_port = service_addresses['database_port']

    # Load message into output list
    logger.debug('Loading completed msg: %s', message.complete)
    out_msg_list.append(copy.copy(message.complete))

    # Return response message
    return out_msg_list



# Process update command ACK messages *****************************************
def process_update_command_msg_ack(logger, msg):
    """ When a UC-ACK message is received, this function will:
        log that message and then exit
    """
    # Configure logging for this function
    logger = logger or logging.getLogger(__name__)

    # Initialize result list
    out_msg_list = []

    # Map message into LSU message class
    message = UpdateCommandMessageACK(logger)
    message.complete = msg

    # Log receipt of ACK for debug purposes
    logger.debug('Update Command ACK message Received: %s', message.complete)

    # Return response message
    return out_msg_list
