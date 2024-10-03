from datetime import date
from typing import Optional

from sqlmodel import Field

from src.models.timestamp_mixin import TimestampMixin


class Content(TimestampMixin, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    budget: float = Field(default=0.0)
    revenue: float = Field(default=0.0)
    runtime: int = Field(default=0)
    status: Optional[str] = Field(default="NA")

    homepage: Optional[str] = Field(default=None)
    original_language: Optional[str] = Field(default="NA")
    original_title: str
    title: str
    overview: Optional[str] = Field(default=None)
    # cast date string in yyyy-mm-dd format to date
    release_date: date
    vote_average: float = Field(default=0.0)
    vote_count: int = Field(default=0)
    production_company_id: int
    genre_id: int
    is_deleted: bool = False
