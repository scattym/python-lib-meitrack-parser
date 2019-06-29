"""
Module for building gprs commands
"""

from meitrack import command
from meitrack.gprs_protocol import GPRS
from meitrack.common import s2b


def stc_request_delete_file(imei, file_name):
    """
    Build request device info gprs message

    :param imei: The imei of the device.
    :param file_name: The name of the file to delete.
    :return: Set gprs message to request device information.

    >>> stc_request_delete_file(b'0407', b'test.file').as_bytes()
    b'@@a24,0407,D02,test.file*F4\\r\\n'
    """
    com = command.stc_file_delete(file_name)
    gprs = GPRS()
    gprs.direction = b'@@'
    gprs.data_identifier = b'a'
    gprs.enclosed_data = com
    gprs.imei = s2b(imei)

    return gprs


def cts_build_file_list(imei, file_name, file_bytes):
    """
    Build message for requesting client file list

    :param imei: The imei of the device
    :param file_name:
    :param file_bytes:
    :return: List of file download commands

    >>> for u in cts_build_file_list(b'0407', b'filename', 1024): u.as_bytes()
    b'$$A32,0407,D00,filename,1,0,1024*F8\\r\\n'
    >>> for u in cts_build_file_list(b'0407', b'filename', 32768): u.as_bytes()
    b'$$A33,0407,D00,filename,1,0,32768*3C\\r\\n'
    """
    com = command.cts_file_download(file_name, 1, 0, file_bytes)
    gprs = GPRS()
    gprs.direction = b'$$'
    gprs.data_identifier = b'A'
    gprs.enclosed_data = com
    gprs.imei = s2b(imei)

    return [gprs]


def stc_set_output_pin(imei, speed=1, pin=0, state=2):
    """
    Build message for setting output pin state

    :param imei: The imei of the device
    :param speed: The maximum speed to apply the change
    :param pin: The pin number to set
    :param state: The state to set the pin to.
    :return: Set pin states gprs command

    >>> stc_set_output_pin(b'0407').as_bytes()
    b'@@b22,0407,C01,1,22222*BA\\r\\n'
    >>> stc_set_output_pin(b'0407', 2).as_bytes()
    b'@@b22,0407,C01,2,22222*BB\\r\\n'
    >>> stc_set_output_pin(b'0407', 2, 3).as_bytes()
    b'@@b22,0407,C01,2,22222*BB\\r\\n'
    >>> stc_set_output_pin(b'0407', 2, 3, 1).as_bytes()
    b'@@b22,0407,C01,2,22212*BA\\r\\n'
    >>> print(stc_set_output_pin(b'0407', 2, 255, 1))
    None
    """
    pins = [2, 2, 2, 2, 2]
    try:
        pins[pin] = state
    except IndexError as _:
        return None
    com = command.stc_set_output_pin(speed, pins[0], pins[1], pins[2], pins[3], pins[4])
    gprs = GPRS()
    gprs.direction = b'@@'
    gprs.data_identifier = b'b'
    gprs.enclosed_data = com
    gprs.imei = s2b(imei)

    return gprs


def stc_set_output_pins(imei, speed=1, output_a=2, output_b=2, output_c=2, output_d=2, output_e=2):
    """
    Build message for setting all output pin states

    :param imei: The imei of the device
    :param speed: The maximum speed to apply the change
    :param output_a: The state of pin 1.
    :param output_b: The state of pin 2.
    :param output_c: The state of pin 3.
    :param output_d: The state of pin 4.
    :param output_e: The state of pin 5.
    :return: Set pin states gprs command

    >>> stc_set_output_pins(b'0407').as_bytes()
    b'@@b22,0407,C01,1,22222*BA\\r\\n'
    >>> stc_set_output_pins(b'0407', 2).as_bytes()
    b'@@b22,0407,C01,2,22222*BB\\r\\n'
    >>> stc_set_output_pins(b'0407', 2, 1, 1, 1, 1, 1).as_bytes()
    b'@@b22,0407,C01,2,11111*B6\\r\\n'
    """
    com = command.stc_set_output_pin(speed, output_a, output_b, output_c, output_d, output_e)
    gprs = GPRS()
    gprs.direction = b'@@'
    gprs.data_identifier = b'b'
    gprs.enclosed_data = com
    gprs.imei = s2b(imei)

    return gprs


