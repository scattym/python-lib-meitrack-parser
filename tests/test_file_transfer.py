"""
Unit tests for D00 (File Download) and D01 (File Listing) commands,
aggregators, and file management workflows.
"""
import datetime

import pytest

from meitrack.build_message import (
    cts_build_file_list,
    stc_request_delete_file,
    stc_request_get_file,
    stc_request_photo_list,
)
from meitrack.command import (
    stc_request_file_download,
)
from meitrack.command import (
    stc_request_photo_list as stc_cmd_photo_list,
)
from meitrack.command.command_D00 import FileDownloadCommand
from meitrack.command.command_D01 import FileListCommand
from meitrack.common import DIRECTION_CLIENT_TO_SERVER, DIRECTION_SERVER_TO_CLIENT
from meitrack.file_download import (
    FileDownload,
    FileDownloadAggregator,
    to_bytes,
)
from meitrack.file_list import FileListing, FileListingError
from meitrack.gprs_protocol import GPRS


def test_command_d00_request():
    cmd = FileDownloadCommand(
        DIRECTION_SERVER_TO_CLIENT,
        b"D00,180428115949_C1E11_N1U1D1.jpg,0"
    )
    assert isinstance(cmd, FileDownloadCommand)
    assert cmd.direction == DIRECTION_SERVER_TO_CLIENT
    assert cmd.file_name == b"180428115949_C1E11_N1U1D1.jpg"
    assert cmd.data_packet_start_number == b"0"
    assert cmd.as_bytes() == b"D00,180428115949_C1E11_N1U1D1.jpg,0"

    # stc_request_file_download returns Command
    cmd_factory = stc_request_file_download(b"180428115949_C1E11_N1U1D1.jpg", 0)
    assert cmd_factory.as_bytes() == b"D00,180428115949_C1E11_N1U1D1.jpg,0"


def test_command_d00_response_and_date_parsing():
    raw_payload = b"D00,180428115949_C1E11_N1U1D1.jpg,2,0,RAW_IMAGE_BYTES_PART1"
    cmd = FileDownloadCommand(DIRECTION_CLIENT_TO_SERVER, raw_payload)

    assert cmd.command == b"D00"
    assert cmd.file_name == b"180428115949_C1E11_N1U1D1.jpg"
    assert cmd.number_of_data_packets == b"2"
    assert cmd.data_packet_number == b"0"
    assert cmd.file_bytes == b"RAW_IMAGE_BYTES_PART1"

    # Datetime parsed from the filename (180428115949 -> 2018-04-28 11:59:49)
    dt = cmd.field_dict["date_time"]
    assert isinstance(dt, datetime.datetime)
    assert dt.year == 2018
    assert dt.month == 4
    assert dt.day == 28
    assert dt.hour == 11
    assert dt.minute == 59
    assert dt.second == 49

    fn, num_pkts, pkt_num, data = cmd.get_file_data()
    assert fn == b"180428115949_C1E11_N1U1D1.jpg"
    assert num_pkts == b"2"
    assert pkt_num == b"0"
    assert data == b"RAW_IMAGE_BYTES_PART1"


def test_command_d00_build():
    cmd = FileDownloadCommand(DIRECTION_CLIENT_TO_SERVER)
    cmd.build(b"sample.jpg", b"1", b"0", b"DATA")
    assert cmd.as_bytes() == b"D00,sample.jpg,1,0,DATA"


def test_command_d01_request_and_response():
    # Request
    req = FileListCommand(DIRECTION_SERVER_TO_CLIENT, b"D01,0")
    assert isinstance(req, FileListCommand)
    assert req.direction == DIRECTION_SERVER_TO_CLIENT
    assert req.as_bytes() == b"D01,0"

    # Command factory helper
    req_factory = stc_cmd_photo_list(0)
    assert req_factory.as_bytes() == b"D01,0"

    # Response
    res_payload = b"D01,2,0,photo1.jpg|photo2.jpg"
    res = FileListCommand(DIRECTION_CLIENT_TO_SERVER, res_payload)
    assert res.command == b"D01"
    assert res.number_of_data_packets == b"2"
    assert res.data_packet_number == b"0"
    assert res.file_list == b"photo1.jpg|photo2.jpg"

    num_pkts, pkt_num, fl = res.get_file_list()
    assert num_pkts == b"2"
    assert pkt_num == b"0"
    assert fl == b"photo1.jpg|photo2.jpg"


