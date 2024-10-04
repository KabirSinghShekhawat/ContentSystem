from datetime import date, datetime
from typing import Optional

from pydantic import field_serializer
from sqlmodel import Field, SQLModel

from src.models.timestamp_mixin import TimestampMixin


class ContentLanguage(SQLModel, table=True):
    content_id: Optional[int] = Field(default=None, primary_key=True)
    language_id: Optional[int] = Field(default=None, primary_key=True)


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
    languages: Optional[str] = Field(default="[]")
    overview: Optional[str] = Field(default=None)
    # cast date string in yyyy-mm-dd format to date
    release_date: date
    vote_average: float = Field(default=0.0)
    vote_count: int = Field(default=0)
    production_company_id: int
    genre_id: int
    is_deleted: bool = False

    @field_serializer("release_date", check_fields=False)
    def serialize_date(self, dt: Optional[date]) -> Optional[str]:
        if dt is None:
            return None
        return dt.strftime("%Y-%m-%d")

    @field_serializer("created_at", "updated_at", check_fields=False)
    def serialize_datetime(self, dt: Optional[datetime]) -> Optional[str]:
        DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"  # ISO 8601 format
        if dt is None:
            return None
        return dt.strftime(DATE_FORMAT)


class Language(TimestampMixin, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
