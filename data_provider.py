import json
import os.path
from data_helpers import abs_path, md_doc_path, read_markdown_text
from jsonschema import validate
from jsonschema.exceptions import ValidationError
from md_image import get_image_from_md

SCHEMA = {
    "type": "object",
    "properties": {
        "things": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "category": {
                        "enum": [
                            "factions",
                            "books",
                            "games"
                        ]
                    },

                    "parents": {
                        "type": "array",
                        "items": {"type": "string"}
                    },

                    "content": {"type": "object"}
                },
                "required": ["category", "parents"]
            },
        },
    },
}


class DataProvider:
    def _read_data(self, encoding) -> dict:
        """Loads json data and then validate it"""
        with open(self.json_file_path, "r", encoding=encoding) as read_file:
            data = json.load(read_file)
            validate(data, SCHEMA)
            return data

    def __init__(self, json_file_path: str, encoding: str = 'utf-8'):
        self.json_file_path = abs_path(json_file_path)
        self._json_data = self._read_data(encoding)

    def collect_path_of_factions(self) -> list[tuple[str, str]]:
        paths = list()
        for x in self._json_data['things']:
            if x['category'] == 'factions':
                paths.append((x['content']['name'], x['content']['md_doc_path']))
        return paths

    def filter_by_category(self, category_name: str) -> list[dict]:
        filtered = list()
        for x in self._json_data['things']:
            if x['category'] is category_name:
                filtered.append(x)
        return filtered

    @property  # json getter
    def json_data(self):
        return self._json_data

    @json_data.setter  # json setter
    def json_data(self, value):
        try:
            validate(value, SCHEMA)
            self._json_data = value
        except ValidationError as err:
            raise ValueError(f"Error while reassigning json data:"
                             f" invalid data\n{err.message}")

    def prepare_md_docs(self):
        md_paths = self.collect_path_of_factions()
        res = dict()

        for (name, path) in md_paths:
            dir_path = abs_path(path)
            # we have a md_doc path -> we can use it! (but we don't want.. for now..)
            md_path = md_doc_path(dir_path)
            text = read_markdown_text(md_path)

            abs_images = [
                os.path.join(dir_path, pic) for pic in get_image_from_md(text)  # TODO: strip_image_from_text
            ]

            res[name] = abs_images

        for key, val in res.items():
            print(f"{key}: {val}")


if __name__ == "__main__":
    prov = DataProvider('data.json')
    prov.prepare_md_docs()
