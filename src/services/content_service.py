import math
from io import StringIO
from typing import List, Tuple

import pandas as pd
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlmodel import and_, text

from src.models.content import Content, ContentLanguage, Language
from src.schema.query_params import (
    ContentFilterParams,
    ContentListResponse,
    ContentResponse,
    ContentSortParams,
    PaginationParams,
    PaginationResponse,
    SortDirection,
)
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

    async def get_all_languages(self):
        result = await self.session.execute(select(Language))
        return result.scalars().all()

    async def get_content(
        self,
        filter_params: ContentFilterParams = None,
        sort_params: List[ContentSortParams] = [],
        pagination: PaginationParams = PaginationParams(),
    ):
        filter_params = filter_params.to_dict()
        languages: List[str] = filter_params.get("languages", None)
        year: int | Tuple[int] = filter_params.get("year", None) or filter_params.get(
            "year_range", None
        )

        query = select(Content)
        if languages and len(languages) > 0:
            languages = [f"'{lang.strip().lower()}'" for lang in languages]
            sql_query = f"""
            WITH lang as (SELECT id FROM language where lower(name) in ({','.join(languages)})),
            cl as (select content_id from contentlanguage cl join lang l on cl.language_id = l.id)
            select distinct c.id as content_id from content c join cl on c.id = cl.content_id
            """
            lang_filtered = await self.session.execute(text(sql_query))
            lang_filtered = lang_filtered.all()
            content_ids = [c.content_id for c in lang_filtered]
            query = query.where(Content.id.in_(content_ids))

        if year:
            if isinstance(year, tuple):
                start_year, end_year = year
                conditions = []
                conditions.append(
                    func.date_part("year", Content.publication_date) <= end_year
                )
                conditions.append(
                    func.date_part("year", Content.publication_date) >= start_year
                )
                query = query.where(and_(*conditions))
            else:
                query = query.where(
                    func.date_part("year", Content.release_date) == year
                )
        # vote_average field in db is exposed as rating in the API.
        sort_key_map = {
            "rating": "vote_average",
        }
        for sort_param in sort_params:
            sort_field = sort_param.field
            sort_direction = sort_param.direction
            if sort_field:
                sort_field = sort_key_map.get(sort_field.value, sort_field.value)
                if sort_direction == SortDirection.ASC:
                    query = query.order_by(getattr(Content, sort_field).asc())
                else:
                    query = query.order_by(getattr(Content, sort_field).desc())
                    # Count total items
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.session.scalar(count_query)

        # Apply pagination to query
        items_query = query.offset((pagination.page - 1) * pagination.page_size).limit(
            pagination.page_size
        )
        items = await self.session.execute(items_query)
        items = items.scalars().all()
        items = [ContentResponse.model_validate(item) for item in items]

        # Calculate total pages
        pages: int = math.ceil(total / pagination.page_size)
        return ContentListResponse(
            data=items,
            pagination=PaginationResponse(
                current_page=pagination.page,
                page_size=pagination.page_size,
                total_items=total,
                total_pages=pages,
            ),
        )

    async def create_content(self, csv_buffer: StringIO):
        df = pd.read_csv(csv_buffer)
        df = self.clean_data(df)

        await self.update_languages(df["languages"])
        all_languages = await self.get_all_languages()
        lang_map: dict[str, int] = {lang.name: lang.id for lang in all_languages}

        records = df.to_dict(orient="records")
        content_records = []
        content_languages = []
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
                languages=record["languages"],
            )
            content_records.append(content)

        self.session.add_all(content_records)
        await self.session.commit()
        for content in content_records:
            for lang in parse_languages(content.languages):
                content_languages.append(
                    ContentLanguage(content_id=content.id, language_id=lang_map[lang])
                )
        self.session.add_all(content_languages)
        await self.session.commit()
