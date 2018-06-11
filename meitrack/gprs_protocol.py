#!/usr/bin/env python
import logging

import sys
from meitrack import event
from meitrack.command.command_to_object import command_to_object
from meitrack.error import GPRSParseError
from meitrack.common import CLIENT_TO_SERVER_PREFIX, SERVER_TO_CLIENT_PREFIX, DIRECTION_CLIENT_TO_SERVER
from meitrack.common import DIRECTION_SERVER_TO_CLIENT, END_OF_MESSAGE_STRING, MAX_DATA_LENGTH


logger = logging.getLogger(__name__)

"""
payload $$<Data identifier><Data length>,<IMEI>,<Command type>,<Command><*Checksum>\r\n
"""


def prefix_to_direction(prefix):
    if prefix == SERVER_TO_CLIENT_PREFIX:
        return DIRECTION_SERVER_TO_CLIENT
    elif prefix == CLIENT_TO_SERVER_PREFIX:
        return DIRECTION_CLIENT_TO_SERVER
    raise GPRSParseError("Invalid prefix %s" % (prefix,))


class GPRS(object):
    def __init__(self, payload=None):
        self.payload = b""
        self.direction = None
        self.data_identifier = None
        self.data_length = b"0"
        self.data_payload = None
        self.imei = None
        self.command_type = None
        self.checksum = None
        self.enclosed_data = None
        self.leftover = ""
        if payload:
            self.parse_data_payload(payload)

    def parse_data_payload(self, payload):
        self.payload = payload
        self.direction = payload[0:2]
        self.data_identifier = chr(payload[2]).encode()
        self.checksum = payload[-4:-2]
        first_comma = payload.find(b',')
        # print("Data length is")
        # print(payload[3:first_comma])
        # print(type(payload[3:first_comma]))
        self.data_length = payload[3:first_comma]
        self.data_payload = payload[first_comma:]
        self.leftover = payload[first_comma+1:-5]

        next_comma = self.leftover.find(b',')
        self.imei = self.leftover[:next_comma]
        self.leftover = self.leftover[next_comma+1:]

        self.command_type = self.leftover[0:3]
        self.leftover = self.leftover
        self.enclosed_data = command_to_object(
            prefix_to_direction(self.direction),
            self.command_type,
            self.leftover
        )

    @property
    def checksum(self):
        if self.__checksum:
            return self.__checksum
        return b"XX"

    @checksum.setter
    def checksum(self, checksum):
        self.__checksum = checksum

    @property
    def enclosed_data(self):
        return self.__enclosed_data

    @enclosed_data.setter
    def enclosed_data(self, enclosed_commmand_object):
        if enclosed_commmand_object is not None:
            self.leftover = enclosed_commmand_object.as_bytes()
            self.__enclosed_data = enclosed_commmand_object

    @property
    def data_length(self):
        data = (
                b"," + self.imei + b"," +
                self.leftover + b"*" + self.checksum + END_OF_MESSAGE_STRING
        )
        return str(len(data)).encode()

    @data_length.setter
    def data_length(self, data_length):
        self.__data_length = str(data_length).encode()

    def __str__(self):
        return_str = "Payload: %s\n" % (self.payload,)
        return_str += "Direction: %s\n" % (self.direction,)
        return_str += "identifier: %s\n" % (self.data_identifier,)
        return_str += "length: %s\n" % (self.data_length,)
        return_str += "data payload: %s\n" % (self.data_payload,)
        return_str += "imei: %s\n" % (self.imei,)
        return_str += "command_type: %s\n" % (self.command_type,)
        return_str += "checksum: %s\n" % (self.checksum,)
        return_str += "leftover: %s\n" % (self.leftover,)
        if self.enclosed_data:
            return_str += str(self.enclosed_data)
        return return_str

    def as_bytes(self, counter=None):
        # print(chr(self.data_identifier).encode())
        # print(type(chr(self.data_identifier).encode()))
        # print(self.data_length)
        if counter is not None:
            subset = (counter % 58) + 65
            self.data_identifier = bytes([subset])
        string_to_sign = (
            b"".join(
                [
                    self.direction, self.data_identifier, self.data_length,
                    b",", self.imei, b",", self.leftover, b"*"
                ]
            )
        )
        checksum_hex = "{:02X}".format(calc_signature(string_to_sign))
        self.checksum = checksum_hex.encode()
        # self.checksum = "{:02X}".format(calc_signature(string_to_sign))
        # print(type(self.data_identifier))
        return_str = (
            b"".join(
                [
                    self.direction, self.data_identifier, self.data_length, b",",
                    self.imei, b",", self.leftover, b"*", self.checksum, END_OF_MESSAGE_STRING
                ]
            )
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


def parse_data_payload(payload, direction):
    leftover = b''
    before = b''
    gprs_list = []
    while len(payload) > 0:

        if direction == DIRECTION_CLIENT_TO_SERVER:
            direction_start = payload.find(CLIENT_TO_SERVER_PREFIX)
        else:
            direction_start = payload.find(SERVER_TO_CLIENT_PREFIX)
        if direction_start < 0:
            logger.error("Unable to find start payload")
            leftover = payload
            payload = b''
        else:
            # direction_end = direction_start + 2
            if direction_start > 0:
                before = payload[0:direction_start]

            payload = payload[direction_start:]

            # data_identifier = payload[2]

            first_comma = payload.find(b',')
            if not first_comma:
                logger.error("No first comma found. Can't get to calculate length of payload")
                leftover = payload
                payload = b''
            else:
                logger.log(13, "Data length is %s", payload[3:first_comma])
                try:
                    data_length = int(payload[3:first_comma])
                except ValueError as err:
                    logger.error("Unable to calculate length field from payload %s", payload)
                    # raise GPRSParseError("Unable to calculate length from data: {}".format(payload[3:first_comma]))
                    data_length = 0

                if data_length > MAX_DATA_LENGTH:
                    raise GPRSParseError("Data length is longer than the protocol allows: {}".format(data_length))

                if data_length != 0 and len(payload) >= (first_comma + data_length):
                    logger.log(13, "Start of payload is {}".format(payload[0:2]))
                    logger.log(13, "End of payload is {}".format(payload[-2:]))
                    message = payload[:first_comma+data_length]
                    payload = payload[first_comma+data_length:]

                    if message[-2:] != END_OF_MESSAGE_STRING:
                        logger.error("Last two characters of message is >%s<", message[-2:])
                        raise GPRSParseError("Found begin token, but length does not lead to end of payload. %s", payload)

                    current_gprs = GPRS(message)
                    gprs_list.append(current_gprs)
                else:
                    leftover = payload
                    payload = b''

    return gprs_list, before, leftover


def calc_signature(payload):
    # print(type(payload))
    # print(payload)
    checksum = 0
    lastchar = payload.find(b'*')
    for char in payload[0:lastchar+1]:
        checksum = checksum + char
    checksum = checksum & 0xFF
    # print("checksum is ", checksum)
    return checksum


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

    test_data = [
        b"""$$D160,864507032228727,AAA,35,24.819116,121.026091,180323023615,A,7,16,0,176,1.3,83,7,1174,466|97|527B|01035DB4,0000,0001|0000|0000|019A|0981,00000001,,3,,,36,23*DC\r\n""",
        b"""$$G162,864507032228727,AAA,35,24.818730,121.025900,180323055955,A,5,13,0,250,1.2,65,67,12460,466|97|527B|01035DB3,0000,0001|0000|0000|019C|0980,00000001,,3,,,42,39*49\r\n""",
        b"""$$L162,864507032228727,AAA,35,24.819173,121.026060,180323060454,A,8,12,0,24,1.4,60,108,12757,466|97|527B|01035DB3,0000,0001|0000|0000|019C|0984,00000001,,3,,,44,39*4D\r\n""",
        b"""$$M163,864507032228727,AAA,35,24.819173,121.026053,180323060554,A,8,12,0,189,0.9,59,108,12817,466|97|527B|01036CAB,0000,0000|0000|0000|019D|0983,00000001,,3,,,90,47*A4\r\n""",
        b"""$$N163,864507032228727,AAA,35,24.819116,121.026023,180323060654,A,9,15,0,268,0.9,58,112,12877,466|97|527B|010319B1,0000,0001|0000|0000|019D|0983,00000001,,3,,,35,82*82\r\n""",
        b"""$$H163,864507032228727,AAA,35,24.819120,121.026041,180323061242,A,7,14,1,200,0.9,58,172,13212,466|97|527B|01035C49,0000,0001|0000|0000|019D|0983,00000001,,3,,,53,84*61\r\n""",
        b"""$$I163,864507032228727,AAA,35,24.819040,121.026001,180323061342,A,7,14,0,310,0.9,58,180,13272,466|97|527B|01035DB3,0000,0001|0000|0000|019D|0983,00000001,,3,,,50,92*6B\r\n""",
        b"""$$J163,864507032228727,AAA,35,24.819090,121.026008,180323061441,A,7,14,0,233,0.9,57,184,13331,466|97|527B|01035DB3,0000,0001|0000|0000|019D|0983,00000001,,3,,,38,46*80\r\n""",
        b"""$$K163,864507032228727,AAA,35,24.819126,121.026058,180323061541,A,8,14,0,149,0.9,57,185,13391,466|97|527B|01035DB4,0000,0001|0000|0000|019D|0984,00000001,,3,,,43,47*94\r\n""",
        b"""$$S163,864507032228727,AAA,35,24.819118,121.026070,180323062200,A,9,14,0,114,0.8,57,196,13770,466|97|527B|01035DB3,0000,0001|0000|0000|019C|0983,00000001,,3,,,93,73*8C\r\n""",
        b"""$$T163,864507032228727,AAA,35,24.819118,121.026070,180323062300,A,9,14,0,114,0.8,57,196,13829,466|97|527B|01035DB3,0000,0000|0000|0000|019D|0983,00000001,,3,,,88,44*95\r\n""",
        b"""@@Q25,353358017784062,A10*6A\r\n""",
        b"""@@S28,353358017784062,A11,10*FD\r\n""",
        b"""$$S28,353358017784062,A11,OK*FE\r\n""",
        b"""@@Q25,353358017784062,A10*6A\r\n""",
        b"""$$Q128,353358017784062,AAA,34,22.543176,114.078448,100313093738,A,5,22,2,205,5,-14,0,60,0|0|10133|4110,0000,149|153|173|2707|914,*91\r\n""",
        b"""@@S28,353358017784062,A11,10*FD\r\n""",
        b"""$$S28,353358017784062,A11,OK*FE\r\n""",
        b"""@@V27,353358017784062,A12,6*D5\r\n""",
        b"""$$V28,353358017784062,A12,OK*02\r\n""",
        b"""@@X29,353358017784062,A13,120*37\r\n""",
        b"""$$X28,353358017784062,A13,OK*05\r\n""",
        b"""@@D30,353358017784062,A14,1000*4A\r\n""",
        b"""$$D28,353358017784062,A14,OK*F2\r\n""",
        b"""@@E27,353358017784062,A15,6*C7\r\n""",
        b"""$$E28,353358017784062,A15,OK*F4\r\n""",
        b"""@@F27,353358017784062,A16,0*C3\r\n""",
        b"""$$F28,353358017784062,A16,OK*F6\r\n""",
        b"""@@T27,353358017784062,A17,1*D3\r\n""",
        b"""$$T28,353358017784062,A17,OK*05\r\n""",
        b"""@@H27,353358017784062,A19,1*C9\r\n""",
        b"""$$H28,353358017784062,A19,OK*F8\r\n""",
        b"""@@H48,353358017784062,A21,1,67.203.13.26,8800,,,*C9\r\n""",
        b"""$$H28,353358017784062,A21,OK*F4\r\n""",
        b"""@@K38,353358017784062,A22,75.127.67.90*FD\r\n""",
        b"""$$K28,353358017784062,A22,OK*F8\r\n""",
        b"""@@S43,353358017784062,A23,67.203.13.26,8800*F0\r\n""",
        b"""$$S28,353358017784062,A23,OK*01\r\n""",
        b"""@@T25,353358017784062,A70*93\r\n""",
        b"""$$T85,353358017784062,A70,13811111111,13822222222,13833333333,13844444444,13855555555*21\r\n""",
        b"""@@U61,353358017784062,A71,13811111111,13822222222,13833333333*7D\r\n""",
        b"""$$U28,353358017784062,A71,OK*06\r\n""",
        b"""@@V49,353358017784062,A72,13844444444,13855555555*55\r\n""",
        b"""$$V28,353358017784062,A72,OK*08\r\n""",
        b"""@@W27,353358017784062,A73,2*D9\r\n""",
        b"""$$W28,353358017784062,A73,OK*0A\r\n""",
        b"""@@h27,353358017784062,AFF,1*0B\r\n""",
        b"""$$h28,353358017784062,AFF,OK*3D\r\n""",
        b"""@@H57,353358017784062,B05,1,22.913191,114.079882,1000,0,1*96\r\n""",
        b"""$$H28,353358017784062,B05,OK*F7\r\n""",
        b"""@@J27,353358017784062,B06,1*C8\r\n""",
        b"""$$J28,353358017784062,B06,OK*FA\r\n""",
        b"""@@P28,353358017784062,B07,60*05\r\n""",
        b"""$$P28,353358017784062,B07,OK*01\r\n""",
        b"""@@I27,353358017784062,B08,3*CB\r\n""",
        b"""$$I28,353358017784062,B08,OK*FB\r\n""",
        b"""@@C27,353358017784062,B21,1*BE\r\n""",
        b"""$$C28,353358017784062,B21,OK*F0\r\n""",
        b"""@@J28,353358017784062,B31,10*F7\r\n""",
        b"""$$J28,353358017784062,B31,OK*F8\r\n""",
        b"""@@N28,353358017784062,B34,60*03\r\n""",
        b"""$$N28,353358017784062,B34,OK*FF\r\n""",
        b"""@@O29,353358017784062,B35,480*3C\r\n""",
        b"""$$O28,353358017784062,B35,OK*01\r\n""",
        b"""@@P29,353358017784062,B36,480*3E\r\n""",
        b"""$$P28,353358017784062,B36,OK*03\r\n""",
        b"""@@U27,353358017784062,B60,1*D3\r\n""",
        b"""$$U28,353358017784062,B60,OK*05\r\n""",
        b"""@@R31,353358017784062,B91,1,SOS*F0\r\n""",
        b"""$$R28,353358017784062,B91,OK*06\r\n""",
        b"""@@q42,353358017784062,B92,1234567890ABCDEF*62\r\n""",
        b"""$$q28,353358017784062,B92,OK*26\r\n""",
        b"""@@V25,353358017784062,B93*7B\r\n""",
        b"""$$V42,353358017784062,B93,00000007E01C001F*B5\r\n""",
        b"""@@A42,353358017784062,B96,0000000000000001*95\r\n""",
        b"""$$A28,353358017784062,B96,OK*FA\r\n""",
        b"""@@C25,353358017784062,B97*6C\r\n""",
        b"""$$C42,353358017784062,B97,0000000000000001*60\r\n""",
        b"""@@B34,863070010825791,B99,gprs,get*BC\r\n""",
        b"""$$B33,863070010825791,B99,1,17,18*B5\r\n""",
        b"""@@M34,353358017784062,C01,20,10122*18\r\n""",
        b"""$$M28,353358017784062,C01,OK*F9\r\n""",
        # b"""@@f47,353358017784062,C02,0,15360853789,Meitrack*B1\r\n""",
        b"""@@f47,353358017784062,C02,0,15360853789,Meitrac*B1\r\n""",
        b"""$$f28,353358017784062,C02,OK*13\r\n""",
        b"""@@f27,353358017784062,C03,0*E1\r\n""",
        b"""$$f28,353358017784062,C03,OK*14\r\n""",
        b"""@@m42,013777001338688,C13,0,E,TestMessage*08\r\n""",
        b"""$$m28,013777001338688,C13,OK*1C\r\n""",
        # b"""@@q35,012896001078259,C40,(1BD5#040000W02*50\r\n""",
        # b"""$$q36,012896001078259,C40,(1BD5#040000W0201*1B\r\n""",
        b"""@@n28,012896001078259,C41,01*19\r\n""",
        b"""$$n30,012896001078259,C41,01,1*37\r\n""",
        b"""@@m25,012896001078259,C42*89\r\n""",
        # b"""$$t45,012896001078259,C42,(B4v#040000R00,(1BD5#040000W00*13\r\n""",
        # b"""@@o57,012896001078259,C43,01(1BD5#040000W<0005000101T1#00000000000000000000000000*3F""",
        # b"""$$o28,012896001078259,C43,0101*85\r\n""",
        b"""$$o32,012896001078259,C43,0101*85\r\n""",
        b"""@@r25,012896001078259,C44*90\r\n""",
        # b"""$$r274,012896001078259,C44,01(B4v#040000R0000000000000000000000000000000000000000000002(1BD5#040000W00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000*1E\r\n""",
        b"""@@i25,012896001078259,C46*89\r\n""",
        # b"""$$i28,012896001078259,C46,12_*F1\r\n""",
        b"""$$i28,012896001078259,C46,12*F1\r\n""",
        b"""@@f33,353358017784062,C47,2,90,10*0A\r\n""",
        b"""$$f28,353358017784062,C47,OK*1C\r\n""",
        b"""@@c25,353358017784062,C48*89\r\n""",
        b"""$$c33,353358017784062,C48,2,90,10*D0\r\n""",
        b"""@@c29,353358017784062,C49,3,2*4B\r\n""",
        b"""$$c28,353358017784062,C49,ok*5B\r\n""",
        b"""@@O48,353358017784062,D00,0215080432_C2E03.jpg,0*DB\r\n""",
        b"""@@A27,353358017784062,D01,0*BB\r\n""",
        b"""$$A480,353358017784062,D01,3,0,0506162517_C1E03.jpg|0506162517_C1E11.jpg|0506162624_C1E03.jpg|0506162630_C1E11.jpg|0506162720_C1E03.jpg|0506162721_C1E03.jpg|0215080547_C1E03.jpg|0215080547_C1E11.jpg|0215080626_C1E03.jpg|0215080626_C1E11.jpg|0215080827_C1E03.jpg|0215080827_C1E11.jpg|0215080850_C1E03.jpg|0215080850_C1E11.jpg|0507145426_C1E03.jpg|0507145426_C1E11.jpg|0507145512_C2E03.jpg|0507145512_C2E11.jpg|0215080050_C3E03.jpg|0215080050_C3E11.jpg|0215080459_C3E03.jpg|021508050*41\r\n""",
        b"""@@E110,353358017784062,D02,0506162517_C1E03.jpg|0506162517_C1E11.jpg|0506162624_C1E03.jpg|0506162630_C1E11.jpg|*4E\r\n""",
        b"""$$F28,353358017784062,D02,OK*F4\r\n""",
        b"""@@D46,353358017784062,D03,1,camerapicture.jpg*E2\r\n""",
        b"""$$D28,353358017784062,D03,OK*F3\r\n""",
        b"""@@f43,353358017784062,D10,13737431,13737461*17\r\n""",
        b"""$$f28,353358017784062,D10,OK*13\r\n""",
        b"""@@e36,353358017784062,D11,13737431,1*AA\r\n""",
        b"""$$e28,353358017784062,D11,OK*13\r\n""",
        b"""@@C34,353358017784062,D12,13737431*2A\r\n""",
        b"""$$C27,353358017784062,D12,0*87\r\n""",
        b"""@@w27,353358017784062,D13,0*F4\r\n""",
        b"""@@Q34,353358017784062,D14,13723455*3B\r\n""",
        b"""$$Q28,353358017784062,D14,OK*02\r\n""",
        b"""@@K36,353358017784062,D15,13723455,3*97\r\n""",
        b"""$$K28,353358017784062,D15,OK*FD\r\n""",
        b"""@@u25,353358017784062,D16*97\r\n""",
        b"""$$u28,353358017784062,D16,18*F7\r\n""",
        b"""@@V75,353358017784062,D65,30000,50000,60000,70000,80000,90000,100000,110000*EA\r\n""",
        b"""$$V28,353358017784062,D65,OK*OD\r\n""",
        b"""@@V65,353358017784062,D66,8726,8816,8906,8996,9086,9176,9266,9356*A2\r\n""",
        b"""$$V28,353358017784062,D66OK*E2\r\n""",
        b"""@@W25,353358017784062,E91*7D\r\n""",
        b"""$$W38,353358017784062,FWV1.00,12345678*1C\r\n""",
        b"""@@j25,353358017784062,F01*88\r\n""",
        b"""$$j28,353358017784062,F01,OK*19\r\n""",
        b"""@@Z25,353358017784062,F02*79\r\n""",
        b"""$$Z28,353358017784062,F02,OK*0A\r\n""",
        b"""@@D40,353358017784062,F08,0,4825000*51\r\n""",
        b"""$$D28,353358017784062,F08,OK*FA\r\n""",
        b"""@@E27,353358017784062,F09,1*CA\r\n""",
        b"""$$E28,353358017784062,F09,OK*FC\r\n""",
        b"""@@[25,353358017784062,F11*7A\r\n""",
        b"""$$[28,353358017784062,F11,OK*0B\r\n""",
        b"""$$D160,864507032228727,AAA,35,24.819116,121.026091,180323023615,A,7,16,0,176,1.3,83,7,1174,466|97|527B|01035DB4,0000,0001|0000|0000|019A|0981,00000001,,3,,,36,23*DC\r\n""",
        b"""$$D160,864507032228727,AAA,35,24.819116,121.026091,180323023615,A,7,16,0,176,1.3,83,7,1174,466|97|527B|01035DB4,0000,0001|0000|0000|019A|0981,00000001,,3,,,36,23*DC\r\n$$D160,864507032228727,AAA,35,24.819116,121.026091,180323023615,A,7,16,0,176,1.3,83,7,1174,466|97|527B|01035DB4,0000,0001|0000|0000|019A|0981,00000001,,3,,,36,23*DC\r\n"""
        b"""$$D161,864507032228727,AAA,50,24.819116,121.026091,180323023615,A,7,16,0,176,1.3,83,7,1174,466|97|527B|01035DB4,0000,0001|0000|0000|019A|0981,00000001,,,3,,,36,23*DC\r\n""",
#       b"""$$`164,864507032228727,AAA,35,24.818910,121.025936,180329052345,A,7,13,0,16,1.2,69,2720,86125,466|97|527B|01035DB4,0000,0001|0000|0000|019E|097F,00000001,,3,,,124,96*F2""",
        b"""$$A182,864507032323403,AAA,29,-33.815820,151.200085,180424172103,A,6,9,1,0,1.2,68,2450,7931,0|0|0000|00000000,0000,0000|0000|0000|0167|0000,,,108,0000,,3,0,,0|0000|0000|0000|0000|0000*C9\r\n""",
        b"""@@X27,864507032323403,D01,0*C6\r\n""",
        b"""@@A27,353358017784062,D01,0*BB\r\n""",
        b'$$n1084,864507032323403,D00,180425071619_C1E1_N2U1D1.jpg,16,0,\xff\xd8\xff\xdb\x00\x84\x00\x14\x0e\x0f\x12\x0f\r\x14\x12\x10\x12\x17\x15\x14\x18\x1e2!\x1e\x1c\x1c\x1e=,.$2I@LKG@FEPZsbPUmVEFd\x88emw{\x81\x82\x81N`\x8d\x97\x8c}\x96s~\x81|\x01\x15\x17\x17\x1e\x1a\x1e;!!;|SFS||||||||||||||||||||||||||||||||||||||||||||||||||\xff\xc0\x00\x11\x08\x01\xe0\x02\x80\x03\x01!\x00\x02\x11\x01\x03\x11\x01\xff\xdd\x00\x04\x00\n\xff\xc4\x01\xa2\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x10\x00\x02\x01\x03\x03\x02\x04\x03\x05\x05\x04\x04\x00\x00\x01}\x01\x02\x03\x00\x04\x11\x05\x12!1A\x06\x13Qa\x07"q\x142\x81\x91\xa1\x08#B\xb1\xc1\x15R\xd1\xf0$3br\x82\t\n\x16\x17\x18\x19\x1a%&\'()*456789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\x01\x00\x03\x01\x01\x01\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x11\x00\x02\x01\x02\x04\x04\x03\x04\x07\x05\x04\x04\x00\x01\x02w\x00\x01\x02\x03\x11\x04\x05!1\x06\x12AQ\x07aq\x13"2\x81\x08\x14B\x91\xa1\xb1\xc1\t#3R\xf0\x15br\xd1\n\x16$4\xe1%\xf1\x17\x18\x19\x1a&\'()*56789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00?\x00e(\xaf\x1c\xb0\xa5\xa0\x02\x8a\x00Z1@\x06*\x1b\x8b8.\x93l\xa82:8\x1c\x8a\xa8\xc9\xc5\xdd\t\x98w\xba|\xb6m\x93\xf3\xc4y\x0e==\xea\xa5z1\x92\x92\xba$)*\x80)h\x01(\xc5\x00-%\x00\x7f\xff\xd0\xe4E\x15\x00-\x14\x00\x84Sh\x00\xa2\x98\tOW#\x83\xc8\xa2\xd7\x01\xdb\x81\xef\xf8S\t\xc9\xa4\x90\tE0\n(\x00\xa2\x80\n\x96\x0b\x89m\xdft.T\xf7\x19\xe0\xd2j\xfa\x01\xff\xd1\xad\xa7k\ts\x84\x98\x85\x93\xdf\x8c\xd6\x9e{\x8e\x95\xc38\xf2\xb1\x05\x15\x00-\x14\x00QL\x02\x8a`\x14P\x00Fj\xb5\xc5\xaa\xc8:\n@a\xddZ\x18\xdb\x81\xc1\xf4\xaaD\x159\x07\x07\xda\xbab\xee\x80\xbbivA\x01\xcf\xe7Z\x91\xbf\x1cv\xaez\x91\xb3\x1989\x14t\xa1\x12\xcf\xff\xd2\x90\x1a\x92\xb8I\x1c\xb4\xa6\x90\r\xa5\x14\x00Q@\tE0\n\x01\xa0\x05\xa0\x9a@%(\xa0\x05\xcd <\xd0\x00i\x01\xc5\x00\x7f\xff\xd3m\x02\xbcr\xc5\xa2\x80\x16\x97\x14\x00b\x8cP\x02\xe2\x8cP\x01\xd8\x82\x01\x07\xa8=\re\xdeh\xca\xc1\x9e\xcf!\x87>Y\xe8}\x85kJ\xa7#\x131\x99J6\xd7R\xad\xe8F)\xb5\xdeHQL\x02\x8a\x00(\xa0\x0f\xff\xd4\xe4\xa8\xa8\x00\xa2\x90\x054\xd3@%\x14\xc0J)\x80\xb4R\x01)h\x00\xa2\x80\n(\x00\xa2\x80?\xff\xd5\xe3\xfb\xe4u\x15\xb1\xa6\xeb-\x19\x11\\\x9c\xaff\xac\xa7\x1ed#\xa0\x8eE\x957FA\x1e\xd4\xfa\xe4\x00\xa2\x80\n(\x00\xa2\x80\nZ\x00)(\x02\xbd\xc5\xba\xc8\xa7\x8a\xc3\xbb\xb41\x92W\xa5\\%g`(\x90T\xf1W\xad.\xcfF=\xebY\xc7*1D\r\n',
        b'$$e299,864507032323403,AAA,37,-33.815818,151.200091,180503063444,A,11,11,0,0,0.9,66,9995,755819,505|3|00FA|***REMOVED***?+  3100            1            58003163  00101?,,108,0000,,3,0,,0|0000|0000|0000|0000|0000*29\r\n',
        # b"""@@b1440,013777002436846,FC1,\x00\x00\xfd\x00\x05\x80\xeb\xe0\xe4\xf4\xfb\xb7\xc7\xf9\xff\xfe\xe8\xb9\xa3\xa2\xa1\x90\x88\x83\x80\x81\x9d\x82\x84\xa5\x96\x8e\x88\xa9\x90\x8a\x8c\xad\x92\xb6\xb0\x91J\xb3\xb4\x95\xe8\xb8\xb8\x99I\xbb\xbc\x9d\x07\xa7\xa0\x81\x02\xa3\xa4\x85\xa7\xa1\x88\x94\x93\x92\x8c\xfe\xab\xa0\xa4\xb4\xbb\xf7\x91\xad\xb3\xaf\xf8\x8a\xb2\xba\xb9\xad\xe2\xc3\xc0\xc1\x8f\xc4\xc4\xe5\x80\xc8\xc8\xe9\xa6\xfa\xcc\xed\x12\xf0\xf0\xd1\xc6\xe1\xf4\xd5\x18\xf8\xf8\xd9\xbe\xfb\xfc\xdd\xa0\xe7\xe0\xc1j\xe3\xe4\xc5z\xef\xe8\xc9\x86\xec\xec\xcd\x06\x13\x101\x9a\x14\x145\x8a\x18\x189^\x1f\x18\x1d\x18\x03\x00!\x02w\x05\r\x07\x01()321D\\ZD\x11fVFT\x1ahYO[\x1fsv\x1f\x1e\x1d!w"$\x05\'!\x08\x14\x13\x12\x0c~+ $4;w\x1b\x13\x1c{edcRV]BSA\x01#CDe\x07HHi\x00LLm}spQ[ZECNJIKOIMION`akmD#\x06\n\x1b\x01CW!/\x9f\x99\x90\x91\x8d\x97\x94\xb5\x8e\xdb\x98\xb9\x93\x95\xbc\xdb\xee\xe2\xf3\xe9\xa6\xc2\xf6\xf7\xe5\xf9\x85\x83\x8e\x8f\x8c\x8d\x82\xb5\xb0\x91\xbe\xb7\xc8\xb5\xe7\xd4\xb9\xb1\x1f\xba\xbc\x9d\xaf\xa9\x80\x8c\x8b\x8a\x89\x88\x87\x86\x85\x84\x83\x82\x81\x80\xff\xfe\xfd\xfc\xfb\xfa\xf9\xf8\xf7\xf6\xf5\xf4\xf3\xf2\xf1\xdd\xcf\xc9\xe0\xeb\xec\xed\xee\xef\xe0\xe1\xe2\x86\x9a\x8e\xec\xb8\x82\x97\x91\x85\x97\xd7\xbb\xbe\xd0\xd1\xd2\xd3\xd4\xd5\xd6\xfd\xef\xe9\xc0\xcc\xcb\xca\xc9\xc8\xc7\xc6\xc5\xc4\xc3\xc2\xc1\xc0?>=<;:987654321\x10\x08\x03\x00\x01e\x02\x04%\x02{AA\x0b\x7f\xac\xf53s\rA#\xd7<\x17|r\x7fq\xc8\xc8\xc3\xc7Z\x92f\x81\xd6\xd0\x95\xd9g\x8b\xd8\xde\x80\xd3y\x8d\xa2\xa4\xfb\xad\xde\xafT\x15d\x11Px\x06\x19\xab\xaa\xca\xbd\xbd\xb6\xe7\xbaEgTjX\x0f\xb8\xb8\xde\xb4pQnPwW\x89\x82I\x84\xf2\x81~/\x8f\x8a\xb8\x9e\x9f\x96\xc5\x9d\x9b\x92\x94\x92\x96\x9e\xf8\x94\x93\x9auj\xa8\xe9\x97\xbf\x96D\x9bk\x8ca\xa2\xefbj\xa4x\xc9\xcc\x13\x7fw\x87\x83\xa3\x89Z\x0bw\x7f\xcf\xf4\x13@F\xccK!MI\xb9\xf1\xf0\xefG\x9c\xbdRT\xd3]\xe1\x07TR\xdaW=Qy\xad\\ZA/\x7f#\xa6\xf7$"\xb2\'m!D\xdd\xccd\xc0\xe3e9\\\xc5\x80\x8b\x8e\x84\xc8\xed\x987\xe8\xdd\xb3B\xf7\x1a\xf2\xe7\xd4\xc5\x0c\x0c\x8f\x03\x9a\xe3\x18O\xd0\xcf\x132s\x1f+\xe7\xd7\xa2\xe0\x99{\x17"\xef.Z\x18a\xc9\xf2\x04\xa0!R$S\x1e?_A\x11W@\x1d\xc6\xb5\x14-\xf3\xd8\x18+6F;E\xc4\xc4\xb5\xcb6\x1f>\xe4\x0c\x9b\xc8\xce\x08\xc3\x07u\xe3K\x01\xd5&F\xe5E\x13b+\t&_<\x90\xd9VPqfQTu?4YQSU|ponmlkjihgfedcba`_^]\\[ZYXWVUT~\x7f|}oi@KLMNO@A\'=/O\x19\x1d\xf6\xf2\xe4\xf0\xb6\xf2\xe6\xe7\xf5\xe9\xb2\xb3\xb4\xb5\xb6\xb7\x82\x83\x80\x81\x8b\x8d\xa4\xa8\xa7\xa6\xa5\xa4\xa3\xa2\xa1\xa0\x9f\x9e\x9d\x9c\x9b\x9a\x99\x98\x97\x96\x95\x94\x93\x92\x91\x90\x8f\x8e\x8d\x8c\xab\xad\xa4\xa5\xc2\x9e\xa8\x89\xa3\xa5\x8c\x90\xef\xee\xf0\x96\x85\x9a\xf4\x97\x9b\x95\x9c\xf9\xe4\xff\xdc\xdd\xe6\xc6\xc0\xe1\xe6\xe7\xf9\xf8\xea\x8c\x98\x9a\xee\x8b\x89\x8c\xbe\xd3\xca\xd1\xf6\xf7\xf4\xf5\xfa\xf9\xf8\xd9N\xc3\xfc\xdd\xfc\xe7\xe0\xc1\xc7\xe3\xe4\xc5\xca\x15\xe9\xe9\xde\xf9\xec\xcd\xa93\x101\x1b\x1d4Fchl|s?Yoplr^OJAL*\x06\x02\t\x0e\x1f\rM=30\x114q"~:\x1b\xf9e/k\x0c\x04\xeb\x91)\x08%\xffd9\xea\x998\x01\xdb\xfc\\j]\x1at`_?^[X+SU\x1d/WW\xc13\x811Lg\xf4\xaeXTI\x99No<\nsS\x006p>VDs\xf3rs|\x0f=\rhC\xd0\x8atxe\xb5jK\x18.oO\x1c*\xfd\x12\xee\xee\xc4\x01\x1b\xabi\xac\xe7\x9e\xe0\xc8\xbb3v\xb0\x9f\x86\xf9\xd0\xaf*\xf4\xd3\xf7\xd3x\xbe\xf2\xda\xe3\x1c\xcd\xe6\x84\x19k\xb2\xc5\xec\x8d\x16d\xb0\xa3\xb8\xdd\xf4\x99\x0f\x96,\xcd\xaauU\xfd\xf6(\'\xf4)\x87\x8cZYCT\x1dR=\xa6\xb7\x17\x8b\x80]U\xacA\xd8\xce\xdc\xc9\x1e\xcbP\xc4\x12\xc4\xcb\xf9\x99\x92\x85\xfc\xf5\xc6\x8c\xf8\xf1\xc3\xc4v\xf7\xf6\x89\x00\x15z\x01\x9e\xe7\xd7\x91\xe8\xe3:(|g\xd7ag\xde)\xcd\xe5oFt\xb9BJ\x9c\x93f\x9dH@\x96\x95\xb9\x80\xc9\x86\xe1zk\xcb\\T\x89\x81\x9a\x8ckP?\x05<\x06K\xb8\x03\xb44\x0c\x02\xc60\xe0@\xb2\xb0\xa0]~9(>+\xf0%\xb2&\xf6"&\xf2\xf7\xcb\x92\xc6\xd9\xa9ubd\\&\x0f#\xf1l\xd6+M\xbe\xbfI\x7fas%\x81\x7fNCz@y~@\x0e&\x15\xd8\t"\x1c\xd5\x0f\x7f\x0b(\'\xd0\xd5d\xe06\x12\xca\x0b\x92i<\x12\xc4\t\x98o:\xef>\xcff\x95\xc0\xe99-\x9c\xa7\xfa)\x90+\x9a\xfe\xd4\xfb-\xf1\x80\xfb\xd2\xf4%\xf6\xd6y\x80\xe3O\xddD\xb3\xe6\xcc\x10\r\n+IPD,95:\xd3B\xb9\xec\xc5\x1e\xe1H\xbf\xea(\x05\x90*\xcf\xa8S[\xc5i\xd7\xf6\xd9\xa1\x1b\xa2\xbd\x11\x90\xe7\xe1\xd0\xaa\x82\xa1t\xa5\x8e\xa0q\xa2\x825\xcc\xcf\xf9\xf6L\xad\xca=5\xc7\xf1\x9cYC\xf3\xcf\xc2\xbf\xf6\x89\xa0\'Z\xb0\xc9o\xff\x81\xa8+S\x9b\xbcw\xef\xf1\xe0\xd4j\x95\x9c\x96\xbe\xd6@\x91\xba*E8\r\n""",
        b"""@@U1440,013777002436846,FC1,\x00\x00\xf7\x80\x05\x80\xe2\xe8\xea\xe2\x93\xa8\xab\xaa\xe8\xf0\x9e\x96\xac\xaa\xa3\xa2\xb0\xb6\x9f\xed\xc0\xcb\xcf\xdf\xd8\x94\xf2\xc4\xc3\xdf\xc1\xed\xde\xc2\xaf\x83\x83\x88\x8b\x8a\x88\x8e\xa7\xd5\xcf\xba\x83\x82\x90\x96\xbf\xce\xd6\xcf\xde\xc8\xb5\xdb\xd1\xd0\xb1\xaa\xb3\xc7\x83\x8d\x9a\x9a\x81\x87\x99\x83\x9f\x81\x83\xeb\xeb\xe0\xe3\xe2\xfd\xec\xfe\xbe\xf6\xf8\xfb\xda\xf8\xfe\xd7\xb4\xbe\xbf\xa7\xd2\x9b\x89\x9d\xf4\x9f\xc8\xcb\xca\xeb\xc4\xc7\xc6\xcc\xca\xe3\x80\x92\x93\x8b\xfe\x8f\x9d\x89\xe0\xd8\xde\xd7\xd6\xdc\xda\xf3\x81z\x0cyk{\x12+*1d\'\x06,*\x03jj\x1ci{k\x02s:8>\x17`TB@[bb5\x0e\x12\x08\x0b*\x15\x01\x07&\x0c\n#JJ<I[K"\x16\x10\x15\x14\x17\x16\xcc\x13\x132PhoN\x01kkJhnG1\x13\t\x17\x07](\x10^?\x14\x1a\t\x1dNW:\x10\x04\x1a\x068(*c\x05\'%-,02"$m\x17+09\x7fsgx[Z\xe5hWvXKWR]\x93\xaf\x8e\xf9\xbf\xaf\xaa\xa2\xa1\xa7\x86\xc9\x95\xa3\x82\xb6\xbc\xbf\x9e\xb1\xbd\xbb\x9a\xa5\xb4\xb7\x96I\xb4\xb3\x92\x16t\x8f\x8e\x89\xa0\xd0Z{\xcdz\xce\x89\xe0}e\xac\xe4@fm+\x9a\xb3\x93Ek\xdf\x9b\xe8\x90\xb8\xeb<\x14\xa4\xfb\x90\xf1[\xd5\x9c\xe5\xce\xe60\xfd\x02v\x04\xff\xfe\xd5\x88\xf7\x8a\xf7\xd4\xc7\x86\xe6\x10\xdb\x8ae}\xfb\xbe:h;=];\xef\xbe17\x7f=%|/)K\'\xc0\xfa,#\x9e)\xca\xf0%%\xe7\x13@\x10\xef\xae\x18\xa4\xe7bk\x18\xe7\xa6~\x1c\xfb\xfa\xa0\xbe\xff\xd6\x9d,\x02\xba\xf1\x88\xf1\xde\xa9%;\x82\xc9\xb0\xc9\xe6\x95\x1d,\x8a\xc1\xb8\xc7\xee\x91\x155\x92\xd9\xa0\xdf\xf6\x8d\r>\x9a\xd1\xa8\xd7\xfe\x99\x05\xa9\x8a\x91\xd8\xa3\xde\x81\xdcI\xea\xa5\xd0\x93\xd6\x1d\\-\xa8\x10@\xbf\xae7D\xb3\xf2V\x10GA\xe8K\xb0j\xa0\xf0\x06=S\xc5\x8a\xfa\x87\xa9\xb2VX\xcd\x92\xe2\x9f\xb1\xaeN\xa9\xecu\xdb\x9d\xe0q\xdf\x99\xe4\x8d#e\xe8\x89\'a\xec\x85+m\x10\x81,$\x96\x0b\x0bh\xf8\xe7\x86\xe1n\x978`\x00\x93?}\x04\xaf\x03A8w>\xa9\xec\xb3\xb5v\xbfo>\xb5\xb3\x00\xa5\x91\xf8\xaf\xa9l\xa3\xfa\xaaQ\x10\xcd\xaeUT\x0b\x9b\xef`%\x0f,\xac%\xc2\'\xc0<\x06\xdc\xd3\xe5\xc4"\x18\xc9\xc9\x9c\xc4\x1fB\xefx6N5\x1dv\xdb\x0c)\x0e~\xd1D\x02z\x01)p\xd6\x01tT\xee\x9b=7X\xe5\xeb\xda\xea\xc9ZX\xe2\xfcu\xc3\xac\x11\x1f\xdd\x16\xef\xce6\xab7\xa8\x11\x11\xd6\x19/\xb7\xfb\xda+\xb7U\xe0\x05\x05\xdc\r\xf5\xd4&\xbd\xe3\xd7??\xe73\xcf\xee\x12\x8bi\xdd11\xe69\xdf\xf8\t\x91\xda/\xd5\xdc%%\xcc-\xd3\xf4\x1b\x9d\xae[\xa5\xa8YY\xbaQo\xea\xa0\xc8\xa4\x8f\xa0}p\xf3\xb3\xd0\xbc\xd6\xa7\xf8\xb9\xd2\xb5\xd0v\xfe\xb1\x96C\xc3\x99\xb8yy\x8aq=\xca\x85\xa2A\xcf\x91\xb4mm\x98e$\xd6\x99\xbeR\xdb\x89\xa0aanh\xd3 )I\xae&\x95\x9b\xcf\x9a\xa0-O\x1eeL"\xaa\xb91\xcc6\x8b\x8b\xa6\x8eQQ\xc6<=w\xb3\xbd\xd6\xb0c>\xf0\xa4\xb3\x1d\xfa\xe0C\xb6+\xfcg*qx\xa6\xa96\xa2{r\xa7\xa7y\xae\xed\xac\xb3(\t\x99\x07\x0e\xd2\xdbv\xda\x9bh#V\xdc\xd3\xe0\xc4\xc3\xcf\xd4\xc3r\xc8\xb1\x17\x19v7\xd6\x07\xd4\xf3\xfd]\xf0\x92DB\xf8\xeac)F\xf0\xf1\xb8\xfb\xe4\xedM\xe5\x01<\x17=\x112\xe7\xe7\x94\xed\xbb\xb4\x1b\x1db\x16d\x16\xed\xacR\xab)\x88\xc7\x12\xe5\x843\x9aI\xb0u\x96/\xf8\x0f\'\xf5\x80}\x9e\'\xf0\xc9\x1f\xcb\xb0\xce\xe45\x1dh\x8b\xcd\xb0l\x8c\r\xe7\xc8\xaa\xd3\xa0\xcdg\xdf\xa4\xd2\xf8+\x01\xdb\xa6\x8c\x9d\xfc\xe2\xa1\xc8QI\x10DS=\x8cIW\xf9\xa6\x80dB5\x1a<\xf0\x1c\xfa1\xfaIG\tN\x9d\r\xbb\xf2f\xa0\x8d_\xfd\xf4\x95\xaa\x85P\xe3\x98\x91td\x9ehI\x87~!-\t2ag\xd9h\x084\x9b\x9d"\x96\xf0#\xcd cBH<F2%x\xbb\xc8YP\x86\xad\x0e4s\x82\xe3\x8a\x9f\xc5uU#\x16\x16`]\x9e^\xac\xdb\xe2\xb1\xb7q\xb8\xcd\x0c\x9a2x\xac_?\x9c<\xd9\xaaQ\xc0\xa8\xa14\xa9\xcb\xcdAty\x06*\xfcj>\xe8\x92\x07\x0f\xdd\xf7r&\xf0\x8a\x1f\x17\xde\xef{\x12Yd\x7f*FL\xcb\xb89*\r\xe5\x1e\x1f(VA\x1ct~\xc5\xb6\x18\xea\x16\x1b/-6HS\x0e\xe2h\xd7\xa4\x0e\x1d\xee:\x1a\x90\xed\x05\xfe\xfe\xc9\xb6\xa1\xfc\'T\x17\x9c\xf9\n\xf6\xfa\xcf\xcc\xd7\xa8\xf7\x12\xf6\x10\x95\xaa\xbc\xe8\xe1\x9e\x00z\x8f\xd2\r~\xe3\xea6\x13\x18>1u\xa0\x90\xd1\xf9\x87\x98*+\xa1-\xd9\xf2\xaf\x9f\xaf\x9c]]\x9cTpVu-\xa2\x87\xd9\xef\xa7\x82\xa5\x8c\x9fj\xce\x18OI\\A\xce\x12AGiK1\x14{}Ru\x07v\x8d\xcc\xc1\xc4\x89\xa1\xdf\xc0rs#e\xab\xb8\xaf\xee\xb1\xbc\xe3\xe2\xf3\xd9\'\x8acc\x8a\x91\xe9t\xad\xdcZ%#\x94\xa2\x10g\x96\xd0\x9f\xfb3\xf8\x80\x7f\xeez\\f;\x8c\x90t\x97utJJ\xb3MC\xa3M\xac\xb5FA`NFEdQZYxRT}anoq\x03.%!1F\nlPFZ\riUGOT\x07eJ@^\x00\x198\x1f\x03\x00\x01>810=35\x14\xcc\t\t(R\r\r,\x11\x06\x01 J\x02\x05$\x7f\x1f\x198\xb5\x1a\x1d<\x1e\x181-*+5G*10\r\n""",

    ]

    for gprs_item in test_data:
        direction = DIRECTION_CLIENT_TO_SERVER
        if gprs_item[0:2] == SERVER_TO_CLIENT_PREFIX:
            direction = DIRECTION_SERVER_TO_CLIENT
        test_gprs_list, before_bytes, extra_bytes = parse_data_payload(gprs_item, direction)
        for gprs in test_gprs_list:
            print(gprs)
            print("============================================================================================")
            print(gprs.as_bytes())
        if before_bytes:
            print("Before bytes is ", before_bytes)
        if extra_bytes:
            print("Leftover is ", extra_bytes)
        if b"AAA" in gprs_item:
            print(gprs.enclosed_data["longitude"])
            print(gprs.enclosed_data.longitude)

        print(hex(calc_signature(gprs_item)))
