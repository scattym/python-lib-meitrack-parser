#!/usr/bin/env python
"""
Library for converting requests to responses in bots and tests.
"""
import binascii
import logging

from meitrack.build_message import cts_build_file_list
from meitrack.gprs_protocol import GPRS


logger = logging.getLogger(__name__)
SPURIOUS_REPORT = b'$$D160,864507032228727,AAA,35,24.819116,121.026091,180323023615,A,7,16,0,176,1.3,83,7,1174,466|' \
                  b'97|527B|01035DB4,0000,0001|0000|0000|019A|0981,00000001,,3,,,36,23*DC\r\n',
REQUEST_TO_RESPONSE = {
    b'A11,': b'$$S28,353358017784062,A11,OK*FE\r\n',
    b'A10,': b'$$Q164,864507032228727,AAA,35,24.818910,121.025936,180329052345,A,7,13,0,16,1.2,69,2720,86125,466|97|'
             b'527B|01035DB4,0000,0001|0000|0000|019E|097F,00000001,,3,,,124,96*F2\r\n',
    b'A12,': b'$$V28,353358017784062,A12,OK*02\r\n',
    b'A13,': b'$$X28,353358017784062,A13,OK*05\r\n',
    b'A14,': b'$$D28,353358017784062,A14,OK*F2\r\n',
    b'A15,6': b'$$E28,353358017784062,A15,OK*F4\r\n',
    b'A16,0': b'$$F28,353358017784062,A16,OK*F6\r\n',
    b'A17,1': b'$$T28,353358017784062,A17,OK*05\r\n',
    b'A19,1': b'$$H28,353358017784062,A19,OK*F8\r\n',
    b'A21,1,67.203.13.26,8800,,,': b'$$H28,353358017784062,A21,OK*F4\r\n',
    b'A22,75.127.67.90': b'$$K28,353358017784062,A22,OK*F8\r\n',
    b'A23,67.203.13.26,8800': b'$$S28,353358017784062,A23,OK*01\r\n',
    b'A70': b'$$T85,353358017784062,A70,13811111111,13822222222,13833333333,13844444444,13855555555*21\r\n',
    b'A71,13811111111,13822222222,13833333333': b'$$U28,353358017784062,A71,OK*06\r\n',
    b'A72,13844444444,13855555555': b'$$V28,353358017784062,A72,OK*08\r\n',
    b'A73,2': b'$$W28,353358017784062,A73,OK*0A\r\n',
    b'AFF,1': b'$$h28,353358017784062,AFF,OK*3D\r\n',
    b'B05,1,22.913191,114.079882,1000,0,1': b'$$H28,353358017784062,B05,OK*F7\r\n',
    b'B06,1': b'$$J28,353358017784062,B06,OK*FA\r\n',
    b'B07,60': b'$$P28,353358017784062,B07,OK*01\r\n',
    b'B08,3': b'$$I28,353358017784062,B08,OK*FB\r\n',
    b'B21,1': b'$$C28,353358017784062,B21,OK*F0\r\n',
    b'B31,10': b'$$J28,353358017784062,B31,OK*F8\r\n',
    b'B34,60': b'$$N28,353358017784062,B34,OK*FF\r\n',
    b'B35,480': b'$$O28,353358017784062,B35,OK*01\r\n',
    b'B36': b'$$P28,353358017784062,B36,OK*03\r\n',
    b'B46': b'$$P28,353358017784062,B46,OK*03\r\n',
    b'B60,1': b'$$U28,353358017784062,B60,OK*05\r\n',
    b'B91,1,SOS': b'$$R28,353358017784062,B91,OK*06\r\n',
    b'B92,1234567890ABCDEF': b'$$q28,353358017784062,B92,OK*26\r\n',
    b'B93': b'$$V42,353358017784062,B93,00000007E01C001F*B5\r\n',
    b'B96,0000000000000001': b'$$A28,353358017784062,B96,OK*FA\r\n',
    b'B97': b'$$C42,353358017784062,B97,0000000000000001*60\r\n',
    b'B99,gprs,get': b'$$B33,863070010825791,B99,1,17,18*B5\r\n',
    b'C01,20,10122': b'$$M28,353358017784062,C01,OK*F9\r\n',
    b'C02,0,15360853789,Meitrac': b'$$f28,353358017784062,C02,OK*13\r\n',
    b'C03,0': b'$$f28,353358017784062,C03,OK*14\r\n',
    b'C13,0,E,TestMessage': b'$$m28,013777001338688,C13,OK*1C\r\n',
    b'C41,01': b'$$n30,012896001078259,C41,01,1*37\r\n',
    b'C47,2,90,10': b'$$f28,353358017784062,C47,OK*1C\r\n',
    b'C48': b'$$c33,353358017784062,C48,2,90,10*D0\r\n',
    b'C49,3,2': b'$$c28,353358017784062,C49,ok*5B\r\n',
    b'C50': b'$$P28,353358017784062,C50,OK*03\r\n',
    b'C52': b'$$P28,353358017784062,C52,OK*03\r\n',
    b'C91': b'$$P28,353358017784062,C91,OK*03\r\n',
    b'D01,0': b'$$A480,353358017784062,D01,3,0,0506162517_C1E03.jpg|0506162517_C1E11.jpg|0506162624_C1E03.jpg|0506162'
              b'630_C1E11.jpg|0506162720_C1E03.jpg|0506162721_C1E03.jpg|0215080547_C1E03.jpg|0215080547_C1E11.jpg|021'
              b'5080626_C1E03.jpg|0215080626_C1E11.jpg|0215080827_C1E03.jpg|0215080827_C1E11.jpg|0215080850_C1E03.jpg'
              b'|0215080850_C1E11.jpg|0507145426_C1E03.jpg|0507145426_C1E11.jpg|0507145512_C2E03.jpg|0507145512_C2E11'
              b'.jpg|0215080050_C3E03.jpg|0215080050_C3E11.jpg|0215080459_C3E03.jpg|021508050*41\r\n',
    b'D02,': b'$$F28,35335801778'
                                                                                                 b'4062,D02,OK*F4\r\n',
    b'D03,1,camerapicture.jpg': b'$$D28,353358017784062,D03,OK*F3\r\n',
    b'D10,13737431,13737461': b'$$f28,353358017784062,D10,OK*13\r\n',
    b'D11,13737431,1': b'$$e28,353358017784062,D11,OK*13\r\n',
    b'D12,13737431': b'$$C27,353358017784062,D12,0*87\r\n',
    b'D14,13723455': b'$$Q28,353358017784062,D14,OK*02\r\n',
    b'D15,13723455,3': b'$$K28,353358017784062,D15,OK*FD\r\n',
    b'D16': b'$$u28,353358017784062,D16,18*F7\r\n',
    b'D65,30000,50000,60000,70000,80000,90000,100000,110000': b'$$V28,353358017784062,D65,OK*OD\r\n',
    b'D66,8726,8816,8906,8996,9086,9176,9266,9356': b'$$V28,353358017784062,D66OK*E2\r\n',
    b'E91': b'$$X57,864507032323403,E91,T333_Y10H1412V046_T,46281520253*86\r\n',
    b'F01': b'$$j28,353358017784062,F01,OK*19\r\n',
    b'F02': b'$$Z28,353358017784062,F02,OK*0A\r\n',
    b'F08,0,4825000': b'$$D28,353358017784062,F08,OK*FA\r\n',
    b'F09,1': b'$$E28,353358017784062,F09,OK*FC\r\n',
    b'FC5': b'$$B28,864507032323403,FC5,\x00\x27*89\r\n',
    b'FC6': b'$$[27,353358017784062,FC6,1*0B\r\n',
    b'FC7': b'$$[28,353358017784062,FC7,OK*0B\r\n',
    # b'FC7': b'$$A40,864507032323403,FC7,OTA,\x00',,\x00\x00\x00\x00\x05\x80*71\r\n',
    b'FC0': b'$$K55,864507032323403,FC0,\x00A,OK,1408,T333_Y10H1412V046,*AA\r\n',  # T333_Y10H1412V046_T
    b'FC1': b'$$[28,353358017784062,FC1,OK*0B\r\n',
    b'FC2': b'$$[46,353358017784062,FC2,000000FF000000EEABAB*0B\r\n',
    b'FC3': b'$$[27,353358017784062,FC3,1*0B\r\n',
    b'FC4': b'$$[28,353358017784062,FC4,OK*0B\r\n',
}

