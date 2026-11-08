"""
Meitrack protocol parser library.
"""

from meitrack.gprs_protocol import GPRS, calc_signature, parse_data_payload

__version__ = "2.11.dev0"

__all__ = [
    "GPRS",
    "__version__",
    "calc_signature",
    "parse_data_payload",
]
