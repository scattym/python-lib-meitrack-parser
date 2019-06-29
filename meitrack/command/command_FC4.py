"""
Module for working with the meitrack FC4 command
"""
import logging

from meitrack.command.common import Command
from meitrack.common import DIRECTION_SERVER_TO_CLIENT

logger = logging.getLogger(__name__)


class CancelOtaUpdateCommand(Command):
    """
    Class for setting the field names for the cancel ota update command
    """
    request_field_names = [
        "command",
    ]
    response_field_names = [
        "command", "response",
    ]

    def __init__(self, direction, payload=None, device_type=None):
        """
        Constructor for setting the cancel ota update command parameters
        :param direction: The payload direction.
        :param payload: The payload to parse.
        """

        super(CancelOtaUpdateCommand, self).__init__(direction, payload=payload, device_type=device_type)
        if direction == DIRECTION_SERVER_TO_CLIENT:
            self.field_name_selector = self.request_field_names
        else:
            self.field_name_selector = self.response_field_names

        if payload:
            self.parse_payload(payload)


def stc_cancel_ota_update_command():
    """
    Function to generate cancel ota update command
    :return: FC4 gprs Command
    >>> stc_cancel_ota_update_command().as_bytes()
    b'FC4'
    >>> stc_cancel_ota_update_command()
    <meitrack.command.command_FC4.CancelOtaUpdateCommand object at ...>
    """
    return CancelOtaUpdateCommand(0, b'FC4')


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

    print(stc_cancel_ota_update_command())


if __name__ == '__main__':
    main()
