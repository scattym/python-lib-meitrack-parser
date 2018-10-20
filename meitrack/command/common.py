import binascii

import datetime
import logging

from meitrack.common import b2s
from meitrack.command.event import event_to_name, event_to_id
from meitrack.error import GPRSParseError
from license.cardreader import License

logger = logging.getLogger(__name__)


class TaxiMeterData(object):
    def __init__(self, payload=None):
        self.assisted_info = None
        self.start_time = None
        self.end_time = None
        self.fare_distance = None
        self.fare_price = None
        self.fare_trip_time = None
        self.fare_waiting_time = None
        if payload is not None:
            self.parse(payload)

    def parse(self, payload):
        fields = payload.split(b'|')
        if len(fields) >= 2:
            self.assisted_info = fields[0]
            self.start_time = fields[1]
        if len(fields) >= 7:
            self.end_time = fields[2]
            self.fare_distance = fields[3]
            self.fare_price = fields[4]
            self.fare_trip_time = fields[5]
            self.fare_waiting_time = fields[6]

    def get_start_time(self):
        return meitrack_date_to_datetime(self.start_time)

    def get_end_time(self):
        if self.end_time:
            return meitrack_date_to_datetime(self.end_time)

    def get_fare_distance(self):
        if self.fare_distance:
            return self.fare_distance.decode()

    def get_fare_price(self):
        if self.fare_price:
            return self.fare_price.decode()

    def get_fare_trip_time(self):
        if self.fare_trip_time:
            if len(self.fare_trip_time) == 6:
                return ":".join([
                    self.fare_trip_time[0:2].decode(),
                    self.fare_trip_time[2:4].decode(),
                    self.fare_trip_time[4:].decode()
                ])

    def get_fare_waiting_time(self):
        if self.fare_waiting_time:
            if len(self.fare_waiting_time) == 6:
                return ":".join([
                    self.fare_waiting_time[0:2].decode(),
                    self.fare_waiting_time[2:4].decode(),
                    self.fare_waiting_time[4:].decode()
                ])


class Command(object):
    def __init__(self, direction, payload=None):
        self.payload = payload
        self.direction = direction
        self.field_name_selector = []
        self.field_dict = {}

    def __str__(self):
        result_str = "%s\n" % (self.payload,)
        for field in self.field_name_selector:
            result_str += "\tField %s has value %s\n" % (field, self.field_dict.get(field))
        return result_str

    def as_bytes(self):
        fields = []
        if self.field_name_selector:
            for field in self.field_name_selector:
                if self.field_dict.get(field) is not None:
                    if field == "date_time":
                        logger.log(13, "Date field is %s", self.field_dict.get(field))
                        fields.append(datetime_to_meitrack_date(self.field_dict.get(field)))
                    else:
                        fields.append(self.field_dict.get(field))
        if fields:
            return b','.join(fields)
        else:
            return self.payload

    def __getitem__(self, item):
        if item in self.field_dict:
            return self.field_dict[item]
        return None
        # raise AttributeError("Field %s not set" % (item,))

    def __getattr__(self, item):
        if item in self.field_dict:
            return self.field_dict[item]
        return None
        # raise AttributeError("Field %s not set" % (item,))

    def parse_payload(self, payload, max_split=None):
        if max_split:
            fields = payload.split(b',', max_split)
        else:
            fields = payload.split(b',')
        if len(fields) < 1:
            raise GPRSParseError("Field length does not include event code", self.payload)
        if self.field_name_selector is None:
            logger.log(13, "No field names set")
            return

        if len(self.field_name_selector) < len(fields):
            logger.log(13, "%s %s", len(fields), len(self.field_name_selector))
            logger.log(13, payload)
            raise GPRSParseError(
                "Incorrect number of fields for data. Data field length is ", len(fields),
                " but should be ", len(self.field_name_selector), ". Fields should be ",
                str(self.field_name_selector), ", Data was: ", str(payload)
            )
        for i in range(0, len(fields)):
            field_name = self.field_name_selector[i]
            if field_name == "date_time":
                self.field_dict[field_name] = meitrack_date_to_datetime(fields[i])
            else:
                self.field_dict[field_name] = fields[i]

    def get_analog_input_value(self, input_number):
        if self.field_dict.get("analog_input_value"):
            analog_list = self.field_dict.get("analog_input_value").split(b"|")
            if input_number <= len(analog_list):
                logger.debug(analog_list[input_number-1])
                logger.debug(int(analog_list[input_number-1], 16))
                return int(analog_list[input_number-1], 16) / 100

    def get_battery_voltage(self):
        return self.get_analog_input_value(4)

    def get_battery_level(self):
        battery_voltage = self.get_battery_voltage()
        if battery_voltage:
            return int(self.get_battery_voltage() / 4.2 * 100)

    def get_base_station_info(self):
        if self.field_dict.get("base_station_info"):
            fields = self.field_dict.get("base_station_info").split(b"|")
            if len(fields) == 4:
                return_dict = {
                    "mcc": fields[0],
                    "mnc": fields[1],
                    "lac": str(int(fields[2], 16)).encode(),
                    "ci": str(int(fields[3], 16)).encode(),
                    "gsm_signal_strength": self.get_gsm_signal_strength()
                }
                return return_dict

    def get_gsm_signal_strength(self):
        if self.field_dict.get("gsm_signal_strength"):
            return self.field_dict.get("gsm_signal_strength")

    def get_file_data(self):
        if self.field_dict.get("file_bytes"):
            return (
                self.field_dict.get("file_name"),
                self.field_dict.get("number_of_data_packets"),
                self.field_dict.get("data_packet_number"),
                self.field_dict.get("file_bytes")
            )
        else:
            return None, None, None, None

    def get_file_list(self):
        if self.field_dict.get("file_list"):
            return (
                self.field_dict.get("number_of_data_packets"),
                self.field_dict.get("data_packet_number"),
                self.field_dict.get("file_list")
            )
        else:
            return None, None, None

    def get_event_id(self):
        if self.field_dict.get("event_code"):
            return event_to_id(self.field_dict.get("event_code"))

    def get_event_name(self):
        if self.field_dict.get("event_code"):
            return event_to_name(self.field_dict.get("event_code"))

    def get_firmware_version(self):
        return self.field_dict.get("firmware_version")

    def get_serial_number(self):
        return self.field_dict.get("serial_number")

    def get_taxi_meter_data(self):
        if self.field_dict.get("taxi_meter_data"):
            return TaxiMeterData(self.field_dict.get("taxi_meter_data"))

    def get_license_data(self):
        if self.field_dict.get("rfid"):
            return License(self.field_dict.get("rfid"))

    def is_response_error(self):
        return False

    # "io_port_status", "analog_input_value"
    def get_digital_pin_states(self):
        if self.field_dict.get("io_port_status"):
            return meitrack_digital_pins_to_dict(self.field_dict.get("io_port_status"))

    def get_analogue_pin_states(self):
        if self.field_dict.get("analog_input_value"):
            return meitrack_analogue_pins_to_dict(b"0000|0000|0000|018D|0579")