def test_file_download_class():
    fd = FileDownload(b"image.jpg")
    assert fd.file_name == b"image.jpg"
    assert fd.next_packet() == 0
    assert fd.is_complete() is False

    # Add packet 0 of 2
    fd.add_file_bytes(b"image.jpg", b"2", b"0", b"CHUNK_0_")
    assert fd.next_packet() == 1
    assert fd.is_complete() is False

    # Add packet 1 of 2
    fd.add_file_bytes(b"image.jpg", b"2", b"1", b"CHUNK_1")
    assert fd.is_complete() is True
    assert fd.return_file_contents() == b"CHUNK_0_CHUNK_1"

    # Mismatched file name ignored
    fd.add_file_bytes(b"other.jpg", b"2", b"0", b"OTHER")
    assert "other.jpg" not in str(fd)


def test_file_download_aggregator():
    agg = FileDownloadAggregator()
    imei = b"353358017784062"
    file_name = b"test.jpg"

    # Packet 0 of 2
    fn, content = agg.add_file_bytes(imei, file_name, b"2", b"0", b"HELLO ")
    assert fn == file_name
    assert content is None  # Not complete yet

    # Packet 1 of 2
    fn, content = agg.add_file_bytes(imei, file_name, b"2", b"1", b"WORLD")
    assert fn == file_name
    assert content == b"HELLO WORLD"

    # Str representation
    assert isinstance(str(agg), str)


def test_to_bytes_helper():
    assert to_bytes(b"already_bytes") == b"already_bytes"
    assert to_bytes("string") == b"string"
    assert to_bytes(123) == b"123"


def test_file_listing():
    fl = FileListing()
    fl.add_item("file1.jpg")
    assert fl.num_files == 1
    # Adding duplicate
    fl.add_item("file1.jpg")
    assert fl.num_files == 1

    fl.add_item("file2.jpg")
    assert fl.num_files == 2

    fl.remove_item("file1.jpg")
    assert fl.num_files == 1
    assert fl.file_arr == ["file2.jpg"]

    fl.clear_list()
    assert len(fl.file_arr) == 0


def test_file_listing_packet_aggregation():
    fl = FileListing()
    imei = b"864507032323403"

    # Packet 0 of 2 (pipe terminated)
    pkt0 = GPRS(b"$$A35," + imei + b",D01,2,0,f1.jpg|f2.jpg|*AA\r\n")
    count, num = fl.add_packet(pkt0)
    assert count == 2
    assert num == 0
    assert fl.is_complete() is False

    # Packet 1 of 2
    pkt1 = GPRS(b"$$A35," + imei + b",D01,2,1,f3.jpg|f4.jpg|*AA\r\n")
    count, num = fl.add_packet(pkt1)
    assert count == 2
    assert num == 1
    # Completing resets internal state and populates file_arr
    assert b"f1.jpg" in fl.file_arr
    assert b"f2.jpg" in fl.file_arr
    assert b"f3.jpg" in fl.file_arr
    assert b"f4.jpg" in fl.file_arr


def test_file_listing_errors():
    fl = FileListing()
    imei = b"864507032323403"

    pkt_bad = GPRS(b"$$A35," + imei + b",D00,f.jpg,1,0,bytes*AA\r\n")
    # Not D01
    c, n = fl.add_packet(pkt_bad)
    assert c is None and n is None

    # Mismatched total packets count raises FileListingError
    pkt0 = GPRS(b"$$A35," + imei + b",D01,2,0,f1.jpg*AA\r\n")
    fl.add_packet(pkt0)
    pkt_mismatch = GPRS(b"$$A35," + imei + b",D01,3,1,f2.jpg*AA\r\n")
    with pytest.raises(FileListingError, match="Max packet count has changed"):
        fl.add_packet(pkt_mismatch)


def test_build_message_file_helpers():
    imei = b"0407"
    del_gprs = stc_request_delete_file(imei, b"test.jpg")
    assert del_gprs.direction == b"@@"
    assert b"D02,test.jpg" in del_gprs.as_bytes()

    list_req = stc_request_photo_list(imei, 0)
    assert list_req.direction == b"@@"
    assert b"D01,0" in list_req.as_bytes()

    dl_req = stc_request_get_file(imei, b"pic.jpg", 0)
    assert dl_req.direction == b"@@"
    assert b"D00,pic.jpg,0" in dl_req.as_bytes()

    cts_list = cts_build_file_list(imei, b"filename", 1024)
    assert len(cts_list) == 1
    assert cts_list[0].direction == b"$$"
    assert b"D00,filename,1,0,1024" in cts_list[0].as_bytes()
