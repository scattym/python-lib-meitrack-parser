"""
Unit tests for OTA firmware update suite (FC0 through FC7) and state machine,
confirming Phase 1A bugfix on little-endian byte ordering.
"""
import binascii

from meitrack.command.command_FC0 import (
    AuthOtaUpdateCommand,
    stc_auth_ota_update_command,
)
from meitrack.command.command_FC1 import (
    SendOtaDataCommand,
    stc_send_ota_data_command,
)
from meitrack.command.command_FC2 import (
    ObtainOtaChecksumCommand,
    stc_obtain_ota_checksum_command,
)
from meitrack.command.command_FC3 import (
    StartOtaUpdateCommand,
    stc_start_ota_update_command,
)
from meitrack.command.command_FC4 import (
    CancelOtaUpdateCommand,
    stc_cancel_ota_update_command,
)
from meitrack.command.command_FC5 import (
    CheckDeviceCodeCommand,
    stc_check_device_code_command,
)
from meitrack.command.command_FC6 import (
    CheckFirmwareVersionCommand,
    stc_check_firmware_version_command,
)
from meitrack.command.command_FC7 import (
    SetOtaServerCommand,
    stc_set_ota_server_command,
)
from meitrack.common import DIRECTION_CLIENT_TO_SERVER, DIRECTION_SERVER_TO_CLIENT
from meitrack.firmware_update import (
    STAGE_FIRST,
    STAGE_SECOND,
    FirmwareUpdate,
    stc_obtain_ota_checksum,
)
from meitrack.gprs_protocol import GPRS


def test_fc0_auth_ota_update():
    cmd = stc_auth_ota_update_command()
    assert cmd.as_bytes() == b"FC0,AUTH"

    # Client response success
    res_success = AuthOtaUpdateCommand(
        DIRECTION_CLIENT_TO_SERVER,
        b"FC0,000A,OK,1024,T333_V100,T333_V101.OTA"
    )
    assert res_success.device_code == b"000A"
    assert res_success.response == b"OK"
    assert res_success.packet_size == b"1024"
    assert res_success.current_firmware == b"T333_V100"
    assert res_success.ota_file_name == b"T333_V101.OTA"
    assert res_success.is_response_error() is False

    # Client response error
    res_err = AuthOtaUpdateCommand(DIRECTION_CLIENT_TO_SERVER, b"FC0,000A,Err")
    assert res_err.is_response_error() is True


def test_fc1_send_ota_data():
    file_bytes = b"A" * 2500
    cmds = stc_send_ota_data_command(file_bytes, 1024)
    assert len(cmds) == 3
    # Check offsets: 0, 1024, 2048
    assert cmds[0].index == 0
    assert len(cmds[0].file_contents) == 1024
    assert cmds[1].index == 1024
    assert len(cmds[1].file_contents) == 1024
    assert cmds[2].index == 2048
    assert len(cmds[2].file_contents) == 452

    # Empty chunk size handling
    assert stc_send_ota_data_command(file_bytes, 0) == []

    # Client response success
    res_ok = SendOtaDataCommand(DIRECTION_CLIENT_TO_SERVER, b"FC1,00000000040001")
    assert res_ok.is_response_error() is False
    idx, length = res_ok.ota_response_data()
    assert idx == 0
    assert length == 1024

    # Client response failure
    res_fail = SendOtaDataCommand(DIRECTION_CLIENT_TO_SERVER, b"FC1,00000000040000")
    assert res_fail.is_response_error() is True

    # Client response NOT
    res_not = SendOtaDataCommand(DIRECTION_CLIENT_TO_SERVER, b"FC1,NOT")
    assert res_not.is_response_error() is True
    assert res_not.ota_response_data() == (None, None)