def stc_request_device_info(imei):
    """
    Build request device info gprs message

    :param imei: The imei of the device
    :return: Set gprs message to request device information.

    >>> stc_request_device_info(b'0407').as_bytes()
    b'@@a14,0407,E91*42\\r\\n'
    """
    com = command.stc_request_info()
    gprs = GPRS()
    gprs.direction = b'@@'
    gprs.data_identifier = b'a'
    gprs.enclosed_data = com
    gprs.imei = s2b(imei)

    return gprs


def stc_request_get_file(imei, file_name, payload_start_index=0):
    """
    Build request file gprs message

    :param imei: The imei of the device
    :param file_name: The name of the file to request
    :param payload_start_index: The index of the file to download from
    :return: Set gprs message to request file transfer

    >>> stc_request_get_file(b'0407', b'testfile').as_bytes()
    b'@@b25,0407,D00,testfile,0*22\\r\\n'
    >>> stc_request_get_file(b'0407', b'testfile', 72).as_bytes()
    b'@@b26,0407,D00,testfile,72*5C\\r\\n'
    """
    com = command.stc_request_file_download(file_name, payload_start_index)
    gprs = GPRS()
    gprs.direction = b'@@'
    gprs.data_identifier = b'b'
    gprs.enclosed_data = com
    gprs.imei = s2b(imei)

    return gprs


def stc_request_location_message(imei):
    """
    Build request device location gprs message

    :param imei: The imei of the device
    :return: Set gprs message to request device location

    >>> stc_request_location_message(b'0407').as_bytes()
    b'@@c14,0407,A10*37\\r\\n'
    """
    com = command.stc_request_location()
    gprs = GPRS()
    gprs.direction = b'@@'
    gprs.data_identifier = b'c'
    gprs.enclosed_data = com
    gprs.imei = s2b(imei)

    return gprs


def stc_request_photo_list(imei, start=0):
    """
    Build request photo list gprs message

    :param imei: The imei of the device
    :param start: The file list start index
    :return: gprs message to request device file list

    >>> stc_request_photo_list(b'0407').as_bytes()
    b'@@d16,0407,D01,0*99\\r\\n'
    >>> stc_request_photo_list(b'0407', 7).as_bytes()
    b'@@d16,0407,D01,7*A0\\r\\n'
    """
    com = command.stc_request_photo_list(start)
    gprs = GPRS()
    gprs.direction = b'@@'
    gprs.data_identifier = b'd'
    gprs.enclosed_data = com
    gprs.imei = s2b(imei)

    return gprs


def stc_request_take_photo(imei, camera_number, file_name):
    """
    Build request take photo gprs message

    :param imei: The imei of the device
    :param camera_number: The camera index to take the photo
    :param file_name: The file name to store the image as
    :return: gprs message to request device to take a photo

    >>> stc_request_take_photo(b'0407', 1, 'testfile').as_bytes()
    b'@@e25,0407,D03,1,testfile*29\\r\\n'
    """
    com = command.stc_request_take_photo(camera_number, file_name=file_name)
    gprs = GPRS()
    gprs.direction = b'@@'
    gprs.data_identifier = b'e'
    gprs.enclosed_data = com
    gprs.imei = s2b(imei)

    return gprs


