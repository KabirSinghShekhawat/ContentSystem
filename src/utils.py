from datetime import date, datetime


def yyyy_mm_dd(date_str: str) -> date:
    return datetime.strptime(date_str, "%Y-%m-%d")
