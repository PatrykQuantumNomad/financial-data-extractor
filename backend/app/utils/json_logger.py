"""
Json Formatter Module.

This module provides a custom JSON formatter for logging which
excludes specific fields from the output.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

from pythonjsonlogger import jsonlogger


class JsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter for logging.

    The purpose of this formatter is to filter out specific fields
    from the log records before they are outputted as JSON.

    Attributes:
        reserved_attrs (List[str]): A list of attributes that are reserved and
                                    will be excluded from the final log output.

    Args:
        args (Tuple[Any]): Variable length argument list.
        kwargs (dict[str, Any]): Arbitrary keyword arguments.

    Usage:
        formatter = JsonFormatter(fmt="%(asctime)s %(levelname)s %(message)s")

    Notes:
        Extend or modify the reserved_attrs list to exclude more fields.
    """

    def __init__(self, *args, **kwargs):
        kwargs["reserved_attrs"] = ["color_message", *jsonlogger.RESERVED_ATTRS]
        super().__init__(*args, **kwargs)