def test_fc2_obtain_ota_checksum_endianness_phase1a_bugfix():
    """
    Explicit regression test confirming Phase 1A bugfix:
    FC2 packets must default to little-endian byte ordering per Section 3.2,
    while supporting explicit configurable byteorder.
    """
    # Default is little-endian
    cmd_le = stc_obtain_ota_checksum_command(3, 5)
    expected_le = b"FC2," + (3).to_bytes(4, byteorder="little") + (5).to_bytes(4, byteorder="little")
    assert cmd_le.as_bytes() == expected_le
    assert cmd_le.as_bytes() == b"FC2,\x03\x00\x00\x00\x05\x00\x00\x00"

    # Big-endian option
    cmd_be = stc_obtain_ota_checksum_command(3, 5, byteorder="big")
    expected_be = b"FC2," + (3).to_bytes(4, byteorder="big") + (5).to_bytes(4, byteorder="big")
    assert cmd_be.as_bytes() == expected_be
    assert cmd_be.as_bytes() == b"FC2,\x00\x00\x00\x03\x00\x00\x00\x05"

    # firmware_update.stc_obtain_ota_checksum wrapper
    gprs_le = stc_obtain_ota_checksum(b"0407", 0, 5, byteorder="little")
    assert b"FC2,\x00\x00\x00\x00\x05\x00\x00\x00" in gprs_le.as_bytes()

    # Client response: NOT
    res_not = ObtainOtaChecksumCommand(DIRECTION_CLIENT_TO_SERVER, b"FC2,NOT")
    assert res_not.is_response_error() is True
    assert res_not.ota_data_checksum() is None

    # Client response: 4-byte hex checksum
    # e.g. 0x1234 in little-endian hex string
    cs_bytes = (0x1234).to_bytes(2, byteorder="little")
    hex_cs = binascii.hexlify(cs_bytes)
    res_cs = ObtainOtaChecksumCommand(DIRECTION_CLIENT_TO_SERVER, b"FC2," + hex_cs)
    assert res_cs.is_response_error() is False
    assert res_cs.ota_data_checksum(byteorder="little") == 0x1234


def test_fc3_start_ota_update():
    cmd = stc_start_ota_update_command()
    assert cmd.as_bytes() == b"FC3"

    # Status 1 (entering bootloader) and Status 2 (boot success)
    res1 = StartOtaUpdateCommand(DIRECTION_CLIENT_TO_SERVER, b"FC3,1")
    assert res1.is_response_error() is False

    res2 = StartOtaUpdateCommand(DIRECTION_CLIENT_TO_SERVER, b"FC3,2")
    assert res2.is_response_error() is False

    # Status 3 (checksum error) and NOT (unauthorized)
    res3 = StartOtaUpdateCommand(DIRECTION_CLIENT_TO_SERVER, b"FC3,3")
    assert res3.is_response_error() is True

    res_not = StartOtaUpdateCommand(DIRECTION_CLIENT_TO_SERVER, b"FC3,NOT")
    assert res_not.is_response_error() is True


def test_fc4_cancel_ota_update():
    cmd = stc_cancel_ota_update_command()
    assert cmd.as_bytes() == b"FC4"

    res = CancelOtaUpdateCommand(DIRECTION_CLIENT_TO_SERVER, b"FC4,OK")
    assert res.response == b"OK"


def test_fc5_check_device_code():
    cmd = stc_check_device_code_command()
    assert cmd.as_bytes() == b"FC5"

    res = CheckDeviceCodeCommand(DIRECTION_CLIENT_TO_SERVER, b"FC5,\x00\x0A")
    assert res.ota_response_device_code() == b"000a"

    res_empty = CheckDeviceCodeCommand(DIRECTION_SERVER_TO_CLIENT, b"FC5")
    assert res_empty.ota_response_device_code() is None


def test_fc6_check_firmware_version():
    cmd = stc_check_firmware_version_command(b"T333_Y39V083.OTA")
    assert cmd.as_bytes() == b"FC6,T333_Y39V083.OTA"

    res_ok = CheckFirmwareVersionCommand(DIRECTION_CLIENT_TO_SERVER, b"FC6,OK")
    assert res_ok.is_response_error() is False

    res_same = CheckFirmwareVersionCommand(DIRECTION_CLIENT_TO_SERVER, b"FC6,1")
    assert res_same.is_response_error() is False

    res_err = CheckFirmwareVersionCommand(DIRECTION_CLIENT_TO_SERVER, b"FC6,2")
    assert res_err.is_response_error() is True


def test_fc7_set_ota_server():
    cmd = stc_set_ota_server_command(b"1.2.3.4", b"6100")
    assert cmd.as_bytes() == b"FC7,1.2.3.4,6100"

    res_ok = SetOtaServerCommand(DIRECTION_CLIENT_TO_SERVER, b"FC7,OK")
    assert res_ok.is_response_error() is False

    res_err = SetOtaServerCommand(DIRECTION_CLIENT_TO_SERVER, b"FC7,Err")
    assert res_err.is_response_error() is True

    res_ffff = SetOtaServerCommand(DIRECTION_CLIENT_TO_SERVER, b"FC7,FFFF")
    assert res_ffff.is_response_error() is True


