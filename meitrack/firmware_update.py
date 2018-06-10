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
logger.setLevel(logging.DEBUG)

STAGE_FIRST = "stage1"
STAGE_SECOND = "stage2"
EPOCH = datetime.datetime(1970, 1, 1)


class FirmwareUpdate(object):
    def __init__(self, imei, device_code, ip_address, port, file_name, file_bytes, stage):
        self.imei = imei
        self.device_code = device_code
        self.file_name = file_name
        self.ip_address = ip_address
        self.port = port
        self.file_bytes = file_bytes
        self.current_message = None
        self.messages = []
        self.gprs_file_list = []
        self.is_finished = False
        self.is_error = False
        self.chunk_size = None

        self.last_message = datetime.datetime.now()
        if self.imei and self.ip_address and self.port and self.file_name and self.device_code:
            self.build_messages(stage)

    def __str__(self):
        firmware_string = "imei: {}, file_name: {}, is_finished: {}, is_error {}\n".format(
            self.imei, self.file_name, self.is_finished, self.is_error
        )
        for index, message in enumerate(self.messages):
            if message["response"] is not None:
                firmware_string += "message {} is not complete\n".format(index)
        return firmware_string

    def build_messages(self, stage):
        if stage == STAGE_FIRST:
            self.messages = [
                {"request": self.fc5(), "response": None, "sent": 0},
                {"request": self.fc6(), "response": None, "sent": 0},
                {"request": self.fc7(), "response": None, "sent": 0},
                {"request": self.fc0(), "response": None, "sent": 0},
            ]

        else:
            # At stage 2 of the firmware update process, we are expecting a new
            # connection with the fc0 message so that we know the chunk size
            self.messages = [
                {"request": self.fc0(), "response": None, "sent": (datetime.datetime.now()-EPOCH).total_seconds()},
            ]
            self.current_message = self.messages[0]["request"]

        logger.info("Message list is %s", self.messages)
        # self.messages.append({"request": self.fc4(), "response": None}, )

    def parse_fc0(self, gprs_message):
        self.chunk_size = gprs_message.enclosed_data["packet_size"]
        if self.chunk_size:
            if self.file_bytes:
                if self.file_name != gprs_message.enclosed_data["ota_file_name"]:
                    logger.error(
                        "File name from FC0: %s, does not match update object: %s",
                        self.file_name,
                        gprs_message.enclosed_data["ota_file_name"],
                    )
                else:
                    self.gprs_file_list = stc_send_ota_data(self.imei, self.file_bytes, self.chunk_size)
                    if not self.gprs_file_list:
                        logger.error("Error in creating file list. Preparing to cancel download")
                        self.is_error = True
                    for gprs in self.gprs_file_list:
                        self.messages.append({"request": gprs, "response": None, "sent": 0})

                    self.messages.append({"request": self.fc2(), "response": None, "sent": 0})
                    # self.messages.append({"request": self.fc3(), "response": None, "sent": 0})

            else:
                logger.log(13, "No file bytes. Not adding FC1 commands")
        else:
            self.is_error = True

    def parse_response(self, response_gprs):
        for message in self.messages:
            logger.info("Checking message %s", message)
            if message["sent"] != 0 and message["response"] is None:
                logger.info(
                    "Comparing request command %s to response command %s",
                    message["request"].enclosed_data.command,
                    response_gprs.enclosed_data.command
                )
                if message["request"].enclosed_data.command == response_gprs.enclosed_data.command:
                    logger.info("Found match for command %s", message["request"].enclosed_data.command)

                    # fc0 command has the chunk size, so we can now populate the fc1 commands
                    # with the specific chunks.
                    if response_gprs.enclosed_data.command == b'FC0':
                        self.parse_fc0(response_gprs)

                    message["response"] = response_gprs
                    self.current_message = None

                    if message["response"].enclosed_data.is_response_error():
                        logger.error(
                            "An error was returned during firmware update. Request %s, Response %s",
                            message["request"],
                            message["response"]
                        )
                        self.is_error = True

                    if response_gprs.enclosed_data.command == b'FC5':
                        if response_gprs.enclosed_data.ota_response_device_code() != self.device_code:
                            logger.error(
                                "Response device id %s does not match firmware device code: %s",
                                response_gprs.enclosed_data.ota_response_device_code(),
                                self.device_code
                            )
                            self.is_error = True
        for message in self.messages:
            if message["response"] is None:
                return
        self.is_finished = True
        # self.check_is_complete()

    # def check_is_complete(self):
    #     if self.is_error:
    #         self.is_finished = True
    #         return True
    #     for message in self.messages:
    #         if message["response"] is None:
    #             return False
    #     self.is_finished = True
    #     return True

    def timeout_old(self):
        now = (datetime.datetime.now() - EPOCH).total_seconds()
        for message in self.messages:
            if message["sent"] != 0 and message["response"] is None and (now - message["sent"]) >= 30:
                logger.info("Timing out firmware message %s", message)
                message["response"] = "timeout"
                if self.current_message == message["request"]:
                    self.current_message = None

    def return_next_payload(self):
        self.timeout_old()
        if self.is_finished:
            return None
        if self.is_error:
            self.is_finished = True
            return self.fc4()
        if self.current_message is not None:
            logger.info(
                "Current message already sent. Not returning a new one yet. Current message: %s",
                self.current_message
            )
        else:
            logger.info("We have a new message to sent.")
            for message in self.messages:
                if message["response"] is None and message["sent"] == 0:
                    message["sent"] = (datetime.datetime.now() - EPOCH).total_seconds()
                    if message["request"].enclosed_data.command == b'FC1':
                        message["response"] = "ignore"
                    else:
                        self.current_message = message["request"]
                    logger.info("Returning message %s", message)
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


def stc_send_ota_data(imei, file_bytes, chunk_size):
    gprs_list = []
    com_list = stc_send_ota_data_command(file_bytes, chunk_size)
    if not com_list:
        logger.error("No command list returned.")
        return []
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
