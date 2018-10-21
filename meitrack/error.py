"""
Meitrack error class definitions
"""

class GPRSError(Exception):
    """
    Generic top level error. All others derived from this.
    """
    pass


class GPRSParseError(GPRSError):
    """
    Error class for issues in parsing gprs payloads
    """
    pass


class GPRSParameterError(GPRSError):
    """
    Error class for issues with parameters used to create gprs commands.
    """
    pass
