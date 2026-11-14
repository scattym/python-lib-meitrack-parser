"""
Unit tests for AAA (Automatic Event Report / Location Telemetry) command.
Covers events 35, 37, 39, 50, 51, 109, model variations, and field extractions.
"""

import datetime

import pytest

from meitrack.command.command_AAA import TrackerCommand
from meitrack.command.common import TaxiMeterData
from meitrack.common import DIRECTION_CLIENT_TO_SERVER
from meitrack.error import GPRSParseError
from meitrack.gprs_protocol import GPRS


def test_aaa_standard_event_35():
    raw_packet = (
        b"$$D160,864507032228727,AAA,35,24.819116,121.026091,180323023615,A,7,16,0,176,1.3,83,7,1174,"
        b"466|97|527B|01035DB4,0000,0001|0000|0000|019A|0981,00000001,,3,,,36,23*DC\r\n"
    )
    gprs = GPRS(raw_packet)
    cmd = gprs.enclosed_data

    assert isinstance(cmd, TrackerCommand)
    assert cmd.command == b"AAA"
    assert cmd.event_code == b"35"
    assert cmd.latitude == b"24.819116"
    assert cmd.longitude == b"121.026091"
    assert cmd.pos_status == b"A"
    assert cmd.num_sats == b"7"
    assert cmd.gsm_signal_strength == b"16"
    assert cmd.speed == b"0"
    assert cmd["direction"] == b"176"
    assert cmd.horizontal_accuracy == b"1.3"
    assert cmd.altitude == b"83"
    assert cmd.mileage == b"7"
    assert cmd.run_time == b"1174"
    assert cmd.base_station_info == b"466|97|527B|01035DB4"
    assert cmd.io_port_status == b"0000"
    assert cmd.analog_input_value == b"0001|0000|0000|019A|0981"

    # Datetime parsed as datetime object
    assert isinstance(cmd.date_time, datetime.datetime)
    assert cmd.date_time.year == 2018
    assert cmd.date_time.month == 3
    assert cmd.date_time.day == 23

    # GSM / Base station info helper
    bs_info = cmd.get_base_station_info()
    assert bs_info is not None
    assert bs_info["mcc"] == b"466"
    assert bs_info["mnc"] == b"97"
    assert bs_info["lac"] == str(int("527B", 16)).encode()
    assert bs_info["ci"] == str(int("01035DB4", 16)).encode()
    assert bs_info["gsm_signal_strength"] == b"16"

    # Event ID and Name
    assert cmd.get_event_id() == 35
    assert cmd.get_event_name() == "Track By Time Interval"


def test_aaa_rfid_event_37():
    # Event 37 contains 'rfid' at field index 17
    raw_packet = (
        b"$$K170,864507032323403,AAA,37,-33.815803,151.200066,180707113006,A,10,13,0,60,0.9,83,63610,943694,"
        b"505|3|00FA|04E381F5,0500,0000|0000|0000|0189|0576,0102030405,,108,0000,,3,0,,0|0000|0000|0000|0000|0000*8A\r\n"
    )
    gprs = GPRS(raw_packet)
    cmd = gprs.enclosed_data

    assert isinstance(cmd, TrackerCommand)
    assert cmd.event_code == b"37"
    assert cmd.rfid == b"0102030405"
    assert cmd["rfid"] == b"0102030405"

    license_val = cmd.get_license_data()
    assert license_val is not None


def test_aaa_photo_event_39():
    # Event 39 contains 'file_name' at field index 17
    raw_packet = (
        b"$$K180,864507032323403,AAA,39,-33.815803,151.200066,180707113006,A,10,13,0,60,0.9,83,63610,943694,"
        b"505|3|00FA|04E381F5,0500,0000|0000|0000|0189|0576,180427100921_C1E1_N2U1D1.jpg,,108,0000,,3,0,,0|0000|0000|0000|0000|0000*8A\r\n"
    )
    gprs = GPRS(raw_packet)
    cmd = gprs.enclosed_data

    assert isinstance(cmd, TrackerCommand)
    assert cmd.event_code == b"39"
    assert cmd.file_name == b"180427100921_C1E1_N2U1D1.jpg"
    assert cmd["file_name"] == b"180427100921_C1E1_N2U1D1.jpg"


def test_aaa_temp_sensors_event_50_and_51():
    # Event 50 / 51 contains 'temperature_sensor_number' at field index 18
    raw_packet_50 = (
        b"$$K180,864507032323403,AAA,50,-33.815803,151.200066,180707113006,A,10,13,0,60,0.9,83,63610,943694,"
        b"505|3|00FA|04E381F5,0500,0000|0000|0000|0189|0576,info,01,,108,0000,,3,0,,0|0000|0000|0000|0000|0000*8A\r\n"
    )
    gprs_50 = GPRS(raw_packet_50)
    cmd_50 = gprs_50.enclosed_data

    assert isinstance(cmd_50, TrackerCommand)
    assert cmd_50.event_code == b"50"
    assert cmd_50.assisted_event_info == b"info"
    assert cmd_50.temperature_sensor_number == b"01"

    # Event 51
    raw_packet_51 = (
        b"$$K180,864507032323403,AAA,51,-33.815803,151.200066,180707113006,A,10,13,0,60,0.9,83,63610,943694,"
        b"505|3|00FA|04E381F5,0500,0000|0000|0000|0189|0576,info,02,,108,0000,,3,0,,0|0000|0000|0000|0000|0000*8A\r\n"
    )
    gprs_51 = GPRS(raw_packet_51)
    cmd_51 = gprs_51.enclosed_data
    assert cmd_51.event_code == b"51"
    assert cmd_51.temperature_sensor_number == b"02"


