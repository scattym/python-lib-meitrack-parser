"""
Module for working with the meitrack FC0 command
"""
import logging

from meitrack.command.common import Command
from meitrack.common import DIRECTION_SERVER_TO_CLIENT, DIRECTION_CLIENT_TO_SERVER

logger = logging.getLogger(__name__)


class AuthOtaUpdateCommand(Command):
    """
    Class for setting the field names for the auth ota update command
    """
    request_field_names = [
        "command", "action",
    ]
    response_field_names = [
        "command", "device_code", "response", "packet_size", "current_firmware", "ota_file_name"
    ]

    def __init__(self, direction, payload=None, device_type=None):
        """
        Constructor for setting the auth ota update parameters
        :param direction: The payload direction.
        :param payload: The payload to parse.
        """

        super(AuthOtaUpdateCommand, self).__init__(direction, payload=payload, device_type=device_type)
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
            if self.field_dict.get("response", b'') in [b'Err']:
                return True
        return False


def stc_auth_ota_update_command():
    """
    Function to generate auth ota update command
    :return: FC0 gprs Command
    >>> stc_auth_ota_update_command().as_bytes()
    b'FC0,AUTH'
    >>> stc_auth_ota_update_command()
    <meitrack.command.command_FC0.AuthOtaUpdateCommand object at ...>
    """
    return AuthOtaUpdateCommand(0, b"FC0,AUTH")


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

    print(stc_auth_ota_update_command())


if __name__ == '__main__':
    main()
