#!/usr/bin/env python
"""
Module for working with the meitrack commands
"""
import logging
import time

from meitrack.command.command_D00 import FileDownloadCommand
from meitrack.command.common import Command
from meitrack.common import DIRECTION_CLIENT_TO_SERVER, s2b
from meitrack.error import GPRSParameterError

logger = logging.getLogger(__name__)


def stc_format_sdcard():
    """
    Build a file download command based on parameters from device

    :param file_name: The name of the file to delete

    >>> test = stc_format_sdcard(); print(test.as_bytes())
    b'D83'
    """
    return Command(0, b'DB3')


def stc_file_delete(file_name):
    """
    Build a file download command based on parameters from device

    :param file_name: The name of the file to delete

    >>> test = stc_file_delete("test.file"); print(test.as_bytes())
    b'D02,test.file'
    >>> test = stc_file_delete(b"\\xff\\xff\\xff\\x0f\\xff\\xff\\xff\\x0f."); print(test.as_bytes())
    b'D02,\\xff\\xff\\xff\\x0f\\xff\\xff\\xff\\x0f.'
    """
    try:
        file_name = file_name.encode()
    except AttributeError:
        pass
    return Command(0, b','.join([b"D02", file_name]))


def cts_file_download(file_name, num_packets, packet_number, file_bytes):
    """
    Build a file download command based on parameters from device

    :param file_name: The name of the file to download
    :param num_packets: The number of packets to download
    :param packet_number: The starting packet number
    :param file_bytes: The number of bytes in the file.
    :return: FileDownloadCommand object

    >>> test = cts_file_download("test.file", 12, 10, 100); print(test.as_bytes())
    b'D00,test.file,12,10,100'
    """
    file_name = s2b(file_name)
    num_packets = s2b(num_packets)
    packet_number = s2b(packet_number)
    file_bytes = s2b(file_bytes)
    file_download = FileDownloadCommand(DIRECTION_CLIENT_TO_SERVER)
    file_download.build(file_name, num_packets, packet_number, file_bytes)
    return file_download


def stc_set_output_pin(speed, output_a, output_b, output_c, output_d, output_e):
    """
    Build a command to set the status of the output pins.

    :param speed: The maximum speed at which to apply the settings.
    :param output_a: output a status
    :param output_b: output b status
    :param output_c: output c status
    :param output_d: output d status
    :param output_e: output e status
    :return: Set pin status command
    >>> stc_set_output_pin(1, 0, 0, 0, 0, 0).as_bytes()
    b'C01,1,00000'
    """

    command_set = b'%b%b%b%b%b' % (
        s2b(output_a),
        s2b(output_b),
        s2b(output_c),
        s2b(output_d),
        s2b(output_e)
    )
    return Command(0, b','.join([b"C01", s2b(speed), command_set]))


def stc_request_file_download(file_name, payload_start_index):
    """
    Build a file download command for sending to the device

    This will trigger the download of a file from the specified packet
    number.

    :param file_name: The name of the file to download
    :param payload_start_index: The packet number to download from
    :return: file download command to send to the device.

    >>> stc_request_file_download("test.file", 6).as_bytes()
    b'D00,test.file,6'
    """
    try:
        file_name = file_name.encode()
    except AttributeError:
        pass
    if isinstance(payload_start_index, int):
        payload_start_index = str(payload_start_index).encode()

    return Command(0, b','.join([b"D00", file_name, payload_start_index]))


def stc_request_take_photo(camera_number, file_name):
    """
    Build a command to request the client to take a photo.

    Use to trigger a photo event on the client device
    :param camera_number: The number of the camera
    :param file_name: The filename to save the image as
    :return: take photo command object

    >>> stc_request_take_photo(2, "testfile.jpg").as_bytes()
    b'D03,2,testfile.jpg'
    """
    if file_name is None:
        file_name = "camera-{}-{}.jpg".format(camera_number, int(time.time()))
    return Command(0, b"D03," + str(camera_number).encode() + b"," + str(file_name).encode())


def stc_request_photo_list(start=0):
    """
    Build a command to request client file list.

    :param start: File listing index offset
    :return: request file list command

    >>> stc_request_photo_list(7).as_bytes()
    b'D01,7'
    """
    return Command(0, b"D01,%b" % (str(start).encode(),))


def stc_request_location():
    """
    Build a request client location command

    :return: request client location command

    >>> stc_request_location().as_bytes()
    b'A10'
    """
    return Command(0, b"A10")


def stc_restart_gsm():
    """
    Build a restart gsm command

    :return: restart gsm command

    >>> stc_restart_gsm().as_bytes()
    b'F01'
    """
    return Command(0, b"F01")


