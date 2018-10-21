"""
Module for converting meitrack gprs commands to Command objects
"""
import logging

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
from meitrack.common import DIRECTION_CLIENT_TO_SERVER, DIRECTION_SERVER_TO_CLIENT

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
    b"FC1": {"name": "Send ota data", "class": SendOtaDataCommand},
    b"FC2": {"name": "Obtain ota checksum", "class": ObtainOtaChecksumCommand},
    b"FC3": {"name": "Start ota update", "class": StartOtaUpdateCommand},
    b"FC4": {"name": "Cancel ota update", "class": CancelOtaUpdateCommand},
    b"FC5": {"name": "Check device code", "class": CheckDeviceCodeCommand},
    b"FC6": {"name": "Check firmware version", "class": CheckFirmwareVersionCommand},
    b"FC7": {"name": "Set ota server", "class": SetOtaServerCommand},
    b"F01": {"name": "Restarting the GSM Module", "class": None},
    b"F02": {"name": "Restarting the GPS Module", "class": None},
    b"F08": {"name": "Setting the Mileage and Run Time", "class": None},
    b"F09": {"name": "Deleting SMS/GPRS Cache Data", "class": None},
    b"F11": {"name": "Restoring Initial Settings", "class": None},
}


def command_to_object(direction, command_type, payload):
    """
    Function for converting a command byte strings to a command object.
    :param direction: Direction of message, client to server or server to client.
    :param command_type: The type of command to generate
    :param payload: The command payload to parse.
    :return: A command object from the incoming payload
    >>> command_to_object(DIRECTION_SERVER_TO_CLIENT, b"A11", b'A11,0').as_bytes()
    b'A11,0'
    >>> command_to_object(DIRECTION_SERVER_TO_CLIENT, b"A11", b'A11,0')
    <meitrack.command.common.Command object at ...>
    >>> command_to_object(DIRECTION_CLIENT_TO_SERVER, b"AAA", b'').as_bytes()
    b''
    >>> command_to_object(DIRECTION_CLIENT_TO_SERVER, b"AAA", b'')
    <meitrack.command.command_AAA.TrackerCommand object at ...>
    """
    logger.log(13, "command type: %s, with payload %s", command_type, payload)
    if command_type in COMMAND_LIST and COMMAND_LIST[command_type]["class"] is not None:
        return COMMAND_LIST[command_type]["class"](direction, payload)
    else:
        return Command(direction, payload)


def main():
    """
    Main section for running interactive testing.
    """
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


if __name__ == '__main__':
    """
    Main section for running interactive testing.
    """
    main()
