"""
Module for working with the meitrack A10 command
"""

import logging
from typing import ClassVar

from meitrack.command.common import Command
from meitrack.common import DIRECTION_SERVER_TO_CLIENT

logger = logging.getLogger(__name__)


class LocationQueryCommand(Command):
    """
    Class for setting the field names for the real-time location query command
    """

    request_field_names: ClassVar[list[str]] = [
        "command",
    ]
    response_field_names: ClassVar[list[str]] = [
        "command",
        "response",
    ]

    def __init__(self, direction, payload=None, device_type=None):
        """
        Constructor for setting the location query command parameters
        :param direction: The payload direction.
        :param payload: The payload to parse.
        :param device_type: The device type.
        """
        super().__init__(direction, payload=payload, device_type=device_type)
        if direction == DIRECTION_SERVER_TO_CLIENT:
            self.field_name_selector = self.request_field_names
        else:
            self.field_name_selector = self.response_field_names

        if payload:
            self.parse_payload(payload)


def stc_request_location_command():
    """
    Function to generate real-time location query command
    :return: A10 gprs Command
    >>> stc_request_location_command().as_bytes()
    b'A10'
    >>> stc_request_location_command()
    <meitrack.command.command_A10.LocationQueryCommand object at ...>
    """
    return LocationQueryCommand(0, b"A10")


def main():
    """
    Main section for running interactive testing.
    """
    main_logger = logging.getLogger("")
    main_logger.setLevel(logging.DEBUG)
    char_handler = logging.StreamHandler()
    char_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    char_handler.setFormatter(formatter)
    main_logger.addHandler(char_handler)

    test_command = LocationQueryCommand(0, b"A10")
    print(test_command.as_bytes())
    print(test_command)


if __name__ == "__main__":
    main()
