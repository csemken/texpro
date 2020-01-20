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
    contents = list(dir_path.iterdir())
    # contents each get pointers that are ├── with a final └── :
    pointers = [tee] * (len(contents) - 1) + [last]
    for pointer, path in zip(pointers, contents):
        yield prefix + pointer + path.name
        if path.is_dir(): # extend the prefix and recurse:
            extension = branch if pointer == tee else space
            # i.e. space because last, └── , above so no more |
            yield from tree(path, prefix=prefix+extension)
