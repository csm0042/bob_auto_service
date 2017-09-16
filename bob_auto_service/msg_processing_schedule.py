#!/usr/bin/python3
""" interface_to_cal.py:
"""

# Import Required Libraries (Standard, Third Party, Local) ********************
import copy
import os
import sys
if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bob_auto_service.tools.log_support import setup_function_logger    
from bob_auto_service.tools.device import search_device_list
from bob_auto_service.messages.get_device_scheduled_state import GetDeviceScheduledStateMessage
from bob_auto_service.messages.get_device_scheduled_state_ack import GetDeviceScheduledStateMessageACK
from bob_auto_service.messages.set_device_state import SetDeviceStateMessage


# Authorship Info *************************************************************
__author__ = "Christopher Maue"
__copyright__ = "Copyright 2017, The RPi-Home Project"
__credits__ = ["Christopher Maue"]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Christopher Maue"
__email__ = "csmaue@gmail.com"
__status__ = "Development"


# Create get device scheduled state message ***********************************
def create_get_device_scheduled_state_msg(log_path, ref_num, devices, service_addresses, message_types):
    """ When called, this function will generate and queue a get device
        scheduled state message for every device in the device list
    """
    # Configure logging for this function
    log = setup_function_logger(log_path, 'Function_create_get_device_scheduled_state_msg')
    print(__name__)
    # Initialize result list
    out_msg_list = []

    # Create CCS messages for each device in the list
    for device in devices:
        if device.dev_rule == 'schedule' or \
           device.dev_rule == 'dusk_to_dawn' or \
           device.dev_rule == '':
            out_msg = GetDeviceScheduledStateMessage(
                log_path,
                ref=ref_num.new(),
                dest_addr=service_addresses['schedule_addr'],
                dest_port=service_addresses['schedule_port'],
                source_addr=service_addresses['automation_addr'],
                source_port=service_addresses['automation_port'],
                msg_type=message_types['get_device_scheduled_state'],
                dev_name=device.dev_name)

            # Load message into output list
            log.debug('Loading completed msg: [%s]', out_msg.complete)
            out_msg_list.append(copy.copy(out_msg.complete))

    # Return response message
    return out_msg_list


# Process get device scheduled state message **********************************
def process_get_device_scheduled_state_msg(log_path, msg, service_addresses):
    """ If a mis-directed get device scheduled state message is received, this
        function will update destination addr and port values in the message to
        the appropraite values for the schedule service, then queue it to be
        sent to the schedule service via the outgoing message queue
    """
    # Configure logging for this function
    log = setup_function_logger(log_path, 'Function_process_get_device_scheduled_state_msg')
    print(__name__)
    # Initialize result list
    out_msg_list = []

    # Map message into GDSS message class
    message = GetDeviceScheduledStateMessage(log_path)
    message.complete = msg

    # Modify GDSS message to forward to schedule service
    message.dest_addr = service_addresses['schedule_addr']
    message.dest_port = service_addresses['schedule_port']

    # Load message into output list
    log.debug('Loading completed msg: [%s]', message.complete)
    out_msg_list.append(copy.copy(message.complete))

    # Return response message
    return out_msg_list


# Process get device scheduled state ACK message ******************************
def process_get_device_scheduled_state_msg_ack(log_path, ref_num, devices, msg, service_addresses, message_types):
    """ When a get device scheduled state ACK message is received, this
        function will first check if the command in the message matches the
        last command sent to the device and if a change of state is detected
        it will create a new set device state message to send to the device
        via the outgoing message queue
    """
    # Configure logging for this function
    log = setup_function_logger(log_path, 'Function_process_get_device_scheduled_state_msg_ack')

    # Initialize result list
    out_msg_list = []

    # Map message into LSU message class
    message = GetDeviceScheduledStateMessageACK(log_path)
    message.complete = msg

    # Search device table to find device name
    log.debug('Searching device table for [%s]', message.dev_name)
    dev_pointer = search_device_list(log, devices, message.dev_name)
    log.debug('Match found at device table index: %s', dev_pointer)

    # Update values based on message content
    if dev_pointer is not None:
        log.debug('[%s] found in table at index [%s]', message.dev_name, dev_pointer)

        # Check for command change-of-state
        if devices[dev_pointer].dev_cmd != message.dev_cmd:
            log.debug('New command detected [%s]', message.dev_cmd)
            # Snapshot command so we only issue command message once
            devices[dev_pointer].dev_cmd = copy.copy(message.dev_cmd)

            # Issue messages to wemo servivce for wemo device commands
            if devices[dev_pointer].dev_type == 'wemo_switch':
                # Build new message to forward to wemo service
                log.debug('Generating message to wemo service')
                out_msg = SetDeviceStateMessage(
                    log_path,
                    ref=ref_num.new(),
                    dest_addr=service_addresses['wemo_addr'],
                    dest_port=service_addresses['wemo_port'],
                    source_addr=message.source_addr,
                    source_port=message.source_port,
                    msg_type=message_types['set_device_state'],
                    dev_name=message.dev_name,
                    dev_addr=devices[dev_pointer].dev_addr,
                    dev_cmd=message.dev_cmd,
                    dev_status=devices[dev_pointer].dev_status,
                    dev_last_seen=devices[dev_pointer].dev_last_seen)

                # Load message into output list
                log.debug('Loading completed msg: [%s]', out_msg.complete)
                out_msg_list.append(copy.copy(out_msg.complete))
    else:
        log.debug('Device not in device list: %s', message.dev_name)

    # Return response message
    return out_msg_list
