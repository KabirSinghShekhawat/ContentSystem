import io
import json

import pandas as pd
from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db_session
from src.models.content import Content
from src.utils import yyyy_mm_dd

router = APIRouter()


@router.post("/content/upload")
async def upload_csv(
    file: UploadFile = File(...), session: AsyncSession = Depends(get_db_session)
):
    contents = await file.read()
    df = pd.read_csv(io.StringIO(contents.decode("utf-8")))
    df = df.fillna("NA")

    records = df.to_dict(orient="records")
    records = records[0:10]
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
            release_date=yyyy_mm_dd(record["release_date"]),
            vote_average=record["vote_average"],
            vote_count=record["vote_count"],
            production_company_id=record["production_company_id"],
            genre_id=record["genre_id"],
        )
        content_records.append(content)
    content_record_one = content_records[0]
    session.add(content_record_one)
    await session.commit()
    await session.refresh(content_record_one)

    records = json.dumps(records[0:10], allow_nan=True)
    return JSONResponse(content={"data": records}, status_code=200)
