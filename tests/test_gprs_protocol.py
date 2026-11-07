"""
Unit tests for GPRS protocol framing, length calculation, checksum, and stream parsing.
"""
import pytest

from meitrack.common import (
    CLIENT_TO_SERVER_PREFIX,
    DIRECTION_CLIENT_TO_SERVER,
    DIRECTION_SERVER_TO_CLIENT,
    END_OF_MESSAGE_STRING,
    MAX_DATA_LENGTH,
    SERVER_TO_CLIENT_PREFIX,
)
from meitrack.error import GPRSParseError
from meitrack.gprs_protocol import (
    GPRS,
    calc_signature,
    parse_data_payload,
    prefix_to_direction,
)


def test_prefix_to_direction():
    assert prefix_to_direction(SERVER_TO_CLIENT_PREFIX) == DIRECTION_SERVER_TO_CLIENT
    assert prefix_to_direction(CLIENT_TO_SERVER_PREFIX) == DIRECTION_CLIENT_TO_SERVER

    with pytest.raises(GPRSParseError, match="Invalid prefix"):
        prefix_to_direction(b"!!")

    with pytest.raises(GPRSParseError, match="Invalid prefix"):
        prefix_to_direction(b"")


def test_calc_signature():
    assert calc_signature(b"1234ABCD*AA") == 254
    assert calc_signature(b"$$n1084,864507032323,D00,1804.jpg,16,0,\xff\xd8\xff\xdb\x00\x84\x00@%\x14\xc0J)*AA") == 120
    assert calc_signature(b"$$n1084,864507032323,D00,1804.jpg,16,0,*\xd8\xff\xdb\x00\x84\x00\x00\xd3@%\x14J)*AA") == 182
    assert calc_signature(b"$$n1084,864507032323,D00,1804.jpg,16,0,\xff\xd8\xff\xdb\x00\x84\x00*AA") == 204

    # Calculation up to and including '*'
    payload = b"@@Q25,353358017784062,A10*6A\r\n"
    star_idx = payload.rfind(b"*")
    expected_cs = sum(payload[: star_idx + 1]) & 0xFF
    assert calc_signature(payload) == expected_cs


def test_gprs_default_initialization():
    gprs = GPRS()
    assert gprs.device_type == "T333"
    assert gprs.payload == b""
    assert gprs.direction is None
    assert gprs.data_identifier is None
    assert gprs.checksum == b"XX"
    assert gprs.enclosed_data is None

    # Custom device type and None fallback
    gprs_custom = GPRS(device_type="T366G")
    assert gprs_custom.device_type == "T366G"

    gprs_default = GPRS()
    assert gprs_default.device_type == "T333"


def test_gprs_properties_and_accessors():
    gprs = GPRS()
    gprs.checksum = b"FE"
    assert gprs.checksum == b"FE"

    gprs.imei = b"123456789012345"
    gprs.leftover = b"AAA,35"
    assert gprs.data_length == str(len(b"," + gprs.imei + b"," + gprs.leftover + b"*" + b"FE" + END_OF_MESSAGE_STRING)).encode()

    gprs.data_length = 50
    # Overridden internal data length
    assert gprs.data_length == str(len(b"," + gprs.imei + b"," + gprs.leftover + b"*" + b"FE" + END_OF_MESSAGE_STRING)).encode()

    # Str output
    str_repr = str(gprs)
    assert "imei: b'123456789012345'" in str_repr
    assert "checksum: b'FE'" in str_repr


def test_gprs_parse_downlink_packet():
    raw_packet = b"@@Q25,353358017784062,A10*6A\r\n"
    gprs = GPRS(raw_packet)

    assert gprs.direction == b"@@"
    assert gprs.data_identifier == b"Q"
    assert gprs.imei == b"353358017784062"
    assert gprs.command_type == b"A10"
    assert gprs.checksum == b"6A"
    assert gprs.enclosed_data is not None
    assert gprs.enclosed_data["command"] == b"A10"


def test_gprs_as_bytes_and_counter():
    raw_packet = b"@@Q25,353358017784062,A10*6A\r\n"
    gprs = GPRS(raw_packet)

    # Serializing without counter preserves identifier
    serialized = gprs.as_bytes()
    assert serialized == raw_packet

    # Serializing with counter modifies identifier: (counter % 58) + 65
    # Counter 0 -> 65 = 'A'
    serialized_0 = gprs.as_bytes(counter=0)
    assert serialized_0.startswith(b"@@A")
    assert serialized_0.endswith(b"\r\n")

    # Counter 59 -> (59 % 58) + 65 = 66 = 'B'
    serialized_59 = gprs.as_bytes(counter=59)
    assert serialized_59.startswith(b"@@B")


