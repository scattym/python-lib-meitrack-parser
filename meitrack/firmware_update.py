

class FirmwareUpdate(object):
    def __init__(self):
        self.imei = None
        self.device_code = None
        self.file_name = None
        self.ip_address = None
        self.port = None

    def fc4(self):
        """
        use to cancel the update process at any point
        FC4
        FC4,OK
        :return: gprs object
        """
        pass

    def fc5(self):
        """
        Check device code
        FC5
        FC5,Device code
        :return: gprs
        """
        pass

    def fc6(self):
        """
        Check firmware version
        FC6,OTA file name
        FC6,ACK
        :return: gprs
        """
        pass

    def fc7(self):
        """
        Set OTA server location.
        FC7,IP address,Port
        FC7,OK
        Or FC7,<Err>/<FFFF>
        FC7,OTA
        :return: gprs
        """
        pass

    def fc0(self):
        """
        Auth.
        FC0,AUTH
        FC0,Device code,OK,Data packet size,Current firmware version,OTA file name
        FC0,Device code,Err
        :return: gprs
        """
        pass

    def fc1(self):
        """
        Send ota data to device
        FC1,INDEX/OTA data length/OTA data
        FC1,Received INDEX/OTA data length received/Result
        Or FC1,NOT
        :return:
        """
        pass

    def fc2(self):
        """
        Obtaining OTA data checksum
        FC2,INDEX/Data length
        FC2,OTA data checksum
        Or FC2,NOT
        :return:
        """
        pass

    def fc3(self):
        """
        Start the ota update
        FC3
        FC3,1
        Or FC3,2
        Or FC3,3
        Or FC3,NOT
        :return:
        """
        pass