# Example: 0400
def meitrack_digital_pins_to_dict(io_string):
    """
    Function to convert meitrack digital pin report to a dictionary of pin states

    :param io_string: The hexadecimal representation of the pin states
    :return: a dictionary of pin states

    >>> meitrack_digital_pins_to_dict(b'0400')
    {0: False, 1: False, 2: False, 3: False, 4: False, 5: False, 6: False, 7: False, 8: False, 9: False, 10: True, 11: False, 12: False, 13: False, 14: False, 15: False}
    """
    mapping = {}
    try:
        bytes = binascii.unhexlify(io_string)
    except binascii.Error:
        return {}

    for i, byte in enumerate(bytes[::-1]):
        logger.debug("byte is %s", byte)
        for j in range(0, 8):
            if (byte >> j & 1) == 1:
                logger.debug("bit on %s %s", i, j)
                mapping[i*8+j] = True
            else:
                mapping[i*8+j] = False

    return mapping


# Example: 0400
def meitrack_analogue_pins_to_dict(io_string):
    """
    Function to convert meitrack analogue pin report to a dictionary of pin states

    :param io_string: The hexadecimal representation of the pin states
    :return: a dictionary of pin states

    >>> meitrack_analogue_pins_to_dict(b'0400')
    {0: 10.24}
    """
    mapping = {}
    fields = io_string.split(b'|')
    for i, field in enumerate(fields):
        mapping[i] = int(field, 16) / 100

    return mapping


def meitrack_date_to_datetime(date_time):
    """
    Function to convert a meitrack datetime to a python datetime object
    :param date_time: Byte representation of a meitrack datetime
    :return: python datetime object.
    >>> meitrack_date_to_datetime(b'770704000000')
    datetime.datetime(1977, 7, 4, 0, 0)
    >>> meitrack_date_to_datetime('770704000000')
    datetime.datetime(1977, 7, 4, 0, 0)
    """
    # yymmddHHMMSS
    try:
        date_time_str = b2s(date_time)
        date_time_str_utc = "%s%s" % (date_time_str, "Z")
        d = datetime.datetime.strptime(date_time_str_utc, "%y%m%d%H%M%SZ")
        return d
    except UnicodeDecodeError as err:
        logger.error("Unable to convert datetime field to a string %s", date_time)
    except ValueError as err:
        logger.error("Unable to calculate date from string %s", date_time)
    return None


def datetime_to_meitrack_date(date_time):
    """
    Function to convert a datetime object to the meitrack date format

    :param date_time: The input date time object
    :return: Byte representation of the date.

    >>> datetime_to_meitrack_date(datetime.datetime(1977, 7, 4, 0, 0))
    b'770704000000'
    """
    return date_time.strftime("%y%m%d%H%M%S").encode()


if __name__ == "__main__":
    print(meitrack_digital_pins_to_dict(b"0401"))
    print(meitrack_digital_pins_to_dict(b"04011"))
    print(meitrack_digital_pins_to_dict(b"0003"))
    print(meitrack_analogue_pins_to_dict(b"0000|0000|0000|018D|0579"))