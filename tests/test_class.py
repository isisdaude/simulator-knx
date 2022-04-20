

class Attr():
    def __init__(self):
        self.init = 0

    def attri(self):
        print('1 ',not hasattr(self, 'motion'))
        self.motion = 14
        print('2 ',not hasattr(self, 'motion'))
        delattr(self, 'motion')
        print('3 ',not hasattr(self, 'motion'))

A = Attr()
A.attri()
