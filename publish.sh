sudo rm -rf book/_build
python3 publishing/biblio.py
jb build book/
jb build book/ --builder pdflatex
ghp-import -n -p -f book/_build/html
