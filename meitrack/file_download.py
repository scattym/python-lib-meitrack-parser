"""
Library for working with file download gprs messages.
"""
import logging
import copy
import datetime
from functools import singledispatch

logger = logging.getLogger(__name__)


@singledispatch
def to_bytes(data):
    # This is the generic implementation
    return str(data).encode()


@to_bytes.register(bytes)
def _(data):
    return data


class FileDownloadAggregator(object):
    """
    Object for aggregating file download commands. Across different files and devices.
    """
    def __init__(self):
        """
        FileDownloadAggregator constructor
        """
        self.download_list = {}

    def add_packet(self, gprs_packet):
        """
        Add a gprs file download packet to the aggregator
        :param gprs_packet: The file download packet
        :return: Completed file or None
        """
        imei = gprs_packet.imei
        file_name = gprs_packet.get_file_name()

        key = self.check_and_create_key(imei, file_name)
        self.download_list[key].add_packet(gprs_packet)

        return self.complete_file(imei, file_name)

    def add_file_bytes(self, imei, file_name, num_packets, packet_number, file_bytes):
        """
        Add file bytes to the file aggregator class
        :param imei: The imei of the device
        :param file_name: The name of the file
        :param num_packets: The number of packets in the file
        :param packet_number: The current packet number
        :param file_bytes: The file bytes from the gprs message
        :return: Completed file or None
        """
        imei = to_bytes(imei)
        file_name = to_bytes(file_name)
        num_packets = to_bytes(num_packets)
        packet_number = to_bytes(packet_number)
        key = self.check_and_create_key(imei, file_name)
        self.download_list[key].add_file_bytes(file_name, num_packets, packet_number, file_bytes)
        return self.complete_file(imei, file_name)

    def check_and_create_key(self, imei, file_name):
        """
        Create an imei, filename key used to identify the download
        :param imei: The imei of the device
        :param file_name: The file name for download
        :return: The file download key
        """
        key = '{}-{}'.format(imei, file_name)
        if key not in self.download_list:
            self.download_list[key] = FileDownload(file_name)
        return key

    def complete_file(self, imei, file_name):
        """
        Check if file has completed transfer and return it if so. Otherwise None
        :param imei: The imei of the device
        :param file_name: The file being tracked
        :return: The file and params if file is complete. Otherwise file_name and file_bytes.
        """
        key = self.check_and_create_key(imei, file_name)
        file_bytes = None
        if self.download_list[key].is_complete():
            file_bytes = self.download_list[key].return_file_contents()
            del self.download_list[key]

        return file_name, file_bytes

    def __str__(self):
        """
        A string representation of the file download aggregator
        :return: string representation of the file download aggregator
        """
        return_str = ""
        for key in self.download_list:
            return_str = "{}\n{} {}".format(return_str, key, self.download_list[key])

        return return_str


class FileDownload(object):
    """
    Class to track a single file download
    """
    def __init__(self, file_name):
        """
        Constructor for the file download obejct
        :param file_name: The name of the file to track
        """
        self.file_name = file_name
        self.expecting_packets = None
        self.packets = {}
        self.last_updated = datetime.datetime.now()

    def add_packet(self, gprs_packet):
        """
        Add a gprs packet to this download
        :param gprs_packet: The gprs object containing the file bytes
        :return: None
        """
        if gprs_packet and gprs_packet.enclosed_data:
            file_name, num_packets, packet_number, file_bytes = gprs_packet.enclosed_data.get_file_data()
            self.add_file_bytes(file_name, num_packets, packet_number, file_bytes)

    def add_file_bytes(self, file_name, num_packets, packet_number, file_bytes):
        """
        Low level function for adding the gprs contents to the track of the file download
        :param file_name: The name of the file
        :param num_packets: The number of packets in the file
        :param packet_number: The packet number in this message
        :param file_bytes: The number of bytes
        :return: None
        """
        if file_name and file_name == self.file_name:
            self.last_updated = datetime.datetime.now()
            if not self.expecting_packets:
                self.expecting_packets = int(num_packets.decode())
            logger.log(13, "Adding packet %s to file %s", packet_number, self.file_name)
            packet_number_int = int(packet_number.decode())
            self.packets[packet_number_int] = copy.deepcopy(file_bytes)

    def next_packet(self):
        """
        Function to show which is the next packet we are expecting for this
        file download
        :return: The next packet expected as an integer.
        """
        if not self.expecting_packets:
            return 0
        for i in range(0, self.expecting_packets):
            if i not in self.packets:
                return i
        return None

    def is_complete(self):
        """
        Function to calculate if we have all packets and the download is therefore complete
        :return: Whether or not the download is complete as a boolean
        """
        if not self.expecting_packets:
            return False
        for i in range(0, self.expecting_packets):
            if i not in self.packets:
                logger.log(13, "File is not yet complete. Missing %s from %s", i, self.expecting_packets)
                return False
        logger.log(13, "File is complete")
        return True

    def fragment_list_as_string(self):
        """
        Return a list of current fragments as a string for debug
        :return: String representation of the current packets in the download
        """
        return_str = ""
        for i in self.packets:
            return_str += "{}({}) ".format(i, len(self.packets[i]))
        return return_str

    def return_file_contents(self):
        """
        Function to returnt the actual file contents once complete
        :return: The file contents as a byte string or None if the download is not yet complete.
        """
        if not self.is_complete():
            logger.log(13, "File is not complete yet. Returning None")
            return None
        else:
            file_bytes = b""
            for i in range(0, self.expecting_packets):
                file_bytes = b"".join([file_bytes, self.packets[i]])
            return file_bytes

    def __str__(self):
        return "{} {} of {}".format(self.file_name, len(self.packets), self.expecting_packets)


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

    file_agg = FileDownloadAggregator()
    for test_byte in range(0, 14):
        for test_imei in [b"0407", b"0408"]:
            test_file_name, test_file_bytes = file_agg.add_file_bytes(
                test_imei,
                b"testfile.jpg",
                str(14).encode(),
                str(test_byte).encode(),
                b"a"
            )
            print(file_agg)
            if test_file_bytes:
                print("{} {}".format(test_file_name, test_file_bytes))

    print(file_agg)

    for test_byte in range(0, 14):
        for test_imei in ["0407", "0408"]:
            test_file_name, test_file_bytes = file_agg.add_file_bytes(
                test_imei,
                b"testfile.jpg",
                14,
                test_byte,
                b"a"
            )
            print(file_agg)
            if test_file_bytes:
                print("{} {}".format(test_file_name, test_file_bytes))

    print(file_agg)


if __name__ == '__main__':
    main()
