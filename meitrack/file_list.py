"""
Library for working with file listing gprs messages
"""
import logging

from meitrack.common import DIRECTION_CLIENT_TO_SERVER
from meitrack.error import GPRSError

logger = logging.getLogger(__name__)


class FileListingError(GPRSError):
    """
    File listing error class
    """
    pass


class FileListing(object):
    """
    Class to track file listing messages and combined them
    """
    def __init__(self):
        """
        FileListing constructor
        """
        self.max_packets = 0
        self.full_file_list_dict = {}
        self.file_arr = []
        self.num_files = 0

    def clear_list(self):
        """
        Function to clear the list of files tracked by the class
        :return: None
        """
        self.max_packets = 0
        self.full_file_list_dict = {}
        self.file_arr = []

    def add_item(self, file_name):
        """
        Function to add a file to the list of files tracked by this class
        :param file_name: The name of the file to track
        :return: None
        """
        try:
            item = file_name.decode()
        except AttributeError:
            item = file_name
        if item:
            if item not in self.file_arr:
                logger.log(13, "File was not in list. Adding: %s", file_name)
                self.file_arr.append(item)
                logger.log(13, "List is now %s", self.file_arr)
                self.num_files = len(self.file_arr)
            else:
                logger.error("File was already in list. Not adding: %s", file_name)

    def remove_item(self, file_name):
        """
        Function to remove a file from the list of files tracked by this class
        :param file_name: The name of the file to remove
        :return: None
        """
        try:
            remove = file_name.decode()
        except AttributeError:
            remove = file_name
        if remove in self.file_arr:
            logger.log(13, "Found file, removing from list %s", file_name)
            self.file_arr.remove(remove)
            self.num_files = len(self.file_arr)
            logger.log(13, "List is now %s", self.file_arr)
        else:
            logger.error("File was not in list. file_name: %s", file_name)

    def add_packet(self, gprs_packet):
        """
        Add a gprs packet to the class. Will parse to determine if a new file should be tracked.
        :param gprs_packet: The GPRS class object
        :return: packet_count, packet_number
        """
        # self.packets.append(gprs_packet)
        packet_count = None
        packet_number = None
        if gprs_packet.enclosed_data['command'] == b'D01':
            packet_count, packet_number, file_list = gprs_packet.enclosed_data.get_file_list()
            if packet_count is None or packet_number is None or file_list is None:
                logger.error("Unable to extract details from packet")
                raise FileListingError("Unable to extract details from packet")
            else:
                packet_count = int(packet_count.decode())
                packet_number = int(packet_number.decode())
                file_list = str(file_list.decode())
                if not self.max_packets:
                    self.max_packets = packet_count
                else:
                    if self.max_packets != packet_count:
                        logger.error("Max packet count has changed across packets.")
                        raise FileListingError("Max packet count has changed across packets")
                self.full_file_list_dict[packet_number] = file_list
            if self.is_complete():

                for file in self.return_file_listing_list():
                    self.add_item(file)

                self.full_file_list_dict = {}
                self.max_packets = 0
                logger.log(13, "File list is complete %s", self.file_arr)
        return packet_count, packet_number

    def is_complete(self):
        """
        Function to determine if a file listing set of commands is complete
        :return: True if complete, False if not
        """
        if self.max_packets == 0:
            return False
        for i in range(0, self.max_packets):
            if self.full_file_list_dict.get(i, None) is None:
                logger.log(13, "Missing packet number %s", i)
                return False
        return True

    def fragment_list_as_string(self):
        """
        Function to return the fragment list as a string for debug
        :return: Fragment list tracked as a string
        """
        return_str = ""
        for i in self.full_file_list_dict:
            return_str += "{}({}) ".format(i, len(self.full_file_list_dict[i]))
        return return_str

    def return_file_listing(self):
        """
        Function to return a list of files currently tracked to be on the device
        :return: List of files on the device that have been reported.
        """
        if not self.is_complete():
            logger.log(13, "File list is not complete yet. Returning None")
            return None
        else:
            full_file_list = ""
            for i in range(0, self.max_packets):
                if self.full_file_list_dict.get(i, None) is None:
                    logger.error("Missing packet number %s", i)
                    return None
                else:
                    full_file_list = full_file_list + self.full_file_list_dict[i]
            if full_file_list[-1:] == '|':
                full_file_list = full_file_list[0:-1]
            return full_file_list

    def return_file_listing_list(self):
        """
        Return files on device as a list.
        :return: File list or None
        """
        file_str = self.return_file_listing()
        if file_str:
            return file_str.split('|')
        return None

    def __str__(self):
        """
        String representation fo the file list class
        :return: String representation fo the file list class
        """
        return "Length: {}, Content: {}".format(len(self.file_arr), str(self.file_arr))


