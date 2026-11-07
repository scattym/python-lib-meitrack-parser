"""
Comprehensive tests covering A13, C91, E91, event resolution,
command factory parameter validations, stub processor, and module runners.
"""
import pytest

import meitrack.event
import meitrack.file_download
import meitrack.file_list
import meitrack.firmware_update
import meitrack.gprs_protocol
import meitrack.stub_processor
from meitrack import build_message, command
from meitrack.command import (
    command_A13,
    command_AAA,
    command_C91,
    command_D00,
    command_E91,
    command_FC0,
    command_FC3,
    command_FC4,
    command_FC5,
    command_FC6,
    command_FC7,
    command_to_object,
)
from meitrack.command import (
    common as command_common,
)
from meitrack.command import (
    event as command_event,
)
from meitrack.command.command_A13 import SetCorneringCommand
from meitrack.command.command_C91 import SetIOParamsCommand
from meitrack.command.command_E91 import RequestDeviceInfoCommand
from meitrack.command.common import Command
from meitrack.common import DIRECTION_CLIENT_TO_SERVER, DIRECTION_SERVER_TO_CLIENT
from meitrack.error import GPRSParameterError


def test_command_a13_cornering():
    req = SetCorneringCommand(DIRECTION_SERVER_TO_CLIENT, b"A13,30")
    assert req.command == b"A13"
    assert req.angle == b"30"
    assert req.as_bytes() == b"A13,30"

    res = SetCorneringCommand(DIRECTION_CLIENT_TO_SERVER, b"A13,OK")
    assert res.command == b"A13"
    assert res.response == b"OK"
    assert res.as_bytes() == b"A13,OK"


def test_command_c91_io_params():
    req = SetIOParamsCommand(DIRECTION_SERVER_TO_CLIENT, b"C91,A78,1:0,2:0,3:0,4:13,5:13")
    assert req.command == b"C91"
    assert req.model == b"A78"
    assert req.device1 == b"1:0"
    assert req.as_bytes() == b"C91,A78,1:0,2:0,3:0,4:13,5:13"

    res = SetIOParamsCommand(DIRECTION_CLIENT_TO_SERVER, b"C91,OK")
    assert res.command == b"C91"
    assert res.response == b"OK"
    assert res.as_bytes() == b"C91,OK"


def test_command_e91_device_info():
    req = RequestDeviceInfoCommand(DIRECTION_SERVER_TO_CLIENT, b"E91")
    assert req.command == b"E91"
    assert req.as_bytes() == b"E91"

    res = RequestDeviceInfoCommand(DIRECTION_CLIENT_TO_SERVER, b"E91,T333_Y39V083,123456789")
    assert res.command == b"E91"
    assert res.firmware_version == b"T333_Y39V083"
    assert res.serial_number == b"123456789"
    assert res.as_bytes() == b"E91,T333_Y39V083,123456789"

    # Command helper methods on res
    assert res.get_firmware_version() == b"T333_Y39V083"
    assert res.get_serial_number() == b"123456789"
    assert res.get_device_type() == "T333"

    # None cases
    empty_cmd = Command(DIRECTION_CLIENT_TO_SERVER)
    assert empty_cmd.get_firmware_version() is None
    assert empty_cmd.get_serial_number() is None
    assert empty_cmd.get_device_type() is None
    assert empty_cmd.is_response_error() is False


def test_event_resolution():
    # command_event.event_to_name
    assert command_event.event_to_name(35) == "Track By Time Interval"
    assert command_event.event_to_name("35") == "Track By Time Interval"
    assert command_event.event_to_name(b"35") == "Track By Time Interval"
    assert command_event.event_to_name("invalid_int") is None
    assert command_event.event_to_name(b"invalid_bytes") is None
    assert command_event.event_to_name(9999) is None
    assert command_event.event_to_name([1, 2, 3]) is None

    # command_event.event_to_id
    assert command_event.event_to_id(145) == 145
    assert command_event.event_to_id("145") == 145
    assert command_event.event_to_id(b"145") == 145
    assert command_event.event_to_id("not_a_number") is None
    assert command_event.event_to_id(b"not_a_number") is None
    assert command_event.event_to_id([1]) is None

    # meitrack.event.event_id_to_name
    assert meitrack.event.event_id_to_name(109) == "Taxi data"
    with pytest.raises(KeyError):
        meitrack.event.event_id_to_name(9999)
    ev = meitrack.event.Event()
    assert ev is not None