# A13
def stc_set_cornering_angle(imei, angle=30):
    """
    Build set cornering angle gprs message

    :param imei: The imei of the device
    :param angle: The angle required to trigger an event
    :return: gprs message to set the cornering angle on a device.

    >>> stc_set_cornering_angle(b'0407').as_bytes()
    b'@@f17,0407,A13,30*CF\\r\\n'
    >>> stc_set_cornering_angle(b'0407', 45).as_bytes()
    b'@@f17,0407,A13,45*D5\\r\\n'
    """
    com = command.stc_set_cornering_angle(angle)
    gprs = GPRS()
    gprs.direction = b'@@'
    gprs.data_identifier = b'f'
    gprs.enclosed_data = com
    gprs.imei = s2b(imei)

    return gprs


# B07
def stc_set_speeding_alert(imei, speed_kmh=0, disabled=True):
    """
    Build set speeding alert gprs message

    :param imei: The imei of the device
    :param speed_kmh: The speed at which to trigger the alert
    :param disabled: Whether or not speeding is disabled.
    :return: gprs message to set the speeding alert speed on a device.

    >>> stc_set_speeding_alert(b'0407').as_bytes()
    b'@@g18,0407,B07,0,1*FF\\r\\n'
    >>> stc_set_speeding_alert(b'0407', 12).as_bytes()
    b'@@g19,0407,B07,12,1*33\\r\\n'
    >>> stc_set_speeding_alert(b'0407', 12, False).as_bytes()
    b'@@g19,0407,B07,12,0*32\\r\\n'
    """
    com = command.stc_set_speeding_alert(speed_kmh, disabled)
    gprs = GPRS()
    gprs.direction = b'@@'
    gprs.data_identifier = b'g'
    gprs.enclosed_data = com
    gprs.imei = s2b(imei)

    return gprs


# B14
def stc_set_idle_alert_time(imei, consecutive_speed_time_secs=0, speed_kmh=0, alert_time_secs=0):
    """
    Build set engine idle alert parameters message

    :param imei: The imei of the device
    :param consecutive_speed_time_secs: The time at speed on which to alert.
    :param speed_kmh: The speed to trigger alerts at
    :param alert_time_secs: The time to alert for.
    :return: gprs message to set the engine idle alert parameters e on a device.

    >>> stc_set_idle_alert_time(b'0407').as_bytes()
    b'@@h20,0407,B14,0,0,0*52\\r\\n'
    >>> stc_set_idle_alert_time(b'0407', 3, 5, 7).as_bytes()
    b'@@h20,0407,B14,3,5,7*61\\r\\n'
    """
    com = command.stc_set_idle_alert_time(consecutive_speed_time_secs, speed_kmh, alert_time_secs)
    gprs = GPRS()
    gprs.direction = b'@@'
    gprs.data_identifier = b'h'
    gprs.enclosed_data = com
    gprs.imei = s2b(imei)

    return gprs


# B15
def stc_set_fatigue_driving_alert_time(imei, consecutive_driving_time_mins=0, alert_time_secs=0, acc_off_time_mins=0):
    """
    Build set fatigure driving alert parameters message

    :param imei: The imei of the device
    :param consecutive_driving_time_mins: The numeber of driving minutes on which to alert.
    :param alert_time_secs: The time to alert for.
    :param acc_off_time_mins: Engine off time
    :return: gprs message to set the fatigure driving alert parameters e on a device.

    >>> stc_set_fatigue_driving_alert_time(b'0407').as_bytes()
    b'@@i20,0407,B15,0,0,0*54\\r\\n'
    >>> stc_set_fatigue_driving_alert_time(b'0407', 3, 5, 7).as_bytes()
    b'@@i20,0407,B15,3,5,7*63\\r\\n'
    """
    com = command.stc_set_fatigue_driving_alert(consecutive_driving_time_mins, alert_time_secs, acc_off_time_mins)
    gprs = GPRS()
    gprs.direction = b'@@'
    gprs.data_identifier = b'i'
    gprs.enclosed_data = com
    gprs.imei = s2b(imei)

    return gprs


