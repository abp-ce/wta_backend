from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Task, Theme, association_table

TASK_LIMIT = 10


async def get_by_no(session: AsyncSession, no: str):
    result = await session.scalars(select(Task).where(Task.no == no))
    return result.all()


async def get_by_name(session: AsyncSession, name: str):
    result = await session.scalars(
        select(Task).where(Task.name.ilike(f"%{name}%"))
    )
    return result.all()


async def get_by_level_and_theme(
    session: AsyncSession, level: int, theme_id: int
):
    result = await session.scalars(
        select(Task)
        .join(association_table)
        .join(Theme)
        .where(Task.level == level, Theme.id == theme_id)
        .limit(TASK_LIMIT)
    )
    return result.all()


async def get_levels(session: AsyncSession):
    result = await session.scalars(
        select(Task.level).distinct().order_by(Task.level)
    )
    return result.all()


async def get_themes(session: AsyncSession):
    result = await session.scalars(select(Theme))
    return result.all()


async def get_themes_by_level(session: AsyncSession, level: int):
    result = await session.scalars(
        select(Theme)
        .join(association_table)
        .join(Task)
        .where(Task.level == level)
        .distinct()
    )
    return result.all()


async def get_themes_by_task_no(session: AsyncSession, task_no: str):
    result = await session.scalars(
        select(Theme)
        .join(association_table)
        .where(association_table.c.task_no == task_no)
    )
    return result.all()


async def upsert_tasks(session: AsyncSession, values: list[dict]):
    stmt = insert(Task)
    stmt = stmt.on_conflict_do_update(
        constraint="task_pkey",
        set_={
            "name": stmt.excluded.name,
            "level": stmt.excluded.level,
            "solved": stmt.excluded.solved,
        },
    )
    await session.execute(stmt, values)
    await session.commit()


async def insert_association_table(session: AsyncSession, values: list[dict]):
    await session.execute(insert(association_table), values)
    await session.commit()


async def create_theme(session: AsyncSession, name: str):
    theme_to_add = Theme(name=name)
    session.add(theme_to_add)
    await session.commit()
    return theme_to_add
