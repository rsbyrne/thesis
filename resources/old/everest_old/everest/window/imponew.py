###############################################################################
''''''
###############################################################################

from dataclasses import dataclass

from PIL import Image as _PILImage

from .image import Image as _Image

@dataclass
class Translation:
    width: int
    height: int
    @classmethod
    def convert_to_pilx(cls, width, dcsx):
        return max(0, min(width, round(width * (dcsx - 0.5))))
    @classmethod
    def convert_to_pily(cls, height, dcsy):
        return max(0, min(height, round(height * (dcsy + 0.5))))
    @classmethod
    def convert_to_desx(cls, width, pilx):
        return pilx / width + 0.5
    @classmethod
    def convert_to_desy(cls, height, pily):
        return pily / height - 0.5
    def pilx(self, x):
        return self.convert_to_pilx(self.width, x)
    def pily(self, y):
        return self.convert_to_pily(self.height, y)
    def desx(self, x):
        return self.convert_to_desx(self.width, x)
    def desy(self, y):
        return self.convert_to_desy(self.height, y)
    def x(self, val):
        return self.pilx(val) if isinstance(val, float) else self.desx(val)
    def y(self, val):
        return self.pily(val) if isinstance(val, float) else self.desy(val)

class ImOp(_Image):
    ...

# def resize_dimension(trans)

class Resize(ImOp):
    __slots__ = ('tosize', 'inimage', 'grab')
    def __init__(self, image, size, grab = None, **kwargs):
        self.inimage, self.tosize = image, tosize
        self.grab = grab
        super().__init__(**kwargs)
    def get_pilimg(self):
        image = self.inimage.pilimg
        width, height = image.width, image.height
        towidth, toheight = tosize = tuple(
            val if isinstance(val, int) else min(dim, max(0, round(dim * val)))
                for val, dim in zip(self.newsize, image.size)
            )
        grab = self.grab
        if grab is None:
            return image.resize(size, **self.pilkwargs)
        trans = Translation(image.width, image.height)
        if width > towidth:
            image.crop


###############################################################################
###############################################################################