# C50
def stc_set_driver_license_type(imei, license_type_str=None):
    """
    Build set drivers license type parameters message

    :param imei: The imei of the device
    :param license_type_str: Comma separated list of allowed license types.
    :return: gprs message to set the drivers license type parameters on a device.

    >>> stc_set_driver_license_type(b'0407').as_bytes()
    b'@@j14,0407,C50*44\\r\\n'
    >>> stc_set_driver_license_type(b'0407', b'3100').as_bytes()
    b'@@j19,0407,C50,3100*39\\r\\n'
    >>> stc_set_driver_license_type(b'0407', b'3100,25,26').as_bytes()
    b'@@j25,0407,C50,3100,25,26*5D\\r\\n'
    """
    com = command.stc_set_driver_license_type(license_type_str)
    gprs = GPRS()
    gprs.direction = b'@@'
    gprs.data_identifier = b'j'
    gprs.enclosed_data = com
    gprs.imei = s2b(imei)

    return gprs


# C52
def stc_set_driver_license_validity_time(imei, validity_time):
    """
    Build set drivers license validity time message

    :param imei: The imei of the device
    :param validity_time: The time a license swipe is valid for..
    :return: gprs message to set the drivers license validity time on a device.

    >>> stc_set_driver_license_type(b'0407').as_bytes()
    b'@@j14,0407,C50*44\\r\\n'
    >>> stc_set_driver_license_type(b'0407', 0).as_bytes()
    b'@@j14,0407,C50*44\\r\\n'
    >>> stc_set_driver_license_type(b'0407', 100).as_bytes()
    b'@@j18,0407,C50,100*05\\r\\n'
    """
    com = command.stc_set_driver_license_validity_time(validity_time)
    gprs = GPRS()
    gprs.direction = b'@@'
    gprs.data_identifier = b'k'
    gprs.enclosed_data = com
    gprs.imei = s2b(imei)

    return gprs


# C91
def stc_set_io_device_params(imei, model, config):
    """
    Build set io device parameters message

    :param imei: The imei of the device
    :param model: The device model for the io parameters to be valid
    :param config: The configuration for the io pins as a tuple
    :return: gprs message to set the io device parameters on a device.

    >>> stc_set_io_device_params(b'0407', b"model", ((1,1), (2,2))).as_bytes()
    b'@@k28,0407,C91,model,1:1,2:2*1E\\r\\n'
    """
    com = command.stc_set_io_device_params(model, config)
    gprs = GPRS()
    gprs.direction = b'@@'
    gprs.data_identifier = b'k'
    gprs.enclosed_data = com
    gprs.imei = s2b(imei)

    return gprs


def stc_set_heartbeat_interval(imei, minutes=0):
    """
    Build set the heartbeat interval message

    :param imei: The imei of the device
    :param minutes: The heartbeat interval in minutes
    :return: gprs message to set the hearbeat interval on a device.

    >>> stc_set_heartbeat_interval(b'0407').as_bytes()
    b'@@l16,0407,A11,0*9F\\r\\n'
    >>> stc_set_heartbeat_interval(b'0407', 3).as_bytes()
    b'@@l16,0407,A11,3*A2\\r\\n'
    """
    com = command.stc_set_heartbeat(minutes)
    gprs = GPRS()
    gprs.direction = b'@@'
    gprs.data_identifier = b'l'
    gprs.enclosed_data = com
    gprs.imei = s2b(imei)

    return gprs


# A14
def stc_set_tracking_by_distance(imei, meters=0):
    """
    Build set the tracking by distance parameters message

    :param imei: The imei of the device
    :param meters: The maximum distance for reporting a location
    :return: gprs message to set the tracking by distance parameters on a device.

    >>> stc_set_tracking_by_distance(b'0407').as_bytes()
    b'@@m16,0407,A14,0*A3\\r\\n'
    >>> stc_set_tracking_by_distance(b'0407', 3).as_bytes()
    b'@@m16,0407,A14,3*A6\\r\\n'
    """
    com = command.stc_set_tracking_by_distance(meters)
    gprs = GPRS()
    gprs.direction = b'@@'
    gprs.data_identifier = b'm'
    gprs.enclosed_data = com
    gprs.imei = s2b(imei)

    return gprs


