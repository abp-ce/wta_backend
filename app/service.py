import asyncio
from typing import List

import httpx
from bs4 import BeautifulSoup, NavigableString, Tag

from . import crud
from .database import async_session, engine
from .models import Base

URL = "https://codeforces.com/problemset//page/{page}?order=BY_SOLVED_DESC"
HEADERS = {"Accept-Language": "ru,en-US;q=0.7,en;q=0.3"}


class Parse:
    def __init__(self):
        self.session = None
        self.client = None
        self.themes = None
        self.last_page = None

    @staticmethod
    async def recreate_tables(*args: str):
        tables = []
        for arg in args:
            tables.append(Base.metadata.tables[arg])
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all, tables=tables)
            await conn.run_sync(Base.metadata.create_all, tables=tables)

    async def __get_themes(self):
        themes = {}
        for theme in await crud.get_themes(self.session):
            themes[theme.name] = theme.id
        return themes

    def __convert_data(self, row: List[List[NavigableString]]) -> dict:
        return {
            "no": row[0][0],
            "name": row[1][0],
            "themes": row[1][1:] if len(row[1]) > 1 else [],
            "level": int(row[3][0]) if row[3] else 0,
            "solved": int(row[4][0][1:]) if row[4] else 0,
        }

    def __parse_table(self, table: Tag) -> List[dict]:
        return [
            self.__convert_data(
                [
                    [string for string in td.stripped_strings if string != ","]
                    for td in tr.find_all("td")
                ],
            )
            for tr in table.find_all("tr")
            if tr.contents[1].name == "td"
        ]

    async def __process_page(self, page: int) -> List[dict]:
        r = await self.client.get(
            URL.format(page=page), headers=HEADERS, timeout=None
        )
        soup = BeautifulSoup(r.text, "html.parser")
        if self.last_page is None:
            self.last_page = int(
                soup.find_all("span", class_="page-index")[-1].string
            )
        return await self.__process_task_data(
            self.__parse_table(soup.find("table"))
        )

    async def __process_task_data(self, data: List[dict]):
        async with async_session() as session:
            await crud.upsert_tasks(session, data)
        return data

    async def __process_theme_data(self, data: List[dict]):
        association_table_data = []
        self.themes = await self.__get_themes()
        for item in data:
            for el in set(item["themes"]):
                if el not in self.themes:
                    theme = await crud.create_theme(self.session, el)
                    self.themes[theme.name] = theme.id
                association_table_data.append(
                    {"task_no": item["no"], "theme_id": self.themes[el]}
                )
        return association_table_data

    async def __process_association_data(self, data: List[dict]):
        async with async_session() as self.session:
            await crud.insert_association_table(
                self.session, await self.__process_theme_data(data)
            )

    async def parse_site(self):
        async with httpx.AsyncClient() as self.client:
            # To initiate self.last_page
            first_page_data = await self.__process_page(1)
            tasks = [
                self.__process_page(i) for i in range(2, self.last_page + 1)
            ]
            pages_data = await asyncio.gather(*tasks)

        pages_data.append(first_page_data)
        await self.recreate_tables("association_table")
        for data in pages_data:
            await self.__process_association_data(data)
