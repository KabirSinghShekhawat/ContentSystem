from io import StringIO

import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.models.content import Content
from src.utils import parse_date


class ContentService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def get_content(self):
        pass

    async def create_content(self, csv_buffer: StringIO):
        df = pd.read_csv(csv_buffer)
        numerical_columns = [
            "budget",
            "revenue",
            "runtime",
            "vote_average",
            "vote_count",
        ]
        string_columns = [
            "status",
            "homepage",
            "original_language",
            "original_title",
            "title",
            "overview",
        ]
        date_columns = ["release_date"]
        # cleanup missing values
        df[numerical_columns] = df[numerical_columns].fillna(0)
        df[string_columns] = df[string_columns].fillna("NA")
        df[date_columns] = df[date_columns].fillna("1900-01-01")

        records = df.to_dict(orient="records")
        content_records = []
        for record in records:
            content = Content(
                budget=record["budget"],
                revenue=record["revenue"],
                runtime=record["runtime"],
                status=record["status"],
                homepage=record["homepage"],
                original_language=record["original_language"],
                original_title=record["original_title"],
                title=record["title"],
                overview=record["overview"],
                release_date=parse_date(record["release_date"]),
                vote_average=record["vote_average"],
                vote_count=record["vote_count"],
                production_company_id=record["production_company_id"],
                genre_id=record["genre_id"],
            )
            content_records.append(content)
        self.session.add_all(content_records)
        await self.session.commit()
        q = select(Content)
        result = await self.session.execute(q)
        scalar_result = result.scalars().all()
        return scalar_result
