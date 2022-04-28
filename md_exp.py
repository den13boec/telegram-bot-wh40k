from markdown.treeprocessors import Treeprocessor
from markdown.extensions import Extension


class ImgReplacer(Treeprocessor):
    def run(self, root):
        # Loop through all img elements
        self.md.images = []
        for img in root.getiterator('img'):
            # Join base to the src URL
            img.set('src', urljoin(BASE, img.get('src')))


class ImgBase(Extension):
    def extendMarkdown(self, md, md_globals):
        # register the new treeprocessor with priority 15 (run after 'inline')
        md.treeprocessors.register(ImgBaseTreeprocessor(md), 'imgbase', 15)