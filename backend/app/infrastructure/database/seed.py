"""Seed an empty database with the maintained source-backed datasets."""
import asyncio

from sqlalchemy import func, select

from app.infrastructure.database.current_year_seed import add_current_year_data
from app.infrastructure.database.models import EstablishmentModel
from app.infrastructure.database.session import SessionFactory
from app.infrastructure.database.verified_seed import replace_demo_data


async def seed():
    async with SessionFactory() as session:
        is_empty = not await session.scalar(
            select(func.count()).select_from(EstablishmentModel)
        )
    if is_empty:
        await replace_demo_data()
    await add_current_year_data()


if __name__ == "__main__":
    asyncio.run(seed())
