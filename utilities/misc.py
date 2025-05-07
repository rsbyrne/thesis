import io
import nbformat
from glob import glob

def word_count(*paths):
    filepath = os.path.join(*paths)
    if os.path.isdir(filepath) or '*' in filepath:
        if filepath.endswith('.ipynb') or filepath.endswith('.md'):
            paths = glob(filepath, recursive = True)
        else:
            paths = [
                *glob(filepath + '/**/*.ipynb', recursive = True),
                *glob(filepath + '/**/*.md', recursive = True),
                ]
        return sum(word_count(path) for path in paths)
    elif not os.path.isfile(filepath):
        raise FileNotFoundError
    if filepath.endswith('.md'):
        with open(filepath, 'r') as f:
            return len(f.read().replace('#', '').lstrip().split(' '))
    if filepath.endswith('.ipynb'):
        with io.open(filepath, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, 4)
        wordcount = 0
        for cell in nb.cells:
            if cell.cell_type == "markdown":
                wordcount += len(
                    cell['source'].replace('#', '').lstrip().split(' ')
                    )
        return wordcount
    raise TypeError(os.path.splitext(filepath)[-1])
