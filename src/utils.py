from datetime import date, datetime


def parse_date(date_str: str) -> date:
    """Parse a date string in the format YYYY-MM-DD to a date object."""

    return datetime.strptime(date_str, "%Y-%m-%d")
