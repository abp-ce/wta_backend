from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from . import crud
from .dependencies import get_session
from .service import Parse
from .tasks import celery_parse

router = APIRouter()


@router.get("/list/")
async def get_by_tasks(
    no: str | None = None,
    name: str | None = None,
    level: int | None = None,
    theme_id: int | None = None,
    session: AsyncSession = Depends(get_session),
):
    if no:
        return await crud.get_by_no(session, no)
    if name:
        return await crud.get_by_name(session, name)
    if level and theme_id:
        return await crud.get_by_level_and_theme(session, level, theme_id)
    return []


@router.get("/levels")
async def get_levels(session: AsyncSession = Depends(get_session)):
    return await crud.get_levels(session)


@router.get("/themes")
async def get_themes(session: AsyncSession = Depends(get_session)):
    return await crud.get_themes(session)


@router.get("/themes/")
async def get_themes_by_level(
    level: int, session: AsyncSession = Depends(get_session)
):
    return await crud.get_themes_by_level(session, level)


@router.get("/themes/{task_no}")
async def get_themes_by_task_no(
    task_no: str, session: AsyncSession = Depends(get_session)
):
    return await crud.get_themes_by_task_no(session, task_no)


@router.get("/parse")
async def parse_pages():
    return await Parse().parse_site()


@router.get("/celery", status_code=status.HTTP_202_ACCEPTED)
async def celery():
    celery_parse.delay()
    return {"message": "Parse queued"}
