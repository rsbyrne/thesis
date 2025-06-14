import random
import os
import string

from . import Reseed, reseed

parentPath = os.path.abspath(os.path.dirname(__file__))
namesDir = os.path.join(parentPath, '_namesources')
pathFn = lambda n: os.path.join(namesDir, n)

with open(pathFn('cities.txt'), mode = 'r') as file:
    CITIES = file.read().split('\n')
with open(pathFn('english_words.txt'), mode = 'r') as file:
    ENGLISH = file.read().split('\n')
with open(pathFn('names.txt'), mode = 'r') as file:
    NAMES = file.read().split('\n')
PROPER = sorted(set([*CITIES, *NAMES]))

GREEK = [
    'alpha',
    'beta',
    'gamma',
    'delta',
    'epsilon',
    'zeta',
    'eta',
    'theta',
    'iota',
    'kappa',
    'lambda',
    'mu',
    'nu',
    'xi',
    'omicron',
    'pi',
    'rho',
    'sigma',
    'tau',
    'upsilon',
    'phi',
    'chi',
    'psi',
    'omega',
    ]
PHONETIC = [
    'Alfa',
    'Bravo',
    'Charlie',
    'Delta',
    'Echo',
    'Foxtrot',
    'Golf',
    'Hotel',
    'India',
    'Juliett',
    'Kilo',
    'Lima',
    'Mike',
    'November',
    'Oscar',
    'Papa',
    'Quebec',
    'Romeo',
    'Sierra',
    'Tango',
    'Uniform',
    'Victor',
    'Whiskey',
    'Xray',
    'Yankee',
    'Zulu',
    ]
WORDNUMS = [
    'zero',
    'one',
    'two',
    'three',
    'four',
    'five',
    'six',
    'seven',
    'eight',
    'nine',
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

def random_syllable():
    syllable = random.choice(SYLLABLES)
    return syllable

def random_word(length = 3):
    outWord = ''
    for _ in range(length):
        outWord += random_syllable()
    return outWord

def random_alphanumeric(length = 6):
    characters = 'abcdefghijklmnopqrstuvwxyz0123456789'
    choices = [random.choice(characters) for i in range(length)]
    return ''.join(choices)

@reseed
def get_random_alphanumeric(**kwargs):
    return random_alphanumeric(**kwargs)

@reseed
def get_random_word(*args, **kwargs):
    return random_word(*args, **kwargs)

@reseed
def get_random_phrase(phraselength = 2, wordlength = 2):
    # 2 * 2 yields 64 bits of entropy
    phraseList = []
    for _ in range(phraselength):
        phraseList.append(
            random_word(wordlength)
            )
    phrase = "-".join(phraseList)
    return phrase

@reseed
def get_random_english(n = 1):
    return '-'.join([random.choice(ENGLISH) for i in range(n)])
@reseed
def get_random_numerical(n = 1):
    return ''.join([random.choice(string.digits) for _ in range(n)])
@reseed
def get_random_greek(n = 1):
    return '-'.join([random.choice(GREEK) for i in range(n)])
@reseed
def get_random_city(n = 1):
    return '-'.join([random.choice(CITIES) for i in range(n)])
@reseed
def get_random_phonetic(n = 1):
    return '-'.join([random.choice(PHONETIC) for i in range(n)])
@reseed
def get_random_codeword(n = 1):
    return '-'.join([random.choice(CODEWORDS) for i in range(n)])
@reseed
def get_random_wordnum(n = 1):
    return '-'.join([random.choice(WORDNUMS) for i in range(n)])
@reseed
def get_random_name(n = 1):
    return '-'.join([random.choice(NAMES) for i in range(n)])
@reseed
def get_random_proper(n = 1):
    return '-'.join([random.choice(PROPER) for i in range(n)])
@reseed
def get_random_cityword():
    return '-'.join([random.choice(s) for s in [CITIES, WORDS]])
