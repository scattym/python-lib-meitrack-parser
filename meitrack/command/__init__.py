#!/usr/bin/env python
import logging
import time

from meitrack.command.command_D00 import FileDownloadCommand
from meitrack.command.common import Command
from meitrack.common import DIRECTION_CLIENT_TO_SERVER
from meitrack.error import GPRSParameterError

logger = logging.getLogger(__name__)


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


def stc_restart_gsm():
    return Command(0, b"F01")


def stc_restart_gps():
    return Command(0, b"F02")


def stc_set_heartbeat(minutes=0):
    if minutes < 0 or minutes > 65535:
        raise GPRSParameterError("Heartbeat must be between 0 and 65535. Was %s" % (minutes,))
    return Command(0, b"A11,%b" % (str(minutes).encode(),))


# device1=0, device2=20, device3=11, device4=13, device5=13
def stc_set_io_device_params(model=b"A78", config=((1, 0), (2, 20), (3, 11), (4, 13), (5, 13))):
    command_bytes = b"C91,%b" % (model,)
    for item in config:
        command_bytes = b",".join([command_bytes, b"%b:%b" % (str(item[0]).encode(), str(item[1]).encode())])
    return Command(
        0,
        command_bytes
    )


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

    print(stc_request_file_download(b"test_file", b"0"))
    print(stc_request_file_download(b"test_file", 0))
    print(stc_set_io_device_params(b"A78", ((1, 0), (2, 20), (3, 11), (4, 13), (5, 13))))
    print(stc_set_io_device_params(b"A78", [[1, 0], [2, 20], [3, 11], [4, 13], [5, 13]]))

