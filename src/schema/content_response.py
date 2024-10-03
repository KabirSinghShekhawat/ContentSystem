from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class ContentResponse(BaseModel):
    id: int
    budget: float
    revenue: float
    runtime: int
    status: Optional[str] = "NA"
    homepage: Optional[str] = "NA"
    original_language: Optional[str] = "NA"
    original_title: str
    title: str
    overview: Optional[str] = None
    release_date: date
    vote_average: Optional[float] = 0.0
    vote_count: Optional[int] = 0
    production_company_id: int
    genre_id: int
    created_at: datetime
    updated_at: datetime
