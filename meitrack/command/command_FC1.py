"""
Module for working with the meitrack FC1 command
"""
import logging

from meitrack.command.common import Command
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
                self.parse_payload(payload, 1)
            else:
                self.index = payload[0:8]
                self.length = payload[8:12]
                self.file_contents = payload[12:]
                self.field_dict['payload'] = payload

        if index is not None and file_contents is not None:
            self.field_dict['command'] = b'FC1'
            self.index = index
            self.file_contents = file_contents
            self.field_dict["payload"] = b"%s%s%s" % (
                self.index.to_bytes(4, byteorder='big'),
                len(file_contents).to_bytes(2, byteorder='big'),
                file_contents
            )
            # self.field_dict["payload"] = b"%08x%04x%s" % (self.index, len(file_contents), file_contents)
            self.payload = self.field_dict["payload"]

    def is_response_error(self):
        if self.direction == DIRECTION_CLIENT_TO_SERVER:
            response = self.field_dict.get("response", b'')
            if response in [b'NOT']:
                return True
            else:
                if len(response) == 14 and response[14:16] in [b'00', b'02']:
                    return True
        return False

    def ota_response_data(self):
        if self.direction == DIRECTION_CLIENT_TO_SERVER:
            response = self.field_dict.get("response", b'')
            if len(response) == 14 and response[14:16] == b'01':
                return int(response[0:8], 16), int(response[8:12], 16)
        return None, None


def stc_send_ota_data_command(file_bytes, chunk_size):
    if not chunk_size:
        logger.error("Chunk size was not set")
        return []
    try:
        chunk_size_int = int(chunk_size.decode())
    except AttributeError as _:
        chunk_size_int = int(chunk_size)
    command_list = []
    for index, x in enumerate(range(0, len(file_bytes), chunk_size_int)):
        command_list.append(
            SendOtaDataCommand(0, None, index=index*chunk_size_int, file_contents=file_bytes[x:x+chunk_size_int])
        )
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

    commands = stc_send_ota_data_command(b"testfile"*190, b'1024')
    for command in commands:
        print(command)
