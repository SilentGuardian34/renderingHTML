import json
import os

from datetime import date
from django.core.management.base import BaseCommand

from api.filters import Filter, FilterType
from api.importers import JSONImporter


class Command(BaseCommand):
    help = "Тестовая команда для парсинга JSON"

    def handle(self, *args, **kwargs):
        datadir = os.path.abspath("testdata")
        for file in os.listdir(datadir):
            if file.endswith(".json"):
                with open(os.path.join(datadir, file), "r", encoding="utf-8") as fd:
                    data = json.load(fd)
                    self.stdout.write(f"Заполнение данных из файла {file}")
                    json_importer = JSONImporter(data)
                    json_importer.import_data()
                    schedule = json_importer.schedules[0]
                    # schedule_filtered = Filter.from_daterange(date(2024, 9, 10), date(2024, 9, 10)).apply_to(schedule)
                    # schedule_filtered = Filter.from_filter_type(FilterType.GROUP, "0d1c584d-e609-49d9-8b68-f2b3a2ea2a0d").apply_to(schedule)
                    # schedule_filtered = Filter.from_filter_type(FilterType.TEACHER, "e5c47ff1-7193-41f6-80a5-d0e3c97ec6f1").apply_to(schedule)
                    schedule_filtered = Filter.from_filter_type(FilterType.PLACE,"9a2d6609-1d99-4ad1-bcbf-bb3b1dbdd6").apply_to(schedule)
                    self.stdout.write("OK")
        self.stdout.write(self.style.SUCCESS("Тестовые данные успешно загружены расперсены"))