def stc_restart_gps():
    """
    Build a restart gps command

    :return: restart gps command

    >>> stc_restart_gps().as_bytes()
    b'F02'
    """
    return Command(0, b"F02")


def stc_set_heartbeat(minutes=0):
    """
    Build a set heartbeat interval command

    :param minutes: the hearbeat interval in minutes
    :return: set heartbeart interval command

    >>> stc_set_heartbeat().as_bytes()
    b'A11,0'
    >>> stc_set_heartbeat(4).as_bytes()
    b'A11,4'
    >>> stc_set_heartbeat(65536).as_bytes()
    Traceback (most recent call last):
        ...
    meitrack.error.GPRSParameterError: Heartbeat must be between 0 and 65535. Was 65536
    >>> stc_set_heartbeat(-1).as_bytes()
    Traceback (most recent call last):
        ...
    meitrack.error.GPRSParameterError: Heartbeat must be between 0 and 65535. Was -1

    """
    if minutes < 0 or minutes > 65535:
        raise GPRSParameterError("Heartbeat must be between 0 and 65535. Was %s" % (minutes,))
    return Command(0, b"A11,%b" % (str(minutes).encode(),))


# device1=0, device2=20, device3=11, device4=13, device5=13
def stc_set_io_device_params(model=b"A78", config=((1, 0), (2, 20), (3, 11), (4, 13), (5, 13))):
    """
    Build a set io device parameters command.

    This command is used to configure which peripheral devices are connected to
    the client device.
    :param model: The model number of the peripheral device
    :param config: The configuration for each of the peripheral devices
    :return: set io device parameters command

    >>> stc_set_io_device_params(b"A78").as_bytes()
    b'C91,A78,1:0,2:20,3:11,4:13,5:13'
    >>> stc_set_io_device_params("A78").as_bytes()
    b'C91,A78,1:0,2:20,3:11,4:13,5:13'
    """
    command_bytes = b"C91,%b" % (s2b(model),)
    for item in config:
        command_bytes = b",".join([command_bytes, b"%b:%b" % (s2b(item[0]), s2b(item[1]))])
    return Command(
        0,
        command_bytes
    )


def stc_set_tracking_by_time_interval(deci_seconds=0):
    """
    Build a set tracking by time interval command

    :param deci_seconds: The interval in ten second increments. (example: 5 would be 50 seconds)
    :return: request client location command

    >>> stc_set_tracking_by_time_interval().as_bytes()
    b'A12,0'
    >>> stc_set_tracking_by_time_interval(10).as_bytes()
    b'A12,10'
    >>> stc_set_tracking_by_time_interval(-1).as_bytes()
    Traceback (most recent call last):
        ...
    meitrack.error.GPRSParameterError: Time interval must be between 0 and 65535. Was -1
    >>> stc_set_tracking_by_time_interval(65536).as_bytes()
    Traceback (most recent call last):
        ...
    meitrack.error.GPRSParameterError: Time interval must be between 0 and 65535. Was 65536
    """
    if deci_seconds < 0 or deci_seconds > 65535:
        raise GPRSParameterError("Time interval must be between 0 and 65535. Was %s" % (deci_seconds,))
    return Command(0, b"A12,%b" % (str(deci_seconds).encode(),))


def stc_set_cornering_angle(angle=0):
    """
    Build a set cornering angle command

    :param angle: The minimum angle change to trigger a report
    :return: set cornering angle command

    >>> stc_set_cornering_angle().as_bytes()
    b'A13,0'
    >>> stc_set_cornering_angle(5).as_bytes()
    b'A13,5'
    >>> stc_set_cornering_angle(-1).as_bytes()
    Traceback (most recent call last):
    ...
    meitrack.error.GPRSParameterError: Cornering angle must be between 0 and 359. Was -1
    >>> stc_set_cornering_angle(360).as_bytes()
    Traceback (most recent call last):
    ...
    meitrack.error.GPRSParameterError: Cornering angle must be between 0 and 359. Was 360
    """
    if angle < 0 or angle > 359:
        raise GPRSParameterError("Cornering angle must be between 0 and 359. Was %s" % (angle,))
    return Command(0, b"A13,%b" % (s2b(angle)))


