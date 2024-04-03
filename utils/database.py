import logging
import os
import json
from datetime import datetime


log = logging.getLogger(__name__)


class Database(dict):
    def __init__(self, location: str, main_key: str = "__main__"):
        super().__init__()
        self.database_calling = 0
        self.main_key = main_key
        self.location = location
        self.update(**self.load())

    def __repr__(self):
        return object.__repr__(self)

    def change_root(self, main_key):
        self.main_key = main_key

    def load(self):
        return (
            json.load(open(self.location, "r", encoding="utf-8"))
            if os.path.exists(self.location)
            else {}
        )

    def save(self):
        if not os.path.exists(self.location):
            os.makedirs(os.path.dirname(self.location))

        json.dump(
            self, open(self.location, "w+", encoding="utf-8"),
            ensure_ascii=False, indent=4
        )
        return True

    def set(self, key, value):
        self[self.main_key] = dict(self).get(self.main_key, {})
        self[self.main_key][key] = value
        return self.save()

    def get(self, key, default=None):
        if self.database_calling % 15 == 0:  # бекап каждые 15 вызовов
            self.make_backup()

        return dict(self).get(self.main_key, {}).get(key, default)

    def pop(self, key):
        popped = dict(self).get(self.main_key, {}).get(key)
        del self[self.main_key][key]
        self.save()
        return popped

    def reset(self):
        self.clear()
        return self.save()

    def make_backup(self):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_filename = f"{self.location}.{timestamp}.bak"

        with open(self.location, "r", encoding="utf-8") as f:
            data = json.load(f)

        with open(backup_filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        backup_files = ['database/' + f for f in os.listdir("database/") if f.endswith(".bak")]
        if len(backup_files) > 3:
            oldest_backup = min(backup_files, key=os.path.getctime)
            os.remove(oldest_backup)
