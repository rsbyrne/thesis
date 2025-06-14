###############################################################################
###############################################################################


from riskengine import load, aggregate


def plot_unique_quads(reg):
    frm = load.load_fb(reg)
    frm = frm.reset_index().groupby('datetime')['quadkey'] \
        .aggregate(lambda s: len(s.unique()))
    return frm.plot(figsize = (18, 6))


def show_quad_coverage(reg, aggtype, date = None):
    frm = load.load_fb(reg)
    if not date is None:
        frm = frm.loc[date]
#     frm = frm.loc[idx[:], ['31123012313030',], ['31123012313030'],] # TESTING
    spatialagg = aggregate.SpatialAggregator(aggtype, reg)
    weights = spatialagg[frm]
    weights = {
        key: sorted(weight, key = lambda x: x[-1])[-1][0]
            for key, weight in weights.items()
        }
#     frm = frm.reset_index().groupby('datetime')['quadkey'].unique()
#     frm = frm.apply(lambda s: sorted(set(weights[qk] for qk in s)))

    quadfrm = aggregate.make_quadfrm(weights)

    quadfrm['region'] = list(quadfrm.reset_index()['quadkey'].apply(lambda x: weights[x]))
    quadfrm = quadfrm.loc[quadfrm['region'] != 'Other']
    yield display(quadfrm.plot('region', figsize = (9, 9)))

    metro = load.load_sa(int(aggtype[-1]), reg)
    yield display(metro.loc[quadfrm['region'].unique()].reset_index().plot('name', figsize = (9, 9)))

#     return quadfrm, metro


###############################################################################
###############################################################################
