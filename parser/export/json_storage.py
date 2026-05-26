import json
from datetime import datetime
from pathlib import Path

from loguru import logger

from parser.export.base import ResultStorage
from models import Item


class JsonStorage(ResultStorage):
    """
    Сохранение результатов парсинга в JSON.
    Каждый вызов save() создаёт новый файл — уже записанный файл не изменяется.
    """
    name = "json"

    def __init__(self, dir_path: Path):
        self.dir_path = dir_path
        self.dir_path.mkdir(parents=True, exist_ok=True)

    def save(self, ads: list[Item]) -> None:
        if not ads:
            return

        ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S_%f")
        file_path = self.dir_path / f"avito_{ts}.json"

        try:
            data = [ad.model_dump(mode="json") for ad in ads]
            file_path.write_text(
                json.dumps(data, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception as err:
            logger.error(f"JsonStorage: не удалось записать файл {file_path}: {err}")
