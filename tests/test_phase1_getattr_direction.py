"""Tests for Command.__getattr__ semantics, AAA properties and direction auto-detect."""

import copy
import pickle

import pytest

from meitrack.command.command_AAA import TrackerCommand
from meitrack.common import DIRECTION_CLIENT_TO_SERVER
from meitrack.gprs_protocol import GPRS, parse_data_payload

AAA = (
    b"$$D160,864507032228727,AAA,35,24.819116,121.026091,180323023615,A,7,16,0,176,1.3,83,7,1174,"
    b"466|97|527B|01035DB4,0000,0001|0000|0000|019A|0981,00000001,,3,,,36,23*DC\r\n"
)


def _cmd():
    return GPRS(AAA).enclosed_data


def test_missing_attribute_raises():
    cmd = _cmd()
    assert not hasattr(cmd, "no_such_field")
    with pytest.raises(AttributeError):
        cmd.no_such_field  # noqa: B018


def test_dunder_and_unset_field_dict():
    cmd = TrackerCommand.__new__(TrackerCommand)
    with pytest.raises(AttributeError):
        cmd.field_dict  # noqa: B018
    with pytest.raises(AttributeError):
        cmd.__wrapped__  # noqa: B018


def test_copy_and_pickle_roundtrip():
    cmd = _cmd()
    assert copy.copy(cmd).latitude == cmd.latitude
    assert copy.deepcopy(cmd).field_dict == cmd.field_dict
    assert pickle.loads(pickle.dumps(cmd)).field_dict == cmd.field_dict


def test_aaa_properties():
    cmd = _cmd()
    assert cmd.lat == b"24.819116"
    assert cmd.lon == b"121.026091"
    assert cmd.speed == b"0"
    assert cmd.heading == b"176"
    assert cmd.event == b"35"
    assert cmd.date_time == cmd.field_dict["date_time"]
    assert cmd.imei is None


def test_aaa_properties_none_when_absent():
    cmd = TrackerCommand.__new__(TrackerCommand)
    cmd.field_dict = {}
    assert cmd.lat is None and cmd.lon is None and cmd.speed is None
    assert cmd.heading is None and cmd.event is None
    assert cmd.date_time is None and cmd.imei is None


def test_parse_data_payload_autodetect_c2s():
    explicit, left_e, _ = parse_data_payload(AAA, DIRECTION_CLIENT_TO_SERVER)
    auto, left_a, _ = parse_data_payload(AAA)
    assert len(auto) == len(explicit) == 1
    assert left_a == left_e


def test_parse_data_payload_autodetect_s2c():
    pkt = GPRS(AAA)
    pkt_bytes = b"@@" + AAA[2:]
    # prefix detection must select '@@'; frame may fail checksum but must not use '$$'
    auto = parse_data_payload(pkt_bytes)
    explicit = parse_data_payload(pkt_bytes, 0)
    assert len(auto[0]) == len(explicit[0])
    assert auto[1:] == explicit[1:]
    assert pkt is not None