# B36
def stc_set_time_zone(imei, minutes=0):
    """
    Build set time zone offset message

    :param imei: The imei of the device
    :param minutes: The minutes offset from gmt as a positive or negative value
    :return: gprs message to set the time zone offset parameters on a device.

    >>> stc_set_time_zone(b'0407').as_bytes()
    b'@@n16,0407,B36,0*A9\\r\\n'
    >>> stc_set_time_zone(b'0407', 3).as_bytes()
    b'@@n16,0407,B36,3*AC\\r\\n'
    """
    com = command.stc_set_time_zone(minutes)
    gprs = GPRS()
    gprs.direction = b'@@'
    gprs.data_identifier = b'n'
    gprs.enclosed_data = com
    gprs.imei = s2b(imei)

    return gprs


# B46
# B46,E,T,S,U,D
# E: Event Code, the event code of SOS is 1
# T: The snapshot interval
# S: The number of photos
# U: Decide whether upload the image or not. 0 means don't upload, 1 means to upload
# D: Decide whether delete the image after being uploaded or not, 0 means no deleting, 1 means to delete
def stc_set_snapshot_parameters(imei, event_code=1, interval=60, count=1, upload=1, delete=1):
    """
    Build set the snapshot parameters message

    :param imei: The imei of the device
    :param event_code: The event code for triggering a snapshot
    :param interval: The interval at which to take snapshots
    :param count: The number of snapshots to take
    :param upload: Whether or not to upload the snapshots
    :param delete: Whether or not to delete the snapshots on upload
    :return: gprs message to set the camera snapshot parameters on a device.

    >>> stc_set_snapshot_parameters(b'0407').as_bytes()
    b'@@o25,0407,B46,1,60,1,1,1*55\\r\\n'
    >>> stc_set_snapshot_parameters(b'0407', 3).as_bytes()
    b'@@o25,0407,B46,3,60,1,1,1*57\\r\\n'
    >>> stc_set_snapshot_parameters(b'0407', 3, 5).as_bytes()
    b'@@o24,0407,B46,3,5,1,1,1*25\\r\\n'
    >>> stc_set_snapshot_parameters(b'0407', 3, 5, 7).as_bytes()
    b'@@o24,0407,B46,3,5,7,1,1*2B\\r\\n'
    >>> stc_set_snapshot_parameters(b'0407', 3, 5, 7, 0).as_bytes()
    b'@@o24,0407,B46,3,5,7,0,1*2A\\r\\n'
    >>> stc_set_snapshot_parameters(b'0407', 3, 5, 7, 1, 0).as_bytes()
    b'@@o24,0407,B46,3,5,7,1,0*2A\\r\\n'
    """
    com = command.stc_set_snapshot_parameters(event_code, interval, count, upload, delete)
    gprs = GPRS()
    gprs.direction = b'@@'
    gprs.data_identifier = b'o'
    gprs.enclosed_data = com
    gprs.imei = s2b(imei)

    return gprs


def stc_set_tracking_by_time_interval(imei, deci_seconds=0):
    """
    Build set tracking by time interval message

    :param imei: The imei of the device
    :param deci_seconds: The time between updates in 10 second increments.
    :return: gprs message to set tracking by time interval parameters on a device.

    >>> stc_set_tracking_by_time_interval(b'0407').as_bytes()
    b'@@p16,0407,A12,0*A4\\r\\n'
    >>> stc_set_tracking_by_time_interval(b'0407', 3).as_bytes()
    b'@@p16,0407,A12,3*A7\\r\\n'
    """
    com = command.stc_set_tracking_by_time_interval(deci_seconds)
    gprs = GPRS()
    gprs.direction = b'@@'
    gprs.data_identifier = b'p'
    gprs.enclosed_data = com
    gprs.imei = s2b(imei)

    return gprs


