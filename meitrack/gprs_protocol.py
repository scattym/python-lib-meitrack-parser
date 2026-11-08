"""
Library for parsing gprs protocol messages into GPRS objects.
"""

import logging

from meitrack.command.command_to_object import command_to_object
from meitrack.common import (
    CLIENT_TO_SERVER_PREFIX,
    DIRECTION_CLIENT_TO_SERVER,
    DIRECTION_SERVER_TO_CLIENT,
    END_OF_MESSAGE_STRING,
    MAX_DATA_LENGTH,
    SERVER_TO_CLIENT_PREFIX,
)
from meitrack.error import GPRSParseError

logger = logging.getLogger(__name__)

"""
payload $$<Data identifier><Data length>,<IMEI>,<Command type>,<Command><*Checksum>\r\n
"""


def prefix_to_direction(prefix):
    """
    Functinon to convert a prefix to a direction
    :param prefix: The prefix as a byte array
    :return: The enum definition of message directions
    >>> prefix_to_direction(SERVER_TO_CLIENT_PREFIX)
    0
    >>> prefix_to_direction(CLIENT_TO_SERVER_PREFIX)
    1
    """
    if prefix == SERVER_TO_CLIENT_PREFIX:
        return DIRECTION_SERVER_TO_CLIENT

    if prefix == CLIENT_TO_SERVER_PREFIX:
        return DIRECTION_CLIENT_TO_SERVER

    raise GPRSParseError(f"Invalid prefix {prefix}")


class GPRS:
    """
    Top level gprs object
    """

    def __init__(self, payload=None, device_type="T333"):
        """
        Constructor the gprs object with an optional payload
        :param payload: The gprs message payload to parse.
        :param device: The name of the device.
        """
        self.payload = b""
        self.direction = None
        self.data_identifier = None
        self.data_length = b"0"
        self.data_payload = None
        self.imei = None
        self.command_type = None
        self.checksum = None
        self.enclosed_data = None
        self.leftover = b""
        if device_type is not None:
            self.device_type = device_type
        else:
            self.device_type = "T333"
        if payload:
            self.parse_data_payload(payload)

    def parse_data_payload(self, payload):
        """
        Function to handle data payload parsing
        :param payload: The gprs command payload as a byte string
        :return: None
        """
        self.payload = payload
        self.direction = payload[0:2]
        self.data_identifier = chr(payload[2]).encode()
        self.checksum = payload[-4:-2]
        first_comma = payload.find(b",")
        # print("Data length is")
        # print(payload[3:first_comma])
        # print(type(payload[3:first_comma]))
        self.data_length = payload[3:first_comma]
        self.data_payload = payload[first_comma:]
        self.leftover = payload[first_comma + 1 : -5]

        next_comma = self.leftover.find(b",")
        self.imei = self.leftover[:next_comma]
        self.leftover = self.leftover[next_comma + 1 :]

        self.command_type = self.leftover[0:3]
        self.leftover = self.leftover
        self.enclosed_data = command_to_object(
            prefix_to_direction(self.direction),
            self.command_type,
            self.leftover,
            device_type=self.device_type,
        )

    def recalc_date(self):
        """
        Helper function to recalculate the leftover

        If the underlying command is changed then we want to be able to
        set the leftover as that is used when converting the command back
        into a byte string.
        :return: None
        """
        self.enclosed_data.recalc_date()

    def recalc_leftover(self):
        """
        Helper function to recalculate the leftover

        If the underlying command is changed then we want to be able to
        set the leftover as that is used when converting the command back
        into a byte string.
        :return: None
        """
        self.leftover = self.enclosed_data.as_bytes()

    @property
    def checksum(self):
        """
        Return the checksum from the parsed payload
        :return: Checksum as a byte string or b"XX" if not set
        """
        if self.__checksum:
            return self.__checksum
        return b"XX"

    @checksum.setter
    def checksum(self, checksum):
        """
        Setter for the checksum
        :param checksum: The checksum to apply
        :return: None
        """
        self.__checksum = checksum

    @property
    def enclosed_data(self):
        """
        Getter for the enclosed data property
        :return: The enclosed data
        """
        return self.__enclosed_data

    @enclosed_data.setter
    def enclosed_data(self, enclosed_commmand_object):
        """
        Setter for the enclosed data.

        Used to set both the leftover and the enclosed data if the underlying command
        is updated.
        :param enclosed_commmand_object: The new command object
        :return: None
        """
        if enclosed_commmand_object is not None:
            # print("Enclosed leftover as bytes is ")
            # print("%s" % (enclosed_commmand_object.as_bytes()))
            self.leftover = enclosed_commmand_object.as_bytes()
            self.__enclosed_data = enclosed_commmand_object
        else:
            self.__enclosed_data = None

    @property
    def data_length(self):
        """
        Getter for the payload length
        :return: Length of the payload as a byte string
        """
        data = (
            b","
            + self.imei
            + b","
            + self.leftover
            + b"*"
            + self.checksum
            + END_OF_MESSAGE_STRING
        )
        return str(len(data)).encode()

    @data_length.setter
    def data_length(self, data_length):
        """
        Helper function to reset the length to the input value
        :param data_length: The new data length
        :return: None
        """
        self.__data_length = str(data_length).encode()

    def __str__(self):
        """
        Return a string representation of the gprs object for debug
        :return: The parameters contained in the gprs message as a string.
        """
        return_str = f"Payload: {self.payload}\n"
        return_str += f"Direction: {self.direction}\n"
        return_str += f"identifier: {self.data_identifier}\n"
        return_str += f"length: {self.data_length}\n"
        return_str += f"data payload: {self.data_payload}\n"
        return_str += f"imei: {self.imei}\n"
        return_str += f"command_type: {self.command_type}\n"
        return_str += f"checksum: {self.checksum}\n"
        return_str += f"leftover: {self.leftover}\n"
        if self.enclosed_data:
            return_str += str(self.enclosed_data)
        return return_str

    def as_bytes(self, counter=None):
        """
        Function to return the gprs message as a byte string for sending on the socker
        :param counter: The counter to use in the message header
        :return: Byte representation of the gprs message
        """
        # print(chr(self.data_identifier).encode())
        # print(type(chr(self.data_identifier).encode()))
        # print(self.data_length)
        if counter is not None:
            subset = (counter % 58) + 65
            self.data_identifier = bytes([subset])
        string_to_sign = b"".join(
            [
                self.direction,
                self.data_identifier,
                self.data_length,
                b",",
                self.imei,
                b",",
                self.leftover,
                b"*",
            ]
        )

        # print("LEFTOVER IS ++++++++++++++++++++++++++++++++++++++++")
        # print("%s" % (self.leftover,))
        checksum_hex = f"{calc_signature(string_to_sign):02X}"
        self.checksum = checksum_hex.encode()
        # self.checksum = "{:02X}".format(calc_signature(string_to_sign))
        # print(type(self.data_identifier))
        return_str = b"".join(
            [
                self.direction,
                self.data_identifier,
                self.data_length,
                b",",
                self.imei,
                b",",
                self.leftover,
                b"*",
                self.checksum,
                END_OF_MESSAGE_STRING,
            ]
        )
        # print("RETURN STRING")
        # print(return_str)
        # return_str = "%s%s%s,%s,%s*%s%s" % (
        #     self.direction,
        #     self.data_identifier,
        #     self.data_length,
        #     self.imei,
        #     self.leftover,
        #     self.checksum,
        #     END_OF_MESSAGE_STRING
        # )
        return return_str


