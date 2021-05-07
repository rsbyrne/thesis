###############################################################################
''''''
###############################################################################

import pandas as pd

import aliases
import analysis
from thesiscode.utilities import hard_cache, hard_cache_df, hard_cache_df_multi

reader = analysis.utilities.AnalysisReader('Arrhenius', aliases.datadir)

def make_inputs():
    return reader['*/inputs']

def make_inputs_frame():
    _inputs = hard_cache('arrhenius_inputs', make_inputs)
    return analysis.common.make_inputs_frame(_inputs)
def get_inputs_frame():
    out = hard_cache_df('arrhenius_inputs', make_inputs_frame)
    if 'hashID' in out.columns:
        out = out.set_index('hashID')
    return out

def make_averages_frame():
    inputs = get_inputs_frame()
    return analysis.common.make_averages_frame(reader, inputs)
def get_averages_frame():
    out = hard_cache_df('arrhenius_averages', make_averages_frame)
    if 'hashID' in out.columns:
        out = out.set_index('hashID')
    return out

def make_endpoints_frames():
    inputs = get_inputs_frame()
    yield from analysis.common.make_endpoints_frames(reader, inputs)
def get_endpoints_frames():
    outs = hard_cache_df_multi(('arrhenius_initials', 'arrhenius_finals'), make_endpoints_frames)
    for out in outs:
        if 'hashID' in out.columns:
            out = out.set_index('hashID')
        yield out

def get_summary_frames():
#     frames = (get_inputs_frame(), *get_endpoints_frames(), get_averages_frame())
    frames = (get_inputs_frame(), get_averages_frame())
    commonkeys = set.intersection(*list(set(frame.index) for frame in frames))
    frames = tuple(frame.loc[commonkeys] for frame in frames)
    return frames

# def make_hashids(self):
#     return reader['*/hashID']
# hashIDs = hard_cache('isovisc_hashids', make_hashids)

###############################################################################
###############################################################################