file_listing = [
    b'$$p1054,864507032323403,D01,8,0,180520032140_C1E1_N4U1D1.jpg|180520041216_C1E35_N1U1D1.jpg|180520004140_C1E1_N4'
    b'U1D1.jpg|180519204241_C1E1_N5U1D1.jpg|180519210839_C1E35_N1U1D1.jpg|180519211937_C1E1_N2U1D1.jpg|180519212140_C'
    b'1E1_N4U1D1.jpg|180519212242_C1E1_N5U1D1.jpg|180519215836_C1E1_N1U1D1.jpg|180519215937_C1E1_N2U1D1.jpg|180519220'
    b'140_C1E1_N4U1D1.jpg|180519220241_C1E1_N5U1D1.jpg|180519223836_C1E1_N1U1D1.jpg|180519231836_C1E1_N1U1D1.jpg|1805'
    b'19224140_C1E1_N4U1D1.jpg|180518223837_C1E1_N1U1D1.jpg|180518231837_C1E1_N1U1D1.jpg|180518224141_C1E1_N4U1D1.jpg'
    b'|180518224242_C1E1_N5U1D1.jpg|180518231938_C1E1_N2U1D1.jpg|180518235837_C1E1_N1U1D1.jpg|180518232242_C1E1_N5U1D'
    b'1.jpg|180519000039_C1E1_N3U1D1.jpg|180519000141_C1E1_N4U1D1.jpg|180519000242_C1E1_N5U1D1.jpg|180519004242_C1E1_'
    b'N5U1D1.jpg|180519004141_C1E1_N4U1D1.jpg|180519010837_C1E3_N1U1D1.jpg|180519012039_C1E1_N3U1D1.jpg|180519012141_'
    b'C1E1_N4U1D1.jpg|180519015837_C1E1_N1U1D1.jpg|180519023938_C1E1_N2U1D1.jpg|180519015939_C1E35_N1U1D1.jpg|1805190'
    b'20141_C1E1_N4U1D1.jpg|180519020242_C1E1_N5U1D1.jpg|180519*B0\r\n',
    b'$$q1054,864507032323403,D01,8,1,024141_C1E1_N4U1D1.jpg|180519024242_C1E1_N5U1D1.jpg|180519030837_C1E3_N1U1D1.jp'
    b'g|180519031837_C1E1_N1U1D1.jpg|180519031938_C1E1_N2U1D1.jpg|180519032039_C1E1_N3U1D1.jpg|180519032242_C1E1_N5U1'
    b'D1.jpg|180519043837_C1E1_N1U1D1.jpg|180519035837_C1E1_N1U1D1.jpg|180519035938_C1E1_N2U1D1.jpg|180519040039_C1E1'
    b'_N3U1D1.jpg|180519040040_C1E35_N1U1D1.jpg|180519040141_C1E1_N4U1D1.jpg|180519040242_C1E1_N5U1D1.jpg|18051904393'
    b'8_C1E1_N2U1D1.jpg|180519044039_C1E1_N3U1D1.jpg|180519044141_C1E1_N4U1D1.jpg|180519052242_C1E1_N5U1D1.jpg|180519'
    b'050837_C1E3_N1U1D1.jpg|180519051837_C1E1_N1U1D1.jpg|180519051938_C1E1_N2U1D1.jpg|180519052039_C1E1_N3U1D1.jpg|1'
    b'80519060140_C1E1_N4U1D1.jpg|180519055837_C1E1_N1U1D1.jpg|180519055937_C1E1_N2U1D1.jpg|180519060039_C1E1_N3U1D1.'
    b'jpg|180519060141_C1E35_N1U1D1.jpg|180519060242_C1E1_N5U1D1.jpg|180519064140_C1E1_N4U1D1.jpg|180519063837_C1E1_N'
    b'1U1D1.jpg|180519063937_C1E1_N2U1D1.jpg|180519064039_C1E1_N3U1D1.jpg|180519064242_C1E1_N5U1D1.jpg|180519071938_C'
    b'1E1_N2U1D1.jpg|180519071837_C1E1_N1U1D1.jpg|180519072040_*54\r\n',
    b'$$A1054,864507032323403,D01,8,2,C1E1_N3U1D1.jpg|180519072243_C1E1_N5U1D1.jpg|180519080249_C1E1_N5U1D1.jpg|18051'
    b'9100141_C1E1_N4U1D1.jpg|180519103837_C1E1_N1U1D1.jpg|180519104040_C1E1_N3U1D1.jpg|180519104242_C1E1_N5U1D1.jpg|'
    b'180519110409_C1E35_N1U1D1.jpg|180519111938_C1E1_N2U1D1.jpg|180519111837_C1E1_N1U1D1.jpg|180519112039_C1E1_N3U1D'
    b'1.jpg|180519112242_C1E1_N5U1D1.jpg|180519124141_C1E1_N4U1D1.jpg|180519224241_C1E1_N5U1D1.jpg|180519230954_C1E35'
    b'_N1U1D1.jpg|180519231937_C1E1_N2U1D1.jpg|180519232038_C1E1_N3U1D1.jpg|180519232241_C1E1_N5U1D1.jpg|180519235836'
    b'_C1E1_N1U1D1.jpg|180520000038_C1E1_N3U1D1.jpg|180520000140_C1E1_N4U1D1.jpg|180520000241_C1E1_N5U1D1.jpg|1805200'
    b'04038_C1E1_N3U1D1.jpg|180520011050_C1E35_N1U1D1.jpg|180520011836_C1E1_N1U1D1.jpg|180520011937_C1E1_N2U1D1.jpg|1'
    b'80520012038_C1E1_N3U1D1.jpg|180520012241_C1E1_N5U1D1.jpg|180520015836_C1E1_N1U1D1.jpg|180520015937_C1E1_N2U1D1.'
    b'jpg|180520020038_C1E1_N3U1D1.jpg|180520020140_C1E1_N4U1D1.jpg|180520020241_C1E1_N5U1D1.jpg|180520024038_C1E1_N3'
    b'U1D1.jpg|180520023836_C1E1_N1U1D1.jpg|180520023937_C1E1_N*66\r\n',
    b'$$B1054,864507032323403,D01,8,3,2U1D1.jpg|180520024140_C1E1_N4U1D1.jpg|180520024241_C1E1_N5U1D1.jpg|18052003183'
    b'6_C1E1_N1U1D1.jpg|180520031937_C1E1_N2U1D1.jpg|180520032038_C1E1_N3U1D1.jpg|180520032241_C1E1_N5U1D1.jpg|180520'
    b'035836_C1E1_N1U1D1.jpg|180520035938_C1E1_N2U1D1.jpg|180520040039_C1E1_N3U1D1.jpg|180520040141_C1E1_N4U1D1.jpg|1'
    b'80520040242_C1E1_N5U1D1.jpg|180520043836_C1E1_N1U1D1.jpg|180520043938_C1E1_N2U1D1.jpg|180520044039_C1E1_N3U1D1.'
    b'jpg|180520044141_C1E1_N4U1D1.jpg|180520044242_C1E1_N5U1D1.jpg|180513184246_C1E1_N5U1D1.jpg|180513191841_C1E1_N1'
    b'U1D1.jpg|180513191942_C1E1_N2U1D1.jpg|180513192043_C1E1_N3U1D1.jpg|180513192145_C1E1_N4U1D1.jpg|180513192246_C1'
    b'E1_N5U1D1.jpg|180513193259_C1E35_N1U1D1.jpg|180513195841_C1E1_N1U1D1.jpg|180513195942_C1E1_N2U1D1.jpg|180513200'
    b'043_C1E1_N3U1D1.jpg|180513200145_C1E1_N4U1D1.jpg|180513200246_C1E1_N5U1D1.jpg|180513203328_C1E35_N1U1D1.jpg|180'
    b'513203841_C1E1_N1U1D1.jpg|180513203942_C1E1_N2U1D1.jpg|180513204043_C1E1_N3U1D1.jpg|180513204144_C1E1_N4U1D1.jp'
    b'g|180513204246_C1E1_N5U1D1.jpg|180513211841_C1E1_N1U1D1.j*5D\r\n',
    b'$$C1054,864507032323403,D01,8,4,pg|180513211942_C1E1_N2U1D1.jpg|180513212043_C1E1_N3U1D1.jpg|180513212144_C1E1_'
    b'N4U1D1.jpg|180513212246_C1E1_N5U1D1.jpg|180513213356_C1E35_N1U1D1.jpg|180513215841_C1E1_N1U1D1.jpg|180513215941'
    b'_C1E1_N2U1D1.jpg|180513220043_C1E1_N3U1D1.jpg|180513220144_C1E1_N4U1D1.jpg|180513220246_C1E1_N5U1D1.jpg|1805132'
    b'23425_C1E35_N1U1D1.jpg|180513223841_C1E1_N1U1D1.jpg|180513223941_C1E1_N2U1D1.jpg|180513224043_C1E1_N3U1D1.jpg|1'
    b'80513224144_C1E1_N4U1D1.jpg|180513224246_C1E1_N5U1D1.jpg|180513231841_C1E1_N1U1D1.jpg|180513231941_C1E1_N2U1D1.'
    b'jpg|180513232043_C1E1_N3U1D1.jpg|180513232144_C1E1_N4U1D1.jpg|180513232246_C1E1_N5U1D1.jpg|180513233454_C1E35_N'
    b'1U1D1.jpg|180513235841_C1E1_N1U1D1.jpg|180513235941_C1E1_N2U1D1.jpg|180514000043_C1E1_N3U1D1.jpg|180514000144_C'
    b'1E1_N4U1D1.jpg|180514000246_C1E1_N5U1D1.jpg|180514003522_C1E35_N1U1D1.jpg|180514003841_C1E1_N1U1D1.jpg|18051400'
    b'3941_C1E1_N2U1D1.jpg|180514004043_C1E1_N3U1D1.jpg|180514004144_C1E1_N4U1D1.jpg|180514004246_C1E1_N5U1D1.jpg|180'
    b'514011841_C1E1_N1U1D1.jpg|180514011941_C1E1_N2U1D1.jpg|18*8B\r\n',
    b'$$D1054,864507032323403,D01,8,5,0514012043_C1E1_N3U1D1.jpg|180514012144_C1E1_N4U1D1.jpg|180514012246_C1E1_N5U1D'
    b'1.jpg|180514013551_C1E35_N1U1D1.jpg|180514015841_C1E1_N1U1D1.jpg|180514015941_C1E1_N2U1D1.jpg|180514020043_C1E1'
    b'_N3U1D1.jpg|180514020144_C1E1_N4U1D1.jpg|180514020246_C1E1_N5U1D1.jpg|180514023620_C1E35_N1U1D1.jpg|18051402384'
    b'1_C1E1_N1U1D1.jpg|180514023941_C1E1_N2U1D1.jpg|180514024043_C1E1_N3U1D1.jpg|180514024144_C1E1_N4U1D1.jpg|180514'
    b'024246_C1E1_N5U1D1.jpg|180514031841_C1E1_N1U1D1.jpg|180514031941_C1E1_N2U1D1.jpg|180514032043_C1E1_N3U1D1.jpg|1'
    b'80514032144_C1E1_N4U1D1.jpg|180514032246_C1E1_N5U1D1.jpg|180514033648_C1E35_N1U1D1.jpg|180514035841_C1E1_N1U1D1'
    b'.jpg|180514035941_C1E1_N2U1D1.jpg|180514040043_C1E1_N3U1D1.jpg|180514040144_C1E1_N4U1D1.jpg|180514040246_C1E1_N'
    b'5U1D1.jpg|180514043717_C1E35_N1U1D1.jpg|180514043841_C1E1_N1U1D1.jpg|180514043941_C1E1_N2U1D1.jpg|180514044043_'
    b'C1E1_N3U1D1.jpg|180514044144_C1E1_N4U1D1.jpg|180514044246_C1E1_N5U1D1.jpg|180514051841_C1E1_N1U1D1.jpg|18051405'
    b'1942_C1E1_N2U1D1.jpg|180514052044_C1E1_N3U1D1.jpg|1805140*E4\r\n',
    b'$$E1054,864507032323403,D01,8,6,52145_C1E1_N4U1D1.jpg|180514052247_C1E1_N5U1D1.jpg|180514053746_C1E35_N1U1D1.jp'
    b'g|180514055841_C1E1_N1U1D1.jpg|180514055942_C1E1_N2U1D1.jpg|180514060044_C1E1_N3U1D1.jpg|180514060145_C1E1_N4U1'
    b'D1.jpg|180514060246_C1E1_N5U1D1.jpg|180514063814_C1E35_N1U1D1.jpg|180514063841_C1E1_N1U1D1.jpg|180514063942_C1E'
    b'1_N2U1D1.jpg|180514064043_C1E1_N3U1D1.jpg|180514064145_C1E1_N4U1D1.jpg|180514064246_C1E1_N5U1D1.jpg|18051407184'
    b'1_C1E1_N1U1D1.jpg|180514071942_C1E1_N2U1D1.jpg|180514072043_C1E1_N3U1D1.jpg|180514072145_C1E1_N4U1D1.jpg|180514'
    b'072246_C1E1_N5U1D1.jpg|180514073843_C1E35_N1U1D1.jpg|180514075841_C1E1_N1U1D1.jpg|180514075942_C1E1_N2U1D1.jpg|'
    b'180514080043_C1E1_N3U1D1.jpg|180514080145_C1E1_N4U1D1.jpg|180514080246_C1E1_N5U1D1.jpg|180514083841_C1E1_N1U1D1'
    b'.jpg|180514083912_C1E35_N1U1D1.jpg|180514083942_C1E1_N2U1D1.jpg|180514084043_C1E1_N3U1D1.jpg|180514084145_C1E1_'
    b'N4U1D1.jpg|180514084246_C1E1_N5U1D1.jpg|180514091841_C1E1_N1U1D1.jpg|180514091942_C1E1_N2U1D1.jpg|180514092043_'
    b'C1E1_N3U1D1.jpg|180514092145_C1E1_N4U1D1.jpg|180514092246*98\r\n',
    b'$$F309,864507032323403,D01,8,7,_C1E1_N5U1D1.jpg|180514093940_C1E35_N1U1D1.jpg|180514095840_C1E1_N1U1D1.jpg|1805'
    b'14100246_C1E1_N5U1D1.jpg|180514111942_C1E1_N2U1D1.jpg|180514100145_C1E1_N4U1D1.jpg|180514112043_C1E1_N3U1D1.jpg'
    b'|180514120043_C1E1_N3U1D1.jpg|180514120144_C1E1_N4U1D1.jpg|180514120246_C1E1_N5U1D1.jpg|*8E\r\n',
]
file_listing = [
     b'$$p1054,864507032323403,D01,1,0,180520032140_C1E1_N4U1D1.jpg|180520041216_C1E35_N1U1D1.jpg|180520004140_C1E1_N4'
     b'U1D1.jpg|180519204241_C1E1_N5U1D1.jpg|180519210839_C1E35_N1U1D1.jpg|180519211937_C1E1_N2U1D1.jpg|180519212140_C'
     b'1E1_N4U1D1.jpg|180519212242_C1E1_N5U1D1.jpg|180519215836_C1E1_N1U1D1.jpg|180519215937_C1E1_N2U1D1.jpg|180519220'
     b'140_C1E1_N4U1D1.jpg|180519220241_C1E1_N5U1D1.jpg|180519223836_C1E1_N1U1D1.jpg|180519231836_C1E1_N1U1D1.jpg|1805'
     b'19224140_C1E1_N4U1D1.jpg|180518223837_C1E1_N1U1D1.jpg|180518231837_C1E1_N1U1D1.jpg|180518224141_C1E1_N4U1D1.jpg'
     b'|180518224242_C1E1_N5U1D1.jpg|180518231938_C1E1_N2U1D1.jpg|180518235837_C1E1_N1U1D1.jpg|180518232242_C1E1_N5U1D'
     b'1.jpg|180519000039_C1E1_N3U1D1.jpg|180519000141_C1E1_N4U1D1.jpg|180519000242_C1E1_N5U1D1.jpg|180519004242_C1E1_'
     b'N5U1D1.jpg|180519004141_C1E1_N4U1D1.jpg|180519010837_C1E3_N1U1D1.jpg|180519012039_C1E1_N3U1D1.jpg|180519012141_'
     b'C1E1_N4U1D1.jpg|180519015837_C1E1_N1U1D1.jpg|180519023938_C1E1_N2U1D1.jpg|180519015939_C1E35_N1U1D1.jpg|1805190'
     b'20141_C1E1_N4U1D1.jpg|180519020242_C1E1_N5U1D1.jpg|180519*B0\r\n',
]


