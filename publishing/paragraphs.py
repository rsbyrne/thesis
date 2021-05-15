import sys

if __name__ == '__main__':
    with open(sys.argv[1], mode = 'r') as file:
        text = file.read()
    text = text.replace('\n', '\n\n')
    with open(sys.argv[1], mode = 'w') as file:
        file.write(text)