def test_aaa_taxi_meter_event_109():
    raw_packet = (
        b"$$J244,864507032323403,AAA,109,-33.815803,151.200066,180707113006,A,10,13,0,60,0.9,83,63610,943694,"
        b"505|3|00FA|04E381F5,0500,0000|0000|0000|0189|0576,,,108,0000,,6,0,,0|0000|0000|0000|0000|0000,,,"
        b"21|180622110810|180622113010|1000|6000|002200|000500*1B\r\n"
    )
    gprs = GPRS(raw_packet)
    cmd = gprs.enclosed_data

    assert isinstance(cmd, TrackerCommand)
    assert cmd.event_code == b"109"
    assert (
        cmd.taxi_meter_data == b"21|180622110810|180622113010|1000|6000|002200|000500"
    )

    taxi_data = cmd.get_taxi_meter_data()
    assert isinstance(taxi_data, TaxiMeterData)
    assert taxi_data.assisted_info == b"21"
    assert taxi_data.start_time == b"180622110810"
    assert taxi_data.end_time == b"180622113010"
    assert taxi_data.fare_distance == b"1000"
    assert taxi_data.fare_price == b"6000"
    assert taxi_data.fare_trip_time == b"002200"
    assert taxi_data.fare_waiting_time == b"000500"

    # TaxiMeterData helper methods
    start_dt = taxi_data.get_start_time()
    assert isinstance(start_dt, datetime.datetime)
    assert start_dt.year == 2018
    assert start_dt.month == 6
    assert start_dt.day == 22

    end_dt = taxi_data.get_end_time()
    assert isinstance(end_dt, datetime.datetime)
    assert end_dt.minute == 30

    assert taxi_data.get_fare_distance() == "1000"
    assert taxi_data.get_fare_price() == "6000"
    assert taxi_data.get_fare_trip_time() == "00:22:00"
    assert taxi_data.get_fare_waiting_time() == "00:05:00"


def test_taxi_meter_partial_payload():
    # Only start time given (e.g. meter just started)
    partial_payload = b"01|180622110810"
    taxi = TaxiMeterData(partial_payload)
    assert taxi.assisted_info == b"01"
    assert taxi.start_time == b"180622110810"
    assert taxi.get_end_time() is None
    assert taxi.get_fare_distance() is None
    assert taxi.get_fare_price() is None
    assert taxi.get_fare_trip_time() is None
    assert taxi.get_fare_waiting_time() is None


def test_aaa_model_variations_event_maps():
    # Event 2 on T366 is "Engine On"
    cmd_t366 = TrackerCommand(
        DIRECTION_CLIENT_TO_SERVER, b"AAA,2,0,0,180101000000,A", device_type="T366G"
    )
    assert cmd_t366.get_event_name() == "Engine On"

    # Event 35 on T333 is "Track By Time Interval"
    cmd_t333 = TrackerCommand(
        DIRECTION_CLIENT_TO_SERVER, b"AAA,35,0,0,180101000000,A", device_type="T333"
    )
    assert cmd_t333.get_event_name() == "Track By Time Interval"

    # Unknown event code
    cmd_unknown = TrackerCommand(
        DIRECTION_CLIENT_TO_SERVER, b"AAA,999,0,0,180101000000,A", device_type="T333"
    )
    assert cmd_unknown.get_event_name() is None


def test_aaa_parse_errors():
    # Less than 2 fields raises GPRSParseError
    with pytest.raises(
        GPRSParseError, match="Field length does not include event code"
    ):
        TrackerCommand(DIRECTION_CLIENT_TO_SERVER, b"AAA")

    # Too many fields raises GPRSParseError
    too_many_fields = b"AAA,35," + b",".join([b"val"] * 50)
    with pytest.raises(GPRSParseError, match="Incorrect number of fields"):
        TrackerCommand(DIRECTION_CLIENT_TO_SERVER, too_many_fields)


def test_aaa_parsed_objects_do_not_share_mutable_state():
    raw = (
        b"$$D160,864507032228727,AAA,35,24.819116,121.026091,180323023615,A,7,16,0,176,1.3,83,7,1174,"
        b"466|97|527B|01035DB4,0000,0001|0000|0000|019A|0981,00000001,,3,,,36,23*DC\r\n"
    )
    a = GPRS(raw).enclosed_data
    b = GPRS(raw).enclosed_data
    assert a is not b
    a.latitude = b"0"
    assert b.latitude == b"24.819116"
    # parsing must not mutate the shared class-level field list
    assert TrackerCommand.field_names[0] == "command"
    assert a.field_name_selector == b.field_name_selector