def test_gprs_recalc_methods():
    raw_packet = b"$$D160,864507032228727,AAA,35,24.819116,121.026091,180323023615,A,7,16,0,176,1.3,83,7,1174,466|97|527B|01035DB4,0000,0001|0000|0000|019A|0981,00000001,,3,,,36,23*DC\r\n"
    gprs = GPRS(raw_packet)

    old_date = gprs.enclosed_data.date_time
    gprs.recalc_date()
    assert gprs.enclosed_data.date_time != old_date

    gprs.recalc_leftover()
    assert gprs.leftover.startswith(b"AAA,35")


def test_parse_data_payload_single_and_multi():
    pkt1 = b"$$S28,353358017784062,A11,OK*FE\r\n"
    pkt2 = b"$$Q128,353358017784062,AAA,34,22.543176,114.078448,100313093738,A,5,22,2,205,5,-14,0,60,0|0|10133|4110,0000,149|153|173|2707|914,*91\r\n"

    # Single packet parsing
    packets, before, leftover = parse_data_payload(pkt1, DIRECTION_CLIENT_TO_SERVER)
    assert len(packets) == 1
    assert packets[0].imei == b"353358017784062"
    assert packets[0].command_type == b"A11"
    assert before == b""
    assert leftover == b""

    # Concatenated multi-packet stream
    combined = pkt1 + pkt2
    packets, before, leftover = parse_data_payload(combined, DIRECTION_CLIENT_TO_SERVER)
    assert len(packets) == 2
    assert packets[0].command_type == b"A11"
    assert packets[1].command_type == b"AAA"
    assert leftover == b""

    # Downlink stream
    downlink_pkt = b"@@Q25,353358017784062,A10*6A\r\n"
    packets, before, leftover = parse_data_payload(downlink_pkt, DIRECTION_SERVER_TO_CLIENT)
    assert len(packets) == 1
    assert packets[0].command_type == b"A10"


def test_parse_data_payload_framing_edges_and_errors():
    pkt = b"$$S28,353358017784062,A11,OK*FE\r\n"

    # Preceding garbage bytes before valid start token
    noisy_buffer = b"GARBAGE_NOISE_BYTES" + pkt
    packets, before, leftover = parse_data_payload(noisy_buffer, DIRECTION_CLIENT_TO_SERVER)
    assert len(packets) == 1
    assert before == b"GARBAGE_NOISE_BYTES"
    assert leftover == b""

    # Incomplete packet (partial buffer)
    partial_buffer = pkt[:15]
    packets, before, leftover = parse_data_payload(partial_buffer, DIRECTION_CLIENT_TO_SERVER)
    assert len(packets) == 0
    assert leftover == partial_buffer

    # Missing start token entirely
    no_prefix_buf = b"12345,some,random,bytes\r\n"
    packets, before, leftover = parse_data_payload(no_prefix_buf, DIRECTION_CLIENT_TO_SERVER)
    assert len(packets) == 0
    assert leftover == no_prefix_buf

    # Missing first comma
    no_comma_pkt = b"$$S28no_comma_here\r\n"
    packets, before, leftover = parse_data_payload(no_comma_pkt, DIRECTION_CLIENT_TO_SERVER)
    assert len(packets) == 0
    assert leftover == no_comma_pkt

    # Corrupted / invalid integer in length field
    corrupt_length_pkt = b"$$SINVALID,353358017784062,A11,OK*FE\r\n"
    packets, before, leftover = parse_data_payload(corrupt_length_pkt, DIRECTION_CLIENT_TO_SERVER)
    assert len(packets) == 0
    assert leftover == corrupt_length_pkt

    # Length field exceeds MAX_DATA_LENGTH (2048)
    huge_length_pkt = f"$$A{MAX_DATA_LENGTH + 100},353358017784062,A11,OK*FE\r\n".encode()
    with pytest.raises(GPRSParseError, match="longer than the protocol allows"):
        parse_data_payload(huge_length_pkt, DIRECTION_CLIENT_TO_SERVER)

    # Length does not lead to \r\n terminator
    # Length says 10 bytes, but slice doesn't end with \r\n
    bad_terminator_pkt = b"$$S10,123456789012345,A11,OK*FE\r\n"
    with pytest.raises(GPRSParseError, match="Found begin token, but length does not lead to end of payload"):
        parse_data_payload(bad_terminator_pkt, DIRECTION_CLIENT_TO_SERVER)
