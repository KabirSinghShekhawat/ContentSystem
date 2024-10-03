import io
from typing import List

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.schema.content_response import ContentResponse
from src.database import get_db_session
from src.models.content import Content
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
    contents = await file.read()
    csv_buffer = io.StringIO(contents.decode("utf-8"))
    content = await ContentService(session).create_content(csv_buffer)
    return content
