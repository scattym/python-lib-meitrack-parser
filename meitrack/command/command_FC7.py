import logging
from meitrack.error import GPRSParseError
from meitrack.command.common import Command, meitrack_date_to_datetime, datetime_to_meitrack_date
from meitrack.common import DIRECTION_SERVER_TO_CLIENT, DIRECTION_CLIENT_TO_SERVER

logger = logging.getLogger(__name__)


class SetOtaServerCommand(Command):
    request_field_names = [
        "command", "ip_address", "port",
    ]
    response_field_names = [
        "command", "response",
    ]

    def __init__(self, direction, payload=None):
        super(SetOtaServerCommand, self).__init__(direction, payload=payload)
        if direction == DIRECTION_SERVER_TO_CLIENT:
            self.field_name_selector = self.request_field_names
        else:
            self.field_name_selector = self.response_field_names

        if payload:
            self.parse_payload(payload)

    def is_response_error(self):
        if self.direction == DIRECTION_CLIENT_TO_SERVER:
            if self.field_dict.get("response", b'') in [b'Err', b'FFFF']:
                return True
        return False


def stc_set_ota_server_command(ip_address, port):
    return SetOtaServerCommand(0, b'FC7,%b,%b' % (ip_address, port))


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

    print(stc_set_ota_server_command(b"1.1.1.1", b"6100"))