def gprs_file_list_as_str(list_of_gprs):
    """
    Convert a list of gprs messages to a list of possible files as a string.
    :param list_of_gprs: The input gprs messages
    :return: List of possible files on the device as a single pipe separated file list string.
    """
    full_file_list_dict = {}
    max_packets = 0
    for gprs in list_of_gprs:
        if gprs.enclosed_data['command'] == b'D01':
            packet_count, packet_number, file_list = gprs.enclosed_data.get_file_list()
            if packet_count is not None and packet_number is not None and file_list is not None:
                packet_count = int(packet_count.decode())
                packet_number = int(packet_number.decode())
                file_list = str(file_list.decode())
                if not max_packets:
                    max_packets = packet_count
                else:
                    if max_packets != packet_count:
                        logger.error("Max packet count has changed across packets.")
                        raise FileListingError("Max packet count has changed across packets")
                full_file_list_dict[packet_number] = file_list
    full_file_list = ""
    for i in range(0, max_packets):
        if full_file_list_dict.get(i, None) is None:
            logger.error("Missing packet number %s", i)
            raise FileListingError("Missing packet number %s" % (i,))
        else:
            full_file_list = full_file_list + full_file_list_dict[i]
    if full_file_list[-1:] == '|':
        full_file_list = full_file_list[0:-1]
    return full_file_list


def gprs_file_list_as_list(list_of_gprs):
    """
    Convert a list of gprs messages to a list of possible files.
    :param list_of_gprs: The input gprs messages
    :return: List of possible files on the device as strings.
    """
    full_file_list_str = gprs_file_list_as_str(list_of_gprs)
    if full_file_list_str:
        return full_file_list_str.split('|')
    return None


