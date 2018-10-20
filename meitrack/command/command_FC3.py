"""
Module for working with the meitrack FC3 command
"""
import logging

from meitrack.command.common import Command
from meitrack.common import DIRECTION_SERVER_TO_CLIENT, DIRECTION_CLIENT_TO_SERVER

logger = logging.getLogger(__name__)


class StartOtaUpdateCommand(Command):
    request_field_names = [
        "command",
    ]
    response_field_names = [
        "command", "response", "firmware_version"
    ]

    def __init__(self, direction, payload=None):
        super(StartOtaUpdateCommand, self).__init__(direction, payload=payload)
        if direction == DIRECTION_SERVER_TO_CLIENT:
            self.field_name_selector = self.request_field_names
        else:
            self.field_name_selector = self.response_field_names

        if payload:
            self.parse_payload(payload)

    def is_response_error(self):
        if self.direction == DIRECTION_CLIENT_TO_SERVER:
            response = self.field_dict.get("response", b'')
            if response in [b'NOT', b'3']:
                return True
        return False


def stc_start_ota_update_command():
    return StartOtaUpdateCommand(0, b'FC3')


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
    print(stc_start_ota_update_command())

