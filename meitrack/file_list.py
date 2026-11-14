"""
Library for working with file listing gprs messages
"""

import logging

from meitrack.error import GPRSError

logger = logging.getLogger(__name__)


class FileListingError(GPRSError):
    """
    File listing error class
    """


class FileListing:
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
        if gprs_packet.enclosed_data["command"] == b"D01":
            packet_count, packet_number, file_list = (
                gprs_packet.enclosed_data.get_file_list()
            )
            if packet_count is None or packet_number is None or file_list is None:
                logger.error("Unable to extract details from packet")
                raise FileListingError("Unable to extract details from packet")
            else:
                packet_count = int(packet_count.decode())
                packet_number = int(packet_number.decode())
                if not self.max_packets:
                    self.max_packets = packet_count
                else:
                    if self.max_packets != packet_count:
                        logger.error("Max packet count has changed across packets.")
                        raise FileListingError(
                            "Max packet count has changed across packets"
                        )
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
            logger.error("Max packets is zero")
            return False

        for i in range(self.max_packets):
            if self.full_file_list_dict.get(i, None) is None:
                logger.error("Missing packet number %s", i)
                return False
        return True

    def fragment_list_as_string(self):
        """
        Function to return the fragment list as a string for debug
        :return: Fragment list tracked as a string
        """
        return_str = ""
        for i in self.full_file_list_dict:
            return_str += f"{i}({len(self.full_file_list_dict[i])}) "
        return return_str

    def return_file_listing(self):
        """
        Function to return a list of files currently tracked to be on the device
        :return: List of files on the device that have been reported.
        """
        if not self.is_complete():
            logger.log(13, "File list is not complete yet. Returning None")
            return None
        chunks = []
        for i in range(self.max_packets):
            chunk = self.full_file_list_dict.get(i)
            if chunk is None:
                logger.error("Missing packet number %s", i)
                return None
            chunks.append(chunk)
        full_file_list = b"".join(chunks)
        if full_file_list.endswith(b"|"):
            full_file_list = full_file_list[:-1]
        return full_file_list

    def return_file_listing_list(self):
        """
        Return files on device as a list.
        :return: File list or None
        """
        file_str = self.return_file_listing()
        if file_str:
            return file_str.split(b"|")
        return None

    def __str__(self):
        """
        String representation fo the file list class
        :return: String representation fo the file list class
        """
        return f"Length: {len(self.file_arr)}, Content: {self.file_arr}"


def _collect_file_list_chunks(list_of_gprs):
    full_file_list_dict = {}
    max_packets = 0
    for gprs in list_of_gprs:
        if gprs.enclosed_data.get("command") != b"D01":
            continue
        packet_count, packet_number, file_list = gprs.enclosed_data.get_file_list()
        if packet_count is None or packet_number is None or file_list is None:
            continue
        pkt_cnt = int(packet_count.decode())
        pkt_num = int(packet_number.decode())
        fl_str = file_list.decode()
        if not max_packets:
            max_packets = pkt_cnt
        elif max_packets != pkt_cnt:
            logger.error("Max packet count has changed across packets.")
            raise FileListingError("Max packet count has changed across packets")
        full_file_list_dict[pkt_num] = fl_str
    return full_file_list_dict, max_packets


def gprs_file_list_as_str(list_of_gprs):
    """
    Convert a list of gprs messages to a list of possible files as a string.
    :param list_of_gprs: The input gprs messages
    :return: List of possible files on the device as a single pipe separated file list string.
    """
    full_file_list_dict, max_packets = _collect_file_list_chunks(list_of_gprs)
    chunks = []
    for i in range(max_packets):
        chunk = full_file_list_dict.get(i)
        if chunk is None:
            logger.error("Missing packet number %s", i)
            raise FileListingError(f"Missing packet number {i}")
        chunks.append(chunk)

    full_file_list = "".join(chunks)
    full_file_list = full_file_list.removesuffix("|")
    return full_file_list


def gprs_file_list_as_list(list_of_gprs):
    """
    Convert a list of gprs messages to a list of possible files.
    :param list_of_gprs: The input gprs messages
    :return: List of possible files on the device as strings.
    """
    full_file_list_str = gprs_file_list_as_str(list_of_gprs)
    if full_file_list_str:
        return full_file_list_str.split("|")
    return None


def main():
    """
    Main section for running interactive testing.
    """


if __name__ == "__main__":
    main()
