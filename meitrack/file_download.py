import logging
import copy

logger = logging.getLogger(__name__)


class FileDownload(object):
    def __init__(self, file_name):
        self.file_name = file_name
        self.expecting_packets = None
        self.packets = {}

    def add_packet(self, gprs_packet):
        if gprs_packet and gprs_packet.enclosed_data:
            file_name, num_packets, packet_number, file_bytes = gprs_packet.enclosed_data.get_file_data()
            if file_name and file_name == self.file_name:
                if not self.expecting_packets:
                    self.expecting_packets = int(num_packets.decode())
                logger.log(13, "Adding packet %s to file %s", packet_number, self.file_name)
                packet_number_int = int(packet_number.decode())
                self.packets[packet_number_int] = copy.deepcopy(file_bytes)

    def next_packet(self):
        if not self.expecting_packets:
            return 0
        for i in range(0, self.expecting_packets):
            if i not in self.packets:
                return i
        return None

    def is_complete(self):
        if not self.expecting_packets:
            return False
        for i in range(0, self.expecting_packets):
            if i not in self.packets:
                logger.log(13, "File is not yet complete. Missing %s from %s", i, self.expecting_packets)
                return False
        logger.log(13, "File is complete")
        return True

    def fragment_list_as_string(self):
        return_str = ""
        for i in self.packets:
            return_str += "{}({}) ".format(i, len(self.packets[i]))
        return return_str

    def return_file_contents(self):
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