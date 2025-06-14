import random

class Reseed:
    def __init__(self, randomseed = None):
        if randomseed is None:
            randomseed = random.random()
        self.randomseed = randomseed
    def __enter__(self):
        random.seed(self.randomseed)
    def __exit__(self, *args):
        random.seed()

def wordhash(hashID, nWords = 2):
    with Reseed(hashID):
        wordhashlist = []
        for n in range(nWords):
            randindex = random.randint(0, (len(wordlist) - 1))
            wordhashlist.append(wordlist[randindex])
        wordhashstr = '-'.join(wordhashlist).replace('--', '-').lower()
    return wordhashstr

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

def random_phrase(phraselength = 2, wordlength = 2):
    # 2 * 2 yields 64 bits of entropy
    phraseList = []
    for _ in range(phraselength):
        phraseList.append(
            random_word(wordlength)
            )
    phrase = "-".join(phraseList)
    return phrase

def random_alphanumeric(length = 6):
    characters = 'abcdefghijklmnopqrstuvwxyz0123456789'
    choices = [random.choice(characters) for i in range(length)]
    return ''.join(choices)

def get_random_alphanumeric(randomseed = None, **kwargs):
    with Reseed(randomseed):
        output = random_alphanumeric(**kwargs)
    return output

def get_random_word(randomseed = None, **kwargs):
    with Reseed(randomseed):
        output = random_word(**kwargs)
    return output

def get_random_phrase(randomseed = None, **kwargs):
    with Reseed(randomseed):
        output = random_phrase(**kwargs)
    return output

def get_random_mix(randomseed = None, **kwargs):
    with Reseed(randomseed):
        phrase = random_phrase(phraselength = 1)
        alphanum = random_alphanumeric()
        output = '-'.join((phrase, alphanum))
    return output
