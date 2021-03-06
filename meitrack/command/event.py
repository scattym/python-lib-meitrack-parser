"""
Library for managing event codes and mappings to text
"""
import logging
from functools import singledispatch

logger = logging.getLogger(__name__)

EVENT_MAP_T333 = {
    1: "SOS Button Pressed",
    2: "Input 2 Active",
    3: "Engine On",
    4: "Input 4 Active",
    5: "Input 5 Active",
    9: "SOS Button Released",
    10: "Input 2 Inactive",
    11: "Engine Off",
    12: "Input 4 Inactive",
    13: "Input 5 Inactive",
    17: "Low Battery",
    18: "Low External Battery",
    19: "Speeding",
    20: "Enter Geo-fence",
    21: "Exit Geo-fence",
    22: "External Battery On",
    23: "External Battery Cut",
    24: "GPS Signal Lost",
    25: "GPS Signal Recovery",
    26: "Enter Sleep",
    27: "Exit Sleep",
    28: "GPS Antenna Cut",
    29: "Device Reboot",
    31: "Heartbeat",
    32: "Cornering",
    33: "Track By Distance",
    34: "Reply Current (Passive)",
    35: "Track By Time Interval",
    36: "Tow",
    37: "RFID",
    39: "Photo",
    40: "Power Off",
    41: "Stop Moving",
    42: "Start Moving",
    44: "GSM Jamming",
    50: "Temperature High",
    51: "Temperature Low",
    52: "Full Fuel",
    53: "Low Fuel",
    54: "Fuel Theft",
    56: "Armed",
    57: "Disarmed",
    58: "Vehicle Theft",
    63: "No GSM Jamming",
    65: "Press Input 1 (SOS) to Call",
    66: "Press Input 2 to Call",
    67: "Press Input 3 to Call",
    68: "Press Input 4 to Call",
    69: "Press Input 5 to Call",
    70: "Reject Incoming Call",
    71: "Get Location by Call",
    72: "Auto Answer Incoming Call",
    73: "Listen-in (Voice Monitoring)",
    79: "Fall",
    80: "Install",
    81: "Drop Off",
    109: "Taxi Meter Data",
    129: "Harsh Braking",
    130: "Harsh Acceleration",
    133: "Idle Overtime",
    134: "Idle Recovery",
    135: "Fatigue Driving",
    136: "Enough Rest After Fatigue Driving",
    139: "Maintenance Notice",
    144: "Ignition On",
    145: "Ignition Off",
}

EVENT_MAP_T366 = {
    1: "SOS Button Pressed",
    2: "Engine On",
    3: "Input 3 Active",
    4: "Input 4 Active",
    5: "Input 5 Active",
    9: "SOS Button Released",
    10: "Engine Off",
    11: "Input 3 Inactive",
    12: "Input 4 Inactive",
    13: "Input 5 Inactive",
    17: "Low Battery",
    18: "Low External Battery",
    19: "Speeding",
    20: "Enter Geo-fence",
    21: "Exit Geo-fence",
    22: "External Battery On",
    23: "External Battery Cut",
    24: "GPS Signal Lost",
    25: "GPS Signal Recovery",
    26: "Enter Sleep",
    27: "Exit Sleep",
    28: "GPS Antenna Cut",
    29: "Device Reboot",
    31: "Heartbeat",
    32: "Cornering",
    33: "Track By Distance",
    34: "Reply Current (Passive)",
    35: "Track By Time Interval",
    36: "Tow",
    37: "RFID",
    39: "Photo",
    40: "Power Off",
    41: "Stop Moving",
    42: "Start Moving",
    44: "GSM Jamming",
    50: "Temperature High",
    51: "Temperature Low",
    52: "Full Fuel",
    53: "Low Fuel",
    54: "Fuel Theft",
    56: "Armed",
    57: "Disarmed",
    58: "Vehicle Theft",
    63: "No GSM Jamming",
    65: "Press Input 1 (SOS) to Call",
    66: "Press Input 2 to Call",
    67: "Press Input 3 to Call",
    68: "Press Input 4 to Call",
    69: "Press Input 5 to Call",
    70: "Reject Incoming Call",
    71: "Get Location by Call",
    72: "Auto Answer Incoming Call",
    73: "Listen-in (Voice Monitoring)",
    79: "Fall",
    80: "Install",
    81: "Drop Off",
    109: "Taxi Meter Data",
    129: "Harsh Braking",
    130: "Harsh Acceleration",
    133: "Idle Overtime",
    134: "Idle Recovery",
    135: "Fatigue Driving",
    136: "Enough Rest After Fatigue Driving",
    139: "Maintenance Notice",
    144: "Ignition On",
    145: "Ignition Off",
}

