
raise Exception

def load_frame(hashID, name, path = '.'):
    with Anchor(name, path):
        return FrameProxy(globevars._FRAMETAG_ + hashID).realised
def load_class(typeHash, name, path = '.'):
    with Anchor(name, path):
        return ClassProxy(globevars._CLASSTAG_ + typeHash).realised
