python3 publishing/biblio.py
jb build book/
#jb build --builder pdfhtml book/
ghp-import -n -p -f book/_build/html
