import logging
from meitrack.error import GPRSParseError
from meitrack.command.common import Command, meitrack_date_to_datetime, datetime_to_meitrack_date
from meitrack.common import DIRECTION_SERVER_TO_CLIENT, DIRECTION_CLIENT_TO_SERVER
logger = logging.getLogger(__name__)


class SetIOParamsCommand(Command):
    request_field_names = [
        "command", "model", "device1", "device2", "device3", "device4", "device5",
    ]
    response_field_names = [
        "command", "response",
    ]

    def __init__(self, direction, payload=None):
        super(SetIOParamsCommand, self).__init__(direction, payload=payload)
        if direction == DIRECTION_SERVER_TO_CLIENT:
            self.field_name_selector = self.request_field_names
        else:
            self.field_name_selector = self.response_field_names

        if payload:
            self.parse_payload(payload)


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
        b"""C91,OK""",
        b"""C91,A78,1:0,2:0,3:0,4:13""",
    ]

    test_command = SetIOParamsCommand(1, b"C91,OK")
    print(test_command.as_bytes())
    print(test_command)
    test_command = SetIOParamsCommand(0, b"C91,A78,1:0,2:0,3:0,4:13,5:13")
    print(test_command.as_bytes())
    print(test_command)