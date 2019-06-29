"""
Module for working with the meitrack FC6 command
"""
import logging

from meitrack.command.common import Command
from meitrack.common import DIRECTION_SERVER_TO_CLIENT, DIRECTION_CLIENT_TO_SERVER

logger = logging.getLogger(__name__)


class CheckFirmwareVersionCommand(Command):
    """
    Class for setting the field names for the check ota firmware version command
    """
    request_field_names = [
        "command", "file_name"
    ]
    response_field_names = [
        "command", "response",
    ]

    def __init__(self, direction, payload=None, device_type=None):
        """
        Constructor for setting the check firmware version parameters
        :param direction: The payload direction.
        :param payload: The payload to parse.
        """

        super(CheckFirmwareVersionCommand, self).__init__(direction, payload=payload, device_type=device_type)
        if direction == DIRECTION_SERVER_TO_CLIENT:
            self.field_name_selector = self.request_field_names
        else:
            self.field_name_selector = self.response_field_names

        if payload:
            self.parse_payload(payload)

    def is_response_error(self):
        """
        Function to help determine if the parsed message is an error
        :return: True or False depending on whether the message is identifying an error
        """
        if self.direction == DIRECTION_CLIENT_TO_SERVER:
            if self.field_dict.get("response", b"") == b'2':
                return True
        return False


def stc_check_firmware_version_command(file_name):
    """
    Function to generate check firmware version command
    :param file_name: The file name for the firmware
    :return: FC6 gprs Command
    >>> stc_check_firmware_version_command(b"test.file").as_bytes()
    b'FC6,test.file'
    >>> stc_check_firmware_version_command(b"test.file")
    <meitrack.command.command_FC6.CheckFirmwareVersionCommand object at ...>
    """
    return CheckFirmwareVersionCommand(0, b'FC6,%b' % (file_name,))


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

    print(stc_check_firmware_version_command(b'testfile.ota'))


if __name__ == '__main__':
    main()
