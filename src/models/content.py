from datetime import date
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel

from src.models.timestamp_mixin import TimestampMixin


class ContentLanguage(SQLModel, table=True):
    content_id: Optional[int] = Field(
        default=None, foreign_key="content.id", primary_key=True
    )
    language_id: Optional[int] = Field(
        default=None, foreign_key="language.id", primary_key=True
    )


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

    languages: list["Language"] = Relationship(
        back_populates="content", link_model=ContentLanguage
    )


class Language(TimestampMixin, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    content: list["Content"] = Relationship(
        back_populates="languages", link_model=ContentLanguage
    )
