import markdown
from markdown.treeprocessors import Treeprocessor
from markdown.extensions import Extension


class ImgExtractor(Treeprocessor):
    def run(self, doc):
        """Find all images and append to markdown.images. """
        self.md.images = []
        for image in doc.findall('.//img'):
            self.md.images.append(image.get('src'))


class ImgExtExtension(Extension):
    def extendMarkdown(self, the_md, md_globals):
        img_ext = ImgExtractor(the_md)
        the_md.treeprocessors.register(img_ext, 'imgext', 1)


md = markdown.Markdown(extensions=[ImgExtExtension()])


def get_image_from_md(md_text: str) -> list[str]:
    _ = md.convert(md_text)
    return md.images