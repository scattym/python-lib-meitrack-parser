import datetime
import logging

from meitrack.command.command_FC0 import stc_auth_ota_update_command
from meitrack.command.command_FC1 import stc_send_ota_data_command
from meitrack.command.command_FC2 import stc_obtain_ota_checksum_command
from meitrack.command.command_FC3 import stc_start_ota_update_command
from meitrack.command.command_FC4 import stc_cancel_ota_update_command
from meitrack.command.command_FC5 import stc_check_device_code_command
from meitrack.command.command_FC6 import stc_check_firmware_version_command
from meitrack.command.command_FC7 import stc_set_ota_server_command
from meitrack.gprs_protocol import GPRS

logger = logging.getLogger(__name__)


class FirmwareUpdate(object):
    def __init__(self, imei, ip_address, port, file_name, file_bytes):
        self.imei = imei
        self.device_code = None
        self.file_name = file_name
        self.ip_address = ip_address
        self.port = port
        self.file_bytes = file_bytes
        self.current_message = None
        self.messages = []
        self.gprs_file_list = []

        self.last_message = datetime.datetime.now()
        if self.imei and self.ip_address and self.port and self.file_name and self.file_bytes:
            self.build_messages()

    def build_messages(self):
        self.messages = [
            {"request": self.fc5(), "response": None, "sent": False},
            {"request": self.fc6(), "response": None, "sent": False},
            {"request": self.fc7(), "response": None, "sent": False},
            {"request": self.fc0(), "response": None, "sent": False},
        ]
        self.gprs_file_list = stc_send_ota_data(self.imei, self.file_bytes)
        for gprs in self.gprs_file_list:
            self.messages.append({"request": gprs, "response": None, "sent": False})

        self.messages.append({"request": self.fc2(), "response": None, "sent": False})
        self.messages.append({"request": self.fc3(), "response": None, "sent": False})
        # self.messages.append({"request": self.fc4(), "response": None}, )

    def parse_response(self, response_gprs):
        for message in self.messages:
            if message["sent"] == True and message["response"] is None:
                if message["request"].enclosed_data.command == response_gprs.enclosed_data.command:
                    self.current_message = None
                    message["response"] = response_gprs

    def return_next_payload(self):
        if self.current_message is None:
            for message in self.messages:
                if message["response"] is None and message["sent"] is False:
                    message["sent"] = True
                    return message["request"]
        return None

    def fc4(self):
        """
        use to cancel the update process at any point
        FC4
        FC4,OK
        :return: gprs object
        """
        return stc_cancel_ota_update(self.imei)

    def fc5(self):
        """
        Check device code
        FC5
        FC5,Device code
        :return: gprs
        """
        return stc_check_device_code(self.imei)

    def fc6(self):
        """
        Check firmware version
        FC6,OTA file name
        FC6,ACK
        :return: gprs
        """
        return stc_check_firmware_version(self.imei, self.file_name)

    def fc7(self):
        """
        Set OTA server location.
        FC7,IP address,Port
        FC7,OK
        Or FC7,<Err>/<FFFF>
        FC7,OTA
        :return: gprs
        """
        return stc_set_ota_server(self.imei, self.ip_address, self.port)

    def fc0(self):
        """
        Auth.
        FC0,AUTH
        FC0,Device code,OK,Data packet size,Current firmware version,OTA file name
        FC0,Device code,Err
        :return: gprs
        """
        return stc_auth_ota_update(self.imei)

    def fc1(self):
        """
        Send ota data to device
        FC1,INDEX/OTA data length/OTA data
        FC1,Received INDEX/OTA data length received/Result
        Or FC1,NOT
        :return: gprs
        """
        if self.gprs_file_list:
            return self.gprs_file_list[0]

    def fc2(self):
        """
        Obtaining OTA data checksum
        FC2,INDEX/Data length
        FC2,OTA data checksum
        Or FC2,NOT
        :return: gprs
        """
        return stc_obtain_ota_checksum(self.imei)


    def fc3(self):
        """
        Start the ota update
        FC3
        FC3,1
        Or FC3,2
        Or FC3,3
        Or FC3,NOT
        :return: gprs
        """
        return stc_start_ota_update(self.imei)


