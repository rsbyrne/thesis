###############################################################################
''''''
###############################################################################

from aliases import *
from .. import common, utilities as analysis_utilities

reader = analysis_utilities.AnalysisReader('Isovisc', datadir)

@utilities.cache.hard_cache('isovisc_inputs')
def get_inputs_frame():
    return common.make_inputs_frame(reader['*/inputs'])

@utilities.cache.hard_cache('isovisc_averages')
def get_averages_frame():
    inputs = get_inputs_frame()
    return common.make_averages_frame(reader, inputs)

@utilities.cache.hard_cache('isovisc_initials', 'isovisc_finals')
def get_endpoints_frames():
    yield from \
        common.make_endpoints_frames(reader, get_inputs_frame())

def get_rasters():
    return common.get_rasters(reader, get_inputs_frame(), 'isovisc')
 
def get_summary_frames():
    frames = (
        get_inputs_frame(), *get_endpoints_frames(), get_averages_frame()
        )
    commonkeys = set.intersection(*list(set(frame.index) for frame in frames))
    frames = tuple(frame.loc[commonkeys] for frame in frames)
    return frames

# def make_hashids(self):
#     return reader['*/hashID']
# hashIDs = hard_cache('isovisc_hashids', make_hashids)

###############################################################################
###############################################################################
