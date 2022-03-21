
class ObservableA():
    def __init__(self, class1, class2):
        self.name = "A"
        self.classes = [class1, class2]

    def notify(self):
        for cl in self.classes:
            cl.update(self)



class ObservableB():
    def __init__(self, class1, class2):
        self.name = "B"
        self.classes = [class1, class2]

    def notify(self):
        for cl in self.classes:
            cl.update(self)



class ObserverC():
    def __init__(self):
        self.name = "C"
        self.observables = []

    def add_obs(self, device):
        self.observables.append(device)

    def update(self, device):
        print("in C, name of device is: ", device.name)



class ObserverD():
    def __init__(self):
        self.name = "D"
        self.observables = []

    def add_obs(self, device):
        self.observables.append(device)
    def update(self, device):
        print("in D, name of device is: ", device.name)


obsc = ObserverC()
obsd = ObserverD()
obsa = ObservableA(obsc, obsd)
obsb = ObservableB(obsc, obsd)

obsa.notify()
obsb.notify()
