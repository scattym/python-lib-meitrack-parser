"""Fluent builder for Meitrack GPRS command messages."""

from __future__ import annotations

from meitrack import command
from meitrack.common import s2b
from meitrack.gprs_protocol import GPRS


class CommandBuilder:
    """Build GPRS command envelopes for one device.

    Design: configuration methods (``with_imei``, ``with_direction``,
    ``with_data_identifier``) return ``self`` for chaining; command methods
    are terminal and return a new :class:`GPRS` object (call ``.as_bytes()``).
    The data identifier is taken from the builder, not per command, so the
    legacy functions in ``meitrack.build_message`` (which hard-code an
    identifier per command) match only when the same identifier is set.
    """

    def __init__(self, imei, direction=b"@@", data_identifier=b"a"):
        self.imei = imei
        self.direction = direction
        self.data_identifier = data_identifier

    def with_imei(self, imei) -> CommandBuilder:
        """Set the IMEI; returns ``self``."""
        self.imei = imei
        return self

    def with_direction(self, direction: bytes) -> CommandBuilder:
        """Set the direction marker; returns ``self``."""
        self.direction = direction
        return self

    def with_data_identifier(self, data_identifier: bytes) -> CommandBuilder:
        """Set the data identifier; returns ``self``."""
        self.data_identifier = data_identifier
        return self

    def _wrap(self, enclosed_data) -> GPRS:
        gprs = GPRS()
        gprs.direction = self.direction
        gprs.data_identifier = self.data_identifier
        gprs.enclosed_data = enclosed_data
        gprs.imei = s2b(self.imei)
        return gprs

    def request_location(self) -> GPRS:
        """Return a request-location (A10) message."""
        return self._wrap(command.stc_request_location())

    def delete_file(self, file_name) -> GPRS:
        """Return a delete-file (D02) message."""
        return self._wrap(command.stc_file_delete(file_name))

    def format_sdcard(self) -> GPRS:
        """Return a format-SD-card (DB3) message."""
        return self._wrap(command.stc_format_sdcard())

    def restart_gsm(self) -> GPRS:
        """Return a restart-GSM message."""
        return self._wrap(command.stc_restart_gsm())

    def restart_gps(self) -> GPRS:
        """Return a restart-GPS message."""
        return self._wrap(command.stc_restart_gps())

    def set_tracking_by_time_interval(self, deci_seconds=0) -> GPRS:
        """Return a set-tracking-interval message."""
        return self._wrap(command.stc_set_tracking_by_time_interval(deci_seconds))

    def set_output_pin(self, speed=1, pin=0, state=2) -> GPRS | None:
        """Return a set-output-pin message, or ``None`` if ``pin`` is out of range
        (same behaviour as ``build_message.stc_set_output_pin``)."""
        pins = [2, 2, 2, 2, 2]
        try:
            pins[pin] = state
        except IndexError:
            return None
        return self._wrap(command.stc_set_output_pin(speed, *pins))
