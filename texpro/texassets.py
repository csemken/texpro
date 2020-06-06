from __future__ import annotations

__all__ = ['TexSnippet', 'TexEquation', 'TexTable', 'StargazerTable', 'TexFigure', 'Image', 'Plot']

from abc import ABC, abstractmethod
from pathlib import Path
from textwrap import indent
from typing import Union

import IPython

from .settings import config


class Asset(ABC):
    label: str
    folder: Path

    def __init__(self, label: str, folder: Union[str, Path],
                 obj_supplied: bool = None):
        self.label = label
        folder = config.get_or_return(folder)
        if not isinstance(folder, Path):
            folder = Path(folder)
        self.folder = folder

        # auto save/load
        if obj_supplied is not None:
            if obj_supplied and config.auto_save:
                self.save()
            elif not obj_supplied and config.auto_load:
                self.load()

    @property
    @abstractmethod
    def file_name(self) -> str:
        pass

    @property
    def rel_path(self) -> Path:
        """Path relative to config.doc_path"""
        return self.folder / self.file_name

    @property
    def path(self) -> Path:
        return config.abspath(self.rel_path)

    @staticmethod
    def _can_save(obj) -> bool:
        if not config.save:
            # warn('Not saved because config.save is False')
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

    def _repr_latex_(self) -> str:
        return self.tex

    @property
    def file_name(self) -> str:
        return f'{self.label}.tex'

    @property
    def tex_output(self) -> str:
        return self.tex

    def save(self) -> Asset:
        if not self._can_save(self.tex_output):
            return
        self.path.write_text(self.tex_output)
        return self


class TexSnippet(TexAsset):
    tex: str

    def __init__(self, label: str, tex: str = None, folder: Union[str, Path] = 'config.snip_path'):
        self.tex = tex
        super().__init__(label, folder, obj_supplied=tex is not None)

    @property
    def tex_output(self) -> str:
        if config.add_percent and \
                (not self.tex[-1] == '%' or self.tex[-2] == r'\%'):
            return f'{self.tex}%'
        else:
            return self.tex

    def load(self) -> Asset:
        self.tex = self.path.read_text()


class TexEquation(TexAsset):
    block: str
    eq: str

    def __init__(self, label: str, eq: str, folder: Union[str, Path] = 'config.eq_path',
                 block: str = 'equation'):
        self.block = block
        self.eq = eq  # without surrounding $$
        super().__init__(label, folder, obj_supplied=True)

    @property
    def tex_label(self) -> str:
        return config.eq_prefix + self.label

    @property
    def tex(self) -> str:
        return f'${self.eq}$'

    @property
    def tex_output(self) -> str:
        return config.eq_template.format(
            label=self.tex_label,
            block=self.block,
            eq=indent(self.eq, '\t')
        )


class TexTable(TexAsset):
    def __init__(self, label: str, df, folder: Union[str, Path] = 'config.tab_path',
                 caption: str = '', formatting: str = 'config.tab_formatting'):
        self.df = df
        self.caption = caption
        self.formatting = config.get_or_return(formatting)
        super().__init__(label, folder, obj_supplied=True)

    def _repr_html_(self):
        return self.df.to_html()

    @property
    def tex_label(self) -> str:
        return config.tab_prefix + self.label

    @property
    def tex(self):
        return config.tab_template.format(
            formatting=self.formatting,
            table=self.df.to_latex(),
            caption=self.caption,
            label=self.tex_label
        )

    def save(self) -> Asset:
        super().save()  # save tex
        return self


class StargazerTable(TexAsset):
    def __init__(self, label: str, stargazer, folder: Union[str, Path] = 'config.tab_path',
                 caption: str = '', use_template: bool = True,
                 formatting: str = 'config.tab_formatting'):
        self.stargazer = stargazer
        self.caption = caption
        self.use_template = use_template
        self.formatting = config.get_or_return(formatting)
        super().__init__(label, folder, obj_supplied=True)

    def _repr_html_(self):
        return self.stargazer.render_html()

    @property
    def tex_label(self) -> str:
        return config.tab_prefix + self.label

    @property
    def tex(self) -> str:
        orig_tex: str = self.stargazer.render_latex()
        if self.use_template:
            # remove the first three and last line from the stargazer output
            # to get only the tabular environment
            # MIGHT HAVE TO BECOME STARGAZER VERSION SPECIFIC
            tabular = '\n'.join(orig_tex.split('\n')[2:-1])
            tex = config.tab_template.format(
                formatting=self.formatting,
                table=tabular,
                caption=self.caption,
                label=self.tex_label
            )
        else:
            tex = orig_tex
        return tex


