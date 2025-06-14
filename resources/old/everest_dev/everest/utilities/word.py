###############################################################################
''''''
###############################################################################


import os as _os
import string as _string

from .reseed import reseed as _reseed


parentPath = _os.path.abspath(_os.path.dirname(__file__))
namesDir = _os.path.join(parentPath, '_namesources')
pathFn = lambda n: _os.path.join(namesDir, n)

with open(pathFn('cities.txt'), mode = 'r') as file:
    CITIES = file.read().split('\n')
with open(pathFn('english_words.txt'), mode = 'r') as file:
    ENGLISH = file.read().split('\n')
with open(pathFn('names.txt'), mode = 'r') as file:
    NAMES = file.read().split('\n')
PROPER = sorted(set([*CITIES, *NAMES]))

GREEK = [
    'alpha', 'beta', 'gamma', 'delta', 'epsilon',
    'zeta', 'eta', 'theta', 'iota', 'kappa',
    'lambda', 'mu', 'nu', 'xi', 'omicron',
    'pi', 'rho', 'sigma', 'tau', 'upsilon',
    'phi', 'chi', 'psi', 'omega',
    ]
PHONETIC = [
    'Alfa', 'Bravo', 'Charlie', 'Delta', 'Echo',
    'Foxtrot', 'Golf', 'Hotel', 'India', 'Juliett',
    'Kilo', 'Lima', 'Mike', 'November', 'Oscar',
    'Papa', 'Quebec', 'Romeo', 'Sierra', 'Tango',
    'Uniform', 'Victor', 'Whiskey', 'Xray', 'Yankee',
    'Zulu',
    ]
WORDNUMS = [
    'zero', 'one', 'two', 'three', 'four',
    'five', 'six', 'seven', 'eight', 'nine',
    ]
CODEWORDS = sorted(set([
    *[n.lower() for n in PHONETIC],
    *[n.lower() for n in GREEK],
    *[n.lower() for n in WORDNUMS],
    ]))

def _make_syllables():
    consonants = list("bcdfghjklmnpqrstvwxyz")
    conclusters = [
        'bl', 'br', 'dr', 'dw', 'fl',
        'fr', 'gl', 'gr', 'kl', 'kr',
        'kw', 'pl', 'pr', 'sf', 'sk',
        'sl', 'sm', 'sn', 'sp', 'st',
        'sw', 'tr', 'tw'
        ]
    condigraphs = [
        'sh', 'ch', 'th', 'ph', 'zh',
        'ts', 'tz', 'ps', 'ng', 'sc',
        'gh', 'rh', 'wr'
        ]
    allcons = [*consonants, *conclusters, *condigraphs]
    vowels = [*list("aeiou")]
    voweldiphthongs = [
        'aa', 'ae', 'ai', 'ao', 'au',
        'ea', 'ee', 'ei', 'eo', 'eu',
        'ia', 'ie', 'ii', 'io', 'iu',
        'oa', 'oe', 'oi', 'oo', 'ou',
        'ua', 'ue', 'ui', 'uo', 'uu'
        ]
    allvowels = [*vowels, *voweldiphthongs]
    cvs = [consonant + vowel for vowel in allvowels for consonant in allcons]
    vcs = [vowel + consonant for consonant in allcons for vowel in allvowels]
    vcvs = [vowel + cv for vowel in allvowels for cv in cvs]
    cvcs = [consonant + vc for consonant in allcons for vc in vcs]
    syllables = [*cvs, *vcs, *vcvs, *cvcs]
    syllables = list(sorted(set(syllables)))
    return syllables

SYLLABLES = _make_syllables()

@_reseed
def get_random_syllable(seed = None):
    syllable = seed.rchoice(SYLLABLES)
    return syllable

@_reseed
def get_random_word(seed = None, length = 3):
    outWord = ''
    for _ in range(length):
        outWord += get_random_syllable(seed = seed)
    return outWord

@_reseed
def get_random_alphanumeric(seed = None, length = 6):
    characters = 'abcdefghijklmnopqrstuvwxyz0123456789'
    choices = [seed.rchoice(characters) for i in range(length)]
    return ''.join(choices)

@_reseed
def get_random_phrase(seed = None, phraselength = 2, wordlength = 2):
    # 2 * 2 yields 64 bits of entropy
    phraseList = []
    for _ in range(phraselength):
        phraseList.append(
            get_random_word(length = wordlength, seed = seed)
            )
    phrase = "-".join(phraseList)
    return phrase

@_reseed
def get_random_english(seed = None, n = 1):
    return '-'.join([seed.rchoice(ENGLISH) for i in range(n)])
@_reseed
def get_random_numerical(seed = None, n = 1):
    return ''.join([seed.rchoice(_string.digits) for _ in range(n)])
@_reseed
def get_random_greek(seed = None, n = 1):
    return '-'.join([seed.rchoice(GREEK) for i in range(n)])
@_reseed
def get_random_city(seed = None, n = 1):
    return '-'.join([seed.rchoice(CITIES) for i in range(n)])
@_reseed
def get_random_phonetic(seed = None, n = 1):
    return '-'.join([seed.rchoice(PHONETIC) for i in range(n)])
@_reseed
def get_random_codeword(seed = None, n = 1):
    return '-'.join([seed.rchoice(CODEWORDS) for i in range(n)])
@_reseed
def get_random_wordnum(seed = None, n = 1):
    return '-'.join([seed.rchoice(WORDNUMS) for i in range(n)])
@_reseed
def get_random_name(seed = None, n = 1):
    return '-'.join([seed.rchoice(NAMES) for i in range(n)])
@_reseed
def get_random_proper(seed = None, n = 1):
    return '-'.join([seed.rchoice(PROPER) for i in range(n)])
@_reseed
def get_random_cityword(seed = None):
    return '-'.join([seed.rchoice(s) for s in [CITIES, ENGLISH]])


###############################################################################
###############################################################################
