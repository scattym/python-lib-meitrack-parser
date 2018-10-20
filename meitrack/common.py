
SERVER_TO_CLIENT_PREFIX = b'@@'
CLIENT_TO_SERVER_PREFIX = b'$$'
END_OF_MESSAGE_STRING = b'\r\n'

DIRECTION_SERVER_TO_CLIENT = 0
DIRECTION_CLIENT_TO_SERVER = 1

MAX_DATA_LENGTH = 2048

def s2b(value):
    """
    convert string or integer to byte array representation

    original value returned if conversion fails so should be safe to pass all
    values into this function
    :param value: (str|int|bytes) The input value
    :return: The byte array converted value
    >>> s2b('test')
    b'test'
    >>> s2b(b'test')
    b'test'
    >>> s2b(1)
    b'1'
    """
    try:
        if isinstance(value, int):
            return str(value).encode()
        return value.encode()
    except AttributeError as _:
        return value


def b2s(value):
    """
    convert byte array to a string representation

    original value returned if conversion fails so should be safe to pass all
    values into this function
    :param value: (str|int|bytes) The input value
    :return: The byte array converted value
    >>> b2s('test')
    'test'
    >>> b2s(b'test')
    'test'
    """
    try:
        return value.decode()
    except AttributeError as _:
        return value