def test_stub_processor():
    imei = b"353358017784062"

    # Request A11
    res_a11 = meitrack.stub_processor.request_to_response(b"A11,10", imei)
    assert res_a11 is not None
    assert len(res_a11) == 1
    assert res_a11[0].command_type == b"A11"

    # Request D00 (photo chunk)
    res_d00 = meitrack.stub_processor.request_to_response(b"D00,photo.jpg,0", imei)
    assert res_d00 is not None
    assert len(res_d00) == 1
    assert b"D00,photo.jpg" in res_d00[0].as_bytes()

    # Request D01 (photo list)
    res_d01 = meitrack.stub_processor.request_to_response(b"D01,0", imei)
    assert res_d01 is not None

    # Unknown command
    res_unknown = meitrack.stub_processor.request_to_response(b"UNKNOWN,COMMAND", imei)
    assert res_unknown is None

    # NotMyIMEIError exception
    err = meitrack.stub_processor.NotMyIMEIError()
    assert isinstance(err, Exception)


def test_command_factory_parameter_validations():
    # stc_request_take_photo with None filename generates default filename
    photo_cmd = command.stc_request_take_photo(1, None)
    assert b"D03,1,camera-1-" in photo_cmd.as_bytes()

    # Heartbeat validation
    with pytest.raises(GPRSParameterError):
        command.stc_set_heartbeat(-1)
    with pytest.raises(GPRSParameterError):
        command.stc_set_heartbeat(70000)

    # Time interval validation
    with pytest.raises(GPRSParameterError):
        command.stc_set_tracking_by_time_interval(-1)
    with pytest.raises(GPRSParameterError):
        command.stc_set_tracking_by_time_interval(70000)

    # Cornering angle validation
    with pytest.raises(GPRSParameterError):
        command.stc_set_cornering_angle(-1)
    with pytest.raises(GPRSParameterError):
        command.stc_set_cornering_angle(360)

    # Timezone offset validation
    with pytest.raises(GPRSParameterError):
        command.stc_set_time_zone(-40000)
    with pytest.raises(GPRSParameterError):
        command.stc_set_time_zone(40000)

    # Fatigue driving alert validation
    with pytest.raises(GPRSParameterError):
        command.stc_set_fatigue_driving_alert(consecutive_driving_time_mins=1001)
    with pytest.raises(GPRSParameterError):
        command.stc_set_fatigue_driving_alert(alert_time_secs=70000)
    with pytest.raises(GPRSParameterError):
        command.stc_set_fatigue_driving_alert(acc_off_time_mins=1001)

    # Idle alert validation
    with pytest.raises(GPRSParameterError):
        command.stc_set_idle_alert_time(consecutive_speed_time_secs=70000)
    with pytest.raises(GPRSParameterError):
        command.stc_set_idle_alert_time(speed_kmh=201)
    with pytest.raises(GPRSParameterError):
        command.stc_set_idle_alert_time(alert_time_secs=70000)

    # Speeding alert validation
    with pytest.raises(GPRSParameterError):
        command.stc_set_speeding_alert(speed_kmh=256)
    with pytest.raises(GPRSParameterError):
        command.stc_set_speeding_alert(disabled="invalid")

    # Tracking by distance validation
    with pytest.raises(GPRSParameterError):
        command.stc_set_tracking_by_distance(-1)
    with pytest.raises(GPRSParameterError):
        command.stc_set_tracking_by_distance(70000)

    # Photo event flags
    flags_cmd = command.stc_set_photo_event_flags([0, 2])
    assert flags_cmd.as_bytes().startswith(b"B96,")


def test_build_message_extra_helpers():
    imei = b"0407"
    validity_gprs = build_message.stc_set_driver_license_validity_time(imei, 10)
    assert validity_gprs.direction == b"@@"
    assert b"C52,10" in validity_gprs.as_bytes()

    io_gprs = build_message.stc_set_io_device_params(imei, b"model", ((1, 1), (2, 2)))
    assert io_gprs.direction == b"@@"
    assert b"C91,model,1:1,2:2" in io_gprs.as_bytes()


def test_module_mains_coverage(capsys):
    """
    Run module main() routines to eliminate dead unexercised main blocks.
    """
    command_A13.main()
    command_C91.main()
    command_E91.main()
    command_to_object.main()
    command_FC0.main()
    command_FC3.main()
    command_FC4.main()
    command_FC5.main()
    command_FC6.main()
    command_FC7.main()
    command_common.main()
    command_event.main()
    command.main()
    command_AAA.main()
    command_D00.main()
    meitrack.stub_processor.main()
    meitrack.build_message.main()
    meitrack.file_download.main()
    meitrack.file_list.main()
    meitrack.firmware_update.main()

    # Flush output
    capsys.readouterr()
