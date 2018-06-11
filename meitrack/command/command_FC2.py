import logging
from meitrack.error import GPRSParseError
from meitrack.command.common import Command, meitrack_date_to_datetime, datetime_to_meitrack_date
from meitrack.common import DIRECTION_SERVER_TO_CLIENT, DIRECTION_CLIENT_TO_SERVER

logger = logging.getLogger(__name__)


class ObtainOtaChecksumCommand(Command):
    request_field_names = [
        "command", "index_length"
    ]
    response_field_names = [
        "command", "ota_checksum",
    ]

    def __init__(self, direction, payload=None):
        super(ObtainOtaChecksumCommand, self).__init__(direction, payload=payload)
        if direction == DIRECTION_SERVER_TO_CLIENT:
            self.field_name_selector = self.request_field_names
        else:
            self.field_name_selector = self.response_field_names

        if payload:
            self.parse_payload(payload, 1)

    def is_response_error(self):
        if self.direction == DIRECTION_CLIENT_TO_SERVER:
            response = self.field_dict.get("response", b'')
            if response in [b'NOT']:
                return True
        return False

    def ota_data_checksum(self):
        if self.direction == DIRECTION_CLIENT_TO_SERVER:
            response = self.field_dict.get("response", b'')
            if len(response) == 20:
                return int(response[18:20], 16)
        return None


def stc_obtain_ota_checksum_command(start_index, length):
    return ObtainOtaChecksumCommand(
        0,
        b''.join([b'FC2,', start_index.to_bytes(4, byteorder='big'), length.to_bytes(4, byteorder='big')])
    )


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

    print(stc_obtain_ota_checksum_command(0, 185121))