def stc_auth_ota_update(imei):
    com = stc_auth_ota_update_command()
    gprs = GPRS()
    gprs.direction = b'@@'
    gprs.data_identifier = b'a'
    gprs.enclosed_data = com
    gprs.imei = imei

    return gprs


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


def stc_obtain_ota_checksum(imei):
    com = stc_obtain_ota_checksum_command()
    gprs = GPRS()
    gprs.direction = b'@@'
    gprs.data_identifier = b'a'
    gprs.enclosed_data = com
    gprs.imei = imei

    return gprs


def stc_start_ota_update(imei):
    com = stc_start_ota_update_command()
    gprs = GPRS()
    gprs.direction = b'@@'
    gprs.data_identifier = b'a'
    gprs.enclosed_data = com
    gprs.imei = imei

    return gprs


def stc_cancel_ota_update(imei):
    com = stc_cancel_ota_update_command()
    gprs = GPRS()
    gprs.direction = b'@@'
    gprs.data_identifier = b'a'
    gprs.enclosed_data = com
    gprs.imei = imei

    return gprs


def stc_check_device_code(imei):
    com = stc_check_device_code_command()
    gprs = GPRS()
    gprs.direction = b'@@'
    gprs.data_identifier = b'a'
    gprs.enclosed_data = com
    gprs.imei = imei

    return gprs


def stc_check_firmware_version(imei, file_name):
    com = stc_check_firmware_version_command(file_name)
    gprs = GPRS()
    gprs.direction = b'@@'
    gprs.data_identifier = b'a'
    gprs.enclosed_data = com
    gprs.imei = imei

    return gprs


def stc_set_ota_server(imei, ip_address, port):
    com = stc_set_ota_server_command(ip_address, port)
    gprs = GPRS()
    gprs.direction = b'@@'
    gprs.data_identifier = b'a'
    gprs.enclosed_data = com
    gprs.imei = imei

    return gprs

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

    print(stc_auth_ota_update(b'0407'))
    print(stc_auth_ota_update(b'0407').as_bytes())

    gprss = stc_send_ota_data(b'0407', b"testfil"*190)
    for test_gprs in gprss:
        print(test_gprs)
        print(test_gprs.as_bytes())

    print(stc_obtain_ota_checksum(b'0407'))
    print(stc_obtain_ota_checksum(b'0407').as_bytes())
    print(stc_start_ota_update(b'0407'))
    print(stc_start_ota_update(b'0407').as_bytes())
    print(stc_cancel_ota_update(b'0407'))
    print(stc_cancel_ota_update(b'0407').as_bytes())
    print(stc_check_device_code(b'0407'))
    print(stc_check_device_code(b'0407').as_bytes())
    print(stc_check_firmware_version(b'0407', b'testfile.ota'))
    print(stc_check_firmware_version(b'0407', b'testfile.ota').as_bytes())
    print(stc_set_ota_server(b'0407', b'1.1.1.1', b'6100'))
    print(stc_set_ota_server(b'0407', b'1.1.1.1', b'6100').as_bytes())
    fu = FirmwareUpdate(b'0407', b'home.scattym.com', b'65533', b'testfile.ota', b'testfilecontents')
    print(fu.return_next_payload())
    print(fu.return_next_payload())
    fu.fc5_response = 'done'
    fu.current_message = None
    print(fu.return_next_payload())
    fu.fc6_response = 'done'
    fu.current_message = None
    print(fu.return_next_payload())
    fu.fc7_response = 'done'
    fu.current_message = None
    print(fu.return_next_payload())
    fu.fc0_response = 'done'
    fu.current_message = None
    print(fu.return_next_payload())
    fu.fc1_response = 'done'
    fu.current_message = None
    print(fu.return_next_payload())
    fu.fc2_response = 'done'
    fu.current_message = None
    print(fu.return_next_payload())
    fu.fc3_response = 'done'
    fu.current_message = None
    print(fu.return_next_payload())
    fu.fc4_response = 'done'
    fu.current_message = None
    print(fu.return_next_payload())
    fu.current_message = None