def _extract_frame_length(payload, first_comma):
    try:
        data_length = int(payload[3:first_comma])
    except ValueError:
        logger.error("Unable to calculate length field from payload %s", payload)
        return 0
    if data_length > MAX_DATA_LENGTH:
        raise GPRSParseError(
            f"Data length is longer than the protocol allows: {data_length}"
        )
    return data_length


def _validate_and_extract_frame(payload, first_comma, data_length):
    end_idx = first_comma + data_length
    if data_length == 0 or len(payload) < end_idx:
        return None, payload
    logger.log(13, "Start of payload is %s", payload[0:2])
    logger.log(13, "End of payload is %s", payload[-2:])
    message = payload[:end_idx]
    remaining = payload[end_idx:]
    if not message.endswith(END_OF_MESSAGE_STRING):
        logger.error("Last two characters of message is >%s<", message[-2:])
        raise GPRSParseError(
            f"Found begin token, but length does not lead to end of payload. {remaining}"
        )
    return message, remaining


def parse_data_payload(payload, direction, device_type=None):
    """
    Helper function to parse a payload into a list of gprs messages
    :param payload: The payload to parse
    :param direction: The direction of the payload
    :param device_type: The string representation of the device type.
    :return: The gprs list as well any part of the payload that was not consumable.
    """
    leftover = b""
    before = b""
    gprs_list = []
    prefix = (
        CLIENT_TO_SERVER_PREFIX
        if direction == DIRECTION_CLIENT_TO_SERVER
        else SERVER_TO_CLIENT_PREFIX
    )

    while payload:
        direction_start = payload.find(prefix)
        if direction_start < 0:
            logger.error("Unable to find start payload, %s", str(payload))
            leftover = payload
            break

        if direction_start > 0 and not before:
            before = payload[:direction_start]

        payload = payload[direction_start:]
        first_comma = payload.find(b",")
        if first_comma <= 0:
            logger.error(
                "No first comma found. Can't get to calculate length of payload"
            )
            leftover = payload
            break

        logger.log(13, "Data length is %s", payload[3:first_comma])
        data_length = _extract_frame_length(payload, first_comma)
        message, remaining = _validate_and_extract_frame(
            payload, first_comma, data_length
        )
        if message is None:
            leftover = remaining
            break

        payload = remaining
        current_gprs = GPRS(message, device_type=device_type)
        logger.debug("gprs fields: %s", current_gprs)
        gprs_list.append(current_gprs)

    return gprs_list, before, leftover


def calc_signature(payload):
    """
    Function used to calculate the checksum of a message
    :param payload: The command payload
    :return: The message checksum
    >>> calc_signature(b'1234ABCD*AA')
    254
    >>> calc_signature(b'$$n1084,864507032323,D00,1804.jpg,16,0,\\xff\\xd8\\xff\\xdb\\x00\\x84\\x00@%\\x14\\xc0J)*AA')
    120
    >>> calc_signature(b'$$n1084,864507032323,D00,1804.jpg,16,0,*\\xd8\\xff\\xdb\\x00\\x84\\x00\\x00\\xd3@%\\x14J)*AA')
    182
    >>> calc_signature(b'$$n1084,864507032323,D00,1804.jpg,16,0,\\xff\\xd8\\xff\\xdb\\x00\\x84\\x00*AA')
    204
    """
    # print(type(payload))
    # print(payload)
    checksum = 0
    lastchar = payload.rfind(b"*")
    for char in payload[0 : lastchar + 1]:
        checksum = checksum + char
    checksum = checksum & 0xFF
    # print("checksum is ", checksum)
    return checksum


def main():
    """
    Main entry point for protocol testing.
    """


if __name__ == "__main__":
    main()
