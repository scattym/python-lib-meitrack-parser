import logging

from meitrack.error import GPRSParseError
from meitrack.command.common import Command, meitrack_date_to_datetime, datetime_to_meitrack_date
from meitrack.common import DIRECTION_SERVER_TO_CLIENT, DIRECTION_CLIENT_TO_SERVER
from meitrack.gprs_protocol import GPRS

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


def stc_auth_ota_update_command():
    return AuthOtaUpdateCommand(0, b"FC0,AUTH")


def stc_auth_ota_update(imei):
    com = stc_auth_ota_update_command()
    gprs = GPRS()
    gprs.direction = b'@@'
    gprs.data_identifier = b'a'
    gprs.enclosed_data = com
    gprs.imei = imei

    return gprs


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

    tests = [
        b"""E91""",
        b"""E91,FWV1.00,12345678""",
    ]

    test_command = AuthOtaUpdateCommand(0, b"E91")
    print(test_command.as_bytes())
    print(test_command)
    test_command = AuthOtaUpdateCommand(1, b"E91,FWV1.00,12345678")
    print(test_command.as_bytes())
    print(test_command)
    print(stc_auth_ota_update())