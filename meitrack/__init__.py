"""
Meitrack protocol parser library.
"""

from meitrack.gprs_protocol import GPRS, calc_signature, parse_data_payload
from meitrack.stream import StreamParser

__version__ = "2.11.dev0"

__all__ = [
    "GPRS",
    "StreamParser",
    "__version__",
    "calc_signature",
    "parse_data_payload",
]
