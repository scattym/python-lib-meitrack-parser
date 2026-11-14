"""
Unit tests for analogue and digital pin telemetry, confirming Phase 1A bugfix.
"""

from meitrack.command.command_AAA import TrackerCommand
from meitrack.command.common import (
    Command,
    meitrack_analogue_pins_to_dict,
    meitrack_digital_pins_to_dict,
)
from meitrack.common import DIRECTION_CLIENT_TO_SERVER


def test_meitrack_analogue_pins_to_dict():
    # Single pin
    res1 = meitrack_analogue_pins_to_dict(b"0400")
    assert res1 == {0: 10.24}

    # 5 standard pins
    # 0x018D = 397 -> 3.97V, 0x0579 = 1401 -> 14.01V
    res5 = meitrack_analogue_pins_to_dict(b"0000|0000|0000|018D|0579")
    assert res5 == {
        0: 0.0,
        1: 0.0,
        2: 0.0,
        3: 3.97,
        4: 14.01,
    }


def test_live_analogue_pin_states_bugfix_phase1a():
    """
    Explicit regression test confirming Phase 1A bugfix:
    get_analogue_pin_states() must parse live telemetry instead of hardcoded bytes.
    """
    cmd = Command(DIRECTION_CLIENT_TO_SERVER)
    # Live telemetry values distinctly different from 0000|0000|0000|018D|0579
    cmd.field_dict["analog_input_value"] = b"0100|0200|0300|0400|0500"

    states = cmd.get_analogue_pin_states()
    assert states is not None
    # 0x0100 = 256 -> 2.56, 0x0200 = 512 -> 5.12, 0x0300 = 768 -> 7.68
    # 0x0400 = 1024 -> 10.24, 0x0500 = 1280 -> 12.80
    assert states[0] == 2.56
    assert states[1] == 5.12
    assert states[2] == 7.68
    assert states[3] == 10.24
    assert states[4] == 12.80

    # Ensure none if analog_input_value is missing
    cmd_empty = Command(DIRECTION_CLIENT_TO_SERVER)
    assert cmd_empty.get_analogue_pin_states() is None


def test_get_analog_input_value_and_battery():
    cmd = TrackerCommand(DIRECTION_CLIENT_TO_SERVER)
    # Battery voltage (pin 4) is 0x01A4 (420 -> 4.20V)
    # Ext power (pin 5) is 0x04E2 (1250 -> 12.50V)
    cmd.field_dict["analog_input_value"] = b"0000|0000|0000|01A4|04E2"

    assert cmd.get_analog_input_value(1) == 0.0
    assert cmd.get_analog_input_value(4) == 4.20
    assert cmd.get_analog_input_value(5) == 12.50
    # Out of range pin
    assert cmd.get_analog_input_value(6) is None

    # Battery helpers
    assert cmd.get_battery_voltage() == 4.20
    # 4.20 / 4.2 * 100 = 100%
    assert cmd.get_battery_level() == 100

    # Test lower battery level: 2.10V -> 2.10 / 4.2 * 100 = 50%
    cmd.field_dict["analog_input_value"] = b"0000|0000|0000|00D2|04E2"
    assert cmd.get_battery_level() == 50

    # Missing analog_input_value
    cmd_none = TrackerCommand(DIRECTION_CLIENT_TO_SERVER)
    assert cmd_none.get_analog_input_value(4) is None
    assert cmd_none.get_battery_voltage() is None
    assert cmd_none.get_battery_level() is None


def test_meitrack_digital_pins_to_dict():
    # All zeros: 16 digital pins all False
    zeros = meitrack_digital_pins_to_dict(b"0000")
    assert len(zeros) == 16
    assert all(not val for val in zeros.values())

    # Pin 0 True (0x0001)
    pin0 = meitrack_digital_pins_to_dict(b"0001")
    assert pin0[0] is True
    assert all(not pin0[i] for i in range(1, 16))

    # Pin 10 True (0x0400: byte 1 bit 2 -> index 8 + 2 = 10)
    pin10 = meitrack_digital_pins_to_dict(b"0400")
    assert pin10[10] is True
    assert pin10[0] is False

    # All pins True (0xFFFF)
    all_ones = meitrack_digital_pins_to_dict(b"FFFF")
    assert len(all_ones) == 16
    assert all(val is True for val in all_ones.values())

    # Invalid / non-hex string returns empty dict
    assert meitrack_digital_pins_to_dict(b"INVALID") == {}
    assert meitrack_digital_pins_to_dict(b"04011") == {}  # odd length hex string


def test_get_digital_pin_states():
    cmd = Command(DIRECTION_CLIENT_TO_SERVER)
    cmd.field_dict["io_port_status"] = b"0400"

    states = cmd.get_digital_pin_states()
    assert states is not None
    assert states[10] is True

    # Missing io_port_status
    cmd_empty = Command(DIRECTION_CLIENT_TO_SERVER)
    assert cmd_empty.get_digital_pin_states() is None
