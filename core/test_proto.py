
import devices as dev
from system import IndividualAddress

button1 = dev.Button("button1", "M-0_B1", IndividualAddress(0,0,20), "enabled")

print(isinstance(button1, dev.FunctionalModule))
