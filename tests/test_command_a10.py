"""
Unit tests for A10 (Real-Time Location Query) command, confirming Phase 1A implementation.
"""
from meitrack.command import stc_request_location
from meitrack.command.command_A10 import (
    LocationQueryCommand,
    stc_request_location_command,
)
from meitrack.command.command_A10 import (
    main as a10_main,
)
from meitrack.command.command_to_object import COMMAND_LIST, command_to_object
from meitrack.common import DIRECTION_CLIENT_TO_SERVER, DIRECTION_SERVER_TO_CLIENT
from meitrack.gprs_protocol import GPRS


def test_command_a10_request():
    cmd = stc_request_location_command()
    assert isinstance(cmd, LocationQueryCommand)
    assert cmd.direction == DIRECTION_SERVER_TO_CLIENT
    assert cmd.field_name_selector == ["command"]
    assert cmd.as_bytes() == b"A10"

    # From meitrack.command package facade
    cmd_facade = stc_request_location()
    assert isinstance(cmd_facade, LocationQueryCommand)
    assert cmd_facade.as_bytes() == b"A10"


def test_command_a10_response():
    cmd = LocationQueryCommand(DIRECTION_CLIENT_TO_SERVER, b"A10,OK")
    assert cmd.direction == DIRECTION_CLIENT_TO_SERVER
    assert cmd.field_name_selector == ["command", "response"]
    assert cmd.command == b"A10"
    assert cmd.response == b"OK"
    assert cmd.as_bytes() == b"A10,OK"


def test_command_a10_registration_in_command_to_object():
    assert COMMAND_LIST[b"A10"]["class"] is LocationQueryCommand
    assert COMMAND_LIST[b"A10"]["name"] == "Real-Time Location Query"

    obj_downlink = command_to_object(DIRECTION_SERVER_TO_CLIENT, b"A10", b"A10")
    assert isinstance(obj_downlink, LocationQueryCommand)
    assert obj_downlink.as_bytes() == b"A10"

    obj_uplink = command_to_object(DIRECTION_CLIENT_TO_SERVER, b"A10", b"A10,OK")
    assert isinstance(obj_uplink, LocationQueryCommand)
    assert obj_uplink.response == b"OK"


def test_command_a10_gprs_envelope():
    raw_downlink = b"@@Q25,353358017784062,A10*6A\r\n"
    gprs = GPRS(raw_downlink)

    assert gprs.direction == b"@@"
    assert gprs.imei == b"353358017784062"
    assert gprs.command_type == b"A10"
    assert isinstance(gprs.enclosed_data, LocationQueryCommand)
    assert gprs.as_bytes() == raw_downlink


def test_command_a10_main_run(capsys):
    # Exercise main() block
    a10_main()
    captured = capsys.readouterr()
    assert "A10" in captured.out