EVENT_MAP_T366G = EVENT_MAP_T366.copy()


@singledispatch
def event_to_name(event_code: int, event_map: dict=EVENT_MAP_T333) -> str:
    """
    Function to convert event code as an integer to a event name string
    :param event_code: The event code
    :param event_map: The event mapping table to use
    :return: The name of the event as a string.
    >>> event_to_name(145)
    'Ignition Off'
    >>> event_to_name("145")
    'Ignition Off'
    >>> event_to_name(b"145")
    'Ignition Off'
    >>> event_to_name(b"3")
    'Engine On'
    >>> event_to_name(b"2", EVENT_MAP_T366)
    'Engine On'
    """
    return_str = event_map.get(event_code)
    if not return_str:
        logger.error("Unable to lookup event code %s", event_code)

    return return_str


@event_to_name.register(str)
def _(event_code: str, event_map: dict=EVENT_MAP_T333) -> str:
    """
    Function to convert event code as an string to a event name string
    :param event_code: The event code
    :param event_map: The event mapping table to use
    :return: The name of the event as a string.
    """
    try:
        lookup_value = int(event_code)
        return event_to_name(lookup_value, event_map=event_map)
    except ValueError as err:
        logger.error("Unable to process integer from string %s with error: %s", event_code, err)


@event_to_name.register(bytes)
def _(event_code: bytes, event_map: dict=EVENT_MAP_T333) -> str:
    """
    Function to convert event code as an byte string to a event name string
    :param event_code: The event code
    :param event_map: The event mapping table to use
    :return: The name of the event as a string.
    """
    try:
        lookup_value = int(event_code.decode())
        return event_to_name(lookup_value, event_map=event_map)
    except ValueError as err:
        logger.error("Unable to process integer from bytes %s with error %s", event_code, err)


@singledispatch
def event_to_id(event_code: int) -> int:
    """
    Function to convert event code as an integer to a event code integer
    :param event_code: The event code
    :return: The event code as an integer.
    >>> event_to_id(145)
    145
    >>> event_to_id("145")
    145
    >>> event_to_id(b"145")
    145
    """
    return event_code


@event_to_id.register(str)
def _(event_code: str) -> str:
    """
    Function to convert event code as a string to a event code string
    :param event_code: The event code
    :return: The name of the event as a string.
    """
    try:
        lookup_value = int(event_code)
        return event_to_id(lookup_value)
    except ValueError as err:
        logger.error("Unable to process integer from string %s with error: %s", event_code, err)


@event_to_id.register(bytes)
def _(event_code: bytes) -> str:
    """
    Function to convert event code as a byte string to a event code string
    :param event_code: The event code
    :return: The name of the event as a string.
    """
    try:
        lookup_value = int(event_code.decode())
        return event_to_id(lookup_value)
    except ValueError as err:
        logger.error("Unable to process integer from bytes %s with error: %s", event_code, err)


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

    for key in EVENT_MAP_T333:
        print(event_to_name(key))
        print(event_to_name(str(key).encode()))
        print(event_to_name(str(key)))
    print(event_to_name(None))

    print(event_to_name(2, EVENT_MAP_T366))
    print(event_to_name(b'2', EVENT_MAP_T366))
    print(event_to_name('2', EVENT_MAP_T366))


if __name__ == "__main__":
    main()


