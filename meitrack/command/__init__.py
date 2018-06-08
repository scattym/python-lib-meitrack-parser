#!/usr/bin/env python
import logging

import sys
import time

from meitrack import event
from meitrack.command.command_AAA import TrackerCommand
from meitrack.command.command_D00 import FileDownloadCommand
from meitrack.command.command_D01 import FileListCommand
from meitrack.command.command_E91 import RequestDeviceInfoCommand
from meitrack.command.command_FC0 import AuthOtaUpdateCommand
from meitrack.command.command_FC1 import SendOtaDataCommand
from meitrack.command.command_FC2 import ObtainOtaChecksumCommand
from meitrack.command.command_FC3 import StartOtaUpdateCommand
from meitrack.command.command_FC4 import CancelOtaUpdateCommand
from meitrack.command.command_FC5 import CheckDeviceCodeCommand
from meitrack.command.command_FC6 import CheckFirmwareVersionCommand
from meitrack.command.command_FC7 import SetOtaServerCommand
from meitrack.command.common import Command
from meitrack.common import DIRECTION_CLIENT_TO_SERVER
from meitrack.error import GPRSParameterError

logger = logging.getLogger(__name__)

COMMAND_LIST = {
    b"A10": {"name": "Real-Time Location Query", "class": None},
    b"A11": {"name": "Setting a Heartbeat Packet Reporting Interval", "class": None},
    b"A12": {"name": "Tracking by Time Interval", "class": None},
    b"A13": {"name": "Setting the Cornering Report Function", "class": None},
    b"A14": {"name": "Tracking by Distance", "class": None},
    b"A15": {"name": "Setting the Parking Scheduled Tracking Function", "class": None},
    b"A16": {"name": "Enabling the Parking Scheduled Tracking Function", "class": None},
    b"A21": {"name": "Setting GPRS Parameters", "class": None},
    b"A22": {"name": "Setting the DNS Server IP Address", "class": None},
    b"A23": {"name": "Setting the Standby GPRS Server", "class": None},
    b"A70": {"name": "Reading All Authorized Phone Numbers", "class": None},
    b"A71": {"name": "Setting Authorized Phone Numbers", "class": None},
    b"A73": {"name": "Setting the Smart Sleep Mode", "class": None},
    b"AAA": {"name": "Automatic Event Report", "class": TrackerCommand},
    b"AFF": {"name": "Deleting a GPRS Event in the Buffer", "class": None},
    b"B05": {"name": "Setting a Geo-Fence", "class": None},
    b"B06": {"name": "Deleting a Geo-Fence", "class": None},
    b"B07": {"name": "Setting the Speeding Alarm Function", "class": None},
    b"B08": {"name": "Setting the Towing Alarm Function", "class": None},
    b"B21": {"name": "Setting the Anti-Theft Function", "class": None},
    b"B34": {"name": "Setting a Log Interval", "class": None},
    b"B35": {"name": "Setting the SMS Time Zone", "class": None},
    b"B36": {"name": "Setting the GPRS Time Zone", "class": None},
    b"B60": {"name": "Checking the Engine First to Determine Tracker Running Status", "class": None},
    b"B99": {"name": "Setting Event Authorization", "class": None},
    b"C01": {"name": "Controlling Output Status", "class": None},
    b"C02": {"name": "Notifying the Tracker of Sending an SMS", "class": None},
    b"C03": {"name": "Setting a GPRS Event Transmission Mode", "class": None},
    b"C08": {"name": "Setting I/O Port Status", "class": None},
    b"C40": {"name": "Registering a Temperature Sensor Number", "class": None},
    b"C41": {"name": "Deleting a Registered Temperature Sensor", "class": None},
    b"C42": {"name": "Reading the Temperature Sensor SN and Number", "class": None},
    b"C43": {"name": "Setting a Temperature Value for the High/Low Temperature Alarm and Logical Name", "class": None},
    b"C44": {"name": "Reading Temperature Sensor Parameters", "class": None},
    b"C46": {"name": "Checking Temperature Sensor Parameters", "class": None},
    b"D00": {"name": "File download command", "class": FileDownloadCommand},
    b"D01": {"name": "File list command", "class": FileListCommand},
    b"D10": {"name": "Authorizing an iButton key", "class": None},
    b"D11": {"name": "Authorizing iButton Keys in Batches", "class": None},
    b"D12": {"name": "Checking iButton Authorization", "class": None},
    b"D13": {"name": "Reading an Authorized iButton Key", "class": None},
    b"D14": {"name": "Deleting an Authorized iButton Key", "class": None},
    b"D15": {"name": "Deleting Authorized iButton Keys in Batches", "class": None},
    b"D16": {"name": "Checking the Checksum of the Authorized iButton ID Database", "class": None},
    b"D34": {"name": "Setting Idling Time", "class": None},
    b"D71": {"name": "Setting GPS Data Filtering", "class": None},
    b"D72": {"name": "Setting Output Triggering", "class": None},
    b"D73": {"name": "Allocating GPRS Cache and GPS LOG Storage Space", "class": None},
    b"E91": {"name": "Reading Device's Firmware Version and SN", "class": RequestDeviceInfoCommand},
    b"FC0": {"name": "Auth ota update", "class": AuthOtaUpdateCommand},
    b"FC1": {"name": "Auth ota update", "class": SendOtaDataCommand},
    b"FC2": {"name": "Auth ota update", "class": ObtainOtaChecksumCommand},
    b"FC3": {"name": "Auth ota update", "class": StartOtaUpdateCommand},
    b"FC4": {"name": "Auth ota update", "class": CancelOtaUpdateCommand},
    b"FC5": {"name": "Auth ota update", "class": CheckDeviceCodeCommand},
    b"FC6": {"name": "Auth ota update", "class": CheckFirmwareVersionCommand},
    b"FC7": {"name": "Auth ota update", "class": SetOtaServerCommand},
    b"F01": {"name": "Restarting the GSM Module", "class": None},
    b"F02": {"name": "Restarting the GPS Module", "class": None},
    b"F08": {"name": "Setting the Mileage and Run Time", "class": None},
    b"F09": {"name": "Deleting SMS/GPRS Cache Data", "class": None},
    b"F11": {"name": "Restoring Initial Settings", "class": None},
}


