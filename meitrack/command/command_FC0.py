import logging

from meitrack.command.common import Command
from meitrack.common import DIRECTION_SERVER_TO_CLIENT, DIRECTION_CLIENT_TO_SERVER

logger = logging.getLogger(__name__)


class AuthOtaUpdateCommand(Command):
    request_field_names = [
        "command", "action",
    ]
    response_field_names = [
        "command", "device_code", "response", "packet_size", "current_firmware", "ota_file_name"
    ]

    def __init__(self, direction, payload=None):
        super(AuthOtaUpdateCommand, self).__init__(direction, payload=payload)
        if direction == DIRECTION_SERVER_TO_CLIENT:
            self.field_name_selector = self.request_field_names
        else:
            self.field_name_selector = self.response_field_names

        if payload:
            self.parse_payload(payload)

    def is_response_error(self):
        if self.direction == DIRECTION_CLIENT_TO_SERVER:
            if self.field_dict.get("response", b'') in [b'Err']:
                return True
        return False


def stc_auth_ota_update_command():
    return AuthOtaUpdateCommand(0, b"FC0,AUTH")


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

    print(stc_auth_ota_update_command())