def stc_set_time_zone(minutes=0):
    """
    Build a set time zone command

    Used to set the time zone offset on the device.
    :param minutes: The number of minutes offset from GMT.
    :return: set time zone command

    >>> stc_set_time_zone().as_bytes()
    b'B36,0'
    >>> stc_set_time_zone(60).as_bytes()
    b'B36,60'
    >>> stc_set_time_zone(-32769).as_bytes()
    Traceback (most recent call last):
    ...
    meitrack.error.GPRSParameterError: Timezone offset must be between -32768 and 32768. Was -32769

    >>> stc_set_time_zone(32769).as_bytes()
    Traceback (most recent call last):
    ...
    meitrack.error.GPRSParameterError: Timezone offset must be between -32768 and 32768. Was 32769

    """
    if minutes < -32768 or minutes > 32768:
        raise GPRSParameterError("Timezone offset must be between -32768 and 32768. Was %s" % (minutes,))
    return Command(0, b"B36,%b" % (s2b(minutes),))


# B46,E,T,S,U,D
# E: Event Code, the event code of SOS is 1
# T: The snapshot interval
# S: The number of photos
# U: Decide whether upload the image or not. 0 means don't upload, 1 means to upload
# D: Decide whether delete the image after being uploaded or not, 0 means no deleting, 1 means to delete
def stc_set_snapshot_parameters(event_code=1, interval=60, count=1, upload=1, delete=1):
    """
    Build a set snapshot parameters command

    :param event_code: Event code triggering the snapshot
    :param interval: The interval at which to take snapshots
    :param count: The number of snapshots to take
    :param upload: Decide whether upload the image or not. 0 means don't upload, 1 means to upload
    :param delete: Decide whether delete the image after being uploaded or not, 0 means no deleting, 1 means to delete
    :return: Set snapshot parameters command

    >>> stc_set_snapshot_parameters().as_bytes()
    b'B46,1,60,1,1,1'
    >>> stc_set_snapshot_parameters(9, 120, 3, 1, 0).as_bytes()
    b'B46,9,120,3,1,0'
    """
    return Command(
        0,
        b"B46,%b,%b,%b,%b,%b" % (
            s2b(event_code),
            s2b(interval),
            s2b(count),
            s2b(upload),
            s2b(delete),
        )
    )


def stc_set_fatigue_driving_alert(consecutive_driving_time_mins=0, alert_time_secs=0, acc_off_time_mins=0):
    """
    Build a set fatigure driving alert parameters command

    :param consecutive_driving_time_mins: Alert on driving longer than this in minutes
    :param alert_time_secs: How long to alert for
    :param acc_off_time_mins: Reset alert when engine off for this time
    :return: set fatigue driving alert command

    >>> stc_set_fatigue_driving_alert().as_bytes()
    b'B15,0,0,0'
    >>> stc_set_fatigue_driving_alert(9, 12, 13).as_bytes()
    b'B15,9,12,13'
    >>> stc_set_fatigue_driving_alert(-1, 12, 13).as_bytes()
    Traceback (most recent call last):
    ...
    meitrack.error.GPRSParameterError: Consecutive alert time must be between 0 and 1000. Was -1
    >>> stc_set_fatigue_driving_alert(1001, 12, 13).as_bytes()
    Traceback (most recent call last):
    ...
    meitrack.error.GPRSParameterError: Consecutive alert time must be between 0 and 1000. Was 1001
    >>> stc_set_fatigue_driving_alert(9, -1, 13).as_bytes()
    Traceback (most recent call last):
    ...
    meitrack.error.GPRSParameterError: Alert time must be between 0 and 60000. Was -1
    >>> stc_set_fatigue_driving_alert(9, 60001, 13).as_bytes()
    Traceback (most recent call last):
    ...
    meitrack.error.GPRSParameterError: Alert time must be between 0 and 60000. Was 60001
    >>> stc_set_fatigue_driving_alert(9, 12, -1).as_bytes()
    Traceback (most recent call last):
    ...
    meitrack.error.GPRSParameterError: Acc off time must be between 0 and 1000. Was -1
    >>> stc_set_fatigue_driving_alert(9, 12, 1001).as_bytes()
    Traceback (most recent call last):
    ...
    meitrack.error.GPRSParameterError: Acc off time must be between 0 and 1000. Was 1001
    """
    if consecutive_driving_time_mins is None or consecutive_driving_time_mins < 0 \
            or consecutive_driving_time_mins > 1000:
        raise GPRSParameterError(
            "Consecutive alert time must be between 0 and 1000. Was %s" % (consecutive_driving_time_mins,)
        )
    if alert_time_secs is None or alert_time_secs < 0 or alert_time_secs > 60000:
        raise GPRSParameterError("Alert time must be between 0 and 60000. Was %s" % (alert_time_secs,))
    if acc_off_time_mins is None or acc_off_time_mins < 0 or acc_off_time_mins > 1000:
        raise GPRSParameterError("Acc off time must be between 0 and 1000. Was %s" % (acc_off_time_mins,))
    return Command(
        0,
        b"B15,%b,%b,%b" % (
            s2b(consecutive_driving_time_mins),
            s2b(alert_time_secs),
            s2b(acc_off_time_mins),
        )
    )


