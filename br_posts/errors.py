class Error(Exception):
    """Base error class for br_posts module"""
    def __init__(self):
        self.message = ''

    def __str__(self):
        return self.message


class InvalidParameterError(Error):
    """
    Raised when the parameter passed is invalid.

    Attributes:
        parameter -- The invalid parameter
        message -- The message describing this error
    """

    def __init__(self, value, message):
        self.value = value
        self.message = message


class MissingParametersError(Error):
    """
    Raised when there are missing parameters

    Attributes:
        parameters -- A list with the name of the missing parameters
        message -- The message describing this error
    """

    def __init__(self, parameters, message):
        self.parameters = parameters
        self.message = message
