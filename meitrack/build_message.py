from meitrack import command
from meitrack.gprs_protocol import GPRS
from meitrack.common import s2b


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
    com = command.stc_set_idle_alert_time(consecutive_speed_time_secs, speed_kmh, alert_time_secs)
    gprs = GPRS()
    gprs.direction = b'@@'
    gprs.data_identifier = b'h'
    gprs.enclosed_data = com
    gprs.imei = s2b(imei)

    return gprs


# B15
def stc_set_fatigue_driving_alert_time(imei, consecutive_driving_time_mins=0, alert_time_secs=0, acc_off_time_mins=0):
    com = command.stc_set_fatigue_driving_alert(consecutive_driving_time_mins, alert_time_secs, acc_off_time_mins)
    gprs = GPRS()
    gprs.direction = b'@@'
    gprs.data_identifier = b'i'
    gprs.enclosed_data = com
    gprs.imei = s2b(imei)

    return gprs


# C50
def stc_set_driver_license_type(imei, license_type_str=None):
    com = command.stc_set_driver_license_type(license_type_str)
    gprs = GPRS()
    gprs.direction = b'@@'
    gprs.data_identifier = b'j'
    gprs.enclosed_data = com
    gprs.imei = s2b(imei)

    return gprs


# C52
def stc_set_driver_license_validity_time(imei, validity_time):
    com = command.stc_set_driver_license_validity_time(validity_time)
    gprs = GPRS()
    gprs.direction = b'@@'
    gprs.data_identifier = b'k'
    gprs.enclosed_data = com
    gprs.imei = s2b(imei)

    return gprs


# C91
def stc_set_io_device_params(imei, model, config):
    com = command.stc_set_io_device_params(model, config)
    gprs = GPRS()
    gprs.direction = b'@@'
    gprs.data_identifier = b'k'
    gprs.enclosed_data = com
    gprs.imei = s2b(imei)

    return gprs


def stc_set_heartbeat_interval(imei, minutes=0):
    com = command.stc_set_heartbeat(minutes)
    gprs = GPRS()
    gprs.direction = b'@@'
    gprs.data_identifier = b'l'
    gprs.enclosed_data = com
    gprs.imei = s2b(imei)

    return gprs


# A14
def stc_set_tracking_by_distance(imei, meters=0):
    com = command.stc_set_tracking_by_distance(meters)
    gprs = GPRS()
    gprs.direction = b'@@'
    gprs.data_identifier = b'm'
    gprs.enclosed_data = com
    gprs.imei = s2b(imei)

    return gprs


# B36
def stc_set_time_zone(imei, minutes=0):
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
    com = command.stc_set_snapshot_parameters(event_code, interval, count, upload, delete)
    gprs = GPRS()
    gprs.direction = b'@@'
    gprs.data_identifier = b'o'
    gprs.enclosed_data = com
    gprs.imei = s2b(imei)

    return gprs


def stc_set_tracking_by_time_interval(imei, deci_seconds=0):
    com = command.stc_set_tracking_by_time_interval(deci_seconds)
    gprs = GPRS()
    gprs.direction = b'@@'
    gprs.data_identifier = b'p'
    gprs.enclosed_data = com
    gprs.imei = s2b(imei)

    return gprs


def stc_restart_gsm(imei):
    com = command.stc_restart_gsm()
    gprs = GPRS()
    gprs.direction = b'@@'
    gprs.data_identifier = b'q'
    gprs.enclosed_data = com
    gprs.imei = s2b(imei)

    return gprs


def stc_restart_gps(imei):
    com = command.stc_restart_gps()
    gprs = GPRS()
    gprs.direction = b'@@'
    gprs.data_identifier = b'r'
    gprs.enclosed_data = com
    gprs.imei = s2b(imei)

    return gprs


if __name__ == '__main__':
    test_gprs = stc_request_location_message(b"testimei")
    print(test_gprs.as_bytes())
    print(stc_request_device_info(b"0407").as_bytes())
    print(stc_restart_gsm(b"0407").as_bytes())
    print(stc_restart_gps(b"0407").as_bytes())
    print(stc_set_output_pin("0407", 1, 2, 2).as_bytes())
    print(stc_set_output_pin("0407", 2, 3, 4).as_bytes())
    print(stc_set_snapshot_parameters("0407", 2, 30, 2, 1, 1).as_bytes())
