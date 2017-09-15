#!/usr/bin/python3
""" service_main.py:
"""

# Import Required Libraries (Standard, Third Party, Local) ********************
import asyncio
import copy
import datetime
import logging
import os
import sys
if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bob_auto_service.tools.log_support import setup_function_logger
from bob_auto_service.messages.log_status_update import LogStatusUpdateMessage

from bob_auto_service.msg_processing import create_heartbeat_msg
from bob_auto_service.msg_processing import process_heartbeat_msg

from bob_auto_service.msg_processing_db import process_log_status_update_msg
from bob_auto_service.msg_processing_db import process_log_status_update_msg_ack
from bob_auto_service.msg_processing_db import process_return_command_msg
from bob_auto_service.msg_processing_db import process_return_command_msg_ack
from bob_auto_service.msg_processing_db import process_update_command_msg
from bob_auto_service.msg_processing_db import process_update_command_msg_ack

from bob_auto_service.msg_processing_wemo import process_get_device_state_msg
from bob_auto_service.msg_processing_wemo import process_get_device_state_msg_ack
from bob_auto_service.msg_processing_wemo import process_set_device_state_msg
from bob_auto_service.msg_processing_wemo import process_set_device_state_msg_ack

from bob_auto_service.msg_processing_schedule import create_get_device_scheduled_state_msg
from bob_auto_service.msg_processing_schedule import process_get_device_scheduled_state_msg
from bob_auto_service.msg_processing_schedule import process_get_device_scheduled_state_msg_ack


# Authorship Info *************************************************************
__author__ = "Christopher Maue"
__copyright__ = "Copyright 2017, The RPi-Home Project"
__credits__ = ["Christopher Maue"]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Christopher Maue"
__email__ = "csmaue@gmail.com"
__status__ = "Development"


