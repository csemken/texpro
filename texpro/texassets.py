from __future__ import annotations

__all__ = ['TexSnippet', 'TexEquation', 'TexTable', 'StargazerTable', 'TexFigure', 'Image', 'Plot']

import os
from abc import ABC, abstractmethod
from pathlib import Path
from textwrap import indent
from typing import TypeVar, Union
from warnings import warn

from .settings import config


class Asset(ABC):
    label: str
    folder: Path

    def __init__(self, label: str, folder: Union[str, Path]):
        self.label = label
        folder = config.get_or_return(folder)
        if not isinstance(folder, Path):
            folder = Path(folder)
        self.folder = folder

    @property
    @abstractmethod
    def fname(self) -> str:
        pass

    @property
    def fpath(self) -> Path:
        return config.abspath(self.folder) / self.fname

    @staticmethod
    def _can_save(obj) -> bool:
        if not config.save:
            warn('Not saved because config.save is False')
            return False
        if obj is None:
            raise Exception('There is nothing to be saved yet')
        return True

    @abstractmethod
    def save(self) -> Asset:
        pass

    def load(self) -> Asset:
        raise NotImplementedError(f'{type(self)} can currently only be saved')


class TexSnippet(Asset):
    tex: str

    def __init__(self, tex: str, label: str, folder: Union[str, Path] = 'config.doc_path'):
        self.tex = tex
        super().__init__(label, folder)

    def _repr_tex_(self) -> str:
        return self.tex

    @property
    def fname(self) -> str:
        return f'{self.label}.tex'

    def save(self) -> Asset:
        if not self._can_save(self.tex):
            return
        with open(self.fpath, 'w') as file:
            file.write(self.tex)

    def load(self) -> Asset:
        with open(self.fpath, 'r') as file:
            self.tex = file.read()


class TexEquation(TexSnippet):
    block: str

    def __init__(self, eq: str, label: str, folder: Union[str, Path] = 'config.eq_path',
                 block: str = 'align'):
        self.label = label  # also done in super init below, but already needed for eq2tex
        self.block = block
        tex = self.eq2tex(eq)
        super().__init__(tex, label, folder)

    def eq2tex(self, eq):
        # TODO strip $$
        return config.eq_template.format(
            label=self.label,
            block=self.block,
            eq=indent(eq, '\t')
        )

    def set_eq(self, eq: str):
        self.tex = self.eq2tex(eq)


class TexTable(TexSnippet):
    ...


class StargazerTable(Asset):
    def __init__(self, stargazer, label: str, folder: Union[str, Path] = 'config.tab_path'):
        self.stargazer = stargazer
        super().__init__(label, folder)

    def _repr_tex_(self) -> str:
        return self.tex

    @property
    def fname(self) -> str:
        return f'{self.label}.tex'

    @property
    def tex(self) -> str:
        return self.stargazer.render_latex()

    def save(self) -> Asset:
        if not self._can_save(self.tex):
            return
        with open(self.fpath, 'w') as file:
            file.write(self.tex)


class Image(Asset):
    file_type: str

    # TODO init that checks type

    # TODO fname property

    def _repr_mimebundle_(self, include=None, exclude=None):
        # see https://ipython.readthedocs.io/en/stable/config/integrating.html
        ...


class Plot(Asset):
    """Holds a plot, which must implement the `savefig()` method"""
    plot: object
    extension: str
    savefig_args: dict

    def __init__(self, plot: str, label: str = None, folder: Union[str, Path] = 'config.img_path',
                 extension: str = 'pdf', savefig_args: dict = {'bbox_inches': 'tight'}):
        self.plot = plot
        self.extension = extension
        self.savefig_args = savefig_args
        super().__init__(label, folder)

    def _ipython_display_(self):
        # use representation of graph object
        # see https://ipython.readthedocs.io/en/stable/config/integrating.html
        # and https://ipython.readthedocs.io/en/stable/api/generated/IPython.display.html#IPython.display.DisplayObject
        ...

    @property
    def fname(self) -> str:
        return f'{self.label}.{self.extension}'

    def save(self) -> Asset:
        self.plot.savefig(self.fpath, **self.savefig_args)
        return self

    def load(self) -> Asset:
        raise NotImplementedError('A Plot asset cannot be loaded, only saved')


class TexFigure(TexSnippet):
    figure: Asset
    caption: str
    incl_args: str

    def __init__(self, figure: Asset, label: str, folder: Union[str, Path] = 'config.fig_path',
                 caption: str = '', incl_args: str = r'width=.8\linewidth'):
        self.figure = figure
        self.caption = caption
        self.incl_args = incl_args
        super().__init__('', label, folder)
        self._update_tex()

    def _ipython_display_(self):
        # display self.figure
        ...

    @property
    def img_rel_path(self):
        # need to use os because Path.relative_to only works for sub-directories
        return os.path.relpath(self.figure.folder, self.folder)

    def _update_tex(self):
        self.tex = config.fig_template.format(
            label=self.label,
            incl_args=self.incl_args,
            img_path=self.img_rel_path,
            caption=self.caption,
        )

    def save(self) -> Asset:
        if not self._can_save(self.figure):
            return
        # use label from figure also for image, if none set yet
        if not hasattr(self.figure, 'label') or self.figure.label is None:
            self.figure.label = self.label
        self.figure.save()  # save image
        self._update_tex()  # update tex
        super().save()  # save tex
        return self
