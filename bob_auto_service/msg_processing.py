#!/usr/bin/python3
""" msg_processing.py:
"""

# Import Required Libraries (Standard, Third Party, Local) ********************
import os
import sys
if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bob_auto_service.messages.heartbeat import HeartbeatMessage
from bob_auto_service.messages.heartbeat_ack import HeartbeatMessageACK
from bob_auto_service.tools.log_support import setup_function_logger


# Authorship Info *************************************************************
__author__ = "Christopher Maue"
__copyright__ = "Copyright 2017, The RPi-Home Project"
__credits__ = ["Christopher Maue"]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Christopher Maue"
__email__ = "csmaue@gmail.com"
__status__ = "Development"


def create_heartbeat_msg(log_path, ref_num, destinations, source_addr, source_port, message_types):
    """ function to create one or more heartbeat messages """
    # Configure logging for this function
    log = setup_function_logger(log_path, 'create_heartbeat_msg')

    # Initialize result list
    log.debug('Clearing outgoing message list')
    out_msg_list = []

    # Generate a heartbeat message for each destination given
    for entry in destinations:
        log.debug('Creating heartbeat to send to: %s:%s',
                  entry[0], entry[1])
        out_msg = HeartbeatMessage(
            log_path,
            ref=ref_num.new(),
            dest_addr=entry[0],
            dest_port=entry[1],
            source_addr=source_addr,
            source_port=source_port,
            msg_type=message_types['heartbeat']
        )
        # Load message into output list
        log.debug('Loading completed msg: %s', out_msg.complete)
        out_msg_list.append(out_msg.complete)

    # Return response message
    log.debug('Returning generated messages: %s', out_msg_list)
    return out_msg_list


def process_heartbeat_msg(log_path, ref_num, msg, message_types):
    """ function to ack wake-up requests to wemo service """
    # Configure logging for this function
    log = setup_function_logger(log_path, 'process_heartbeat_msg')

    # Initialize result list
    out_msg_list = []

    # Map message into wemo wake-up message class
    message = HeartbeatMessage(log_path)
    message.complete = msg

    # Send response indicating query was executed
    log.debug('Building response message header')
    out_msg = HeartbeatMessageACK(
        log_path,
        ref=ref_num.new(),
        dest_addr=message.source_addr,
        dest_port=message.source_port,
        source_addr=message.dest_addr,
        source_port=message.dest_port,
        msg_type=message_types['heartbeat_ack'])

    # Load message into output list
    log.debug('Loading completed msg: [%s]', out_msg.complete)
    out_msg_list.append(out_msg.complete)

    # Return response message
    return out_msg_list