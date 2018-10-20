"""
Module for working with the meitrack FC5 command
"""
import binascii
import logging

from meitrack.command.common import Command
from meitrack.common import DIRECTION_SERVER_TO_CLIENT, DIRECTION_CLIENT_TO_SERVER

logger = logging.getLogger(__name__)


class CheckDeviceCodeCommand(Command):
    request_field_names = [
        "command"
    ]
    response_field_names = [
        "command", "device_code",
    ]

    def __init__(self, direction, payload=None):
        super(CheckDeviceCodeCommand, self).__init__(direction, payload=payload)
        if direction == DIRECTION_SERVER_TO_CLIENT:
            self.field_name_selector = self.request_field_names
        else:
            self.field_name_selector = self.response_field_names

        if payload:
            self.parse_payload(payload, 2)

    def ota_response_device_code(self):
        if self.direction == DIRECTION_CLIENT_TO_SERVER and self.field_dict.get("device_code") is not None:
            return binascii.hexlify(self.field_dict["device_code"])
        return None



def stc_check_device_code_command():
    return CheckDeviceCodeCommand(0, b'FC5')


if __name__ == '__main__':
    log_level = 11 - 11

    logger = logging.getLogger('')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    print(stc_check_device_code_command())