class Image(Asset, IPython.display.Image):
    _ext: str = None

    def __init__(self, label: str = None, folder: Union[str, Path] = 'config.img_path',
                 extension: str = None, url: str = None, data: object = None,
                 **kwargs):
        """Currently supports png, jpg and gif.  There are three ways to create an Image.

        To load an image from a file, specify the label and extension.  For example,
            >>> Image('test', extension='png', folder=Path('./img'))
        will load the file img/test.png.

        To load an image from the web, specify the url.  The extension is automatically inferred.  For example,
            >>> Image('test', url='http://test.org/monkey.png', folder=Path('./img'))
        will download http://test.org/monkey.png and save it to img/test.png.

        To load an image from a byte variable, use data.  The extension is automatically inferred.  For example,
            >>> Image('test', data=img_data, folder=Path('./img'))
        will save img_data to img/test.png.
        """
        # initialise label and folder
        Asset.__init__(self, label, folder)

        # initialise image
        if extension is not None:
            self._ext = extension
            IPython.display.Image.__init__(self, filename=self.path, **kwargs)
        elif url is not None:
            # use embed=True to ensure image is downloaded
            IPython.display.Image.__init__(self, url=url, embed=True, **kwargs)
        elif data is not None:
            IPython.display.Image.__init__(self, data=data, **kwargs)
        else:
            raise SyntaxError('No image provided. Expecting label and extension, url or data.')

    @property
    def extension(self) -> str:
        return self._ext or self.format

    @property
    def file_name(self) -> str:
        return f'{self.label}.{self.extension}'

    def save(self) -> Asset:
        with open(self.path, 'wb') as file:
            file.write(self.data)

    def load(self) -> Asset:
        self.reload()
        return self


class Plot(Asset):
    """Holds a plot, which must implement the `savefig()` or `write_image()` method"""
    plot: object
    extension: str
    savefig_args: dict

    def __init__(self, plot, label: str = None, folder: Union[str, Path] = 'config.img_path',
                 extension: str = 'pdf', savefig_args: dict = {'bbox_inches': 'tight'}):
        self.plot = plot
        self.extension = extension
        self.savefig_args = savefig_args
        super().__init__(label, folder)

    def _ipython_display_(self):
        if callable(getattr(self.plot, '_ipython_display_', None)):
            return self.plot._ipython_display_()

    @property
    def file_name(self) -> str:
        return f'{self.label}.{self.extension}'

    def save(self) -> Asset:
        if callable(getattr(self.plot, 'savefig', None)):
            # save matplotlib plots using savefig
            self.plot.savefig(self.path, **self.savefig_args)
        elif callable(getattr(self.plot, 'write_image', None)):
            # save plotly plots using write_image (https://plot.ly/python/static-image-export/)
            self.plot.write_image(str(self.path))
        # TODO raise error if neither method available
        return self

    def load(self) -> Asset:
        raise NotImplementedError('A Plot asset cannot be loaded, only saved')


class TexFigure(TexAsset):
    figure: Asset
    caption: str
    incl_args: str

    def __init__(self, label: str, figure: Asset, folder: Union[str, Path] = 'config.fig_path',
                 caption: str = '', incl_args: str = r'width=.9\linewidth'):
        self.figure = figure
        self.caption = caption
        self.incl_args = incl_args
        super().__init__(label, folder, obj_supplied=True)

    def _ipython_display_(self):
        IPython.display.display(self.figure)

    @property
    def tex_label(self) -> str:
        return config.fig_prefix + self.label

    @property
    def tex(self):
        return config.fig_template.format(
            label=self.tex_label,
            incl_args=self.incl_args,
            img_path=self.figure.rel_path,
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
