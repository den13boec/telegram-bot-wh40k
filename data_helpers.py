import os
from typing import AnyStr


def get_directory_realpath(file_path: AnyStr) -> AnyStr:
    return os.path.dirname(os.path.realpath(file_path))


def abs_path(unix_rel_path: str) -> str:
    tmp = unix_rel_path.split("/")
    return os.path.join(
        os.path.dirname(
            os.path.realpath(__file__)
        ), *tmp
    )


def md_doc_path(dir_with_md: str) -> str:
    md_docs = []
    for file in os.listdir(dir_with_md):
        if file.endswith(".md"):
            md_docs.append(os.path.join(dir_with_md, file))

    if len(md_docs) == 1:
        return md_docs[0]

    if len(md_docs) == 0:
        raise ValueError(f"Error: no markdown docs found"
                         f"in directory\n{dir_with_md}")

    if len(md_docs) > 1:
        raise ValueError(f"Error: several md_docs found"
                         f"in directory\n{dir_with_md}, but expected only one")


def read_markdown_text(md_path: str):
    with open(md_path, "r", encoding='utf-8') as file:
        return file.read()
