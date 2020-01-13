import os
from dataclasses import dataclass
from pathlib import Path
from typing import List

from texpro.utils import check_valid, tree, warn_if_not_dir

DEFAULT_EQ_TEMPLATE = r'''\begin{{align}}\label{{{label}}}
{eq}
\end{{align}}'''

IMAGE_TYPES = []

PLOT_TYPES = IMAGE_TYPES


@dataclass
class _Config:
    doc_path: str = None  # absolute or relative to current directory

    eq_path: str = './eq'  # absolute or relative to doc_path
    eq_label: str = 'eq'
    eq_template: str = DEFAULT_EQ_TEMPLATE

    img_path: str = './img'  # absolute or relative to doc_path
    fig_path: str = './fig'  # absolute or relative to doc_path
    tab_path: str = './tab'  # absolute or relative to doc_path

    check_paths: bool = False
    save: bool = True

    # default attributes
    auto_load = False
    image_type = 'pdf'
    plot_type = 'pdf'

    def __setattr__(self, name, value):
        if name == 'doc_path':
            if self.check_paths:
                warn_if_not_dir(value)
        elif name.endswith('path'):
            if self.check_paths:
                warn_if_not_dir(self.abspath(value))
        # TODO check types
        super().__setattr__(name, value)

    @property
    def abs_doc_path(self):
        return os.path.abspath(self.doc_path)

    def abspath(self, path: str):
        """Absolute path generator, used to save and load files"""
        if os.path.isabs(path):
            return path
        if self.doc_path is None:
            raise Exception('You need to set a path for the document root first, '
                            'using texpro.config.doc_path = "/your/path".')
        return os.path.abspath(os.path.join(self.doc_path, path))

    @property
    def asset_paths(self):
        """List containing all asset paths"""
        return [self.eq_path, self.img_path, self.fig_path, self.tab_path]

    @property
    def all_paths(self):
        """List containing the doc_path and all asset paths in absolute form"""
        return [self.abs_doc_path] + [self.abspath(p) for p in set(self.asset_paths)]

    def make_folders(self, exist_ok=True):
        """Create the folder structure implied by this config (no overwriting)"""
        for path in self.all_paths:
            os.makedirs(path, exist_ok=exist_ok)

    @property
    def fig2img_path(self):
        """The relative path from the figure directory (default: ./fig)
        to the image directory (default: ./img)"""
        return os.path.relpath(self.abspath(self.img_path), self.abspath(self.fig_path))

    @property
    def file_tree(self) -> List[str]:
        """A visual tree of the doc_path folder"""
        return '\n'.join([self.doc_path] + list(tree(Path(self.abs_doc_path))))


config = _Config()
config.check_paths = True
