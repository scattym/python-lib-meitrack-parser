"""
Module for working with the meitrack FC5 command
"""
import binascii
import logging

from meitrack.command.common import Command
from meitrack.common import DIRECTION_SERVER_TO_CLIENT, DIRECTION_CLIENT_TO_SERVER

logger = logging.getLogger(__name__)


class CheckDeviceCodeCommand(Command):
    """
    Class for setting the field names for the check device code command
    """
    request_field_names = [
        "command"
    ]
    response_field_names = [
        "command", "device_code",
    ]

    def __init__(self, direction, payload=None):
        """
        Constructor for setting the check device code command parameters
        :param direction: The payload direction.
        :param payload: The payload to parse.
        """

        super(CheckDeviceCodeCommand, self).__init__(direction, payload=payload)
        if direction == DIRECTION_SERVER_TO_CLIENT:
            self.field_name_selector = self.request_field_names
        else:
            self.field_name_selector = self.response_field_names

        if payload:
            self.parse_payload(payload, 2)

    def ota_response_device_code(self):
        """
        Function to return the device code from a check device code response message
        :return: The device code or None
        """
        if self.direction == DIRECTION_CLIENT_TO_SERVER and self.field_dict.get("device_code") is not None:
            return binascii.hexlify(self.field_dict["device_code"])
        return None


def stc_check_device_code_command():
    """
    Function to generate check device code command
    :return: FC5 gprs Command
    >>> stc_check_device_code_command().as_bytes()
    b'FC5'
    >>> stc_check_device_code_command()
    <meitrack.command.command_FC5.CheckDeviceCodeCommand object at ...>
    """
    return CheckDeviceCodeCommand(0, b'FC5')


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

    print(stc_check_device_code_command())


if __name__ == '__main__':
    """
    Main section for running interactive testing.
    """
    main()
