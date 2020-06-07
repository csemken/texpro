**TeXpro** is a python package to manage La**TeX pro**jects. Assets - such as equations, figures and tables - created using TeXpro are displayed in Jupyter and saved as LaTeX files.  With minimal code and without copy-pasting, results can be shown in a Jupyter notebook, main TeX document, presentation, and other documents.  TeXpro maintains a consistent folder and file structure, based on the TeX labels.

# Example

For an interactive example, see example/texpro_demo.ipynb and the example TeX file example/texpro_demo.tex.

# Development

TeXpro is build using [flit](https://flit.readthedocs.io/).  To build the package manually, install flit, download the source code and run the following command inside the main folder:
```shell script
python3 -m flit install
```
This will install the required dependencies and TeXpro.