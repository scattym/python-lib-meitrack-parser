"""
Module for working with the meitrack FC3 command
"""
import logging

from meitrack.command.common import Command
from meitrack.common import DIRECTION_SERVER_TO_CLIENT, DIRECTION_CLIENT_TO_SERVER

logger = logging.getLogger(__name__)


class StartOtaUpdateCommand(Command):
    """
    Class for setting the field names for the start ota update command
    """
    request_field_names = [
        "command",
    ]
    response_field_names = [
        "command", "response", "firmware_version"
    ]

    def __init__(self, direction, payload=None):
        """
        Constructor for setting the start ota update command parameters
        :param direction: The payload direction.
        :param payload: The payload to parse.
        """

        super(StartOtaUpdateCommand, self).__init__(direction, payload=payload)
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
            response = self.field_dict.get("response", b'')
            if response in [b'NOT', b'3']:
                return True
        return False


def stc_start_ota_update_command():
    """
    Function to generate start ota update command
    :return: FC4 gprs Command
    >>> stc_start_ota_update_command().as_bytes()
    b'FC3'
    >>> stc_start_ota_update_command()
    <meitrack.command.command_FC3.StartOtaUpdateCommand object at ...>
    """
    return StartOtaUpdateCommand(0, b'FC3')


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
    print(stc_start_ota_update_command())



if __name__ == '__main__':
    main()