# Internal Service Work Task **************************************************
class MainTask(object):
    def __init__(self, log, log_path, **kwargs):
        # Configure logger
        self.log = log
        self.log_path = log_path
        self.log_init = setup_function_logger(self.log_path, 'Class_MainTask_Init')
        self.log_run = setup_function_logger(self.log_path, 'Method_MainTask_Run')
        # Define instance variables
        self.ref_num = None
        self.devices = None
        self.msg_in_queue = None
        self.msg_out_queue = None
        self.service_addresses = []
        self.message_types = []
        self.last_check_schedule = datetime.datetime.now()
        self.last_check_hb = datetime.datetime.now()
        self.sleep_time = 0.2
        self.out_msg = str()
        self.out_msg_list = []
        self.next_msg = str()
        self.next_msg_split = []
        self.msg_source_addr = str()
        self.msg_source_port = str()
        self.msg_type = str()
        self.destinations = []
        self.timestamp_db = datetime.datetime.now() + datetime.timedelta(seconds=-120)
        self.timestamp_schedule = datetime.datetime.now() + datetime.timedelta(seconds=-120)
        self.timestamp_wemo = datetime.datetime.now() + datetime.timedelta(seconds=-120)
        # Map input variables
        if kwargs is not None:
            for key, value in kwargs.items():
                if key == "ref":
                    self.ref_num = value
                    self.log_init.debug('Ref number generator set during __init__ '
                                        'to: %s', self.ref_num)
                if key == "devices":
                    self.devices = value
                    self.log_init.debug('Device list set during __init__ '
                                        'to: %s', self.devices)
                if key == "msg_in_queue":
                    self.msg_in_queue = value
                    self.log_init.debug('Message in queue set during __init__ '
                                        'to: %s', self.msg_in_queue)
                if key == "msg_out_queue":
                    self.msg_out_queue = value
                    self.log_init.debug('Message out queue set during __init__ '
                                        'to: %s', self.msg_out_queue)
                if key == "service_addresses":
                    self.service_addresses = value
                    self.log_init.debug('Service address list set during __init__ '
                                        'to: %s', self.service_addresses)
                if key == "message_types":
                    self.message_types = value
                    self.log_init.debug('Message type list set during __init__ '
                                        'to: %s', self.message_types)

    @asyncio.coroutine
    def run(self):
        """ task to handle the work the service is intended to do """
        self.log_run.info('Starting automation service main task')

        while True:
            # Initialize result list
            self.out_msg_list = []
            self.sleep_time = 0.2
            
            # INCOMING MESSAGE HANDLING
            if self.msg_in_queue.qsize() > 0:
                self.sleep_time = 0.05
                self.log_run.debug('Getting Incoming message from queue')
                self.next_msg = self.msg_in_queue.get_nowait()
                self.log_run.debug('Message pulled from queue: [%s]', self.next_msg)

                # Determine message type
                self.next_msg_split = self.next_msg.split(',')
                if len(self.next_msg_split) >= 6:
                    self.log_run.debug('Extracting source address and message type')
                    self.msg_source_addr = self.next_msg_split[3]
                    self.msg_source_port = self.next_msg_split[4]
                    self.msg_type = self.next_msg_split[5]
                    self.log_run.debug('Source Address: %s', self.msg_source_addr)
                    self.log_run.debug('Source Port: %s', self.msg_source_addr)
                    self.log_run.debug('Message Type: %s', self.msg_type)


                # Process messages from database service
                if self.msg_source_addr == self.service_addresses['database_addr'] \
                    and self.msg_source_port == self.service_addresses['database_port']:


                    # update last-seen timestamp from database service
                    if self.msg_type == self.message_types['heartbeat']:
                        self.log_run.debug('Updating heartbeat timestamp'
                                           'from database service')
                        self.timestamp_db = datetime.datetime.now()

                    # Process log status update message
                    if self.msg_type == self.message_types['log_status_update']:
                        self.log_run.debug('Message is a Log Status Update message')
                        self.out_msg_list = process_log_status_update_msg(
                            self.log_path,
                            self.next_msg,
                            self.service_addresses)

                    # # Process log status update ACK message
                    elif self.msg_type == self.message_types['log_status_update_ack']:
                        self.log_run.debug('Message is a Log Status Update ACK message')
                        process_log_status_update_msg_ack(
                            self.log_path,
                            self.next_msg)

                    # Process return command message
                    elif self.msg_type == self.message_types['return_command']:
                        self.log_run.debug('Message is a Return Command (RC) message')
                        self.out_msg_list = process_return_command_msg(
                            self.log_path,
                            self.next_msg,
                            self.service_addresses)

                    # Process return command ACK message
                    elif self.msg_type == self.message_types['return_command_ack']:
                        self.log_run.debug('Message is a Return Command ACK (RCA) message')
                        self.out_msg_list = process_return_command_msg_ack(
                            self.log_path,
                            self.ref_num,
                            self.devices,
                            self.next_msg,
                            self.service_addresses,
                            self.message_types)

                    # Process update command message
                    elif self.msg_type == self.message_types['update_command']:
                        self.log_run.debug('Message is a Update Command (UC) message')
                        self.out_msg_list = process_update_command_msg(
                            self.log_path,
                            self.next_msg,
                            self.service_addresses)

                    # Process update command ACK message
                    elif self.msg_type == self.message_types['update_command_ack']:
                        self.log_run.debug('Message is a Update Command ACK (UCA) message')
                        process_update_command_msg_ack(
                            self.log_path,
                            self.next_msg)

                    # Que up response messages in outgoing msg que
                    if len(self.out_msg_list) > 0:
                        self.log_run.debug('Queueing response message(s)')
                        for self.out_msg in self.out_msg_list:
                            self.msg_out_queue.put_nowait(copy.copy(self.out_msg))
                            self.log_run.debug('Message [%s] successfully queued', self.out_msg)                            

                # Process messages from wemo service
                if self.msg_source_addr == self.service_addresses['wemo_addr'] \
                    and self.msg_source_port == self.service_addresses['wemo_port']:

                    # update last-seen timestamp from wemo service
                    if self.msg_type == self.message_types['heartbeat']:
                        self.log_run.debug('Updating heartbeat timestamp '
                                       'from wemo service')
                        self.timestamp_wemo = datetime.datetime.now()

                    # Process get device state message
                    if self.msg_type == self.message_types['get_device_state']:
                        self.log_run.debug('Message is a Get Device Status (GDS) message')
                        self.out_msg_list = process_get_device_state_msg(
                            self.log_path,
                            self.next_msg,
                            self.service_addresses)

                    # Process get device state ACK message
                    elif self.msg_type == self.message_types['get_device_state_ack']:
                        self.log_run.debug('Message is a Get Device Status ACK (GDSA) message')
                        self.out_msg_list = process_get_device_state_msg_ack(
                            self.log_path,
                            self.devices,
                            self.next_msg)

                    # Process set device state message
                    elif self.msg_type == self.message_types['set_device_state']:
                        self.log_run.debug('Message is a Set Device Status (SDS) message')
                        self.out_msg_list = process_set_device_state_msg(
                            self.log_path,
                            self.next_msg,
                            self.service_addresses)

                    # Process set device state ACK message
                    elif self.msg_type == self.message_types['set_device_state_ack']:
                        self.log_run.debug('Message is a Set Device Status ACK (SDSA) message')
                        self.out_msg_list = process_set_device_state_msg_ack(
                            self.log_path,
                            self.devices,
                            self.next_msg)

                    # Que up response messages in outgoing msg que
                    if len(self.out_msg_list) > 0:
                        self.log_run.debug('Queueing response message(s)')
                        for self.out_msg in self.out_msg_list:
                            self.msg_out_queue.put_nowait(copy.copy(self.out_msg))
                            self.log_run.debug('Message [%s] successfully queued', self.out_msg)                            

                # Process messages from calendar/schedule service
                if self.msg_source_addr == self.service_addresses['schedule_addr'] \
                    and self.msg_source_port == self.service_addresses['schedule_port']:

                    # update last-seen timestamp from database service
                    if self.msg_type == self.message_types['heartbeat']:
                        self.log_run.debug('Updating heartbeat timestamp '
                                           'from schedule service')
                        self.timestamp_schedule = datetime.datetime.now()

                    # Process get device scheduled state message
                    if self.msg_type == self.message_types['get_device_scheduled_state']:
                        self.log_run.debug('Message is a get device scheduled state message')
                        self.out_msg_list = process_get_device_scheduled_state_msg(
                            self.log_path,
                            self.next_msg,
                            self.service_addresses)

                    # Process get device scheduled state ACK message
                    if self.msg_type == self.message_types['get_device_scheduled_state_ack']:
                        self.log_run.debug('Message is a get device scheduled state ACK message')
                        self.out_msg_list = process_get_device_scheduled_state_msg_ack(
                            self.log_path,
                            self.ref_num,
                            self.devices,
                            self.next_msg,
                            self.service_addresses,
                            self.message_types)

                    # Que up response messages in outgoing msg que
                    if len(self.out_msg_list) > 0:
                        self.log_run.debug('Queueing response message(s)')
                        for self.out_msg in self.out_msg_list:
                            self.msg_out_queue.put_nowait(copy.copy(self.out_msg))
                            self.log_run.debug('Message [%s] successfully queued', self.out_msg)


            # PERIODIC TASKS
            # Periodically send heartbeats to other services
            if datetime.datetime.now() >= (self.last_check_hb + datetime.timedelta(seconds=60)):
                self.destinations = [
                    (self.service_addresses['database_addr'],
                     self.service_addresses['database_port']),
                    (self.service_addresses['motion_addr'],
                     self.service_addresses['motion_port']),
                    (self.service_addresses['nest_addr'],
                     self.service_addresses['nest_port']),
                    (self.service_addresses['occupancy_addr'],
                     self.service_addresses['occupancy_port']),
                    (self.service_addresses['schedule_addr'],
                     self.service_addresses['schedule_port']),
                    (self.service_addresses['wemo_addr'],
                     self.service_addresses['wemo_port'])
                ]
                self.out_msg_list = create_heartbeat_msg(
                    self.log_path,
                    self.ref_num,
                    self.destinations,
                    self.service_addresses['automation_addr'],
                    self.service_addresses['automation_port'],
                    self.message_types)

                # Que up response messages in outgoing msg que
                if len(self.out_msg_list) > 0:
                    self.log_run.debug('Queueing message(s)')
                    for self.out_msg in self.out_msg_list:
                        self.msg_out_queue.put_nowait(copy.copy(self.out_msg))
                        self.log_run.debug('Message [%s] successfully queued', self.out_msg)

                # Update last-check
                self.last_check_hb = datetime.datetime.now()


            # PERIODIC TASKS
            # Periodically check scheduled on/off commands for devices
            if datetime.datetime.now() \
                >= (self.last_check_schedule + datetime.timedelta(minutes=1)):
                self.out_msg_list = create_get_device_scheduled_state_msg(
                    self.log_path,
                    self.ref_num,
                    self.devices,
                    self.service_addresses,
                    self.message_types)

                # Que up response messages in outgoing msg que
                if len(self.out_msg_list) > 0:
                    self.log_run.debug('Queueing message(s)')
                    for self.out_msg in self.out_msg_list:
                        self.msg_out_queue.put_nowait(copy.copy(self.out_msg))
                        self.log_run.debug('Message [%s] successfully queued', self.out_msg)

                # Update last-check
                self.last_check_schedule = datetime.datetime.now()


            # DEVICE STATUS CHANGE OF STATE CHECKS
            # Log any device changes of state to database.  Only log if database
            # service is confirmed alive to avoid data loss (hb received
            # within 120 seconds)
            if datetime.datetime.now() < self.timestamp_db \
                + datetime.timedelta(seconds=120):
                # Initialize outgoing message list
                self.out_msg_list = []
                # Cycle through devices in list looking for changes of state
                for i, d in enumerate(self.devices):
                    # COS detected by comparing stats and last_seen to their memory
                    # values
                    if d.dev_status != d.dev_status_mem or d.dev_last_seen != d.dev_last_seen_mem:
                        # When COS detected, append new LSU message to outgoing list
                        self.log_run.debug('Change of state detected in the status '
                                       'of: %s', d.dev_name)
                        self.out_msg_list.append(
                            copy.copy(
                                LogStatusUpdateMessage(
                                    self.log_path,
                                    ref=self.ref_num.new(),
                                    dest_addr=self.service_addresses['database_addr'],
                                    dest_port=self.service_addresses['database_port'],
                                    source_addr=self.service_addresses['automation_addr'],
                                    source_port=self.service_addresses['automation_port'],
                                    msg_type=self.message_types['log_status_update'],
                                    dev_name=d.dev_name,
                                    dev_addr=d.dev_addr,
                                    dev_status=d.dev_status,
                                    dev_last_seen=d.dev_last_seen
                                ).complete
                            )
                        )
                        # Update values in status_mem and last_seen_mem to prevent
                        # duplicate triggers
                        self.log_run.debug('LSU message for %s created and '
                                       'queued', d.dev_name)
                        self.devices[i].dev_status_mem = copy.copy(d.dev_status)
                        self.devices[i].dev_last_seen_mem = copy.copy(d.dev_last_seen)

                # Que up response messages in outgoing msg que
                if len(self.out_msg_list) > 0:
                    self.log_run.debug('Queueing message(s)')
                    for self.out_msg in self.out_msg_list:
                        self.msg_out_queue.put_nowait(copy.copy(self.out_msg))
                        self.log_run.debug('Message [%s] successfully queued',
                                       self.out_msg)



            # Yield to other tasks for a while
            yield from asyncio.sleep(0.25)
