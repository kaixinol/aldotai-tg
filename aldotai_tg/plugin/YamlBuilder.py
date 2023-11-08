import asyncio
import io

from aiogram.types import InputFile
from gameyamlspiderandgenerator import produce_yaml, verify
from gameyamlspiderandgenerator.util.config import config
from gameyamlspiderandgenerator.util.plugin_manager import pkg
from gameyamlspiderandgenerator.util.spider import get_bytes
from aldotai_tg.setting import config as bot_config

sem = asyncio.Semaphore(3)
config.load(bot_config['plugin']['YamlBuilder'])
pkg.init()


async def to_yaml(url: str) -> dict:
    async with(sem):
        if verify(url) is None:
            raise Exception("URL无效")
        temp = produce_yaml(url)
        return {"document": InputFile(io.BytesIO(bytes(temp)), filename=temp.raw_dict['name'] + '.zip'),
                "thumb": get_bytes(temp.raw_dict["thumbnail"]),
                "caption": temp.raw_dict["brief-description"]}
