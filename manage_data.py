from jsonschema import validate
import json

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


def validate_data(parsed_json: str) -> None:
    validate(parsed_json, schema=SCHEMA)


def read_json_data(path: str) -> dict:
    """Загружаем json схему и валидируем её"""
    with open(path, "r", encoding='utf-8') as read_file:
        json_data = json.load(read_file)
        validate_data(json_data)
        return json_data
