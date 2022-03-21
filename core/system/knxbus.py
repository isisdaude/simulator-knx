
class KNXBus:
    '''Class that implements the transmission over the KNX Bus, between Actuators and FuntionalModules'''
    def __init__(self):
        self.name = "Central Observer"
        self.functional_modules = []
        self.states = []
        self._observers = [] #_ because private list, still visible from outside, but convention to indicate privacy with _

    def add_functional_module(self, device):
        self.functional_modules.append(device)
        self.states.append(device.state) # states of all functional modules added, with respecting indexes

    ### TODO: adapt this system with group addresses

    def notify(self): # alert the _observers
        for observer in self._observers:
            observer.update(self.functional_modules[self._observers.index(observer)]) #the observer Actuator class must have an update method

    def attach(self, observer): #If not in list, add the observer to the list
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer): # Remove the observer from the list
        try:
            self._observers.remove(observer)
        except ValueError:
            pass

    def update(self, notifier): # notifier is a functional module (e.g. button)
    # In this simple case, button switch the lights with teh same indexes
    # has to be improved to manage group addresses
    # maybe by passing it in argument, having a local list or filetring in functional module class (latter is bad idea)
        self.states[self.functional_modules.index(notifier)] = notifier.state
        print(f"{notifier.name} notified {self.name} of its state: {notifier.state}")
        self.notify()
