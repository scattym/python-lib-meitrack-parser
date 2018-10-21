"""
Module for working with the meitrack E91 command
"""
import logging

from meitrack.command.common import Command
from meitrack.common import DIRECTION_SERVER_TO_CLIENT

logger = logging.getLogger(__name__)


class RequestDeviceInfoCommand(Command):
    """
    Class for setting the field names for the request device info command
    """
    request_field_names = [
        "command"
    ]
    response_field_names = [
        "command", "firmware_version", "serial_number"
    ]

    def __init__(self, direction, payload=None):
        """
        Constructor for setting the request device info parameters
        :param direction: The payload direction.
        :param payload: The payload to parse.
        """

        super(RequestDeviceInfoCommand, self).__init__(direction, payload=payload)
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
        b"""E91""",
        b"""E91,FWV1.00,12345678""",
    ]

    test_command = RequestDeviceInfoCommand(0, b"E91")
    print(test_command.as_bytes())
    print(test_command)
    test_command = RequestDeviceInfoCommand(1, b"E91,FWV1.00,12345678")
    print(test_command.as_bytes())
    print(test_command)


if __name__ == '__main__':
    """
    Main section for running interactive testing.
    """
    main()