def command_to_object(direction, command_type, payload):
    logger.log(13, "command type: %s, with payload %s", command_type, payload)
    if command_type in COMMAND_LIST and COMMAND_LIST[command_type]["class"] is not None:
        return COMMAND_LIST[command_type]["class"](direction, payload)
    else:
        return Command(direction, payload)


def cts_file_download(file_name, num_packets, packet_number, file_bytes):
    try:
        file_name = file_name.encode()
    except AttributeError:
        pass
    try:
        num_packets = str(num_packets).encode()
    except AttributeError:
        pass
    try:
        packet_number = str(packet_number).encode()
    except AttributeError:
        pass
    try:
        file_bytes = file_bytes.encode()
    except AttributeError:
        pass
    file_download = FileDownloadCommand(DIRECTION_CLIENT_TO_SERVER)
    file_download.build(file_name, num_packets, packet_number, file_bytes)
    return file_download


def stc_request_file_download(file_name, payload_start_index):
    try:
        file_name = file_name.encode()
    except AttributeError:
        pass
    if isinstance(payload_start_index, int):
        payload_start_index = str(payload_start_index).encode()

    return Command(0, b','.join([b"D00", file_name, payload_start_index]))


def stc_request_take_photo(camera_number, file_name):
    if file_name is None:
        file_name = "camera-{}-{}.jpg".format(camera_number, int(time.time()))
    return Command(0, b"D03," + str(camera_number).encode() + b"," + str(file_name).encode())


def stc_request_photo_list(start=0):
    return Command(0, b"D01,%b" % (str(start).encode(),))


def stc_request_location():
    return Command(0, b"A10")


def stc_set_heartbeat(minutes=0):
    if minutes < 0 or minutes > 65535:
        raise GPRSParameterError("Heartbeat must be between 0 and 65535. Was %s" % (minutes,))
    return Command(0, b"A11,%b" % (str(minutes).encode(),))


def stc_set_tracking_by_time_interval(deci_seconds=0):
    if deci_seconds < 0 or deci_seconds > 65535:
        raise GPRSParameterError("Time interval must be between 0 and 65535. Was %s" % (deci_seconds,))
    return Command(0, b"A12,%b" % (str(deci_seconds).encode(),))


# TODO: Should the following be %b or %s for the byte string replacement
def stc_set_cornering_angle(angle=0):
    if angle < 0 or angle > 359:
        raise GPRSParameterError("Cornering angle must be between 0 and 359. Was %s" % (angle,))
    return Command(0, b"A13,%s" % (str(angle).encode(),))


