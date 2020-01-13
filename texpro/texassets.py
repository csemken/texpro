import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from textwrap import indent
from typing import TypeVar
from warnings import warn

DEFAULT_EQ_TEMPLATE = r'''\begin{{align}}\label{{{label}}}
{eq}
\end{{align}}'''

IMAGE_TYPES = []

PLOT_TYPES = IMAGE_TYPES


def check_valid(value, options, name):
    if value not in options:
        raise AttributeError(f'{name} has to be one of {options}')


def warn_if_not_dir(path):
    if not os.path.isdir(path):
        warn(f'{path} is not a directory', ResourceWarning)


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

    def abspath(self, path: str):
        """Absolute path generator, used to save and load files"""
        if os.path.isabs(path):
            return path
        if self.doc_path is None:
            raise Exception('You need to set a path for the document root first, '
                            'using texpro.config.doc_path = "/your/path".')
        return os.path.abspath(os.path.join(self.doc_path, path))

    @property
    def fig2img_path(self):
        """The relative path from the figure directory (default: ./fig)
        to the image directory (default: ./img)"""
        return os.path.relpath(self.abspath(self.img_path), self.abspath(self.fig_path))

    def make_folders(self):
        """Create the folder structure implied by this config (no overwriting)"""
        ...

    @property
    def file_tree(self):
        # use https://stackoverflow.com/a/59109706
        ...


config = _Config()
config.check_paths = True


A = TypeVar('A', bound='Asset')


@dataclass(eq=False)
class Asset(ABC):
    label: str
    folder: str
    auto_load: bool = field(repr=False, default=config.auto_load)

    def __post_init__(self):
        if self.auto_load:
            self.load()

    @property
    @abstractmethod
    def fname(self) -> str:
        pass

    @property
    def fpath(self) -> str:
        return os.join(config.abspath(self.folder), self.fname)

    @staticmethod
    def _can_save(self, obj) -> bool:
        if not config.save:
            warn('Not saved because config.save is False')
            return False
        if obj is None:
            raise Exception('There is nothing to be saved yet')
        return True

    @abstractmethod
    def save(self) -> A:
        pass

    def load(self) -> A:
        raise NotImplementedError(f'{type(self)} can currently only be saved')


class TexCode(Asset):
    tex: str

    def __init__(self, tex: str, label: str, folder: str, **kwargs):
        self.tex = tex
        super().__init__(label, folder, **kwargs)

    def _repr_tex_(self) -> str:
        return self.tex

    @property
    def fname(self) -> str:
        return f'{self.label}.tex'

    def save(self) -> A:
        if not self._can_save(self.tex):
            return
        with open(self.fname, 'r') as file:
            file.write(self._repr_tex_())


class TexEquation(TexCode):
    def __init__(self, eq: str, label: str, folder: str = config.eq_path, **kwargs):
        self.label = label  # done in init below, but already needed for eq2tex
        tex = self.eq2tex(eq)
        super().__init__(tex, label, folder, **kwargs)

    def eq2tex(self, eq):
        # TODO strip $$
        return config.eq_template.format(label=self.label, eq=indent(eq, '\t'))

    def set_eq(self, eq: str):
        self.tex = self.eq2tex(eq)


class TexTable(TexCode):
    ...


class StargazerTable(Asset):
    ...


class Image(Asset):
    type: str

    # TODO init that checks type

    # TODO fname property

    def _repr_mimebundle_(self, include=None, exclude=None):
        # see https://ipython.readthedocs.io/en/stable/config/integrating.html
        ...


class Plot(Asset):
    type: str

    # TODO init

    def _ipython_display_(self):
        # use representation of graph object
        # see https://ipython.readthedocs.io/en/stable/config/integrating.html
        # and https://ipython.readthedocs.io/en/stable/api/generated/IPython.display.html#IPython.display.DisplayObject
        ...


class TexFigure(TexCode):
    figure: Asset

    # TODO init

    def _ipython_display_(self):
        # display self.figure
        ...

    def save(self) -> A:
        if not self._can_save(self.figure):
            return
        # use label from figure also for image, if none set yet
        if not hasattr(self.figure, 'label') or self.figure.label is None:
            self.figure.label = self.label
        self.figure.save()  # save image
        # TODO update tex
        super().save()  # save tex code
        return self
