import io

from fastapi import HTTPException, UploadFile

from src.schema.query_params import (
    ContentFilterParams,
    ContentSortParams,
    PaginationParams,
    SortDirection,
)
from src.services.content_service import ContentService
from src.utils import validate_csv_file


class ContentController:
    def __init__(self, content_service):
        self.content_service: ContentService = content_service

    async def get_content(
        self, year: str, language: str, sort: str, page: int, page_size: int
    ):
        filters = ContentFilterParams(year=year, language=language)

        sort_params: list[ContentSortParams] = []
        if sort:
            sort_by = sort.split(",")
            if len(sort_by) > 2:
                raise HTTPException(
                    status_code=400, detail="Only two sort fields are allowed"
                )

            for sort in sort_by:
                field, *direction = sort.split(":")
                direction = direction[0] if direction else SortDirection.ASC
                sort_param = ContentSortParams(field=field, direction=direction)
                sort_params.append(sort_param)

        return await self.content_service.get_content(
            filter_params=filters,
            sort_params=sort_params,
            pagination=PaginationParams(page=page, page_size=page_size),
        )

    async def upload_content(self, csv_file: UploadFile):
        validate_csv_file(csv_file)
        contents = await csv_file.read()
        csv_buffer = io.StringIO(contents.decode("utf-8"))
        await self.content_service.create_content(csv_buffer)