def stc_restart_gsm(imei):
    """
    Build restart gsm on device message

    :param imei: The imei of the device
    :return: gprs message to restart the gsm on a device.

    >>> stc_restart_gsm(b'0407').as_bytes()
    b'@@q14,0407,F01*4A\\r\\n'
    """
    com = command.stc_restart_gsm()
    gprs = GPRS()
    gprs.direction = b'@@'
    gprs.data_identifier = b'q'
    gprs.enclosed_data = com
    gprs.imei = s2b(imei)

    return gprs


def stc_restart_gps(imei):
    """
    Build restart gps on device message

    :param imei: The imei of the device
    :return: gprs message to restart the gps on a device.

    >>> stc_restart_gps(b'0407').as_bytes()
    b'@@r14,0407,F02*4C\\r\\n'
    """
    com = command.stc_restart_gps()
    gprs = GPRS()
    gprs.direction = b'@@'
    gprs.data_identifier = b'r'
    gprs.enclosed_data = com
    gprs.imei = s2b(imei)

    return gprs


def stc_read_photo_event_flags(imei):
    """
    Build restart gps on device message

    :return: gprs message to request photo event flag settings

    >>> stc_read_photo_event_flags(b'0407').as_bytes()
    b'@@u14,0407,B97*59\\r\\n'
    """
    com = command.stc_read_photo_event_flags()
    gprs = GPRS()
    gprs.direction = b'@@'
    gprs.data_identifier = b'u'
    gprs.enclosed_data = com
    gprs.imei = s2b(imei)

    return gprs


def stc_set_photo_event_flags(imei, enabled_events):
    """
    Build restart gps on device message

    :param enabled_events: A zero indexed list of enabled events
    :return: gprs message to restart the gps on a device.

    >>> stc_set_photo_event_flags(b'0407', [0,1,2,15]).as_bytes()
    b'@@s31,0407,B96,1110000000000001*85\\r\\n'
    """
    com = command.stc_set_photo_event_flags(enabled_events)
    gprs = GPRS()
    gprs.direction = b'@@'
    gprs.data_identifier = b's'
    gprs.enclosed_data = com
    gprs.imei = s2b(imei)

    return gprs


def stc_set_photo_event_flags_by_bytes(imei, enabled_event_bytes):
    """
    Build restart gps on device message

    :param enabled_event_bytes: a bytes representation of the enabled events
    :return: gprs message to restart the gps on a device.

    >>> stc_set_photo_event_flags_by_bytes(b'0407', b'111').as_bytes()
    b'@@t18,0407,B96,111*1A\\r\\n'
    """
    com = command.stc_set_photo_event_flags_by_bytes(enabled_event_bytes)
    gprs = GPRS()
    gprs.direction = b'@@'
    gprs.data_identifier = b't'
    gprs.enclosed_data = com
    gprs.imei = s2b(imei)

    return gprs


def stc_request_format_sdcard(imei):
    """
    Build request device info gprs message

    :param imei: The imei of the device.
    :param file_name: The name of the file to delete.
    :return: Set gprs message to request device information.

    >>> stc_request_format_sdcard(b'0407').as_bytes()
    b'@@u14,0407,D83*56\\r\\n'
    """
    com = command.stc_format_sdcard()
    gprs = GPRS()
    gprs.direction = b'@@'
    gprs.data_identifier = b'u'
    gprs.enclosed_data = com
    gprs.imei = s2b(imei)

    return gprs


def main():
    """
    Main section for running interactive testing.
    """
    test_gprs = stc_request_location_message(b"testimei")
    print(test_gprs.as_bytes())
    print(stc_request_device_info(b"0407").as_bytes())
    print(stc_restart_gsm(b"0407").as_bytes())
    print(stc_restart_gps(b"0407").as_bytes())
    print(stc_set_output_pin("0407", 1, 2, 2).as_bytes())
    print(stc_set_output_pin("0407", 2, 3, 4).as_bytes())
    print(stc_set_snapshot_parameters("0407", 2, 30, 2, 1, 1).as_bytes())


if __name__ == '__main__':
    main()
