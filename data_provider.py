import json
import os.path
from data_helpers import abs_path, md_doc_path, read_markdown_text
from jsonschema import validate
from jsonschema.exceptions import ValidationError
from md_image import get_image_from_md, remove_image_links

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
        self._md_docs_category: str | None = None
        self._md_docs_images: dict | None = None  # no images on init

    def collect_paths(self, category_name: str) -> dict[str, str]:
        """Collecting all paths of factions"""
        paths = dict()
        for x in self._json_data['things']:
            if x['category'] == category_name:
                paths[x['content']['name']] = x['content']['md_doc_path']
        return paths

    def filter_by_category(self, category_name: str) -> list[dict]:
        filtered = list()
        for x in self._json_data['things']:
            if x['category'] is category_name:
                filtered.append(x)
        return filtered

    def get_items_names_by_category(self, category: str) -> list[str]:
        items_names = []
        for x in self._json_data["things"]:
            if x["category"] == category:
                items_names.append(x["content"]["name"])
        return items_names

    @property  # json getter
    def json_data(self):
        return self._json_data

    @json_data.setter  # json setter
    def json_data(self, new_value):
        try:
            validate(new_value, SCHEMA)
            self._json_data = new_value
        except ValidationError as err:
            raise ValueError(f"Error while reassigning json data:"
                             f" invalid data\n{err.message}")

    def prepare_md_docs(self, category: str):
        md_paths = self.collect_paths(category)
        found_md_docs = dict()

        for name, path in md_paths.items():
            dir_path = abs_path(path)
            md_path = md_doc_path(dir_path)

            images = dict()
            for img in get_image_from_md(read_markdown_text(md_path)):
                images[img.raw_str()] = img.alt, os.path.join(dir_path, img.src)

            # save md_path with list of images to dictionary
            found_md_docs[name] = (md_path, images)

        self._md_docs_images = found_md_docs

    def get_md_for_telegram(self, category: str, content_name: str) -> tuple[str, list]:
        if self._md_docs_images is None or self._md_docs_category != category:
            self.prepare_md_docs(category=category)

        md_path, images_dict = self._md_docs_images[content_name]
        updated_text = remove_image_links(
            read_markdown_text(md_path),
            images_dict
        )

        images_paths = [(alt_caption, path) for _, (alt_caption, path) in images_dict.items()]
        return updated_text, images_paths


if __name__ == "__main__":
    prov = DataProvider('data.json')
    text, img_paths = prov.get_md_for_telegram('books', 'Книги по вселенной')
    print(f"Updated text:\n{text.rstrip().lstrip()}")
    print(f"Images found:\n{img_paths}")
