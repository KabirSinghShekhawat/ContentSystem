from datetime import date, datetime
from fastapi import UploadFile, HTTPException


def parse_date(date_str: str) -> date:
    """Parse a date string in the format YYYY-MM-DD to a date object."""

    return datetime.strptime(date_str, "%Y-%m-%d")


def parse_languages(language_list_str: str):
    """Parse the language list string and convert to a list of languages.

    Args:
        language_list_str (str): A string containing a list of languages. Example: "['English', 'Français']"

    Returns:
        list (str): List of languages.
    """
    languages = language_list_str.strip("[]").replace("'", "").split(", ")
    # filter out certain values from languages
    languages = [
        lang
        for lang in languages
        if lang not in ("", "No Language") and "?" not in lang
    ]
    return languages


def validate_csv_file(file: UploadFile) -> bool:
    """Validate the file type and raise an exception if it is not a CSV file."""

    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Invalid file type",
                "message": "Only CSV files are allowed",
            },
        )
    return True
