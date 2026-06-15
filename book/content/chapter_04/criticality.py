import pickle

from aliases import * # important this goes first to configure PATH

from everest.caching import cache

def incorporate_new_data(filename):
    new_data = pickle.loads((storagepath / filename).read_bytes())
    old_data = pickle.loads((storagepath / 'simple_critical.data').read_bytes())
    updated_data = {**old_data, **new_data}
    (storagepath / 'simple_critical.data').write_bytes(pickle.dumps(updated_data))
    make_frames(cache_refresh=True)
    return len(update_data) - len(old_data)

@cache(cachedir)
def make_frames():
    with (Path(storagedir) / 'simple_critical.data').open(mode='rb') as file:
        data = pickle.load(file)
    keys = tuple(sorted(('f', 'aspect', 'H', 'flux', 'etaDelta')))
    data = pd.DataFrame([
        [*params, results[-1]] for params, results in data.items()],
        columns=(*keys, 'alpha'),
        )
    data = data.loc[data['f'] >= 0.3]
    data['f'] = data['f'].replace(1., 0.999)
    # data.loc[data['f'] == 1.] = 0.999
    iso = data.loc[data['etaDelta'].isna()]
    arr = data.loc[~data['etaDelta'].isna()]
    mixed = data.loc[data['flux'].isna()]
    internal = data.loc[~data['flux'].isna()]
    outs = []
    for left in (iso, arr):
        for right in (mixed, internal):
            frm = pd.merge(left, right, 'inner').dropna(axis=1)
            if 'flux' in frm.columns:
                frm = frm.drop('flux', axis=1)
            outs.append(
                frm.set_index(sorted(set.intersection(*map(set, (frm, keys)))))
                ['alpha']
                .sort_index()
                )
    return tuple(outs)