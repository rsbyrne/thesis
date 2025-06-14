###############################################################################
''''''
###############################################################################

from functools import partial as _partial

from PIL import Image as _PILImage

from .image import Image as _Image

class ImOp(_Image):
    ...


def rescale_width(image, targetwidth, **kwargs):
    width, height = image.width, image.height
    if width == targetwidth:
        return image
    scalefactor = targetwidth / width
    newlength = round(scalefactor * height)
    return image.resize((targetwidth, newlength), **kwargs)
def rescale_height(image, targetheight, **kwargs):
    width, height = image.width, image.height
    if height == targetheight:
        return image
    scalefactor = targetheight / height
    newlength = round(scalefactor * width)
    return image.resize((newlength, targetheight), **kwargs)

def extend_width(image, targetwidth, colour = (255, 255, 255), **kwargs):
    width, height = image.width, image.height
    discrepancy = targetwidth - width
    if discrepancy == 0:
        return image
    if discrepancy < 0:
        return image.crop((0, 0, targetwidth, height), **kwargs) #ltrb
    out = _PILImage.new(image.mode, (targetwidth, height), colour)
    out.paste(image, **kwargs)
    return out
def extend_height(image, targetheight, colour = (255, 255, 255), **kwargs):
    width, height = image.width, image.height
    discrepancy = targetheight - height
    if discrepancy == 0:
        return image
    if discrepancy < 0:
        return image.crop((0, 0, width, targetheight), **kwargs) #ltrb
    out = _PILImage.new(image.mode, (width, targetheight), colour)
    out.paste(image, **kwargs)
    return out

class Concat(ImOp):
    __slots__ = ('horiz', 'terms', 'pad')
    def __init__(self, *terms, horiz = True, pad = None, **kwargs):
        self.horiz = horiz
        self.terms = terms
        self.pad = pad
        super().__init__(*terms, **kwargs)
    def get_pilimg(self):
        images = tuple(im.pilimg for im in self.terms)
        horiz = self.horiz
        pad = self.pad
        longkey, shortkey = \
            ('width', 'height') if horiz else ('height', 'width')
        shortcriterion = min if pad is None else max
        shortlen = shortcriterion(getattr(im, shortkey) for im in images)
        if pad is None:
            rescaler = rescale_height if horiz else rescale_width
        else:
            rescaler = extend_height if horiz else extend_width
            rescaler = _partial(rescaler, colour = pad)
        images = tuple(rescaler(im, shortlen) for im in images)
        assert len(set(getattr(im, shortkey) for im in images)) == 1
        longlen = sum(getattr(im, longkey) for im in images)
        outdims = (longlen, shortlen) if horiz else (shortlen, longlen)
        out = _PILImage.new('RGB', outdims, **self.pilkwargs)
        pos = 0
        for image in images:
            pastedims =  (pos, 0) if horiz else (0, pos)
            out.paste(image, pastedims)
            pos += getattr(image, longkey)
        return out

def hstack(*terms, **kwargs):
    return Concat(*terms, **kwargs)
def vstack(*terms, **kwargs):
    return Concat(*terms, horiz = False, **kwargs)

def process_mask(mask, size):
    if mask is None:
        return mask
    if isinstance(mask, int):
        return _PILImage.new('L', size, mask)
    if isinstance(mask, float):
        if not 0 <= float <= 1:
            raise ValueError("Bad mask parameter.")
        mask = min(255, max(0, round(mask * 255)))
        return process_mask(mask, size)
    return mask.pilimg
def process_paste_coord(box, undersize, oversize, corner = 'tl'):
    width, height = (
        min(dim, max(0, round(dim * boxdim)))
            if isinstance(boxdim, float) else boxdim
        for dim, boxdim in zip(undersize, box)
        )
    tcorner, lcorner = corner[0] == 't', corner[1] == 'l'
    return (
        width if lcorner else width - oversize[0],
        height if tcorner else height - oversize[1],
        )

class Paste(ImOp):
    __slots__ = ('under', 'over', 'mask', 'coord', 'corner',)
    def __init__(self,
            under, over, mask = None, /, *,
            coord = (0, 0), corner = 'tl',
            **kwargs
            ):
        self.under, self.over, self.mask = under, over, mask
        self.coord, self.corner = coord, corner
        super().__init__(**kwargs)
    def get_pilimg(self):
        under, over = self.under.pilimg, self.over.pilimg
        mask = process_mask(self.mask, over.size)
        coord = process_paste_coord(
            self.coord, under.size, over.size, self.corner
            )
        out = _PILImage.new(under.mode, under.size)
        out.paste(under)
        out.paste(over, coord, mask, **self.pilkwargs)
        return out

def paste(*args, **kwargs):
    return Paste(*args, **kwargs)


class Resize(ImOp):
    __slots__ = ('newsize', 'toresize')
    def __init__(self, image, size, **kwargs):
        if isinstance(size, (float, int)):
            size = (size, size)
        else:
            size = tuple(size)
        self.toresize, self.newsize = image, size
        super().__init__(**kwargs)
    def get_pilimg(self):
        image = self.toresize.pilimg
        size = tuple(
            val if isinstance(val, int) else min(dim, max(0, round(dim * val)))
                for val, dim in zip(self.newsize, image.size)
            )
        return image.resize(size, **self.pilkwargs)

def resize(*args, **kwargs):
    return Resize(*args, **kwargs)

###############################################################################
###############################################################################
