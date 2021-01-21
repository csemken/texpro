TeXpro is a collection of wrapper classes to display and save objects used in **Tex pro**jects, such as tables, plots, images, equations, and tex snippets.  The wrapper classes display these assets as rich content in Jupyter Notebooks, while saving them as separate `.tex` files that can be readily included in any (La)TeX document.  Thus, with minimal code and without copy-pasting, results can be shown in a Jupyter notebook, main TeX document, TeX presentation, and other documents.  TeXpro maintains a consistent folder and file structure, based on the TeX labels.

# Example

For an interactive example, see example/texpro_demo.ipynb and the example TeX file example/texpro_demo.tex.

# Development

TeXpro is build using [flit](https://flit.readthedocs.io/).  To build the package, (i) install flit, (ii) download the source code and (iii) run the following command inside the main folder:
```shell script
python3 -m flit install
```
This will install the required dependencies as well as TeXpro.