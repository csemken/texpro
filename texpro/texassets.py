import os
from abc import ABC, abstractmethod
from textwrap import indent
from typing import TypeVar
from warnings import warn

from .settings import config

A = TypeVar('A', bound='Asset')


class Asset(ABC):
    label: str
    folder: str
    auto_load: bool

    def __init__(self, label: str, folder: str, auto_load: bool = False):
        self.label = label
        self.folder = config.get_or_return(folder)
        self.auto_load = auto_load
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

    def __init__(self, tex: str, label: str, folder: str = 'config.doc_path', **kwargs):
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
    def __init__(self, eq: str, label: str, folder: str = 'config.eq_path', **kwargs):
        self.label = label  # also done in super init below, but already needed for eq2tex
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
