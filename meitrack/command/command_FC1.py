import logging
from meitrack.error import GPRSParseError
from meitrack.command.common import Command, meitrack_date_to_datetime, datetime_to_meitrack_date
from meitrack.common import DIRECTION_SERVER_TO_CLIENT, DIRECTION_CLIENT_TO_SERVER

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
            if direction == DIRECTION_CLIENT_TO_SERVER:
                self.parse_payload(payload)
            else:
                self.index = payload[0:8]
                self.length = payload[8:12]
                self.file_contents = payload[12:]
                self.field_dict['payload'] = payload

        if index is not None and file_contents is not None:
            self.field_dict['command'] = b'FC1'
            self.index = index
            self.file_contents = file_contents
            self.field_dict["payload"] = b"%08x%04x%s" % (self.index, len(file_contents), file_contents)
            self.payload = self.field_dict["payload"]

    def is_response_error(self):
        if self.direction == DIRECTION_CLIENT_TO_SERVER:
            response = self.field_dict.get("response", b'')
            if response in [b'NOT']:
                return True
            else:
                if len(response) == 14 and response[14:16] == b'00':
                    return True
        return False

    def ota_response_data(self):
        if self.direction == DIRECTION_CLIENT_TO_SERVER:
            response = self.field_dict.get("response", b'')
            if len(response) == 14 and response[14:16] == b'01':
                return int(response[0:8], 16), int(response[8:12], 16)
        return None, None


def stc_send_ota_data_command(file_bytes):
    command_list = []
    for index, x in enumerate(range(0, len(file_bytes), 1024)):
        command_list.append(SendOtaDataCommand(0, None, index=index, file_contents=file_bytes[x:x+1024]))
    return command_list


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

    commands = stc_send_ota_data_command(b"testfil"*190)
    for command in commands:
        print(command)
