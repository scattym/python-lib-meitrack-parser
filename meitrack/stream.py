"""
Stateful stream parser for socket servers.
"""

from meitrack.common import (
    CLIENT_TO_SERVER_PREFIX,
    MAX_DATA_LENGTH,
    SERVER_TO_CLIENT_PREFIX,
)
from meitrack.error import GPRSParseError
from meitrack.gprs_protocol import _resolve_prefix, _scan_frames


class StreamParser:
    """
    Incremental GPRS framer: feed raw socket bytes, get complete packets back.

    Partial frames are buffered across calls. Corrupt frames (bad length field,
    length not ending in CRLF, oversized length, or a stalled partial frame that
    can never complete) are skipped by resyncing on the next start prefix.
    Framing is delegated to ``gprs_protocol._scan_frames``.
    """

    def __init__(self, direction=None, device_type=None):
        """
        :param direction: DIRECTION_* constant; auto-detected from the first
            prefix seen if None (then fixed for the life of the parser).
        :param device_type: Device type passed to each GPRS packet.
        """
        self._direction = direction
        self._prefix = (
            _resolve_prefix(b"", direction) if direction is not None else None
        )
        self._device_type = device_type
        self._buffer = b""
        self.discarded_bytes = 0

    @property
    def buffered(self):
        """Number of bytes held waiting for the rest of a frame."""
        return len(self._buffer)

    def reset(self):
        """Drop any buffered data."""
        self._buffer = b""

    def feed(self, data):
        """
        Add *data* and return all newly completed packets (possibly empty).
        """
        buf = self._buffer + data if self._buffer else bytes(data)
        if self._prefix is None:
            if (
                CLIENT_TO_SERVER_PREFIX not in buf
                and SERVER_TO_CLIENT_PREFIX not in buf
            ):
                # Direction unknown until a full prefix arrives; keep a possible
                # trailing half-prefix, drop the rest as noise.
                keep = buf[-1:] if buf[-1:] in (b"$", b"@") else b""
                self.discarded_bytes += len(buf) - len(keep)
                self._buffer = keep
                return []
            self._prefix = _resolve_prefix(buf, None)
        prefix = self._prefix
        packets = []
        while buf:
            state = {"pos": 0, "before": b""}
            try:
                leftover = _scan_frames(buf, prefix, self._device_type, packets, state)
            except GPRSParseError:
                # Skip one byte past the bad frame start and look for the next one.
                skip = state["pos"] + 1
                self.discarded_bytes += skip
                buf = buf[skip:]
                continue
            self.discarded_bytes += len(state["before"])
            if leftover and self._is_unrecoverable(leftover, prefix):
                self.discarded_bytes += 1
                buf = leftover[1:]
                continue
            buf = self._trim(leftover, prefix)
            break
        self._buffer = buf
        return packets

    @staticmethod
    def _is_unrecoverable(leftover, prefix):
        """True if leftover starts with a prefix but can never become a frame."""
        if not leftover.startswith(prefix):
            return False
        comma = leftover.find(b",")
        if comma < 0:
            return len(leftover) > MAX_DATA_LENGTH
        try:
            return int(leftover[3:comma]) <= 0
        except ValueError:
            return True

    def _trim(self, leftover, prefix):
        """Discard leading garbage when no prefix is present in the leftover."""
        if leftover.startswith(prefix):
            return leftover
        # No complete prefix: keep only a trailing partial prefix byte, if any.
        keep = leftover[-(len(prefix) - 1) :] if len(prefix) > 1 else b""
        if keep and prefix.startswith(keep):
            self.discarded_bytes += len(leftover) - len(keep)
            return keep
        self.discarded_bytes += len(leftover)
        return b""
