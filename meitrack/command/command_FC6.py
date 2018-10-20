import logging

from meitrack.command.common import Command
from meitrack.common import DIRECTION_SERVER_TO_CLIENT, DIRECTION_CLIENT_TO_SERVER

logger = logging.getLogger(__name__)


class CheckFirmwareVersionCommand(Command):
    request_field_names = [
        "command", "file_name"
    ]
    response_field_names = [
        "command", "response",
    ]

    def __init__(self, direction, payload=None):
        super(CheckFirmwareVersionCommand, self).__init__(direction, payload=payload)
        if direction == DIRECTION_SERVER_TO_CLIENT:
            self.field_name_selector = self.request_field_names
        else:
            self.field_name_selector = self.response_field_names

        if payload:
            self.parse_payload(payload)

    def is_response_error(self):
        if self.direction == DIRECTION_CLIENT_TO_SERVER:
            if self.field_dict.get("response", b"") == b'2':
                return True
        return False


def stc_check_firmware_version_command(file_name):
    return CheckFirmwareVersionCommand(0, b'FC6,%b' % (file_name,))


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

    print(stc_check_firmware_version_command(b'testfile.ota'))