def stc_set_idle_alert_time(consecutive_speed_time_secs=0, speed_kmh=0, alert_time_secs=0):
    """
    Build a set engine idle alert command

    :param consecutive_speed_time_secs: The consecutive time at the speed
    :param speed_kmh: The speed at which to alert at
    :param alert_time_secs: The time to alert for
    :return: set engine idle alert command

    >>> stc_set_idle_alert_time().as_bytes()
    b'B14,0,0,0'
    >>> stc_set_idle_alert_time(3, 5, 7).as_bytes()
    b'B14,3,5,7'
    >>> stc_set_idle_alert_time(-1, 5, 7).as_bytes()
    Traceback (most recent call last):
    ...
    meitrack.error.GPRSParameterError: Consecutive speed time must be between 0 and 60000. Was -1
    >>> stc_set_idle_alert_time(60001, 5, 7).as_bytes()
    Traceback (most recent call last):
    ...
    meitrack.error.GPRSParameterError: Consecutive speed time must be between 0 and 60000. Was 60001
    >>> stc_set_idle_alert_time(3, -1, 7).as_bytes()
    Traceback (most recent call last):
    ...
    meitrack.error.GPRSParameterError: Speed must be between 0 and 200. Was -1
    >>> stc_set_idle_alert_time(3, 201, 7).as_bytes()
    Traceback (most recent call last):
    ...
    meitrack.error.GPRSParameterError: Speed must be between 0 and 200. Was 201
    >>> stc_set_idle_alert_time(3, 5, -1).as_bytes()
    Traceback (most recent call last):
    ...
    meitrack.error.GPRSParameterError: Alert time must be between 0 and 60000. Was -1
    >>> stc_set_idle_alert_time(3, 5, 60001).as_bytes()
    Traceback (most recent call last):
    ...
    meitrack.error.GPRSParameterError: Alert time must be between 0 and 60000. Was 60001
    """
    if consecutive_speed_time_secs is None or consecutive_speed_time_secs < 0 or consecutive_speed_time_secs > 60000:
        raise GPRSParameterError(
            "Consecutive speed time must be between 0 and 60000. Was %s" % (consecutive_speed_time_secs,)
        )
    if speed_kmh is None or speed_kmh < 0 or speed_kmh > 200:
        raise GPRSParameterError("Speed must be between 0 and 200. Was %s" % (speed_kmh,))
    if alert_time_secs is None or alert_time_secs < 0 or alert_time_secs > 60000:
        raise GPRSParameterError("Alert time must be between 0 and 60000. Was %s" % (alert_time_secs,))

    return Command(
        0,
        b"B14,%b,%b,%b" % (
            s2b(consecutive_speed_time_secs),
            s2b(speed_kmh),
            s2b(alert_time_secs),
        )
    )


def stc_set_speeding_alert(speed_kmh=0, disabled=True):
    """
    Build a set speeding alert command

    :param speed_kmh: The speed to alert at
    :param disabled: (bool) True if functionality is disabled
    :return: set speeding alert command

    >>> stc_set_speeding_alert().as_bytes()
    b'B07,0,1'
    >>> stc_set_speeding_alert(10).as_bytes()
    b'B07,10,1'
    >>> stc_set_speeding_alert(10, False).as_bytes()
    b'B07,10,0'
    >>> stc_set_speeding_alert(-1).as_bytes()
    Traceback (most recent call last):
    ...
    meitrack.error.GPRSParameterError: Speed must be between 0 and 255. Was -1
    >>> stc_set_speeding_alert(256).as_bytes()
    Traceback (most recent call last):
    ...
    meitrack.error.GPRSParameterError: Speed must be between 0 and 255. Was 256
    >>> stc_set_speeding_alert(10, 10).as_bytes()
    Traceback (most recent call last):
    ...
    meitrack.error.GPRSParameterError: Disabled must be True or False. Was 10
    """
    if speed_kmh is None or speed_kmh < 0 or speed_kmh > 255:
        raise GPRSParameterError("Speed must be between 0 and 255. Was %s" % (speed_kmh,))
    if disabled is None or (disabled not in [True, False]):
        raise GPRSParameterError("Disabled must be True or False. Was %s" % (speed_kmh,))

    if disabled is True:
        disabled_value = "1"
    else:
        disabled_value = "0"

    return Command(
        0,
        b"B07,%b,%b" % (
            s2b(speed_kmh),
            s2b(disabled_value),
        )
    )


