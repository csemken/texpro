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
    def file_name(self) -> str:
        pass

    @property
    def path(self) -> Path:
        return config.abspath(self.folder) / self.file_name

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


class TexAsset(Asset, ABC):
    """Uses attribute or property self.tex (str) for representation and saving"""

    def _repr_tex_(self) -> str:
        return self.tex

    @property
    def file_name(self) -> str:
        return f'{self.label}.tex'

    def save(self) -> Asset:
        if not self._can_save(self.tex):
            return
        self.path.write_text(self.tex)
        return self


class TexSnippet(TexAsset):
    tex: str

    def __init__(self, tex: str, label: str, folder: Union[str, Path] = 'config.doc_path'):
        self.tex = tex
        super().__init__(label, folder)

    def load(self) -> Asset:
        self.tex = self.path.read_text()


class TexEquation(TexAsset):
    block: str
    eq: str

    def __init__(self, eq: str, label: str, folder: Union[str, Path] = 'config.eq_path',
                 block: str = 'align'):
        self.block = block
        self.eq = eq  # without surrounding $$
        super().__init__(label, folder)

    def _repr_latex_(self) -> str:
        return f'${self.eq}$'

    @property
    def tex_label(self) -> str:
        return config.eq_prefix + self.label

    @property
    def tex(self):
        return config.eq_template.format(
            label=self.tex_label,
            block=self.block,
            eq=indent(self.eq, '\t')
        )


class TexTable(TexAsset):
    ...


class StargazerTable(TexAsset):
    def __init__(self, stargazer, label: str, folder: Union[str, Path] = 'config.tab_path'):
        self.stargazer = stargazer
        super().__init__(label, folder)

    def _repr_html_(self):
        return self.stargazer.render_html()

    @property
    def tex(self) -> str:
        return self.stargazer.render_latex()


class Image(Asset):
    file_type: str

    # TODO init that checks type

    # TODO file_name property

    def _repr_mimebundle_(self, include=None, exclude=None):
        # see https://ipython.readthedocs.io/en/stable/config/integrating.html
        # and https://ipython.readthedocs.io/en/stable/api/generated/IPython.display.html#IPython.display.display
        ...


class Plot(Asset):
    """Holds a plot, which must implement the `savefig()` method"""
    plot: object
    extension: str
    savefig_args: dict

    def __init__(self, plot: object, label: str = None, folder: Union[str, Path] = 'config.img_path',
                 extension: str = 'pdf', savefig_args: dict = {'bbox_inches': 'tight'}):
        self.plot = plot
        self.extension = extension
        self.savefig_args = savefig_args
        super().__init__(label, folder)

    def _ipython_display_(self):
        # graph is already displayed through plt.show()
        return

    @property
    def file_name(self) -> str:
        return f'{self.label}.{self.extension}'

    def save(self) -> Asset:
        self.plot.savefig(self.path, **self.savefig_args)
        return self

    def load(self) -> Asset:
        raise NotImplementedError('A Plot asset cannot be loaded, only saved')


class TexFigure(TexAsset):
    figure: Asset
    caption: str
    incl_args: str

    def __init__(self, figure: Asset, label: str, folder: Union[str, Path] = 'config.fig_path',
                 caption: str = '', incl_args: str = r'width=.8\linewidth'):
        self.figure = figure
        self.caption = caption
        self.incl_args = incl_args
        super().__init__(label, folder)

    def _ipython_display_(self):
        # display self.figure
        from IPython.display import display
        return display(self.figure)

    @property
    def tex_label(self) -> str:
        return config.fig_prefix + self.label

    @property
    def img_rel_path(self) -> str:
        # need to use os.path because Path.relative_to only works for sub-directories
        return os.path.relpath(self.figure.folder, self.folder)

    @property
    def tex(self):
        return config.fig_template.format(
            label=self.tex_label,
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
        super().save()  # save tex
        return self
