import os
import subprocess
from contextlib import contextmanager
from pathlib import Path
from warnings import warn


def check_valid(value, options, name):
    if value not in options:
        raise AttributeError(f'{name} has to be one of {options}')


def warn_if_not_dir(path: Path):
    if not path.is_dir():
        warn(f'{path} is not a directory, consider using config.make_folders()',
             ResourceWarning)


# prefix components:
space =  '    '
branch = '│   '
# pointers:
tee =    '├── '
last =   '└── '


def tree(dir_path: Path, prefix: str=''):
    """A recursive generator, given a directory Path object
    will yield a visual tree structure line by line
    with each line prefixed by the same characters
    (based on https://stackoverflow.com/a/59109706)
    """
    contents = sorted(dir_path.iterdir())
    # contents each get pointers that are ├── with a final └── :
    pointers = [tee] * (len(contents) - 1) + [last]
    for pointer, path in zip(pointers, contents):
        yield prefix + pointer + path.name
        if path.is_dir(): # extend the prefix and recurse:
            extension = branch if pointer == tee else space
            # i.e. space because last, └── , above so no more |
            yield from tree(path, prefix=prefix+extension)


@contextmanager
def cwd(path):
    """Temporarily change the working directory"""
    oldpwd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(oldpwd)


def run_notebook(notebook: Path, kernel: str, allow_errors=False):
    """Executes and saves a jupyter notebook in its parent folder"""
    import nbformat
    from nbconvert.preprocessors import ExecutePreprocessor, CellExecutionError

    with cwd(notebook.parent):
        with open(notebook.name) as f:
            nb = nbformat.read(f, as_version=4)
        ep = ExecutePreprocessor(kernel_name=kernel)
        try:
            ep.preprocess(nb)
        except CellExecutionError:
            if allow_errors:
                # error is already printed
                pass
            else:
                raise
        with open(notebook.name, 'w', encoding='utf-8') as f:
            nbformat.write(nb, f)


def update_example(folder=Path('example'), build_folder='.tex-build', run_nb=True, kernel='pycharm-baac2d74',
                   tex_cmd='xelatex -synctex=1 -interaction=nonstopmode -output-directory={build_folder} {file}.tex'):
    """Updates the example. Assumes working directory is the project directory."""
    from pdf2image import convert_from_path

    assert Path('README.md').is_file(), 'not in main project directory (containing README.md)'
    # make .tex-build folder
    (folder / build_folder).mkdir(exist_ok=True)

    # run demo notebook
    if run_nb:
        run_notebook(folder / 'texpro_demo.ipynb', kernel=kernel, allow_errors=True)

    # build document twice
    tex_cmd = tex_cmd.format(build_folder=build_folder, file='texpro_demo')
    run_args = dict(stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, text=True)
    with cwd(folder):
        for i in range(2):
            result = subprocess.run(tex_cmd, **run_args)
            if result.returncode != 0:
                raise Exception('Error compiling document.\n'
                                f'Command: {result.args}\n{result.stdout}')

    # move pdf, delete build folder
    pdf = folder / 'texpro_demo.pdf'
    (folder / build_folder / 'texpro_demo.pdf').replace(pdf)
    # (folder / build_folder).rmdir()

    # convert to image
    convert_from_path(pdf)[0].save(str(folder / 'texpro_demo.png'))

    # re-run demo notebook and convert to markdown
    if run_nb:
        run_notebook(folder / 'texpro_demo.ipynb', kernel=kernel)

    # TODO paste markdown into readme
