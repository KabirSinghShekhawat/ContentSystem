from datetime import date, datetime
import iso639


def parse_date(date_str: str) -> date:
    """Parse a date string in the format YYYY-MM-DD to a date object."""

    return datetime.strptime(date_str, "%Y-%m-%d")


class LanguageHandler:
    @staticmethod
    def normalize_language(language: str) -> str:
        """
        Normalize language names to ISO 639-1 codes
        Returns original language if no match found
        """
        assert language is not None, "Language cannot be None"
        assert len(language) > 0, "Language cannot be empty"

        try:
            lang = iso639.find(language)
            return lang.part1
        except (iso639.LanguageNotFoundError, AttributeError):
            return language

    @staticmethod
    def denormalize_language(code: str) -> str:
        """
        Convert ISO 639-1 codes back to full names
        Returns original code if no match found
        """
        try:
            lang = iso639.find(code)
            return lang.name
        except iso639.LanguageNotFoundError:
            return code


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


def parse_and_convert_languages(language_list_str: str):
    """Parse the language list string and convert each language to its ISO 639-1 code.

    Args:
        language_list_str (str): A string containing a list of languages. Example: "['English', 'Français']"

    Returns:
        list: List of ISO 639-1 codes for each language in the input string.
    """
    languages = parse_languages(language_list_str)
    # Convert each language to its code
    codes = [LanguageHandler.normalize_language(lang) for lang in languages]
    return codes
