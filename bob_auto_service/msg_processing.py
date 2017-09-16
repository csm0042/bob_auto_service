#!/usr/bin/python3
""" msg_processing.py:
"""

# Import Required Libraries (Standard, Third Party, Local) ********************
import copy
import logging
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


def create_heartbeat_msg(logger, ref_num, destinations, source_addr, source_port, message_types):
    """ function to create one or more heartbeat messages """
    # Configure logging for this function
    logger = logger or logging.getLogger(__name__)

    # Initialize result list
    logger.debug('Clearing outgoing message list')
    out_msg_list = []

    # Generate a heartbeat message for each destination given
    for entry in destinations:
        logger.debug('Creating heartbeat to send to: %s:%s',
                  entry[0], entry[1])
        out_msg = HeartbeatMessage(
            logger=logger,
            ref=ref_num.new(),
            dest_addr=entry[0],
            dest_port=entry[1],
            source_addr=source_addr,
            source_port=source_port,
            msg_type=message_types['heartbeat']
        )
        # Load message into output list
        logger.debug('Loading completed msg: %s', out_msg.complete)
        out_msg_list.append(copy.copy(out_msg.complete))

    # Return response message
    logger.debug('Returning generated messages: %s', out_msg_list)
    return out_msg_list


def process_heartbeat_msg(logger, ref_num, msg, message_types):
    """ function to ack wake-up requests to wemo service """
    # Configure logging for this function
    logger = logger or logging.getLogger(__name__)

    # Initialize result list
    out_msg_list = []

    # Map message into wemo wake-up message class
    message = HeartbeatMessage(logger)
    message.complete = msg

    # Send response indicating query was executed
    logger.debug('Building response message header')
    out_msg = HeartbeatMessageACK(
        logger=logger,
        ref=ref_num.new(),
        dest_addr=message.source_addr,
        dest_port=message.source_port,
        source_addr=message.dest_addr,
        source_port=message.dest_port,
        msg_type=message_types['heartbeat_ack'])

    # Load message into output list
    logger.debug('Loading completed msg: [%s]', out_msg.complete)
    out_msg_list.append(copy.copy(out_msg.complete))

    # Return response message
    return out_msg_list