def stc_set_driver_license_type(license_type_str=""):
    """
    Build a set drivers license command
    :param license_type_str: Comma separated list of allowed types
    :return: set drivers license command

    >>> stc_set_driver_license_type().as_bytes()
    b'C50'
    >>> stc_set_driver_license_type("3200,35").as_bytes()
    b'C50,3200,35'
    """

    if license_type_str:
        return Command(0, b"C50,%b" % (s2b(license_type_str),))

    return Command(0, b"C50")


def stc_set_driver_license_validity_time(validity_time=0):
    """
    Build a set drivers license validity time

    :param validity_time: The validitiy time in X
    :return: set drivers license validity command
    >>> stc_set_driver_license_validity_time().as_bytes()
    b'C52'
    >>> stc_set_driver_license_validity_time(12).as_bytes()
    b'C52,12'
    """
    if validity_time:
        return Command(0, b"C52,%b" % (s2b(validity_time),))

    return Command(0, b"C52")


def stc_set_tracking_by_distance(meters=0):
    """
    Build a command to set tracking by distance change.
    :param meters: The distance in meters to trigger the event
    :return: set tracking distance command

    >>> stc_set_tracking_by_distance().as_bytes()
    b'A14,0'
    >>> stc_set_tracking_by_distance(7).as_bytes()
    b'A14,7'
    >>> stc_set_tracking_by_distance(-1).as_bytes()
    Traceback (most recent call last):
    ...
    meitrack.error.GPRSParameterError: Tracking by distance must be between 0 and 65535. Was -1
    >>> stc_set_tracking_by_distance(65536).as_bytes()
    Traceback (most recent call last):
    ...
    meitrack.error.GPRSParameterError: Tracking by distance must be between 0 and 65535. Was 65536
    """
    if meters < 0 or meters > 65535:
        raise GPRSParameterError("Tracking by distance must be between 0 and 65535. Was %s" % (meters,))
    return Command(0, b"A14,%b" % (s2b(meters),))


def stc_request_info():
    """
    Build a request client device information command

    :return: request client information command

    >>> stc_request_info().as_bytes()
    b'E91'
    """
    return Command(0, b"E91")


# B97
def stc_read_photo_event_flags():
    """
    Build a request client device information command

    :return: request client photo event flag settings

    >>> stc_read_photo_event_flags().as_bytes()
    b'B97'
    """

    return Command(0, b"B97")


# B96,0000000000000001
def stc_set_photo_event_flags(enabled_events):
    """
    Build a request client device information command

    :param enabled_events: List of event numbers that are enabled
    :return: request client information command

    >>> stc_set_photo_event_flags([1,3,5,7,13,16]).as_bytes()
    b'B96,0101010100000100'
    """
    flag_bytes = b""
    for i in range(0, 16):
        if i in enabled_events:
            flag_bytes = b"%b1" % (flag_bytes,)
        else:
            flag_bytes = b"%b0" % (flag_bytes,)
    return Command(0, b"B96,%b" % (flag_bytes,))


# B96,0000000000000001
def stc_set_photo_event_flags_by_bytes(enabled_event_bytes):
    """
    Build a request client device information command

    :param enabled_event_bytes: a bytes representation of the enabled events
    :return: request client information command

    >>> stc_set_photo_event_flags_by_bytes(b'0101').as_bytes()
    b'B96,0101'
    >>> stc_set_photo_event_flags_by_bytes('0102').as_bytes()
    b'B96,0102'
    """
    return Command(0, b"B96,%b" % (s2b(enabled_event_bytes),))


def main():
    """
    Main section for running interactive testing.
    """
    main_logger = logging.getLogger('')
    main_logger.setLevel(logging.DEBUG)
    char_handler = logging.StreamHandler()
    char_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    char_handler.setFormatter(formatter)
    main_logger.addHandler(char_handler)

    print(stc_request_file_download(b"test_file", b"0"))
    print(stc_request_file_download(b"test_file", 0))
    print(stc_set_io_device_params(b"A78", ((1, 0), (2, 20), (3, 11), (4, 13), (5, 13))))
    print(stc_set_io_device_params(b"A78", [[1, 0], [2, 20], [3, 11], [4, 13], [5, 13]]))
    print(stc_set_snapshot_parameters())

    import doctest
    doctest.testmod()


if __name__ == '__main__':
    main()
