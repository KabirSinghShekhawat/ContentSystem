import urllib.parse
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

from src.schema.content_response import ContentResponse


class SortField(str, Enum):
    RELEASE_DATE = "release_date"
    RATING = "rating"


class SortDirection(str, Enum):
    ASC = "asc"
    DESC = "desc"


class PaginationResponse(BaseModel):
    current_page: int
    per_page: int
    total_items: int
    total_pages: int


class ContentListResponse(BaseModel):
    data: List[ContentResponse]
    pagination: PaginationResponse


class ContentFilterParams(BaseModel):
    year: Optional[str] = Field(
        None, description="Single year (YYYY) or range (YYYY-YYYY)"
    )
    language: Optional[str] = Field(None, description="Comma-separated languages")

    def to_dict(self):
        filters = {}
        if self.year:
            if "-" in self.year:
                start_year, end_year = self.year.split("-")
                filters["year_range"] = (int(start_year), int(end_year))
            else:
                filters["year"] = int(self.year)

        if self.language:
            filters["languages"] = [
                urllib.parse.unquote(lang.strip()) for lang in self.language.split(",")
            ]

        return filters


class ContentSortParams(BaseModel):
    field: SortField
    direction: SortDirection = SortDirection.ASC
