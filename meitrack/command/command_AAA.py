"""
Module for working with the meitrack AAA command
"""
import copy
import logging

from meitrack.command.common import Command
from meitrack.error import GPRSParseError

logger = logging.getLogger(__name__)


class TrackerCommand(Command):
    """
    Class for setting the field names for the location update command
    """
    field_names = [
        "command", "event_code", "latitude", "longitude", "date_time", "pos_status", "num_sats",
        "gsm_signal_strength", "speed", "direction", "horizontal_accuracy", "altitude", "mileage",
        "run_time", "base_station_info", "io_port_status", "analog_input_value", "assisted_event_info",
        "customized_data", "protocol_version", "fuel_percentage",
        "temp_sensors", "max_acceleration_value", "max_deceleration_value",
        "unknown_1", "unknown_2", "unknown_3", "unknown_4", "unknown_5",
    ]

    field_names_50_51 = [
        "command", "event_code", "latitude", "longitude", "date_time", "pos_status", "num_sats",
        "gsm_signal_strength",  "speed", "direction", "horizontal_accuracy", "altitude", "mileage",
        "run_time", "base_station_info", "io_port_status", "analog_input_value", "assisted_event_info",
        "temperature_sensor_number", "customized_data", "protocol_version", "fuel_percentage",
        "temp_sensors", "max_acceleration_value", "max_deceleration_value",
        "unknown_1", "unknown_2", "unknown_3", "unknown_4", "unknown_5",
    ]

    field_names_39 = [
        "command", "event_code", "latitude", "longitude", "date_time", "pos_status", "num_sats",
        "gsm_signal_strength", "speed", "direction", "horizontal_accuracy", "altitude", "mileage",
        "run_time", "base_station_info", "io_port_status", "analog_input_value",
        "file_name",
        "customized_data", "protocol_version", "fuel_percentage",
        "temp_sensors", "max_acceleration_value", "max_deceleration_value", "unknown_1",
        "unknown_2", "unknown_3", "unknown_4", "unknown_5",
    ]

    field_names_37 = [
        "command", "event_code", "latitude", "longitude", "date_time", "pos_status", "num_sats",
        "gsm_signal_strength", "speed", "direction", "horizontal_accuracy", "altitude", "mileage",
        "run_time", "base_station_info", "io_port_status", "analog_input_value",
        "rfid",
        "customized_data", "protocol_version", "fuel_percentage",
        "temp_sensors", "max_acceleration_value", "max_deceleration_value", "unknown_1",
        "unknown_2", "unknown_3", "unknown_4", "unknown_5",
    ]

    field_names_109 = [
        "command", "event_code", "latitude", "longitude", "date_time", "pos_status", "num_sats",
        "gsm_signal_strength", "speed", "direction", "horizontal_accuracy", "altitude", "mileage",
        "run_time", "base_station_info", "io_port_status", "analog_input_value",
        "customized_data", "unknown_data", "protocol_version", "fuel_percentage",
        "temp_sensors", "max_acceleration_value", "max_deceleration_value",
        "unknown_1", "unknown_2", "unknown_3", "unknown_4", "taxi_meter_data",
    ]

    def __init__(self, direction, payload=None, device_type=None):
        """
        Constructor for setting tracker command parameters
        :param direction: The payload direction.
        :param payload: The payload to parse.
        """
        super(TrackerCommand, self).__init__(direction, payload=payload, device_type=device_type)
        self.field_name_selector = None

        if payload:
            self.parse_payload(payload)

    def parse_payload(self, payload, max_split=None):
        """
        Override the base parse payload for the AAA command.

        The AAA command complexities live in this file to avoid large blocks in the Command class.
        :param payload: The payload of the message
        :param max_split: The maximum number of times to split fields. Unused in this function
        :return: None
        """
        fields = payload.split(b',')
        if len(fields) < 2:
            raise GPRSParseError("Field length does not include event code", self.payload)
        logger.log(13, "Fields is {}".format(fields[1]))

        if fields[1] in [b"50", b"51"]:
            self.field_name_selector = copy.deepcopy(self.field_names_50_51)
        elif fields[1] in [b"37"]:
            logger.log(13, "Setting AAA fields for license data payload")
            self.field_name_selector = copy.deepcopy(self.field_names_37)
        elif fields[1] in [b"39"]:
            logger.log(13, "Setting AAA fields for file event payload")
            self.field_name_selector = copy.deepcopy(self.field_names_39)
        elif fields[1] in [B"109"]:
            logger.log(13, "Setting AAA fields for taxi data event payload")
            self.field_name_selector = copy.deepcopy(self.field_names_109)
        else:
            logger.log(13, "Setting AAA to default fields")
            self.field_name_selector = copy.deepcopy(self.field_names)

        super(TrackerCommand, self).parse_payload(payload)


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

    tests = [
        b"""AAA,39,-33.815786,151.200165,180427170921,A,9,12,0,15,0.8,71,5146,263808,505|2|7D07|041C15F3,0100,"""
        b"""0000|0000|0000|018D|0505,180427100921_C1E1_N2U1D1.jpg,108,0000,3,0,0|0000|0000|0000|0000|0000""",

        b"""AAA,35,24.819116,121.026091,180323023615,A,7,16,0,176,1.3,83,7,1174,466|97|527B|01035DB4,0000,"""
        b"""0001|0000|0000|019A|0981,00000001,,3,,,36,23""",

        b"""AAA,35,24.819173,121.026060,180323060454,A,8,12,0,24,1.4,60,108,12757,466|97|527B|01035DB3,0000,"""
        b"""0001|0000|0000|019C|0984,00000001,,3,,,44,39""",

        b"""AAA,35,24.819173,121.026053,180323060554,A,8,12,0,189,0.9,59,108,12817,466|97|527B|01036CAB,0000,"""
        b"""0000|0000|0000|019D|0983,00000001,,3,,,90,47""",

        b"""AAA,50,24.819116,121.026091,180323023615,A,7,16,0,176,1.3,83,7,1174,466|97|527B|01035DB4,0000,"""
        b"""0001|0000|0000|019A|0981,00000001,,,3,,,36,23""",

        b"""AAA,35,24.818910,121.025936,180329052345,A,7,13,0,16,1.2,69,2720,86125,466|97|527B|01035DB4,0000,"""
        b"""0001|0000|0000|019E|097F,00000001,,3,,,124,96""",

        b"""AAA,39,-33.815810,151.200128,180427173414,A,8,8,0,21,0.9,67,5186,265282,505|2|7D07|041C15F0,0000,"""
        b"""0000|0000|0000|018D|0505,180427103414_C1E1_N3U1D1.jpg,,108,0000,,3,0,,0|0000|0000|0000|0000|0000""",

        b"""AAA,39,-33.815773,151.200181,180701062906,A,4,8,0,358,5.3,76,30202,425125,505|3|00FA|04E381F5,0400,"""
        b"""0000|0000|0000|018D|0579,180701062906_C1E109_N1U1D1.jpg,,108,0000,,3,0,,0|0000|0000|0000|0000|0000""",

        b"""AAA,109,-33.815813,151.200110,180616124101,A,8,15,0,351,0.9,68,25412,269659,505|3|00FA|04E381F5,0000,"""
        b"""0000|0000|0000|0189|0562,,,108,0000,,6,0,,0|0000|0000|0000|0000|0000,,,20|180616124105""",

        b"""AAA,37,-33.815805,151.200151,180701053440,A,4,10,0,208,19.1,68,29899,421883,505|3|00FA|04E381F5,0500,"""
        b"""0000|0000|0000|018A|0576,%  ^ABCDEFGHI JKLMNOP MR.^^?;6007555100500461157=999919770704="""
        b"""?+  3100            1            58005563  00101?,,108,0000,,3,0,,0|0000|0000|0000|0000|0000""",

        b"""AAA,109,-33.815773,151.200181,180701062059,A,4,8,0,358,5.3,76,30202,424633,505|3|00FA|04E381F5,0400,"""
        b"""0000|0000|0000|018A|0577,,,108,0000,,6,0,,0|0000|0000|0000|0000|0000,,,20|180622144950""",

        b"""AAA,109,-33.815773,151.200181,180701062919,A,4,8,0,358,5.3,76,30202,425133,505|3|00FA|04E381F5,0400,"""
        b"""0000|0000|0000|018D|0579,,,108,0000,,6,0,,0|0000|0000|0000|0000|0000,,,21|180622110810|180622110810|"""
        b"""1000|60|010000|003000""",
    ]

    for test in tests:
        print("{}".format(test))
        test_command = TrackerCommand(0, test)
        # print(test_command.get_battery_voltage())
        # print(test_command.get_battery_level())
        # print(test_command["latitude"])
        # print(test_command.as_bytes())
        for field in test_command.field_dict:
            print("{} {}".format(field, test_command.field_dict[field]))


if __name__ == '__main__':
    main()
