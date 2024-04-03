import os
import json


class Database(dict):
    def __init__(self, location: str, main_key: str = "__main__"):
        super().__init__()
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
        return dict(self).get(self.main_key, {}).get(key, default)

    def pop(self, key):
        popped = dict(self).get(self.main_key, {}).get(key)
        del self[self.main_key][key]
        self.save()
        return popped

    def reset(self):
        self.clear()
        return self.save()