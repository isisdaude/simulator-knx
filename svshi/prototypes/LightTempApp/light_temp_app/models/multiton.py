###
### DO NOT TOUCH THIS FILE!!!
###

def multiton(cls):
    """
    Makes the given class a multiton: only a limited number of instances can exist. If an instance with
    a given name already exists, it is returned instead of creating a new object.
    """
    instances = {}
    allowed_names = ['led', 'button', 'thermometer']
    def getinstance(name):
        if name not in allowed_names:
            raise ValueError(f"Name '{name}' not allowed")
        if name not in instances:
            instances[name] = cls(name)
        return instances[name]  
    return getinstance