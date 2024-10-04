from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ContentResponse(BaseModel):
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

    model_config = ConfigDict(from_attributes=True)
