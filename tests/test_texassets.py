import os
import tempfile
import unittest

import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.formula.api as smf
from stargazer.stargazer import Stargazer

from texpro import *


class FigTestSuite(unittest.TestCase):
    def setUp(self) -> None:
        # path setup
        self.doc_path = tempfile.TemporaryDirectory()
        config.doc_path = self.doc_path.name
        config.make_folders()

        # figures setup
        fig, ax = plt.subplots()
        self.plot = Plot(fig)
        self.tex_fig = TexFigure('test_fig', self.plot)

    def tearDown(self) -> None:
        self.doc_path.cleanup()

    def test_fig_save(self):
        # test save
        self.tex_fig.save()
        self.assertTrue(os.path.exists(os.path.join(self.doc_path.name, 'img', 'test_fig.pdf')))
        self.assertTrue(os.path.exists(os.path.join(self.doc_path.name, 'fig', 'test_fig.tex')))


class StargazerTestSuite(unittest.TestCase):
    def setUp(self) -> None:
        # path setup
        self.doc_path = tempfile.TemporaryDirectory()
        config.doc_path = self.doc_path.name
        config.make_folders()

        # regression table setup
        self.data = sns.load_dataset('iris')
        self.reg = [
            smf.ols('sepal_width ~ 1 + sepal_length', self.data).fit(),
            smf.ols('sepal_width ~ 0 + species + sepal_length', self.data).fit(),
        ]
        self.table = StargazerTable('sepal_reg', Stargazer(self.reg))

    def tearDown(self) -> None:
        self.doc_path.cleanup()

    def test_use_template(self):
        stargazer_tex = self.table.stargazer.render_latex()

        # use template
        self.assertNotEqual(self.table.tex, stargazer_tex)

        # do not use template
        self.table.use_template = False
        self.assertEqual(self.table.tex, stargazer_tex)