def test_firmware_update_stage1_flow():
    fu = FirmwareUpdate(
        imei=b"353358017784062",
        device_code=b"000a",
        ip_address=b"1.2.3.4",
        port=b"6100",
        file_name=b"T333_V100.OTA",
        file_bytes=b"",
        stage=STAGE_FIRST,
    )
    assert len(fu.messages) == 4
    assert fu.is_finished is False

    # Send FC5
    req1 = fu.return_next_payload()
    assert req1.enclosed_data.command == b"FC5"

    # Device returns FC5 response with matching device code
    resp1 = GPRS(b"$$A25,353358017784062,FC5,\x00\x0A*AA\r\n")
    fu.parse_response(resp1)
    assert fu.is_error is False

    # Send FC6
    req2 = fu.return_next_payload()
    assert req2.enclosed_data.command == b"FC6"

    # Device returns FC6,OK
    resp2 = GPRS(b"$$A26,353358017784062,FC6,OK*AA\r\n")
    fu.parse_response(resp2)
    assert fu.is_error is False

    # Send FC7
    req3 = fu.return_next_payload()
    assert req3.enclosed_data.command == b"FC7"

    # Device returns FC7,OK
    resp3 = GPRS(b"$$A26,353358017784062,FC7,OK*AA\r\n")
    fu.parse_response(resp3)
    assert fu.is_error is False

    # Send FC0
    req4 = fu.return_next_payload()
    assert req4.enclosed_data.command == b"FC0"

    # Device returns FC0,OK
    resp4 = GPRS(b"$$A80,353358017784062,FC0,000A,OK,1024,T333_V090,T333_V100.OTA*AA\r\n")
    fu.parse_response(resp4)
    assert fu.is_finished is True
    assert fu.is_error is False


def test_firmware_update_stage2_flow():
    fu = FirmwareUpdate(
        imei=b"353358017784062",
        device_code=b"000a",
        ip_address=b"1.2.3.4",
        port=b"6100",
        file_name=b"T333_V100.OTA",
        file_bytes=b"A" * 500,
        stage=STAGE_SECOND,
    )
    # Stage 2 initial message is FC0
    assert len(fu.messages) == 1
    assert fu.current_message is not None

    # Tracker responds to FC0 with packet_size 1024
    resp0 = GPRS(b"$$A80,353358017784062,FC0,000A,OK,1024,T333_V090,T333_V100.OTA*AA\r\n")
    fu.parse_response(resp0)

    # After FC0 response, FC1 chunk, FC2 checksum, FC3 start are dynamically queued
    assert len(fu.messages) == 4
    assert fu.messages[1]["request"].enclosed_data.command == b"FC1"
    assert fu.messages[2]["request"].enclosed_data.command == b"FC2"
    assert fu.messages[3]["request"].enclosed_data.command == b"FC3"

    # Next payload is FC1
    req_fc1 = fu.return_next_payload()
    assert req_fc1.enclosed_data.command == b"FC1"

    # Feed FC1 response
    resp_fc1 = GPRS(b"$$A35,353358017784062,FC1,0000000001f401*AA\r\n")
    fu.parse_response(resp_fc1)

    # Next payload is FC2
    req_fc2 = fu.return_next_payload()
    assert req_fc2.enclosed_data.command == b"FC2"

    # Feed FC2 response
    resp_fc2 = GPRS(b"$$A28,353358017784062,FC2,1234*AA\r\n")
    fu.parse_response(resp_fc2)

    # Next payload is FC3
    req_fc3 = fu.return_next_payload()
    assert req_fc3.enclosed_data.command == b"FC3"

    # Feed FC3 response (1 = rebooting)
    resp_fc3 = GPRS(b"$$A25,353358017784062,FC3,1*AA\r\n")
    fu.parse_response(resp_fc3)

    assert fu.is_finished is True
    assert fu.is_error is False


def test_firmware_update_error_handling_and_cancellation():
    fu = FirmwareUpdate(
        imei=b"353358017784062",
        device_code=b"000a",
        ip_address=b"1.2.3.4",
        port=b"6100",
        file_name=b"T333_V100.OTA",
        file_bytes=b"BINARY",
        stage=STAGE_FIRST,
    )
    fu.return_next_payload()
    # Device code mismatch error
    resp_mismatch = GPRS(b"$$A25,353358017784062,FC5,\x00\x0B*AA\r\n")
    fu.parse_response(resp_mismatch)
    assert fu.is_error is True

    # Next payload should be FC4 (cancel)
    cancel_req = fu.return_next_payload()
    assert cancel_req.enclosed_data.command == b"FC4"
    assert fu.is_finished is True
