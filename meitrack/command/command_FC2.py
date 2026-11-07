"""
Module for working with the meitrack FC2 command
"""
import binascii
import logging
from typing import ClassVar, Literal

from meitrack.command.common import Command
from meitrack.common import DIRECTION_CLIENT_TO_SERVER, DIRECTION_SERVER_TO_CLIENT

logger = logging.getLogger(__name__)


class ObtainOtaChecksumCommand(Command):
    """
    Class for setting the field names for the obtain ota checksum command
    """
    request_field_names: ClassVar[list[str]] = [
        "command", "index_length"
    ]
    response_field_names: ClassVar[list[str]] = [
        "command", "ota_checksum",
    ]

    def __init__(self, direction, payload=None, device_type=None):
        """
        Constructor for setting the obtain ota checksum parameters
        :param direction: The payload direction.
        :param payload: The payload to parse.
        """

        super().__init__(direction, payload=payload, device_type=device_type)
        if direction == DIRECTION_SERVER_TO_CLIENT:
            self.field_name_selector = self.request_field_names
        else:
            self.field_name_selector = self.response_field_names

        if payload:
            self.parse_payload(payload, 1)

    def is_response_error(self):
        """
        Function to help determine if the parsed message is an error
        :return: True or False depending on whether the message is identifying an error
        """

        if self.direction == DIRECTION_CLIENT_TO_SERVER:
            response = self.field_dict.get("ota_checksum") or self.field_dict.get("response", b'')
            if response in [b'NOT']:
                return True
        return False

    def ota_data_checksum(self, byteorder: Literal["little", "big"] = "little"):
        """
        Helper function to return the checksum from a obtain ota checksum response.
        :return: Checksum or None
        """
        if self.direction == DIRECTION_CLIENT_TO_SERVER:
            response = self.field_dict.get("ota_checksum") or self.field_dict.get("response", b'')
            if not response:
                return None
            if len(response) == 20:
                try:
                    cs_bytes = binascii.unhexlify(response[16:20])
                    return int.from_bytes(cs_bytes, byteorder=byteorder)
                except (binascii.Error, ValueError):
                    return int(response[16:20], 16)
            if len(response) == 10:
                return int.from_bytes(response[8:10], byteorder=byteorder)
            if len(response) == 4:
                try:
                    cs_bytes = binascii.unhexlify(response)
                    return int.from_bytes(cs_bytes, byteorder=byteorder)
                except (binascii.Error, ValueError):
                    return int(response, 16)
            if len(response) == 2:
                return int.from_bytes(response, byteorder=byteorder)
            try:
                return int(response, 16)
            except ValueError:
                pass
        return None


def stc_obtain_ota_checksum_command(start_index, length, byteorder: Literal["little", "big"] = "little"):
    """
    Function to generate obtain ota checksum command
    :return: FC2 gprs Command
    >>> stc_obtain_ota_checksum_command(3, 5).as_bytes()
    b'FC2,\\x03\\x00\\x00\\x00\\x05\\x00\\x00\\x00'
    >>> stc_obtain_ota_checksum_command(3, 5)
    <meitrack.command.command_FC2.ObtainOtaChecksumCommand object at ...>
    """
    return ObtainOtaChecksumCommand(
        0,
        b''.join([b'FC2,', start_index.to_bytes(4, byteorder=byteorder), length.to_bytes(4, byteorder=byteorder)])
    )


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

    print(stc_obtain_ota_checksum_command(0, 185121))


if __name__ == '__main__':
    main()
