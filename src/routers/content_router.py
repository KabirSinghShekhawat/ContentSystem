from typing import List, Optional

from fastapi import APIRouter, Depends, File, Query, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.controllers.content_controller import ContentController
from src.database import get_db_session
from src.schema.content_response import ContentResponse
from src.schema.query_params import ContentListResponse
from src.services.content_service import ContentService

router = APIRouter()


@router.post(
    "/content/upload",
    response_model=List[ContentResponse],
    status_code=201,
)
async def upload_csv(
    file: UploadFile = File(...), session: AsyncSession = Depends(get_db_session)
):
    content_service = ContentService(session)
    await ContentController(content_service).upload_content(file)
    return JSONResponse({"message": "File uploaded successfully"}, status_code=201)


@router.get("/content", response_model=ContentListResponse)
async def list_content(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    year: Optional[str] = Query(None, description="Year filter (YYYY or YYYY-YYYY)"),
    language: Optional[str] = Query(
        None, description="Language filter (comma-separated)"
    ),
    sort: Optional[str] = Query(
        None, description="Sort field:direction (e.g., release_date:desc)"
    ),
    session: AsyncSession = Depends(get_db_session),
):
    content_service = ContentService(session)
    response = await ContentController(content_service).get_content(
        year, language, sort, page, page_size
    )
    return response
