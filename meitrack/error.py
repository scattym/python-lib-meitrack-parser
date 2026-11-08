"""
Meitrack error class definitions
"""


class GPRSError(Exception):
    """
    Generic top level error. All others derived from this.
    """


class GPRSParseError(GPRSError):
    """
    Error class for issues in parsing gprs payloads
    """


class GPRSParameterError(GPRSError):
    """
    Error class for issues with parameters used to create gprs commands.
    """
