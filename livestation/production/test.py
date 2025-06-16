from pathlib import Path
import pickle

with (
        Path(__file__).absolute().parent
        / 'simple_critical.data'
        ).open(mode='rb') as file:
    criticals = pickle.load(file)

print(next(iter(criticals)))