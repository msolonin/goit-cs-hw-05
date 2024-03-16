# -*- coding: utf-8 -*-
"""
Напишіть Python-скрипт, який буде читати всі файли у вказаній користувачем вихідній папці (source folder) і
розподіляти їх по підпапках у директорії призначення (output folder) на основі розширення файлів. Скрипт повинен
виконувати сортування асинхронно для більш ефективної обробки великої кількості файлів.
"""
import argparse
import asyncio
import logging
from aiopath import AsyncPath
from aioshutil import copyfile

parser = argparse.ArgumentParser(description="Sorting files")
parser.add_argument("--source", "-s", required=True, help="Source dir")
parser.add_argument("--output", "-o", help="Output dir", default="destination")
args = vars(parser.parse_args())

source = AsyncPath(args["source"])
output = AsyncPath(args["output"])


async def get_folders(path: AsyncPath):
    async for file in path.iterdir():
        if await file.is_dir():
            await get_folders(file)
        else:
            await copy_file(file)


async def copy_file(file: AsyncPath):
    folder = output / file.suffix[1:]
    try:
        await folder.mkdir(exist_ok=True, parents=True)
        await copyfile(file, folder / file.name)
    except OSError as e:
        logging.error(e)


if __name__ == "__main__":
    format = "%(threadName)s %(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
    asyncio.run(get_folders(source))
    print(f"All files copied from {source} to {output} folder. Source dir will be deleted")

