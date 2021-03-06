"""
Module for working with the meitrack D01 command
"""
import logging

from meitrack.command.common import Command
from meitrack.common import DIRECTION_SERVER_TO_CLIENT

logger = logging.getLogger(__name__)

"""
$$p1054,864507032323403,D01,8,0,180520032140_C1E1_N4U1D1.jpg|180520041216_C1E35_N1U1D1.jpg|180520004140_C1E1_N4U1D1.jpg
|180519204241_C1E1_N5U1D1.jpg|180519210839_C1E35_N1U1D1.jpg|180519211937_C1E1_N2U1D1.jpg|180519212140_C1E1_N4U1D1.jpg|
180519212242_C1E1_N5U1D1.jpg|180519215836_C1E1_N1U1D1.jpg|180519215937_C1E1_N2U1D1.jpg|180519220140_C1E1_N4U1D1.jpg|
180519220241_C1E1_N5U1D1.jpg|180519223836_C1E1_N1U1D1.jpg|180519231836_C1E1_N1U1D1.jpg|180519224140_C1E1_N4U1D1.jpg|
180518223837_C1E1_N1U1D1.jpg|180518231837_C1E1_N1U1D1.jpg|180518224141_C1E1_N4U1D1.jpg|180518224242_C1E1_N5U1D1.jpg|
180518231938_C1E1_N2U1D1.jpg|180518235837_C1E1_N1U1D1.jpg|180518232242_C1E1_N5U1D1.jpg|180519000039_C1E1_N3U1D1.jpg|
180519000141_C1E1_N4U1D1.jpg|180519000242_C1E1_N5U1D1.jpg|180519004242_C1E1_N5U1D1.jpg|180519004141_C1E1_N4U1D1.jpg|
180519010837_C1E3_N1U1D1.jpg|180519012039_C1E1_N3U1D1.jpg|180519012141_C1E1_N4U1D1.jpg|180519015837_C1E1_N1U1D1.jpg|
180519023938_C1E1_N2U1D1.jpg|180519015939_C1E35_N1U1D1.jpg|180519020141_C1E1_N4U1D1.jpg|180519020242_C1E1_N5U1D1.jpg|
180519*B0
"""


class FileListCommand(Command):
    """
    Class for setting the field names for the file listing command
    """
    request_field_names = [
        "command", "data_packet_start_number"
    ]
    response_field_names = [
        "command", "number_of_data_packets", "data_packet_number", "file_list"
    ]

    def __init__(self, direction, payload=None, device_type=None):
        """
        Constructor for setting the file list command parameters
        :param direction: The payload direction.
        :param payload: The payload to parse.
        """

        super(FileListCommand, self).__init__(direction, payload=payload, device_type=device_type)
        logger.log(13, payload)
        if direction == DIRECTION_SERVER_TO_CLIENT:
            self.field_name_selector = self.request_field_names
        else:
            self.field_name_selector = self.response_field_names

        super(FileListCommand, self).parse_payload(payload)
