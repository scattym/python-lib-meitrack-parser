"""Tests for the stateful StreamParser."""

from meitrack import StreamParser, parse_data_payload
from meitrack.common import DIRECTION_CLIENT_TO_SERVER

PKT1 = b"$$S28,353358017784062,A11,OK*FE\r\n"
PKT2 = (
    b"$$Q128,353358017784062,AAA,34,22.543176,114.078448,100313093738,A,5,22,2,205,"
    b"5,-14,0,60,0|0|10133|4110,0000,149|153|173|2707|914,*91\r\n"
)
STREAM = PKT1 + PKT2 + PKT1


def _payloads(packets):
    return [p.payload for p in packets]


def test_whole_buffer_matches_parse_data_payload():
    expected, _, _ = parse_data_payload(STREAM, DIRECTION_CLIENT_TO_SERVER)
    sp = StreamParser()
    assert _payloads(sp.feed(STREAM)) == _payloads(expected)
    assert sp.buffered == 0


def test_byte_at_a_time_equals_whole_buffer():
    expected, _, _ = parse_data_payload(STREAM, DIRECTION_CLIENT_TO_SERVER)
    sp = StreamParser()
    got = []
    for i in range(len(STREAM)):
        got += sp.feed(STREAM[i : i + 1])
    assert _payloads(got) == _payloads(expected)
    assert len(got) == 3
    assert sp.buffered == 0


def test_split_at_every_boundary():
    expected, _, _ = parse_data_payload(STREAM, DIRECTION_CLIENT_TO_SERVER)
    for cut in range(len(STREAM) + 1):
        sp = StreamParser()
        got = sp.feed(STREAM[:cut]) + sp.feed(STREAM[cut:])
        assert _payloads(got) == _payloads(expected), cut
        assert sp.buffered == 0, cut


def test_buffered_length_reports_partial_frame():
    sp = StreamParser()
    assert sp.feed(PKT1[:10]) == []
    assert sp.buffered == 10
    assert len(sp.feed(PKT1[10:])) == 1
    assert sp.buffered == 0
    sp.feed(PKT1[:5])
    sp.reset()
    assert sp.buffered == 0


def test_garbage_prefix_and_suffix():
    sp = StreamParser()
    got = sp.feed(b"\x00\xffNOISE" + PKT1 + b"trailing junk")
    assert len(got) == 1
    assert sp.buffered == 0
    assert sp.discarded_bytes > 0
    # A suffix that starts a real frame is retained.
    assert sp.feed(PKT2[:20]) == []
    assert sp.buffered == 20
    assert len(sp.feed(PKT2[20:])) == 1


def test_garbage_between_frames_and_partial_prefix_kept():
    sp = StreamParser(direction=DIRECTION_CLIENT_TO_SERVER)
    got = sp.feed(PKT1 + b"xx" + PKT2 + b"$")
    assert len(got) == 2
    assert sp.buffered == 1
    assert len(sp.feed(PKT1[1:])) == 1


def test_corrupt_length_then_recovers():
    bad = b"$$SINVALID,353358017784062,A11,OK*FE\r\n"
    sp = StreamParser()
    got = sp.feed(bad + PKT1)
    assert _payloads(got) == [PKT1]
    assert sp.buffered == 0


def test_bad_terminator_recovers_and_keeps_earlier_packets():
    bad = b"$$S10,123456789012345,A11,OK*FE\r\n"
    sp = StreamParser()
    got = sp.feed(PKT1 + bad + PKT2)
    assert _payloads(got) == [PKT1, PKT2]
    assert sp.buffered == 0


def test_oversized_length_recovers():
    bad = b"$$A99999,353358017784062,A11,OK*FE\r\n"
    sp = StreamParser()
    assert _payloads(sp.feed(bad + PKT1)) == [PKT1]


def test_corrupted_checksum_still_yields_following_packets():
    bad_sum = PKT1.replace(b"*FE", b"*00")
    sp = StreamParser()
    got = sp.feed(bad_sum + PKT2)
    assert len(got) == 2
    assert got[1].payload == PKT2


def test_corrupt_data_split_across_feeds():
    bad = b"$$S10,123456789012345,A11,OK*FE\r\n"
    sp = StreamParser()
    got = []
    data = bad + PKT1
    for i in range(0, len(data), 7):
        got += sp.feed(data[i : i + 7])
    assert _payloads(got) == [PKT1]


def test_downlink_autodetect():
    pkt = b"@@Q25,353358017784062,A10*6A\r\n"
    sp = StreamParser()
    assert _payloads(sp.feed(pkt[:7]) + sp.feed(pkt[7:])) == [pkt]