# TODO: Should the following be %b or %s for the byte string replacement
def stc_set_time_zone(minutes=0):
    if minutes < -32768 or minutes > 32768:
        raise GPRSParameterError("Timezone offset must be between -32768 and 32768. Was %s" % (minutes,))
    return Command(0, b"B36,%s" % (str(minutes).encode(),))


def stc_set_fatigue_driving_alert(consecutive_driving_time_mins=0, alert_time_secs=0, acc_off_time_mins=0):
    if consecutive_driving_time_mins is None or consecutive_driving_time_mins < 0 or consecutive_driving_time_mins > 1000:
        raise GPRSParameterError("Consecutive alert time must be between 0 and 1000. Was %s" % (consecutive_driving_time_mins,))
    if alert_time_secs is None or alert_time_secs < 0 or alert_time_secs > 60000:
        raise GPRSParameterError("Alert time must be between 0 and 60000. Was %s" % (alert_time_secs,))
    if acc_off_time_mins is None or acc_off_time_mins < 0 or acc_off_time_mins > 1000:
        raise GPRSParameterError("Acc off time must be between 0 and 1000. Was %s" % (alert_time_secs,))
    # TODO: Should the following be %b or %s for the byte string replacement
    return Command(
        0,
        b"B15,%s,%s,%s" % (
            str(consecutive_driving_time_mins).encode(),
            str(alert_time_secs).encode(),
            str(acc_off_time_mins).encode(),
        )
    )


def stc_set_idle_alert_time(consecutive_speed_time_secs=0, speed_kmh=0, alert_time_secs=0):
    if consecutive_speed_time_secs is None or consecutive_speed_time_secs < 0 or consecutive_speed_time_secs > 60000:
        raise GPRSParameterError("Consecutive speed time must be between 0 and 60000. Was %s" % (consecutive_speed_time_secs,))
    if speed_kmh is None or speed_kmh < 0 or speed_kmh > 200:
        raise GPRSParameterError("Speed must be between 0 and 200. Was %s" % (speed_kmh,))
    if alert_time_secs is None or alert_time_secs < 0 or alert_time_secs > 60000:
        raise GPRSParameterError("Alert time must be between 0 and 60000. Was %s" % (alert_time_secs,))

    # TODO: Should the following be %b or %s for the byte string replacement
    return Command(
        0,
        b"B14,%s,%s,%s" % (
            str(consecutive_speed_time_secs).encode(),
            str(speed_kmh).encode(),
            str(alert_time_secs).encode(),
        )
    )


def stc_set_speeding_alert(speed_kmh=0, disabled=True):
    if speed_kmh is None or speed_kmh < 0 or speed_kmh > 255:
        raise GPRSParameterError("Speed must be between 0 and 255. Was %s" % (speed_kmh,))
    if disabled is None or (disabled not in [True, False]):
        raise GPRSParameterError("Disabled must be True or False. Was %s" % (speed_kmh,))

    if disabled is True:
        disabled_value = "1"
    else:
        disabled_value = "0"
    # TODO: Should the following be %b or %s for the byte string replacement
    return Command(
        0,
        b"B07,%s,%s" % (
            str(speed_kmh).encode(),
            str(disabled_value).encode(),
        )
    )


def stc_set_driver_license_type(license_type_str=""):
    if license_type_str:
        # TODO: Should the following be %b or %s for the byte string replacement
        return Command(0, b"C50,%s" % (str(license_type_str).encode(),))
    else:
        return Command(0, b"C50")


def stc_set_driver_license_validity_time(validity_time=0):
    if validity_time:
        # TODO: Should the following be %b or %s for the byte string replacement
        return Command(0, b"C52,%s" % (str(validity_time).encode(),))
    else:
        return Command(0, b"C52")


def stc_set_tracking_by_distance(meters=0):
    if meters < 0 or meters > 65535:
        raise GPRSParameterError("Tracking by distance must be between 0 and 65535. Was %s" % (meters,))
    return Command(0, b"A14,%s" % (str(meters).encode(),))


def stc_request_info():
    return Command(0, b"E91")


if __name__ == '__main__':
    log_level = 11 - 11

    logger = logging.getLogger('')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    for each_command in COMMAND_LIST:
        print("%s: %s" % (each_command, COMMAND_LIST[each_command]))

    print(stc_request_file_download(b"test_file", b"0"))
    print(stc_request_file_download(b"test_file", 0))