class NotMyIMEIError(Exception):
    """
    Class for identifying not my imei scenarions
    """
    pass


def request_to_response(request_command, imei):
    """
    Function to convert an incoming gprs message into a fixed response message
    :param request_command: The incoming message from the headend
    :param imei: The imei to use in the response
    :return: gprs message to send back to the headend
    """
    global file_listing
    if request_command == b'D01,0':
        file_list_arr = []
        for segment in file_listing:
            gprs = GPRS(segment)
            gprs.imei = imei
            file_list_arr.append(gprs)
        # Reset file list so we only send once
        file_listing = []
        return file_list_arr
    if request_command[0:3] == b'D00':
        print("Request command is %s", request_command)
        detail_list = request_command.split(b",")
        file_name = detail_list[1]
        start_packet = detail_list[2]
        # file_name, num_packets, packet_number, file_bytes = gprs.enclosed_data.get_file_data()
        image_as_bytes = binascii.unhexlify(
            "FFD8FFE000104A46494600010101004800480000"
            "FFDB004300FFFFFFFFFFFFFFFFFFFFFFFFFFFFFF"
            "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF"
            "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF"
            "FFFFFFFFFFFFFFFFFFFFC2000B08000100010101"
            "1100FFC400141001000000000000000000000000"
            "00000000FFDA0008010100013F10"
        )
        response = cts_build_file_list(imei, file_name, image_as_bytes)
        return response

    for key in REQUEST_TO_RESPONSE:
        command_length = len(key)
        if request_command[0:command_length] == key:
            return_gprs = GPRS(REQUEST_TO_RESPONSE[key])
            return_gprs.imei = imei
            print(return_gprs)
            return [return_gprs]
    return None


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

    for command in REQUEST_TO_RESPONSE:
        gprs_list = request_to_response(command, b"IMEI")
        for gprs in gprs_list:
            print(gprs.as_bytes())
    command = b'D01,0'
    gprs_list = request_to_response(command, b"IMEI")
    for gprs in gprs_list:
        print(gprs.as_bytes())

    command = b'D00,180514120246_C1E1_N5U1D1.jpg,0'
    gprs_list = request_to_response(command, b"IMEI")
    for gprs in gprs_list:
        print(gprs.as_bytes())


if __name__ == '__main__':
    main()
