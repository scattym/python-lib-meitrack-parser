import logging
from meitrack.error import GPRSParseError
from meitrack.command.common import Command, meitrack_date_to_datetime, datetime_to_meitrack_date
from meitrack.common import DIRECTION_SERVER_TO_CLIENT, DIRECTION_CLIENT_TO_SERVER
from meitrack.gprs_protocol import GPRS

logger = logging.getLogger(__name__)


class SendOtaDataCommand(Command):
    request_field_names = [
        "command", "payload",
    ]
    response_field_names = [
        "command", "response",
    ]

    def __init__(self, direction, payload=None, index=None, file_contents=None):
        super(SendOtaDataCommand, self).__init__(direction, payload=payload)
        if direction == DIRECTION_SERVER_TO_CLIENT:
            self.field_name_selector = self.request_field_names
        else:
            self.field_name_selector = self.response_field_names

        if payload:
            self.index = payload[0:4]
            self.length = payload[4:8]
            self.file_contents = payload[8:]
            self.field_dict['payload'] = payload

        if index is not None and file_contents is not None:
            self.field_dict['command'] = b'FC1'
            self.index = index
            self.file_contents = file_contents
            self.field_dict["payload"] = b"%08x%04x%b" % (self.index, len(file_contents), file_contents)
            self.payload = self.field_dict["payload"]


def stc_send_ota_data_command(file_bytes):
    command_list = []
    for index, x in enumerate(range(0, len(file_bytes), 1024)):
        command_list.append(SendOtaDataCommand(0, None, index=index, file_contents=file_bytes[x:x+1024]))
    return command_list


def stc_send_ota_data(imei, file_bytes):
    gprs_list = []
    com_list = stc_send_ota_data_command(file_bytes)
    for com in com_list:
        gprs = GPRS()
        gprs.direction = b'@@'
        gprs.data_identifier = b'a'
        gprs.enclosed_data = com
        gprs.imei = imei
        gprs_list.append(gprs)

    return gprs_list


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
        b"""FC1,000000test""",
        b"""FC1,theresponse""",
    ]

    test_command = SendOtaDataCommand(0, b"FC1,000000test")
    print(test_command.as_bytes())
    print(test_command)
    test_command = SendOtaDataCommand(1, b"FC1,theresponse")
    print(test_command.as_bytes())
    print(test_command)

    commands = stc_send_ota_data(b"testfil"*190)
    for command in commands:
        print(command)