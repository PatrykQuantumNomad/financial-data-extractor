"""
Utility Module: JSON File Loader

This module provides a function to read JSON files and convert them to Python dictionaries.
Given the path to a JSON file, it returns the parsed content as a dictionary.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

import json
from pathlib import Path
from typing import Any

from app.core.exceptions.api_exceptions import (
    JSONFileError,
    JSONFileNotFoundError,
    JSONInvalidEncodingError,
    JSONInvalidError,
)

from ..utils.logger import AppLogger


def load_json_file(filename: str) -> dict[str, Any]:
    """
    Read a JSON file and load its data.

    If the filename is a relative path, it will be resolved relative to the backend
    directory (where this module's package is located). This ensures the file can
    be found regardless of the current working directory.

    Args:
        filename (str): The path to the JSON file. Can be absolute or relative.

    Returns:
        dict[str, Any]: The parsed JSON data.

    Raises:
        JSONFileNotFoundError: If the file is not found.
        JSONInvalidError: If the file content is not valid JSON.
        JSONInvalidEncodingError: If the file encoding is not UTF-8.
        JSONFileError: For other unexpected errors.
    """
    # Resolve relative paths relative to the backend directory
    file_path = Path(filename)
    if not file_path.is_absolute():
        # Get the backend directory (parent of app directory)
        backend_dir = Path(__file__).resolve().parent.parent.parent
        file_path = backend_dir / file_path

    try:
        with open(file_path, encoding="utf-8") as json_file:
            return json.load(json_file)
    except FileNotFoundError as fileexc:
        AppLogger.error(f"File not found: {file_path}")
        raise JSONFileNotFoundError(str(file_path)) from fileexc
    except json.JSONDecodeError as jsonexc:
        AppLogger.error(f"Invalid JSON in file: {file_path}. Error: {str(jsonexc)}")
        raise JSONInvalidError(str(file_path), str(jsonexc)) from jsonexc
    except UnicodeDecodeError as uniexc:
        AppLogger.error(f"Invalid encoding in file: {file_path}. Error: {str(uniexc)}")
        raise JSONInvalidEncodingError(str(file_path), str(uniexc)) from uniexc
    except Exception as exc:
        AppLogger.error(f"Unexpected error while reading '{file_path}': {str(exc)}")
        # Format the message string before passing to JSONFileError
        formatted_message = f"Unexpected error while reading '{file_path}': {str(exc)}"
        raise JSONFileError(formatted_message) from exc
