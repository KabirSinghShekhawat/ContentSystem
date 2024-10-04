import io
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Query, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db_session
from src.schema.content_response import ContentResponse
from src.schema.query_params import (
    ContentFilterParams,
    ContentListResponse,
    ContentSortParams,
    SortDirection,
)
from src.services.content_service import ContentService

router = APIRouter()


@router.post(
    "/content/upload",
    response_model=List[ContentResponse],
    status_code=201,
)
async def upload_csv(
    file: UploadFile = File(...), session: AsyncSession = Depends(get_db_session),
    status_code=201,
):
    contents = await file.read()
    csv_buffer = io.StringIO(contents.decode("utf-8"))
    await ContentService(session).create_content(csv_buffer)


@router.get("/content", response_model=ContentListResponse)
async def list_content(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    year: Optional[str] = Query(None, description="Year filter (YYYY or YYYY-YYYY)"),
    language: Optional[str] = Query(
        None, description="Language filter (comma-separated)"
    ),
    sort: Optional[str] = Query(
        None, description="Sort field:direction (e.g., release_date:desc)"
    ),
    session: AsyncSession = Depends(get_db_session),
):
    filters = ContentFilterParams(year=year, language=language)

    sort_params: list[ContentSortParams] = []
    if sort:
        sort_by = sort.split(",")
        if len(sort_by) > 2:
            raise ValueError("Only two sort fields are allowed")

        for sort in sort_by:
            field, *direction = sort.split(":")
            direction = direction[0] if direction else SortDirection.ASC
            sort_param = ContentSortParams(field=field, direction=direction)
            sort_params.append(sort_param)

    response = await ContentService(session).get_content(
        filters=filters.to_dict(),
        sort_params=sort_params,
    )
    return JSONResponse(
        content={
            "data": {
                "filters": filters,
                "sort_params": sort_params,
                "contents": response,
            }
        },
        status_code=200,
    )
