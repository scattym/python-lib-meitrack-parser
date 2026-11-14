"""CommandBuilder must match build_message output byte-for-byte."""

import pytest

from meitrack import CommandBuilder
from meitrack import build_message as bm


def test_request_location():
    b = CommandBuilder(b"0407", data_identifier=b"c")
    assert (
        b.request_location().as_bytes()
        == bm.stc_request_location_message(b"0407").as_bytes()
    )


def test_delete_file():
    b = CommandBuilder(b"0407")
    assert (
        b.delete_file(b"test.file").as_bytes()
        == bm.stc_request_delete_file(b"0407", b"test.file").as_bytes()
    )


def test_format_sdcard():
    b = CommandBuilder(b"0407").with_data_identifier(b"u")
    assert (
        b.format_sdcard().as_bytes() == bm.stc_request_format_sdcard(b"0407").as_bytes()
    )


@pytest.mark.parametrize("args", [(), (2,), (2, 3), (2, 3, 1)])
def test_set_output_pin(args):
    b = CommandBuilder(b"0407", data_identifier=b"b")
    assert (
        b.set_output_pin(*args).as_bytes()
        == bm.stc_set_output_pin(b"0407", *args).as_bytes()
    )


def test_set_output_pin_bad_pin():
    assert CommandBuilder(b"0407").set_output_pin(2, 255, 1) is None


def test_restart_and_interval():
    b = CommandBuilder(b"0407", data_identifier=b"q")
    assert b.restart_gsm().as_bytes() == bm.stc_restart_gsm(b"0407").as_bytes()
    b.with_data_identifier(b"r")
    assert b.restart_gps().as_bytes() == bm.stc_restart_gps(b"0407").as_bytes()
    b.with_data_identifier(b"p")
    assert (
        b.set_tracking_by_time_interval(10).as_bytes()
        == bm.stc_set_tracking_by_time_interval(b"0407", 10).as_bytes()
    )


def test_chaining_and_str_imei():
    b = CommandBuilder(b"x").with_imei("0407").with_direction(b"$$")
    assert b.request_location().as_bytes().startswith(b"$$a")
