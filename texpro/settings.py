import re
from dataclasses import dataclass
from pathlib import Path
from typing import List

from texpro.utils import check_valid, tree, warn_if_not_dir

DEFAULT_EQ_TEMPLATE = r'''\begin{{{block}}}\label{{{label}}}
{eq}
\end{{{block}}}'''

DEFAULT_FIG_TEMPLATE = r'''\begin{{figure}}
	\centering
	\includegraphics[{incl_args}]{{{img_path}}}
	\caption{{{caption}}}
	\label{{{label}}}
\end{{figure}}'''

DEFAULT_TAB_TEMPLATE = r'''\begin{{table}}
	{formatting}
{table}
	\caption{{{caption}}}
	\label{{{label}}}
\end{{table}}'''

DEFAULT_TAB_FORMATTING = '\centering'

IMAGE_TYPES = []

PLOT_TYPES = IMAGE_TYPES


@dataclass
class _Config:
    doc_path: Path = None  # absolute or relative to current directory

    eq_path: Path = Path('./eq')  # absolute or relative to doc_path
    eq_prefix: str = 'eq:'
    eq_template: str = DEFAULT_EQ_TEMPLATE

    img_path: Path = Path('./img')  # absolute or relative to doc_path

    fig_path: Path = Path('./fig')  # absolute or relative to doc_path
    fig_prefix: str = 'fig:'
    fig_template: str = DEFAULT_FIG_TEMPLATE

    tab_path: Path = Path('./tab')  # absolute or relative to doc_path
    tab_prefix: str = 'tab:'
    tab_template: str = DEFAULT_TAB_TEMPLATE
    tab_formatting: str = DEFAULT_TAB_FORMATTING

    snip_path: Path = Path('.')  # absolute or relative to doc_path

    # behaviour
    check_paths: bool = False
    save: bool = True
    auto_save: bool = True
    auto_load: bool = True
    add_percent: bool = True

    def __setattr__(self, name, value):
        if name.endswith('path') and value is not None and not isinstance(value, Path):
            value = Path(value)
        if name == 'doc_path':
            if self.check_paths:
                warn_if_not_dir(value)
        elif name.endswith('path'):
            if self.check_paths:
                warn_if_not_dir(self.abspath(value))
        # TODO check types
        super().__setattr__(name, value)

    def abspath(self, path: Path) -> Path:
        """Absolute path from doc_path, used to save and load files"""
        if path.is_absolute():
            return path
        if self.doc_path is None:
            raise Exception('You need to set a path for the document root first, '
                            'using texpro.config.doc_path = "/your/path".')
        return (self.doc_path / path).absolute()

    @property
    def asset_paths(self) -> List[Path]:
        """List containing all asset paths"""
        return [self.eq_path, self.img_path, self.fig_path, self.tab_path]

    @property
    def all_paths(self) -> List[Path]:
        """List containing the doc_path and all asset paths in absolute form"""
        return [self.doc_path.absolute()] + [self.abspath(p) for p in set(self.asset_paths)]

    def make_folders(self, exist_ok=True):
        """Create the folder structure implied by this config (no overwriting)"""
        for path in self.all_paths:
            path.mkdir(parents=True, exist_ok=exist_ok)

    @property
    def file_tree(self) -> List[str]:
        """A visual tree of the doc_path folder"""
        return '\n'.join([str(self.doc_path)] + list(tree(self.doc_path)))

    _attribute_re = re.compile(r'^config\.(\w+)$')

    def get_or_return(self, key: str):
        """If `key` is of the format 'config.*', returns `self.*`, otherwise returns `key`"""
        match = self._attribute_re.match(key)
        if match:
            return getattr(self, match.group(1))
        else:
            return key


config = _Config()
config.check_paths = True
