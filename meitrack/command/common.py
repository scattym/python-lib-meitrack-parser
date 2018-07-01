import datetime
import logging

from meitrack.command.event import event_to_name, event_to_id
from meitrack.error import GPRSParseError
from license.cardreader import License

logger = logging.getLogger(__name__)


class TaxiMeterData(object):
    def __init__(self, payload=None):
        self.assisted_info = None
        self.start_time = None
        self.end_time = None
        self.fare = None
        self.trip_time = None
        self.wait_time = None
        if payload is not None:
            self.parse(payload)

    def parse(self, payload):
        fields = payload.split('|')
        if len(fields) >= 2:
            self.assisted_info = fields[0]
            self.start_time = fields[1]
        if len(fields) >= 7:
            self.end_time = fields[3]
            self.fare = fields[4]
            self.trip_time = fields[5]
            self.wait_time = fields[6]


class Command(object):
    def __init__(self, direction, payload=None):
        self.payload = payload
        self.direction = direction
        self.field_name_selector = []
        self.field_dict = {}

    def __str__(self):
        result_str = ""
        result_str = "%s\n" % (self.payload,)
        for field in self.field_name_selector:
            result_str += "\tField %s has value %s\n" % (field, self.field_dict.get(field))
        return result_str

    def as_bytes(self):
        fields = []
        if self.field_name_selector:
            for field in self.field_name_selector:
                if self.field_dict.get(field):
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


def meitrack_date_to_datetime(date_time):
    # yymmddHHMMSS
    try:
        date_time = "%s%s" % (date_time.decode(), "Z")
        d = datetime.datetime.strptime(date_time, "%y%m%d%H%M%SZ")
        return d
    except UnicodeDecodeError as err:
        logger.error("Unable to convert datetime field to a string %s", date_time)
    except ValueError as err:
        logger.error("Unable to calculate date from string %s", date_time)
    return None


def datetime_to_meitrack_date(date_time):
    return date_time.strftime("%y%m%d%H%M%S").encode()
