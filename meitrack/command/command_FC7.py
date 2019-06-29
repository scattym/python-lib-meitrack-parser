"""
Module for working with the meitrack FC7 command
"""
import logging

from meitrack.command.common import Command
from meitrack.common import DIRECTION_SERVER_TO_CLIENT, DIRECTION_CLIENT_TO_SERVER

logger = logging.getLogger(__name__)


class SetOtaServerCommand(Command):
    """
    Class for setting the field names for the set ota server command
    """
    request_field_names = [
        "command", "ip_address", "port",
    ]
    response_field_names = [
        "command", "response", "device_code", "unknown", "unknown2"
    ]

    def __init__(self, direction, payload=None, device_type=None):
        """
        Constructor for setting the set ota server command parameters
        :param direction: The payload direction.
        :param payload: The payload to parse.
        """

        super(SetOtaServerCommand, self).__init__(direction, payload=payload, device_type=device_type)
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
            if self.field_dict.get("response", b'') in [b'Err', b'FFFF']:
                return True
        return False


def stc_set_ota_server_command(ip_address, port):
    """
    Function to generate set ota server command
    :param ip_address: The ip address of the ota host
    :param port: The port of the ota host
    :return: FC7 gprs Command
    >>> stc_set_ota_server_command(b"1.1.1.1", b"1234").as_bytes()
    b'FC7,1.1.1.1,1234'
    >>> stc_set_ota_server_command(b"1.1.1.1", b"1234")
    <meitrack.command.command_FC7.SetOtaServerCommand object at ...>
    """
    return SetOtaServerCommand(0, b'FC7,%b,%b' % (ip_address, port))


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

    print(stc_set_ota_server_command(b"1.1.1.1", b"6100"))


if __name__ == '__main__':
    main()
