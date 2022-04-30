import markdown
from markdown.treeprocessors import Treeprocessor
from markdown.extensions import Extension
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Img:
    alt: str
    src: str

    def raw_str(self) -> str:
        return f"![{self.alt}]({self.src})"


class ImgExtractor(Treeprocessor):
    def run(self, doc):
        """Find all images and append to markdown.images. """
        self.md.images = []
        for image in doc.findall('.//img'):
            self.md.images.append(
                Img(
                    alt=image.get('alt'),
                    src=image.get('src')
                )
            )


class ImgExtExtension(Extension):
    def extendMarkdown(self, the_md, md_globals):
        img_ext = ImgExtractor(the_md)
        the_md.treeprocessors.register(img_ext, 'imgext', 1)


md = markdown.Markdown(extensions=[ImgExtExtension()])


def get_image_from_md(md_text: str) -> list[Img]:
    _html = md.convert(md_text)
    return md.images


def replace_image_links(text: str, links_to_replace: dict[str, tuple[str, str]]) -> str:
    updated = text
    for md_img_link, (alt, _) in links_to_replace.items():
        # updated = updated.replace(md_img_link, alt)
        updated = updated.replace(md_img_link, alt)
    return updated


def remove_image_links(text: str, links_to_del: dict[str, tuple[str, str]]) -> str:
    updated = text
    for md_img_link, (alt, _) in links_to_del.items():
        updated = updated.replace(md_img_link, "")
    return updated
