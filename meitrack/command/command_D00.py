"""
Module for working with the meitrack D00 command
"""
import datetime
import logging

from meitrack.command import common
from meitrack.command.common import Command
from meitrack.common import DIRECTION_SERVER_TO_CLIENT, DIRECTION_CLIENT_TO_SERVER

logger = logging.getLogger(__name__)


class FileDownloadCommand(Command):
    """
    Class for setting the field names for the file download command
    """
    request_field_names = [
        "command", "file_name", "data_packet_start_number"
    ]
    response_field_names = [
        "command", "file_name", "number_of_data_packets", "data_packet_number", "file_bytes"
    ]

    def __init__(self, direction, payload=None, device_type=None):
        """
        Constructor for setting the file download command parameters
        :param direction: The payload direction.
        :param payload: The payload to parse.
        """
        super(FileDownloadCommand, self).__init__(direction, payload=payload, device_type=device_type)
        logger.log(13, payload)
        if direction == DIRECTION_SERVER_TO_CLIENT:
            self.field_name_selector = self.request_field_names
        else:
            self.field_name_selector = self.response_field_names

        if payload:
            self.parse_payload(payload, 4)

            self.field_dict['date_time'] = datetime.datetime.now()
            file_name = self.field_dict.get("file_name")
            if file_name:
                # 180428115949_C1E11_N1U1D1.jpg
                file_name_arr = file_name.split(b"_")
                if len(file_name_arr) == 3:
                    date = common.meitrack_date_to_datetime(file_name_arr[0])
                    if date:
                        self.field_dict["date_time"] = date
        else:
            self.field_dict["command"] = b"D00"

        logger.log(13, self.field_dict)

    def build(self, file_name, number_of_data_packets, data_packet_number, file_bytes):
        """
        Function to build the FileDownloadCommand based on parameters.
        :param file_name: The name of the file
        :param number_of_data_packets: The number of data packets
        :param data_packet_number: The data packet number
        :param file_bytes: The number of bytes in the file
        :return: None
        """
        self.field_dict["file_name"] = file_name
        self.field_dict["number_of_data_packets"] = number_of_data_packets
        self.field_dict["data_packet_number"] = data_packet_number
        self.field_dict["file_bytes"] = file_bytes


def main():
    """
    Main section for running interactive testing.
    """
    main_logger = logging.getLogger('')
    main_logger.setLevel(logging.DEBUG)
    char_handler = logging.StreamHandler()
    char_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    char_handler.setFormatter(formatter)
    main_logger.addHandler(char_handler)

    # "command", "file_name", "number_of_data_packets", "data_packet_number", "file_bytes"
    file_download = FileDownloadCommand(DIRECTION_CLIENT_TO_SERVER)
    file_download.field_dict["file_name"] = b"something.jpg"
    file_download.field_dict["number_of_data_packets"] = b"2"
    file_download.field_dict["data_packet_number"] = b"0"
    file_download.field_dict["file_bytes"] = b"somedata"

    print(file_download.as_bytes())


if __name__ == '__main__':
    main()
