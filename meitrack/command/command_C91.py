"""
Module for working with the meitrack C91 command
"""
import logging

from meitrack.command.common import Command
from meitrack.common import DIRECTION_SERVER_TO_CLIENT

logger = logging.getLogger(__name__)


class SetIOParamsCommand(Command):
    """
    Class for setting the field names for the set io parameters command
    """
    request_field_names = [
        "command", "model", "device1", "device2", "device3", "device4", "device5",
    ]
    response_field_names = [
        "command", "response",
    ]

    def __init__(self, direction, payload=None, device_type=None):
        """
        Constructor for setting setioparams command parameters
        :param direction: The payload direction.
        :param payload: The payload to parse.
        """
        super(SetIOParamsCommand, self).__init__(direction, payload=payload, device_type=device_type)
        if direction == DIRECTION_SERVER_TO_CLIENT:
            self.field_name_selector = self.request_field_names
        else:
            self.field_name_selector = self.response_field_names

        if payload:
            self.parse_payload(payload)


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
        b"""C91,OK""",
        b"""C91,A78,1:0,2:0,3:0,4:13""",
    ]

    test_command = SetIOParamsCommand(1, b"C91,OK")
    print(test_command.as_bytes())
    print(test_command)
    test_command = SetIOParamsCommand(0, b"C91,A78,1:0,2:0,3:0,4:13,5:13")
    print(test_command.as_bytes())
    print(test_command)


if __name__ == '__main__':
    main()
