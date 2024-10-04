from io import StringIO
from typing import List, Tuple

import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.models.content import Content, Language
from src.utils import parse_date, parse_languages


class ContentService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def update_languages(self, languages_df: pd.DataFrame):
        languages: list[str] = languages_df.to_list()
        unique_languages = set()
        for lang in languages:
            unique_languages.update(parse_languages(lang))
        existing_languages = await self.session.execute(
            select(Language).filter(Language.name.in_(unique_languages))
        )
        existing_languages = set(
            lang.name for lang in existing_languages.scalars().all()
        )

        content_languages = unique_languages - existing_languages
        self.session.add_all([Language(name=lang) for lang in content_languages])
        await self.session.commit()

    def clean_data(self, df: pd.DataFrame):
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
        df["languages"] = df["languages"].fillna("[]")
        return df

    async def get_languages(self, languages: List[str]):
        result = await self.session.execute(
            select(Language).filter(Language.name.in_(languages))
        )
        return result.scalars().all()

    async def get_content(
        self,
        languages: List[str] = None,
        year: int | Tuple[int] = None,
        sort_params: List[Tuple[str, str]] = None,
    ):
        query = select(Content)
        if languages and len(languages) > 0:
            query = query.join(Content.languages).filter(Language.name.in_(languages))
        if year:
            if isinstance(year, tuple):
                start_year, end_year = year
                query = query.filter(Content.release_date.between(start_year, end_year))
            else:
                query = query.filter(Content.release_date == year)

        for sort_field, sort_direction in sort_params:
            if sort_field:
                if sort_direction == "asc":
                    query = query.order_by(sort_field)
                else:
                    query = query.order_by(sort_field.desc())
        result = await self.session.execute(query)
        return result.scalars().all()

    async def create_content(self, csv_buffer: StringIO):
        df = pd.read_csv(csv_buffer)
        df = self.clean_data(df)

        await self.update_languages(df["languages"])

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
                languages=[
                    Language(name=lang) for lang in parse_languages(record["languages"])
                ],
            )
            content_records.append(content)

        self.session.add_all(content_records)
        await self.session.commit()
        q = select(Content)
        await self.session.execute(q)