def main():
    """
    Main section for running interactive testing.
    """
    from meitrack.gprs_protocol import parse_data_payload

    main_logger = logging.getLogger('')
    main_logger.setLevel(logging.DEBUG)
    char_handler = logging.StreamHandler()
    char_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    char_handler.setFormatter(formatter)
    main_logger.addHandler(char_handler)

    file_listing = [
        b"""$$p1054,864507032323403,D01,8,0,180520032140_C1E1_N4U1D1.jpg|180520041216_C1E35_N1U1D1.jpg|180520004140"""
        b"""_C1E1_N4U1D1.jpg|180519204241_C1E1_N5U1D1.jpg|180519210839_C1E35_N1U1D1.jpg|180519211937_C1E1_N2U1D1.jpg"""
        b"""|180519212140_C1E1_N4U1D1.jpg|180519212242_C1E1_N5U1D1.jpg|180519215836_C1E1_N1U1D1.jpg|180519215937_"""
        b"""C1E1_N2U1D1.jpg|180519220140_C1E1_N4U1D1.jpg|180519220241_C1E1_N5U1D1.jpg|180519223836_C1E1_N1U1D1.jpg|"""
        b"""180519231836_C1E1_N1U1D1.jpg|180519224140_C1E1_N4U1D1.jpg|180518223837_C1E1_N1U1D1.jpg|180518231837_C1E1"""
        b"""_N1U1D1.jpg|180518224141_C1E1_N4U1D1.jpg|180518224242_C1E1_N5U1D1.jpg|180518231938_C1E1_N2U1D1.jpg|18051"""
        b"""8235837_C1E1_N1U1D1.jpg|180518232242_C1E1_N5U1D1.jpg|180519000039_C1E1_N3U1D1.jpg|180519000141_C1E1_N4U1"""
        b"""D1.jpg|180519000242_C1E1_N5U1D1.jpg|180519004242_C1E1_N5U1D1.jpg|180519004141_C1E1_N4U1D1.jpg|1805190108"""
        b"""37_C1E3_N1U1D1.jpg|180519012039_C1E1_N3U1D1.jpg|180519012141_C1E1_N4U1D1.jpg|180519015837_C1E1_N1U1D1.jp"""
        b"""g|180519023938_C1E1_N2U1D1.jpg|180519015939_C1E35_N1U1D1.jpg|180519020141_C1E1_N4U1D1.jpg|180519020242_C"""
        b"""1E1_N5U1D1.jpg|180519*B0\r\n""",
        b'$$q1054,864507032323403,D01,8,1,024141_C1E1_N4U1D1.jpg|180519024242_C1E1_N5U1D1.jpg|180519030837_C1E3_N1U1D1'
        b'.jpg|180519031837_C1E1_N1U1D1.jpg|180519031938_C1E1_N2U1D1.jpg|180519032039_C1E1_N3U1D1.jpg|180519032242_C1E1'
        b'_N5U1D1.jpg|180519043837_C1E1_N1U1D1.jpg|180519035837_C1E1_N1U1D1.jpg|180519035938_C1E1_N2U1D1.jpg|180519040'
        b'039_C1E1_N3U1D1.jpg|180519040040_C1E35_N1U1D1.jpg|180519040141_C1E1_N4U1D1.jpg|180519040242_C1E1_N5U1D1.jpg|'
        b'180519043938_C1E1_N2U1D1.jpg|180519044039_C1E1_N3U1D1.jpg|180519044141_C1E1_N4U1D1.jpg|180519052242_C1E1_N5U1'
        b'D1.jpg|180519050837_C1E3_N1U1D1.jpg|180519051837_C1E1_N1U1D1.jpg|180519051938_C1E1_N2U1D1.jpg|180519052039_C1'
        b'E1_N3U1D1.jpg|180519060140_C1E1_N4U1D1.jpg|180519055837_C1E1_N1U1D1.jpg|180519055937_C1E1_N2U1D1.jpg|18051906'
        b'0039_C1E1_N3U1D1.jpg|180519060141_C1E35_N1U1D1.jpg|180519060242_C1E1_N5U1D1.jpg|180519064140_C1E1_N4U1D1.jpg|'
        b'180519063837_C1E1_N1U1D1.jpg|180519063937_C1E1_N2U1D1.jpg|180519064039_C1E1_N3U1D1.jpg|180519064242_C1E1_N5U1'
        b'D1.jpg|180519071938_C1E1_N2U1D1.jpg|180519071837_C1E1_N1U1D1.jpg|180519072040_*54\r\n',
        b'$$A1054,864507032323403,D01,8,2,C1E1_N3U1D1.jpg|180519072243_C1E1_N5U1D1.jpg|180519080249_C1E1_N5U1D1.jpg|180'
        b'519100141_C1E1_N4U1D1.jpg|180519103837_C1E1_N1U1D1.jpg|180519104040_C1E1_N3U1D1.jpg|180519104242_C1E1_N5U1D1.'
        b'jpg|180519110409_C1E35_N1U1D1.jpg|180519111938_C1E1_N2U1D1.jpg|180519111837_C1E1_N1U1D1.jpg|180519112039_C1E1'
        b'_N3U1D1.jpg|180519112242_C1E1_N5U1D1.jpg|180519124141_C1E1_N4U1D1.jpg|180519224241_C1E1_N5U1D1.jpg|1805192309'
        b'54_C1E35_N1U1D1.jpg|180519231937_C1E1_N2U1D1.jpg|180519232038_C1E1_N3U1D1.jpg|180519232241_C1E1_N5U1D1.jpg|18'
        b'0519235836_C1E1_N1U1D1.jpg|180520000038_C1E1_N3U1D1.jpg|180520000140_C1E1_N4U1D1.jpg|180520000241_C1E1_N5U1D1'
        b'.jpg|180520004038_C1E1_N3U1D1.jpg|180520011050_C1E35_N1U1D1.jpg|180520011836_C1E1_N1U1D1.jpg|180520011937_C1E'
        b'1_N2U1D1.jpg|180520012038_C1E1_N3U1D1.jpg|180520012241_C1E1_N5U1D1.jpg|180520015836_C1E1_N1U1D1.jpg|180520015'
        b'937_C1E1_N2U1D1.jpg|180520020038_C1E1_N3U1D1.jpg|180520020140_C1E1_N4U1D1.jpg|180520020241_C1E1_N5U1D1.jpg|18'
        b'0520024038_C1E1_N3U1D1.jpg|180520023836_C1E1_N1U1D1.jpg|180520023937_C1E1_N*66\r\n',
        b'$$B1054,864507032323403,D01,8,3,2U1D1.jpg|180520024140_C1E1_N4U1D1.jpg|180520024241_C1E1_N5U1D1.jpg|180520031'
        b'836_C1E1_N1U1D1.jpg|180520031937_C1E1_N2U1D1.jpg|180520032038_C1E1_N3U1D1.jpg|180520032241_C1E1_N5U1D1.jpg|18'
        b'0520035836_C1E1_N1U1D1.jpg|180520035938_C1E1_N2U1D1.jpg|180520040039_C1E1_N3U1D1.jpg|180520040141_C1E1_N4U1D1'
        b'.jpg|180520040242_C1E1_N5U1D1.jpg|180520043836_C1E1_N1U1D1.jpg|180520043938_C1E1_N2U1D1.jpg|180520044039_C1E1'
        b'_N3U1D1.jpg|180520044141_C1E1_N4U1D1.jpg|180520044242_C1E1_N5U1D1.jpg|180513184246_C1E1_N5U1D1.jpg|1805131918'
        b'41_C1E1_N1U1D1.jpg|180513191942_C1E1_N2U1D1.jpg|180513192043_C1E1_N3U1D1.jpg|180513192145_C1E1_N4U1D1.jpg|180'
        b'513192246_C1E1_N5U1D1.jpg|180513193259_C1E35_N1U1D1.jpg|180513195841_C1E1_N1U1D1.jpg|180513195942_C1E1_N2U1D1'
        b'.jpg|180513200043_C1E1_N3U1D1.jpg|180513200145_C1E1_N4U1D1.jpg|180513200246_C1E1_N5U1D1.jpg|180513203328_C1E3'
        b'5_N1U1D1.jpg|180513203841_C1E1_N1U1D1.jpg|180513203942_C1E1_N2U1D1.jpg|180513204043_C1E1_N3U1D1.jpg|180513204'
        b'144_C1E1_N4U1D1.jpg|180513204246_C1E1_N5U1D1.jpg|180513211841_C1E1_N1U1D1.j*5D\r\n',
        b'$$C1054,864507032323403,D01,8,4,pg|180513211942_C1E1_N2U1D1.jpg|180513212043_C1E1_N3U1D1.jpg|180513212144_C1E'
        b'1_N4U1D1.jpg|180513212246_C1E1_N5U1D1.jpg|180513213356_C1E35_N1U1D1.jpg|180513215841_C1E1_N1U1D1.jpg|18051321'
        b'5941_C1E1_N2U1D1.jpg|180513220043_C1E1_N3U1D1.jpg|180513220144_C1E1_N4U1D1.jpg|180513220246_C1E1_N5U1D1.jpg|1'
        b'80513223425_C1E35_N1U1D1.jpg|180513223841_C1E1_N1U1D1.jpg|180513223941_C1E1_N2U1D1.jpg|180513224043_C1E1_N3U1'
        b'D1.jpg|180513224144_C1E1_N4U1D1.jpg|180513224246_C1E1_N5U1D1.jpg|180513231841_C1E1_N1U1D1.jpg|180513231941_C1'
        b'E1_N2U1D1.jpg|180513232043_C1E1_N3U1D1.jpg|180513232144_C1E1_N4U1D1.jpg|180513232246_C1E1_N5U1D1.jpg|18051323'
        b'3454_C1E35_N1U1D1.jpg|180513235841_C1E1_N1U1D1.jpg|180513235941_C1E1_N2U1D1.jpg|180514000043_C1E1_N3U1D1.jpg|'
        b'180514000144_C1E1_N4U1D1.jpg|180514000246_C1E1_N5U1D1.jpg|180514003522_C1E35_N1U1D1.jpg|180514003841_C1E1_N1U'
        b'1D1.jpg|180514003941_C1E1_N2U1D1.jpg|180514004043_C1E1_N3U1D1.jpg|180514004144_C1E1_N4U1D1.jpg|180514004246_C'
        b'1E1_N5U1D1.jpg|180514011841_C1E1_N1U1D1.jpg|180514011941_C1E1_N2U1D1.jpg|18*8B\r\n',
        b'$$D1054,864507032323403,D01,8,5,0514012043_C1E1_N3U1D1.jpg|180514012144_C1E1_N4U1D1.jpg|180514012246_C1E1_N5U'
        b'1D1.jpg|180514013551_C1E35_N1U1D1.jpg|180514015841_C1E1_N1U1D1.jpg|180514015941_C1E1_N2U1D1.jpg|180514020043_'
        b'C1E1_N3U1D1.jpg|180514020144_C1E1_N4U1D1.jpg|180514020246_C1E1_N5U1D1.jpg|180514023620_C1E35_N1U1D1.jpg|18051'
        b'4023841_C1E1_N1U1D1.jpg|180514023941_C1E1_N2U1D1.jpg|180514024043_C1E1_N3U1D1.jpg|180514024144_C1E1_N4U1D1.jp'
        b'g|180514024246_C1E1_N5U1D1.jpg|180514031841_C1E1_N1U1D1.jpg|180514031941_C1E1_N2U1D1.jpg|180514032043_C1E1_N3'
        b'U1D1.jpg|180514032144_C1E1_N4U1D1.jpg|180514032246_C1E1_N5U1D1.jpg|180514033648_C1E35_N1U1D1.jpg|180514035841'
        b'_C1E1_N1U1D1.jpg|180514035941_C1E1_N2U1D1.jpg|180514040043_C1E1_N3U1D1.jpg|180514040144_C1E1_N4U1D1.jpg|18051'
        b'4040246_C1E1_N5U1D1.jpg|180514043717_C1E35_N1U1D1.jpg|180514043841_C1E1_N1U1D1.jpg|180514043941_C1E1_N2U1D1.j'
        b'pg|180514044043_C1E1_N3U1D1.jpg|180514044144_C1E1_N4U1D1.jpg|180514044246_C1E1_N5U1D1.jpg|180514051841_C1E1_N'
        b'1U1D1.jpg|180514051942_C1E1_N2U1D1.jpg|180514052044_C1E1_N3U1D1.jpg|1805140*E4\r\n',
        b'$$E1054,864507032323403,D01,8,6,52145_C1E1_N4U1D1.jpg|180514052247_C1E1_N5U1D1.jpg|180514053746_C1E35_N1U1D1.'
        b'jpg|180514055841_C1E1_N1U1D1.jpg|180514055942_C1E1_N2U1D1.jpg|180514060044_C1E1_N3U1D1.jpg|180514060145_C1E1_'
        b'N4U1D1.jpg|180514060246_C1E1_N5U1D1.jpg|180514063814_C1E35_N1U1D1.jpg|180514063841_C1E1_N1U1D1.jpg|1805140639'
        b'42_C1E1_N2U1D1.jpg|180514064043_C1E1_N3U1D1.jpg|180514064145_C1E1_N4U1D1.jpg|180514064246_C1E1_N5U1D1.jpg|180'
        b'514071841_C1E1_N1U1D1.jpg|180514071942_C1E1_N2U1D1.jpg|180514072043_C1E1_N3U1D1.jpg|180514072145_C1E1_N4U1D1.'
        b'jpg|180514072246_C1E1_N5U1D1.jpg|180514073843_C1E35_N1U1D1.jpg|180514075841_C1E1_N1U1D1.jpg|180514075942_C1E1'
        b'_N2U1D1.jpg|180514080043_C1E1_N3U1D1.jpg|180514080145_C1E1_N4U1D1.jpg|180514080246_C1E1_N5U1D1.jpg|1805140838'
        b'41_C1E1_N1U1D1.jpg|180514083912_C1E35_N1U1D1.jpg|180514083942_C1E1_N2U1D1.jpg|180514084043_C1E1_N3U1D1.jpg|18'
        b'0514084145_C1E1_N4U1D1.jpg|180514084246_C1E1_N5U1D1.jpg|180514091841_C1E1_N1U1D1.jpg|180514091942_C1E1_N2U1D1'
        b'.jpg|180514092043_C1E1_N3U1D1.jpg|180514092145_C1E1_N4U1D1.jpg|180514092246*98\r\n',
        b'$$F309,864507032323403,D01,8,7,_C1E1_N5U1D1.jpg|180514093940_C1E35_N1U1D1.jpg|180514095840_C1E1_N1U1D1.jpg|18'
        b'0514100246_C1E1_N5U1D1.jpg|180514111942_C1E1_N2U1D1.jpg|180514100145_C1E1_N4U1D1.jpg|180514112043_C1E1_N3U1D1'
        b'.jpg|180514120043_C1E1_N3U1D1.jpg|180514120144_C1E1_N4U1D1.jpg|180514120246_C1E1_N5U1D1.jpg|*8E\r\n',
    ]

    file_part_list = []
    for gprs_item in file_listing:
        test_gprs_list, before_bytes, extra_bytes = parse_data_payload(gprs_item, DIRECTION_CLIENT_TO_SERVER)
        file_part_list.append(test_gprs_list[0])
    print(gprs_file_list_as_list(file_part_list))

    file_list_object = FileListing()
    for gprs_item in file_listing:
        test_gprs_list, before_bytes, extra_bytes = parse_data_payload(gprs_item, DIRECTION_CLIENT_TO_SERVER)
        file_list_object.add_packet(test_gprs_list[0])
        print(file_list_object.return_file_listing_list())


if __name__ == '__main__':
    main()
